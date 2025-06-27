import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from ..config import settings
from ..services.embeddings import embedding_service
from ..crud import search_similar_chunks, generate_answer, create_query_history

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self):
        self.embedding_service = embedding_service
        self.min_similarity_threshold = 0.7
        self.max_context_length = 4000
    
    def process_query(self, query: str, user_id: int, db: Session) -> Dict:
        """
        Process a user query using RAG pipeline
        
        Args:
            query: The user's question
            user_id: ID of the user making the query
            db: Database session
            
        Returns:
            Dictionary containing answer and source references
        """
        try:
            # Step 1: Generate query embedding
            logger.info(f"Processing query for user {user_id}: {query[:50]}...")
            query_embedding = self.embedding_service.generate_embedding(query)
            
            # Step 2: Find similar chunks from user's documents
            logger.info("Searching for similar chunks...")
            similar_chunks = search_similar_chunks(
                db=db,
                query_embedding=query_embedding,
                user_id=user_id,
                limit=5
            )
            
            # Check if we found any relevant chunks
            if not similar_chunks:
                return {
                    "answer": "I couldn't find any relevant information in your documents to answer this question.",
                    "sources": [],
                    "context_used": False
                }
            
            # Step 3: Create context from top chunks
            logger.info(f"Found {len(similar_chunks)} similar chunks")
            context, sources = self._build_context(similar_chunks)
            
            if not context:
                return {
                    "answer": "I couldn't find sufficiently relevant information in your documents to answer this question.",
                    "sources": [],
                    "context_used": False
                }
            
            # Step 4: Call OpenAI Chat API with context
            logger.info("Generating answer with OpenAI...")
            answer = generate_answer(query, context)
            
            # Step 5: Store query in history
            try:
                create_query_history(
                    db=db,
                    user_id=user_id,
                    query=query,
                    answer=answer,
                    sources_count=len(sources)
                )
                logger.info("Query stored in history")
            except Exception as e:
                logger.warning(f"Failed to store query history: {str(e)}")
            
            # Step 6: Return answer with source references
            return {
                "answer": answer,
                "sources": sources,
                "context_used": True,
                "query": query
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "answer": "I'm sorry, but I encountered an error while processing your query. Please try again.",
                "sources": [],
                "context_used": False,
                "error": str(e)
            }
    
    def _build_context(self, similar_chunks: List[Dict]) -> tuple[str, List[Dict]]:
        """
        Build context string and source references from similar chunks
        
        Args:
            similar_chunks: List of similar chunks with metadata
            
        Returns:
            Tuple of (context_string, source_references)
        """
        context_parts = []
        sources = []
        current_length = 0
        
        for chunk in similar_chunks:
            # Skip chunks with low similarity
            if chunk.get('similarity', 0) < self.min_similarity_threshold:
                continue
            
            chunk_text = chunk.get('chunk_text', '').strip()
            if not chunk_text:
                continue
            
            # Check if adding this chunk would exceed max context length
            if current_length + len(chunk_text) > self.max_context_length:
                break
            
            # Add chunk to context
            context_parts.append(chunk_text)
            current_length += len(chunk_text)
            
            # Add source reference
            source_info = {
                "document_id": chunk.get('document_id'),
                "document_filename": chunk.get('document_filename'),
                "chunk_index": chunk.get('chunk_index'),
                "similarity": round(chunk.get('similarity', 0), 3)
            }
            
            # Avoid duplicate sources from the same document
            if not any(s['document_id'] == source_info['document_id'] for s in sources):
                sources.append(source_info)
        
        context = "\n\n".join(context_parts)
        
        logger.info(f"Built context with {len(context_parts)} chunks, {len(context)} characters")
        return context, sources
    
    def validate_query(self, query: str) -> tuple[bool, Optional[str]]:
        """
        Validate the query input
        
        Args:
            query: The user's query
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query or not query.strip():
            return False, "Query cannot be empty"
        
        if len(query) > 500:
            return False, "Query is too long. Maximum 500 characters allowed."
        
        if len(query.strip()) < 3:
            return False, "Query is too short. Please provide at least 3 characters."
        
        return True, None

# Create global instance
rag_service = RAGService()