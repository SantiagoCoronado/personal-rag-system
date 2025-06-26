#!/usr/bin/env python3
"""
Environment validation script for RAG System
Run this script to check if all required environment variables are set
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def validate_environment():
    """Validate that all required environment variables are set"""
    
    # Required variables
    required_vars = [
        "SECRET_KEY",
        "OPENAI_API_KEY",
        "AWS_ACCESS_KEY_ID", 
        "AWS_SECRET_ACCESS_KEY",
        "S3_BUCKET_NAME"
    ]
    
    # Optional variables with defaults
    optional_vars = {
        "DATABASE_URL": "postgresql://postgres:password@localhost:5432/rag_db",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "rag_db",
        "DB_USER": "postgres",
        "DB_PASSWORD": "password",
        "ALGORITHM": "HS256",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "OPENAI_MODEL": "gpt-3.5-turbo",
        "EMBEDDING_MODEL": "text-embedding-ada-002",
        "MAX_TOKENS": "500",
        "TEMPERATURE": "0.7",
        "AWS_REGION": "us-east-1",
        "UPLOAD_PATH": "./uploads",
        "MAX_FILE_SIZE": "10485760",
        "ALLOWED_EXTENSIONS": "pdf,txt,md",
        "CORS_ORIGINS": "http://localhost:3000,http://localhost:8000",
        "DEBUG": "True",
        "LOG_LEVEL": "INFO",
        "HOST": "0.0.0.0",
        "PORT": "8000"
    }
    
    print("🔍 Validating environment variables...")
    print("=" * 50)
    
    # Check required variables
    missing_required = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value == "your-secret-key-here-change-in-production":
            missing_required.append(var)
            print(f"❌ {var}: MISSING")
        else:
            # Mask sensitive values
            if "KEY" in var or "SECRET" in var or "PASSWORD" in var:
                masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
                print(f"✅ {var}: {masked_value}")
            else:
                print(f"✅ {var}: {value}")
    
    print("\n📋 Optional variables (with defaults):")
    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        if "KEY" in var or "SECRET" in var or "PASSWORD" in var:
            masked_value = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "***"
            print(f"   {var}: {masked_value}")
        else:
            print(f"   {var}: {value}")
    
    print("\n" + "=" * 50)
    
    if missing_required:
        print(f"❌ Validation failed! Missing required variables: {', '.join(missing_required)}")
        print("\nTo fix this:")
        print("1. Copy env.example to .env: cp env.example .env")
        print("2. Edit .env and set the missing variables")
        print("3. Run this script again to validate")
        return False
    else:
        print("✅ All required environment variables are set!")
        print("🚀 You can now start the application")
        return True

if __name__ == "__main__":
    validate_environment() 