from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import auth, documents, query
from .database import engine
from . import models
from .config import settings

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="RAG System API",
    description="A Retrieval-Augmented Generation system with document management and query capabilities",
    version="1.0.0"
)

# Add CORS middleware with configurable origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(documents.router, prefix="/documents", tags=["documents"])
app.include_router(query.router, prefix="/query", tags=["query"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to RAG System API",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "RAG System API is running",
        "debug": settings.DEBUG,
        "log_level": settings.LOG_LEVEL
    } 