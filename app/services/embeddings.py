import time
import logging
from typing import List, Optional
from openai import OpenAI
from openai import RateLimitError
import numpy as np
from sqlalchemy.orm import Session

from ..config import settings
from ..models import Embedding, Document
from ..database import get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self):
        self.client = None
        self.model = settings.EMBEDDING_MODEL
        self.batch_size = 100
        self.max_retries = 3
    
    def _get_client(self):
        """Lazy initialization of OpenAI client"""
        if self.client is None:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        return self.client
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using OpenAI text-embedding-ada-002
        
        Args:
            text: The text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        for attempt in range(self.max_retries):
            try:
                response = self._get_client().embeddings.create(
                    input=text,
                    model=self.model
                )
                return response.data[0].embedding
                
            except RateLimitError as e:
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Rate limit hit, waiting {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Rate limit exceeded after {self.max_retries} attempts")
                    raise e
            except Exception as e:
                logger.error(f"Error generating embedding: {str(e)}")
                raise e
    
    def batch_generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batches
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1}, size: {len(batch)}")
            
            for attempt in range(self.max_retries):
                try:
                    response = self._get_client().embeddings.create(
                        input=batch,
                        model=self.model
                    )
                    
                    batch_embeddings = [data.embedding for data in response.data]
                    all_embeddings.extend(batch_embeddings)
                    break
                    
                except RateLimitError as e:
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt
                        logger.warning(f"Rate limit hit in batch, waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                    else:
                        logger.error(f"Rate limit exceeded for batch after {self.max_retries} attempts")
                        raise e
                except Exception as e:
                    logger.error(f"Error generating batch embeddings: {str(e)}")
                    raise e
        
        return all_embeddings
    
    def store_embeddings(self, db: Session, document_id: int, chunks: List[str], 
                        embeddings: List[List[float]]) -> bool:
        """
        Store embeddings in the database
        
        Args:
            db: Database session
            document_id: ID of the document
            chunks: List of text chunks
            embeddings: List of embedding vectors
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Verify document exists
            document = db.query(Document).filter(Document.id == document_id).first()
            if not document:
                logger.error(f"Document {document_id} not found")
                return False
            
            # Clear existing embeddings for this document
            db.query(Embedding).filter(Embedding.document_id == document_id).delete()
            
            # Store new embeddings
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                db_embedding = Embedding(
                    document_id=document_id,
                    chunk_text=chunk,
                    embedding=embedding,  # Store as JSON array
                    chunk_index=i
                )
                db.add(db_embedding)
            
            db.commit()
            logger.info(f"Stored {len(embeddings)} embeddings for document {document_id}")
            return True
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error storing embeddings: {str(e)}")
            return False
    
    def search_similar_chunks(self, db: Session, query_embedding: List[float], 
                            user_id: Optional[int] = None, limit: int = 5) -> List[dict]:
        """
        Search for similar chunks using cosine similarity
        
        Args:
            db: Database session
            query_embedding: Query embedding vector
            user_id: Optional user ID to filter by user's documents
            limit: Maximum number of results
            
        Returns:
            List of similar chunks with metadata
        """
        try:
            # Get all embeddings
            query = db.query(Embedding)
            
            # Filter by user if specified
            if user_id:
                query = query.join(Document).filter(Document.user_id == user_id)
            
            embeddings = query.all()
            
            if not embeddings:
                return []
            
            # Calculate cosine similarities
            similarities = []
            query_vector = np.array(query_embedding)
            
            for emb in embeddings:
                if emb.embedding:  # Ensure embedding exists
                    doc_vector = np.array(emb.embedding)
                    # Cosine similarity
                    similarity = np.dot(query_vector, doc_vector) / (
                        np.linalg.norm(query_vector) * np.linalg.norm(doc_vector)
                    )
                    similarities.append({
                        'embedding': emb,
                        'similarity': similarity
                    })
            
            # Sort by similarity (descending) and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            results = []
            for item in similarities[:limit]:
                emb = item['embedding']
                results.append({
                    'id': emb.id,
                    'document_id': emb.document_id,
                    'chunk_text': emb.chunk_text,
                    'chunk_index': emb.chunk_index,
                    'similarity': item['similarity'],
                    'document_filename': emb.document.filename if emb.document else None
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar chunks: {str(e)}")
            return []
    
    def get_document_chunks(self, db: Session, document_id: int) -> List[dict]:
        """
        Get all chunks for a specific document
        
        Args:
            db: Database session
            document_id: ID of the document
            
        Returns:
            List of chunks with metadata
        """
        try:
            embeddings = db.query(Embedding).filter(
                Embedding.document_id == document_id
            ).order_by(Embedding.chunk_index).all()
            
            return [
                {
                    'id': emb.id,
                    'chunk_text': emb.chunk_text,
                    'chunk_index': emb.chunk_index,
                    'embedding': emb.embedding
                }
                for emb in embeddings
            ]
            
        except Exception as e:
            logger.error(f"Error getting document chunks: {str(e)}")
            return []

# Create global instance
embedding_service = EmbeddingService() 