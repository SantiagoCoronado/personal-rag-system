from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas, auth
from ..config import settings
from ..services.pdf_processor import PDFProcessor
import PyPDF2
import io
import os
import boto3

router = APIRouter()

@router.post("/upload", response_model=schemas.Document)
async def upload_document(
    file: UploadFile = File(...),
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Validate file size (max 10MB)
    if file.size and file.size > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413, 
            detail="File too large. Maximum size is 10MB."
        )
    # Validate file type (PDF only)
    file_extension = file.filename.split('.')[-1].lower() if file.filename else ""
    if file_extension != "pdf":
        raise HTTPException(
            status_code=400,
            detail="File type not allowed. Only PDF files are accepted."
        )
    # Read file content
    content = await file.read()
    # Save to local filesystem
    os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_PATH, f"{current_user.id}_{file.filename}")
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Process PDF and extract chunks
    try:
        pdf_processor = PDFProcessor()
        chunks = pdf_processor.process_pdf(file_path)
        
        # Store metadata in database
        document_data = schemas.DocumentCreate(
            filename=file.filename,
            s3_url=file_path
        )
        document = crud.create_document(db=db, document=document_data, user_id=current_user.id)
        
        # Create embeddings for the chunks
        chunk_texts = [chunk['content'] for chunk in chunks]
        
        # Generate embeddings using the embedding service
        embeddings = crud.batch_get_embeddings(chunk_texts)
        
        # Store embeddings in the database
        crud.store_embeddings(db=db, document_id=document.id, chunks=chunk_texts, embeddings=embeddings)
        
        return document
        
    except Exception as e:
        # Clean up file if processing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.get("/", response_model=List[schemas.Document])
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    documents = crud.get_user_documents(db, user_id=current_user.id, skip=skip, limit=limit)
    return documents

@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    document = crud.delete_document(db, document_id=document_id, user_id=current_user.id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"} 