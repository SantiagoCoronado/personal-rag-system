# RAG System - Document Q&A with Retrieval-Augmented Generation

A minimal viable RAG (Retrieval-Augmented Generation) system for document Q&A built with FastAPI, SQLite, OpenAI, and Docker.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key (for full functionality)

### One-Command Deployment
```bash
./deploy.sh
```

This script will:
- Build Docker images
- Start all services (app + database)
- Run database migrations
- Perform health checks
- Provide access URLs

### Manual Setup

1. **Clone and navigate to the project**
```bash
git clone <your-repo-url>
cd rag-system
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Build and start services**
```bash
docker-compose up -d --build
```

4. **Verify deployment**
```bash
curl http://localhost:8000/health
```

## 📋 Environment Configuration

Create a `.env` file with the following variables (or copy from `env.example`):

```bash
# Database Configuration
DATABASE_URL=sqlite:///./rag_system.db

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-in-production-make-it-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI Configuration (required for embeddings and chat)
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002
MAX_TOKENS=500
TEMPERATURE=0.7

# AWS S3 Configuration (optional - for cloud storage)
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name

# File Upload Configuration
UPLOAD_PATH=/app/uploads
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=pdf

# Document Processing
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Application Configuration
DEBUG=False
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
```

**Important Notes:**
- **OPENAI_API_KEY**: Required for embeddings and chat functionality
- **SECRET_KEY**: Change this in production! Use a long, random string
- **AWS Configuration**: Optional, only needed if using S3 for file storage
- **DEBUG**: Set to `False` in production environments

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend UI   │    │   FastAPI App   │    │     SQLite      │
│  (Static HTML)  │◄──►│   + JWT Auth    │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   OpenAI API    │    │ File Storage    │
                       │  (Embeddings +  │    │ (Local/S3)      │
                       │   Chat)         │    │                 │
                       └─────────────────┘    └─────────────────┘
```

### Core Components
- **FastAPI**: REST API with automatic OpenAPI documentation and JWT authentication
- **SQLite**: Document and embedding storage with vector similarity search
- **OpenAI API**: Text embeddings (text-embedding-ada-002) and chat completion (GPT-3.5-turbo)
- **File Storage**: Local filesystem or AWS S3 for document storage
- **Authentication**: JWT-based user authentication with bcrypt password hashing
- **Docker**: Containerized deployment with health checks

## 📁 Project Structure

```
rag-system/
├── app/                          # Main application code
│   ├── api/                      # API route handlers
│   │   ├── auth.py              # Authentication endpoints
│   │   ├── documents.py         # Document management endpoints
│   │   └── query.py             # Query/RAG endpoints
│   ├── services/                # Business logic services
│   │   ├── embeddings.py        # OpenAI embedding service
│   │   ├── pdf_processor.py     # PDF text extraction
│   │   ├── rag.py               # RAG query processing
│   │   └── s3_service.py        # AWS S3 integration
│   ├── static/                  # Static web interface
│   │   └── index.html           # Single-page web UI
│   ├── auth.py                  # Authentication utilities
│   ├── config.py                # Configuration management
│   ├── crud.py                  # Database operations
│   ├── database.py              # Database connection
│   ├── main.py                  # FastAPI application entry point
│   ├── models.py                # SQLAlchemy models
│   └── schemas.py               # Pydantic schemas
├── tests/                       # Test files
├── uploads/                     # Local file storage
├── docker-compose.yml           # Docker services definition
├── Dockerfile                   # Application container
├── deploy.sh                    # One-command deployment script
├── requirements.txt             # Python dependencies
├── env.example                  # Environment variables template
└── README.md                    # This file
```

## 📚 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=your_username&password=your_password
```

#### Get Current User
```http
GET /auth/me
Authorization: Bearer <token>
```

### Document Management

#### Upload Document
```http
POST /documents/upload
Authorization: Bearer <token>
Content-Type: multipart/form-data

file=@document.pdf
```

#### List Documents
```http
GET /documents
Authorization: Bearer <token>
```

#### Delete Document
```http
DELETE /documents/{document_id}
Authorization: Bearer <token>
```

### Query System

#### Ask Question
```http
POST /query
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What is the main topic of the document?",
  "top_k": 5
}
```

## 🧪 Example Usage

### 1. Register and Login
```bash
# Register
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "testpass123"
  }'

# Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"

# Save the token from login response
TOKEN="your-jwt-token-here"
```

### 2. Upload Document
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@your-document.pdf"
```

### 3. Query Document
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key findings?",
    "top_k": 5
  }'
```

### 4. List Documents
```bash
curl -X GET "http://localhost:8000/documents" \
  -H "Authorization: Bearer $TOKEN"
```

## 🌐 Web Interface

Access the simple web interface at: `http://localhost:8000/ui`

The interface provides:
- User registration and login
- File upload
- Document querying
- Results display

## 🛠️ Development

### Run Tests
```bash
# Install dependencies
pip install -r requirements.txt

# Run critical path tests
python -m pytest test_critical.py -v

# Run simple task test
python -m pytest test_task8_simple.py -v

# Run all tests
python -m pytest tests/ -v

# Run specific test suites
python -m pytest tests/test_auth_api.py -v      # Authentication tests
python -m pytest tests/test_embeddings.py -v   # Embedding tests
python -m pytest tests/test_pdf_processor.py -v # PDF processing tests
```

### Local Development (without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your configuration

# Database URL is already configured for SQLite
# export DATABASE_URL="sqlite:///./rag_system.db"

# Run the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the validation script
python validate_env.py  # Check environment configuration
```

### Database Management
```bash
# Access SQLite database console
sqlite3 rag_system.db

# View application logs
docker-compose logs -f app

# Restart services
docker-compose restart

# Stop all services
docker-compose down
```

## 📊 Monitoring and Debugging

### Health Check
```bash
curl http://localhost:8000/health
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f app
docker-compose logs -f db
```

### Database Access
```bash
# Connect to SQLite database
sqlite3 rag_system.db

# View tables
.tables

# View embeddings
SELECT id, document_id, chunk_index, length(chunk_text) as text_length 
FROM embeddings LIMIT 5;
```

## 🔧 Configuration Options

### Upload Limits
- **Max file size**: 10MB (configurable via `MAX_FILE_SIZE`)
- **Supported formats**: PDF only (configurable via `ALLOWED_EXTENSIONS`)
- **Storage**: Local filesystem (`./uploads/`)

### Text Processing
- **Chunk size**: 1000 characters (configurable via `CHUNK_SIZE`)
- **Chunk overlap**: 200 characters (configurable via `CHUNK_OVERLAP`)
- **Embedding model**: text-embedding-ada-002

### Security
- **JWT token expiration**: 30 minutes (configurable)
- **CORS origins**: Configurable for cross-origin requests
- **Password hashing**: bcrypt with salt

## 🚀 Production Deployment

### Production Checklist

Before deploying to production, ensure you:

1. **Security Configuration**
   - Change `SECRET_KEY` to a long, random string
   - Set `DEBUG=False`
   - Use strong database passwords
   - Configure proper CORS origins
   - Set up HTTPS/SSL certificates

2. **Environment Variables**
   - Set all required environment variables
   - Use proper OpenAI API keys with sufficient credits
   - Configure AWS credentials for S3 (if using)

3. **Database**
   - For production, consider migrating to PostgreSQL or another managed database service
   - Enable regular backups of the SQLite database file
   - Monitor database file size and performance

4. **Monitoring**
   - Set up log aggregation
   - Configure health checks
   - Monitor OpenAI API usage and costs

5. **Scaling Considerations**
   - Use a reverse proxy (nginx, traefik)
   - Configure load balancing if needed
   - Consider using managed container services

### Production Docker Compose

For production, modify the docker-compose.yml:

```yaml
# Production overrides
version: '3.8'
services:
  app:
    environment:
      - DEBUG=False
      - LOG_LEVEL=WARNING
    restart: always
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M
```

## 🔒 Security Considerations

- **API Keys**: Store OpenAI and AWS keys securely, never commit to version control
- **Database**: Use strong passwords and limit network access
- **Authentication**: JWT tokens expire in 30 minutes by default
- **File Uploads**: Only PDF files are allowed, with 10MB size limit
- **CORS**: Configure specific origins, avoid wildcards in production
- **Logging**: Avoid logging sensitive information

## 🚨 Troubleshooting

### Common Issues

1. **OpenAI API errors**
   - Ensure `OPENAI_API_KEY` is set correctly
   - Check your OpenAI account has sufficient credits
   - Verify the API key has the necessary permissions

2. **Database connection issues**
   - Ensure SQLite database file exists and is accessible
   - Check application logs: `docker-compose logs app`
   - Verify database file permissions

3. **File upload failures**
   - Check file size is under 10MB
   - Ensure file is a valid PDF
   - Verify upload directory permissions

4. **Memory issues with large PDFs**
   - Reduce `CHUNK_SIZE` for large documents
   - Monitor container memory usage
   - Consider implementing streaming for very large files

### Reset Everything
```bash
# Stop services and remove all data
docker-compose down -v

