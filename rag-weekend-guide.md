# Weekend RAG System - 30 Hour Sprint Guide

## Project Overview
Build a minimal viable RAG (Retrieval-Augmented Generation) system for document Q&A in one weekend using Windsurf AI agents.

**Total Time**: 25-30 hours  
**Approach**: MVP-first, security basics, deploy early  
**Stack**: FastAPI + PostgreSQL + OpenAI + Docker + AWS (or local)

---

## Agent Rules & Guidelines

### 🚀 Core Principles for Windsurf Agents
1. **MVP First**: Skip nice-to-haves, focus on working features
2. **Copy-Paste Ready**: All code should be complete and runnable
3. **No Placeholders**: Implement actual functionality, not TODOs
4. **Error Handling**: Basic try-catch, no complex recovery
5. **Security Basics**: JWT auth, input validation, CORS
6. **Fast Iteration**: Test manually, automated tests only for critical paths

### 🛑 What to SKIP
- Email verification
- Password reset
- Admin panels
- Complex UI
- Extensive logging
- Performance optimization (unless blocking)
- Multiple file formats (PDF only)
- User roles/permissions

---

## Hour-by-Hour Breakdown

### Hours 1-3: Project Setup & Basic API

#### Agent Task 1: Initialize Project
```markdown
Create a FastAPI project with this exact structure:
rag-system/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── crud.py
│   └── api/
│       ├── auth.py
│       ├── documents.py
│       └── query.py
├── requirements.txt
├── .env
├── Dockerfile
└── docker-compose.yml

Requirements.txt must include:
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
openai==1.3.5
pypdf2==3.0.1
pgvector==0.2.3
python-dotenv==1.0.0
boto3==1.29.7
```

#### Agent Task 2: Core Configuration
```python
# app/config.py - Complete this with all needed settings
# Must include: DATABASE_URL, SECRET_KEY, OPENAI_API_KEY, AWS credentials
# Use pydantic BaseSettings for env validation
```

#### Agent Task 3: Database Models
```python
# app/models.py - Create SQLAlchemy models for:
# - User (id, email, hashed_password, created_at)
# - Document (id, user_id, filename, s3_url, created_at)
# - Embedding (id, document_id, chunk_text, embedding[vector], chunk_index)
# Use pgvector for embedding column
```

### Hours 4-6: Authentication System

#### Agent Task 4: JWT Authentication
```python
# app/auth.py - Implement:
# - create_access_token(email: str) -> str
# - verify_token(token: str) -> dict
# - get_password_hash(password: str) -> str
# - verify_password(plain: str, hashed: str) -> bool
# - get_current_user dependency for FastAPI
```

#### Agent Task 5: Auth Endpoints
```python
# app/api/auth.py - Create endpoints:
# POST /register - Create new user
# POST /login - Return JWT token
# GET /me - Get current user info
# Include request/response schemas using Pydantic
```

### Hours 7-10: Document Processing

#### Agent Task 6: File Upload System
```python
# app/api/documents.py - Implement:
# POST /documents/upload - Handle PDF upload
# - Validate file type (PDF only)
# - Max size 10MB
# - Save to local filesystem first (./uploads/)
# - Store metadata in database
# GET /documents - List user's documents
# DELETE /documents/{id} - Delete document
```

#### Agent Task 7: PDF Processing
```python
# app/services/pdf_processor.py - Create service to:
# - Extract text from PDF using PyPDF2
# - Split into chunks (1000 chars, 200 overlap)
# - Clean text (remove extra whitespace, special chars)
# - Return list of text chunks with metadata
```

### Hours 11-15: Embeddings & Vector Storage

#### Agent Task 8: Embedding Service
```python
# app/services/embeddings.py - Implement:
# - generate_embedding(text: str) -> List[float]
#   Use OpenAI text-embedding-ada-002
# - batch_generate_embeddings(texts: List[str]) -> List[List[float]]
#   Process in batches of 100
# - Store embeddings in pgvector
```

#### Agent Task 9: Vector Search
```python
# app/crud.py - Add vector operations:
# - store_embeddings(document_id, chunks, embeddings)
# - search_similar_chunks(query_embedding, limit=5)
#   Use pgvector similarity search: 
#   SELECT * FROM embeddings ORDER BY embedding <-> query_embedding LIMIT 5
# - get_document_chunks(document_id)
```

### Hours 16-20: RAG Implementation

#### Agent Task 10: Query System
```python
# app/services/rag.py - Create RAG pipeline:
# - process_query(query: str, user_id: int) -> dict
#   1. Generate query embedding
#   2. Find similar chunks from user's documents
#   3. Create context from top 5 chunks
#   4. Call OpenAI Chat API with context
#   5. Return answer with source references
```

