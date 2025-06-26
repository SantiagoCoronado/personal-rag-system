from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas, auth
from ..config import settings
import PyPDF2
import io
import os
import boto3

router = APIRouter()

@router.post("/", response_model=schemas.Document)
async def create_document(
    file: UploadFile = File(...),
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Validate file size
    if file.size and file.size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413, 
            detail=f"File too large. Maximum size is {settings.MAX_FILE_SIZE} bytes"
        )
    
    # Validate file extension
    file_extension = file.filename.split('.')[-1].lower() if file.filename else ""
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Upload to S3 if AWS credentials are configured
    s3_url = None
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY and settings.S3_BUCKET_NAME:
        try:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            
            # Create unique filename
            unique_filename = f"{current_user.id}_{file.filename}"
            
            # Upload to S3
            s3_client.put_object(
                Bucket=settings.S3_BUCKET_NAME,
                Key=unique_filename,
                Body=content,
                ContentType=file.content_type
            )
            
            s3_url = f"https://{settings.S3_BUCKET_NAME}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
            
        except Exception as e:
            # Fallback to local storage if S3 upload fails
            print(f"S3 upload failed: {e}")
            s3_url = None
    
    # Fallback to local storage if S3 is not configured or upload failed
    if not s3_url:
        # Create upload directory if it doesn't exist
        os.makedirs(settings.UPLOAD_PATH, exist_ok=True)
        
        # Save file to upload directory
        file_path = os.path.join(settings.UPLOAD_PATH, f"{current_user.id}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(content)
        
        s3_url = file_path  # Use local path as URL for now
    
    # Create document
    document_data = schemas.DocumentCreate(
        filename=file.filename,
        s3_url=s3_url
    )
    
    document = crud.create_document(db=db, document=document_data, user_id=current_user.id)
    
    # TODO: Process document into chunks and create embeddings
    # This would involve:
    # 1. Extracting text from the file
    # 2. Chunking the text
    # 3. Creating embeddings for each chunk
    # 4. Storing embeddings in the database
    
    return document

@router.get("/", response_model=List[schemas.Document])
async def get_documents(
    skip: int = 0,
    limit: int = 100,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    documents = crud.get_user_documents(db, user_id=current_user.id, skip=skip, limit=limit)
    return documents

@router.get("/{document_id}", response_model=schemas.Document)
async def get_document(
    document_id: int,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    document = crud.get_document(db, document_id=document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")
    return document

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