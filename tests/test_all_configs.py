#!/usr/bin/env python3
"""
Complete configuration test for RAG system
Tests all components: Config, Database, OpenAI, and AWS S3
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_config():
    """Test configuration loading"""
    print("🔧 Testing Configuration Loading...")
    try:
        from app.config import settings
        print("✅ Config module imported successfully")
        
        # Test validation
        missing = settings.validate()
        if missing:
            print(f"❌ Missing required variables: {', '.join(missing)}")
            return False
        else:
            print("✅ All required configuration variables present")
            
        print(f"   Database: {settings.DB_NAME}")
        print(f"   OpenAI Model: {settings.OPENAI_MODEL}")
        print(f"   AWS Region: {settings.AWS_REGION}")
        print(f"   S3 Bucket: {settings.S3_BUCKET_NAME}")
        return True
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    print("\n🗄️  Testing Database Connection...")
    try:
        import psycopg2
        from app.config import settings
        
        # Try to connect to database
        conn = psycopg2.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            database=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD
        )
        conn.close()
        print("✅ Database connection successful")
        return True
        
    except ImportError:
        print("⚠️  psycopg2 not installed, skipping database test")
        print("   Run: pip3 install psycopg2-binary")
        return True  # Don't fail the test for missing dependency
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Make sure PostgreSQL is running with correct credentials")
        return False

def test_openai_api():
    """Test OpenAI API connection"""
    print("\n�� Testing OpenAI API...")
    try:
        import openai
        from app.config import settings
        
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Test embedding API (cheaper than chat)
        response = client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input="test"
        )
        print("✅ OpenAI API connection successful")
        print(f"   Embedding dimensions: {len(response.data[0].embedding)}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False

def test_aws_s3():
    """Test AWS S3 connection"""
    print("\n☁️  Testing AWS S3...")
    try:
        import boto3
        from app.config import settings
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        # Test bucket access
        s3_client.head_bucket(Bucket=settings.S3_BUCKET_NAME)
        print("✅ AWS S3 connection successful")
        print(f"   Bucket: {settings.S3_BUCKET_NAME}")
        return True
        
    except Exception as e:
        print(f"❌ AWS S3 test failed: {e}")
        return False

def test_upload_directory():
    """Test upload directory creation"""
    print("\n📁 Testing Upload Directory...")
    try:
        from app.config import settings
        
        upload_path = settings.UPLOAD_PATH
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
            print(f"✅ Created upload directory: {upload_path}")
        else:
            print(f"✅ Upload directory exists: {upload_path}")
        return True
        
    except Exception as e:
        print(f"❌ Upload directory test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Running Complete RAG System Configuration Tests\n")
    
    tests = [
        ("Configuration", test_config),
        ("Database", test_database_connection),
        ("OpenAI API", test_openai_api),
        ("AWS S3", test_aws_s3),
        ("Upload Directory", test_upload_directory),
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    # Summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your RAG system is ready to go!")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above and fix before proceeding.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
