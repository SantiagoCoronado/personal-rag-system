from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from .. import crud, schemas, auth
from ..services.rag import rag_service

router = APIRouter()

@router.post("/", response_model=schemas.QueryResponse)
async def query_documents(
    query_request: schemas.QueryRequest,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Process a query against the user's documents using RAG
    
    - **query**: The question to ask about the documents (max 500 characters)
    - **top_k**: Maximum number of similar chunks to use (optional, default 5)
    """
    # Enhanced query validation
    query = query_request.query.strip()
    is_valid, error_message = rag_service.validate_query(query)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_message)
    
    # Check if user has any documents
    user_documents = crud.get_user_documents(db, user_id=current_user.id, limit=1)
    if not user_documents:
        raise HTTPException(
            status_code=400, 
            detail="You need to upload at least one document before making queries."
        )
    
    # Process query using RAG service
    result = rag_service.process_query(
        query=query,
        user_id=current_user.id,
        db=db
    )
    
    # Handle error case
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["answer"])
    
    return schemas.QueryResponse(
        query=result["query"],
        answer=result["answer"],
        sources=result["sources"],
        context_used=result["context_used"]
    )

@router.get("/history", response_model=List[schemas.QueryHistoryEntry])
async def get_query_history(
    skip: int = 0,
    limit: int = 20,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get the current user's query history
    
    - **skip**: Number of entries to skip (for pagination)
    - **limit**: Maximum number of entries to return (max 50)
    """
    # Validate limit
    if limit > 50:
        limit = 50
    
    # Get user's query history
    history = crud.get_user_query_history(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return history

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "RAG system is running"} 