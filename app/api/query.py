from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud, schemas, auth

router = APIRouter()

@router.post("/", response_model=schemas.QueryResponse)
async def query_documents(
    query_request: schemas.QueryRequest,
    current_user: schemas.User = Depends(auth.get_current_active_user),
    db: Session = Depends(get_db)
):
    # Get embedding for the query
    query_embedding = crud.get_embedding(query_request.query)
    
    # Find similar embeddings
    similar_embeddings = crud.get_similar_embeddings(
        db, 
        query_embedding=query_embedding, 
        top_k=query_request.top_k
    )
    
    if not similar_embeddings:
        raise HTTPException(status_code=404, detail="No relevant documents found")
    
    # Combine context from similar embeddings
    context = "\n".join([embedding.chunk_text for embedding in similar_embeddings])
    
    # Generate answer using OpenAI
    answer = crud.generate_answer(query_request.query, context)
    
    return schemas.QueryResponse(
        query=query_request.query,
        answer=answer,
        sources=similar_embeddings,
        confidence=0.85  # Placeholder confidence score
    )

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "RAG system is running"} 