# RAG System

A Retrieval-Augmented Generation (RAG) system built with FastAPI, PostgreSQL with pgvector, and OpenAI.

## Features

- **User Authentication**: JWT-based authentication system
- **Document Management**: Upload and manage documents (PDF, text files)
- **Vector Search**: Semantic search using OpenAI embeddings and pgvector
- **RAG Queries**: Ask questions and get answers based on your documents
- **Docker Support**: Easy deployment with Docker and Docker Compose
- **Environment Validation**: Built-in validation for required configuration
- **File Upload Security**: Configurable file size limits and type restrictions

## Project Structure

```
rag-system/
├── app/
│   ├── main.py          # FastAPI application entry point
│   ├── config.py        # Configuration and environment variables
│   ├── database.py      # Database connection and session management
│   ├── models.py        # SQLAlchemy models
│   ├── schemas.py       # Pydantic schemas for validation
│   ├── auth.py          # Authentication utilities
│   ├── crud.py          # Database operations
│   └── api/
│       ├── auth.py      # Authentication endpoints
│       ├── documents.py # Document management endpoints
│       └── query.py     # RAG query endpoints
├── requirements.txt     # Python dependencies
├── env.example         # Environment variables template
├── validate_env.py     # Environment validation script
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose configuration
└── README.md          # This file
```

## Prerequisites

- Python 3.11+
- PostgreSQL with pgvector extension
- OpenAI API key
- AWS credentials (for S3 storage)
- Docker and Docker Compose (optional)

## Quick Start with Docker

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd rag-system
   ```

2. **Set up environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

3. **Validate environment** (optional):
   ```bash
   python validate_env.py
   ```

4. **Start the services**:
   ```bash
   docker-compose up -d
   ```

5. **Access the API**:
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Manual Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up PostgreSQL with pgvector**:
   ```bash
   # Install pgvector extension
   CREATE EXTENSION IF NOT EXISTS vector;
   ```

3. **Configure environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. **Validate environment**:
   ```bash
   python validate_env.py
   ```

5. **Run the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

## Configuration

The application uses a comprehensive configuration system with the following sections:

### Required Environment Variables
- `SECRET_KEY`: JWT secret key for authentication
- `OPENAI_API_KEY`: Your OpenAI API key
- `AWS_ACCESS_KEY_ID`: AWS access key for S3 storage
- `AWS_SECRET_ACCESS_KEY`: AWS secret key
- `S3_BUCKET_NAME`: S3 bucket name for file storage

### Database Configuration
- `DATABASE_URL`: Complete PostgreSQL connection string
- `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Individual database settings

### OpenAI Configuration
- `OPENAI_MODEL`: Model for text generation (default: gpt-3.5-turbo)
- `EMBEDDING_MODEL`: Model for embeddings (default: text-embedding-ada-002)
- `MAX_TOKENS`: Maximum tokens for responses (default: 500)
- `TEMPERATURE`: Response creativity (default: 0.7)

### File Upload Configuration
- `UPLOAD_PATH`: Directory for file uploads (default: ./uploads)
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 10MB)
- `ALLOWED_EXTENSIONS`: Comma-separated list of allowed file types

### Security Configuration
- `CORS_ORIGINS`: Allowed origins for CORS (comma-separated)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration time

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/token` - Login and get access token
- `GET /auth/me` - Get current user info

### Documents
- `POST /documents/` - Upload a new document
- `GET /documents/` - List user's documents
- `GET /documents/{id}` - Get specific document
- `DELETE /documents/{id}` - Delete document

### Query
- `POST /query/` - Ask a question about your documents
- `GET /query/health` - Health check

## Usage Example

1. **Register a user**:
   ```bash
   curl -X POST "http://localhost:8000/auth/register" \
        -H "Content-Type: application/json" \
        -d '{"email":"user@example.com","username":"testuser","password":"password123"}'
   ```

2. **Login and get token**:
   ```bash
   curl -X POST "http://localhost:8000/auth/token" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=testuser&password=password123"
   ```

3. **Upload a document**:
   ```bash
   curl -X POST "http://localhost:8000/documents/" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -F "title=My Document" \
        -F "file=@document.pdf"
   ```

4. **Ask a question**:
   ```bash
   curl -X POST "http://localhost:8000/query/" \
        -H "Authorization: Bearer YOUR_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"query":"What is the main topic of the document?","top_k":3}'
   ```

## Environment Validation

The application includes a validation script to check your environment setup:

```bash
python validate_env.py
```

This script will:
- Check for required environment variables
- Validate sensitive values are properly set
- Show current configuration values (masked for security)
- Provide guidance for missing variables

## Development

To run in development mode with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Security Features

- **File Upload Validation**: Configurable file size limits and type restrictions
- **JWT Authentication**: Secure token-based authentication
- **CORS Protection**: Configurable cross-origin resource sharing
- **Environment Validation**: Built-in checks for required configuration
- **Sensitive Data Masking**: Secure logging and validation output

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. 