#### Agent Task 11: Query Endpoint
```python
# app/api/query.py - Implement:
# POST /query - Accept question, return answer
# - Validate query length (max 500 chars)
# - Include which documents were used
# - Handle no relevant context found
# GET /query/history - Return user's past queries (optional)
```

### Hours 21-24: Docker & Basic Frontend

#### Agent Task 12: Dockerization
```dockerfile
# Dockerfile - Multi-stage build:
# - Python 3.9 base
# - Install dependencies
# - Copy application
# - Run with uvicorn

# docker-compose.yml:
# - App service
# - PostgreSQL with pgvector
# - Volumes for uploads and postgres data
# - Environment variables
```

#### Agent Task 13: Simple Test UI
```python
# app/static/index.html - Basic HTML page with:
# - Login form
# - File upload
# - Query input box
# - Results display
# Use vanilla JavaScript, no framework
# Include in main.py: app.mount("/", StaticFiles(directory="static"))
```

### Hours 25-28: Testing & Deployment Prep

#### Agent Task 14: Critical Path Tests
```python
# test_critical.py - Test only:
# - User registration/login
# - File upload
# - Query processing
# Use pytest with test database
```

#### Agent Task 15: Local Deployment
```bash
# deploy.sh script:
# - Build Docker images
# - Run migrations
# - Start services
# - Health check

# Create README with:
# - Setup instructions
# - API documentation
# - Example requests
```

### Hours 29-30: Buffer & Polish

#### Agent Task 16: Error Handling
```python
# Add to all endpoints:
# - Try/catch blocks
# - Meaningful error messages
# - 400 for client errors
# - 500 for server errors
# - Log errors to console
```

---

## Critical Implementation Details

### Database Setup (pgvector)
```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Embeddings table with vector column
CREATE TABLE embeddings (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT,
    chunk_index INTEGER,
    embedding vector(1536), -- OpenAI ada-002 dimensions
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for similarity search
CREATE INDEX embeddings_embedding_idx ON embeddings 
USING ivfflat (embedding vector_cosine_ops);
```

### Environment Variables (.env)
```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/rag_db
SECRET_KEY=your-secret-key-here-make-it-long
OPENAI_API_KEY=sk-...
UPLOAD_PATH=./uploads
MAX_FILE_SIZE=10485760  # 10MB in bytes
```

### OpenAI Integration Pattern
```python
from openai import OpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generate_embedding(text: str) -> List[float]:
    response = client.embeddings.create(
        input=text,
        model="text-embedding-ada-002"
    )
    return response.data[0].embedding

def generate_answer(query: str, context: str) -> str:
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Answer based on the context provided."},
            {"role": "user", "content": f"Context: {context}\n\nQuestion: {query}"}
        ],
        max_tokens=500,
        temperature=0.7
    )
    return response.choices[0].message.content
```

### Quick Start Commands
```bash
# Development
pip install -r requirements.txt
uvicorn app.main:app --reload

# Docker
docker-compose up -d

# Test upload
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.pdf"

# Test query
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?"}'
```

---

## Success Checklist

### Must Have (Core Features)
- [ ] User registration and login
- [ ] JWT authentication on all endpoints
- [ ] PDF upload and storage
- [ ] Text extraction and chunking
- [ ] Embedding generation and storage
- [ ] Vector similarity search
- [ ] Query answering with context
- [ ] Basic error handling
- [ ] Docker setup working

### Nice to Have (If Time Permits)
- [ ] Query history
- [ ] Multiple file format support
- [ ] Batch document upload
- [ ] Delete document functionality
- [ ] Simple UI for testing
- [ ] AWS S3 integration
- [ ] Rate limiting

### Not Needed (Skip These)
- ❌ Email verification
- ❌ Forgot password
- ❌ User profiles
- ❌ Document sharing
- ❌ Complex permissions
- ❌ Production logging
- ❌ Monitoring/metrics
- ❌ Automated testing beyond basics

---

## Common Issues & Quick Fixes

### pgvector not working
```bash
# Use the pgvector Docker image
docker pull pgvector/pgvector:pg15
```

### OpenAI rate limits
```python
# Add retry logic
import time
def retry_on_rate_limit(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except openai.RateLimitError:
            time.sleep(2 ** i)
    raise
```

### Large PDF handling
```python
# Process in chunks to avoid memory issues
def process_large_pdf(file_path, chunk_size=10):
    reader = PyPDF2.PdfReader(file_path)
    for i in range(0, len(reader.pages), chunk_size):
        pages = reader.pages[i:i+chunk_size]
        # Process pages batch
```

---

## Final Notes

1. **Start Simple**: Get auth + upload working first
2. **Test Manually**: Use Postman or curl for quick testing
3. **Deploy Early**: Get Docker working by hour 20
4. **Focus on Flow**: User should be able to upload PDF and ask questions
5. **Security Basics**: JWT + input validation is enough for MVP

Remember: The goal is a WORKING system, not a perfect one. Every feature should be testable end-to-end.