from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import openai
from . import models, schemas, auth
from .config import settings

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

# Embedding CRUD operations
def create_embedding(db: Session, embedding: schemas.EmbeddingBase, document_id: int):
    db_embedding = models.Embedding(**embedding.dict(), document_id=document_id)
    db.add(db_embedding)
    db.commit()
    db.refresh(db_embedding)
    return db_embedding

def get_similar_embeddings(db: Session, query_embedding: List[float], top_k: int = 5):
    # Use pgvector to find similar embeddings
    similar_embeddings = db.query(models.Embedding).order_by(
        func.cosine_distance(models.Embedding.embedding, query_embedding)
    ).limit(top_k).all()
    return similar_embeddings

# OpenAI operations
def get_embedding(text: str) -> List[float]:
    """Get embedding for text using OpenAI API"""
    client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.embeddings.create(
        input=text,
        model=settings.EMBEDDING_MODEL
    )
    return response.data[0].embedding

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