# Remove uploaded files
rm -rf uploads/*

# Restart fresh
./deploy.sh
```

## 📝 API Response Examples

### Successful Query Response
```json
{
  "query": "What is machine learning?",
  "answer": "Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
  "sources": [
    {
      "document_id": 1,
      "filename": "ml_guide.pdf",
      "chunk_index": 0,
      "similarity_score": 0.89
    }
  ],
  "context_used": true
}
```

### Error Response
```json
{
  "detail": "No documents found for this user. Please upload a document before making queries."
}
```

## 💰 Cost Considerations

### OpenAI API Costs
- **Embeddings**: ~$0.0001 per 1K tokens (text-embedding-ada-002)
- **Chat Completions**: ~$0.0015 per 1K tokens (GPT-3.5-turbo input)
- **Typical Cost**: $0.01-0.05 per document upload and processing

### Cost Optimization Tips
- Use smaller chunk sizes for less important documents
- Implement caching for frequently asked questions
- Monitor API usage through OpenAI dashboard
- Consider using local embedding models for development

## ⚡ Performance Considerations

### File Processing
- **PDF Processing**: Can be memory-intensive for large files
- **Embedding Generation**: ~1-2 seconds per document chunk
- **Query Response**: ~2-3 seconds for typical queries

### Optimization Strategies
- Process large documents in batches
- Implement async processing for file uploads
- Use database connection pooling
- Cache frequent queries
- Consider using faster embedding models

### Resource Requirements
- **Memory**: 512MB minimum, 1GB recommended
- **Storage**: Depends on document volume (embeddings ~1KB per chunk)
- **CPU**: Low requirements, mostly I/O bound

## 🔗 URLs

- **Application**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative API Docs**: http://localhost:8000/redoc
- **Web Interface**: http://localhost:8000/ui
- **Health Check**: http://localhost:8000/health

## 📄 License

This project is created for educational purposes as part of a weekend RAG system implementation guide.

## 🔧 Advanced Features

### Available Features
- ✅ JWT Authentication with user registration/login
- ✅ PDF document upload and processing
- ✅ Vector embeddings with SQLite
- ✅ RAG-based question answering
- ✅ Document management (upload, list, delete)
- ✅ Web interface for easy interaction
- ✅ AWS S3 integration for cloud storage
- ✅ Docker containerization
- ✅ Health checks and monitoring
- ✅ Comprehensive test suite

### Future Enhancements
Consider adding these features for production use:
- Multi-user document sharing and permissions
- Support for additional file formats (DOCX, TXT, HTML)
- Advanced search and filtering capabilities
- Real-time collaboration features
- Production logging and monitoring dashboard
- Automated testing and CI/CD pipeline
- Rate limiting and API quotas
- Document versioning
- Bulk document processing
- Custom embedding models

## 📊 Dependencies

### Core Dependencies
```
fastapi==0.104.1          # Web framework
uvicorn==0.24.0           # ASGI server
sqlalchemy==2.0.31        # ORM
openai==1.35.0            # OpenAI API client
pypdf2==3.0.1             # PDF processing
python-jose[cryptography] # JWT handling
passlib[bcrypt]           # Password hashing
python-multipart          # File uploads
```

### Optional Dependencies
```
boto3==1.29.7             # AWS S3 integration
numpy==1.24.3             # Numerical operations
email-validator==2.1.1    # Email validation
```

## 🤝 Contributing

This is a minimal viable product (MVP) designed for learning and rapid prototyping. 

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python -m pytest tests/ -v`
5. Submit a pull request

### Code Style
- Follow PEP 8 for Python code
- Use type hints where possible
- Add docstrings to functions and classes
- Write tests for new features 