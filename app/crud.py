from sqlalchemy.orm import Session
from typing import List, Optional
import openai
import numpy as np
from . import models, schemas, auth
from .config import settings
from .services.embeddings import embedding_service

# User CRUD operations
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Document CRUD operations
def get_document(db: Session, document_id: int):
    return db.query(models.Document).filter(models.Document.id == document_id).first()

def get_documents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Document).offset(skip).limit(limit).all()

def get_user_documents(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Document).filter(models.Document.user_id == user_id).offset(skip).limit(limit).all()

def create_document(db: Session, document: schemas.DocumentCreate, user_id: int):
    db_document = models.Document(**document.dict(), user_id=user_id)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def delete_document(db: Session, document_id: int, user_id: int):
    document = db.query(models.Document).filter(
        models.Document.id == document_id,
        models.Document.user_id == user_id
    ).first()
    if document:
        db.delete(document)
        db.commit()
    return document

# Vector operations using the embedding service
def store_embeddings(db: Session, document_id: int, chunks: List[str], 
                    embeddings: List[List[float]]) -> bool:
    """
    Store embeddings for document chunks
    
    Args:
        db: Database session
        document_id: ID of the document
        chunks: List of text chunks
        embeddings: List of embedding vectors
        
    Returns:
        True if successful, False otherwise
    """
    return embedding_service.store_embeddings(db, document_id, chunks, embeddings)

def search_similar_chunks(db: Session, query_embedding: List[float], 
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
    return embedding_service.search_similar_chunks(db, query_embedding, user_id, limit)

def get_document_chunks(db: Session, document_id: int) -> List[dict]:
    """
    Get all chunks for a specific document
    
    Args:
        db: Database session
        document_id: ID of the document
        
    Returns:
        List of chunks with metadata
    """
    return embedding_service.get_document_chunks(db, document_id)

# OpenAI operations
def get_embedding(text: str) -> List[float]:
    """Get embedding for text using OpenAI API"""
    return embedding_service.generate_embedding(text)

def batch_get_embeddings(texts: List[str]) -> List[List[float]]:
    """Get embeddings for multiple texts in batches"""
    return embedding_service.batch_generate_embeddings(texts)

def generate_answer(query: str, context: str) -> str:
    """Generate answer using OpenAI API"""
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context. Only use information from the context to answer questions."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ],
        max_tokens=settings.MAX_TOKENS,
        temperature=settings.TEMPERATURE
    )
    return response.choices[0].message.content

# Query History CRUD operations
def create_query_history(db: Session, user_id: int, query: str, answer: str, sources_count: int):
    """Create a new query history entry"""
    db_query = models.QueryHistory(
        user_id=user_id,
        query=query,
        answer=answer,
        sources_count=sources_count
    )
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query

def get_user_query_history(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    """Get query history for a user"""
    return db.query(models.QueryHistory).filter(
        models.QueryHistory.user_id == user_id
    ).order_by(models.QueryHistory.created_at.desc()).offset(skip).limit(limit).all()