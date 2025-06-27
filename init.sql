-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- The application will create tables via SQLAlchemy
-- This just ensures pgvector is available