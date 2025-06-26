import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError, NoCredentialsError
import tempfile

# Load environment variables
load_dotenv()

def test_aws_credentials():
    """Test if AWS credentials are properly configured"""
    print("🔑 Testing AWS Credentials...")
    
    # Check if credentials exist
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    region = os.getenv('AWS_REGION')
    bucket_name = os.getenv('S3_BUCKET_NAME')
    
    if not all([access_key, secret_key, region, bucket_name]):
        print("❌ Missing AWS environment variables")
        print(f"Access Key: {'✓' if access_key else '❌'}")
        print(f"Secret Key: {'✓' if secret_key else '❌'}")
        print(f"Region: {'✓' if region else '❌'}")
        print(f"Bucket Name: {'✓' if bucket_name else '❌'}")
        return False
    
    print(f"Access Key: {access_key[:8]}...")
    print(f"Region: {region}")
    print(f"Bucket: {bucket_name}")
    return True

def test_s3_connection():
    """Test S3 connection and permissions"""
    print("\n🔗 Testing S3 Connection...")
    
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION')
        )
        
        # Test credentials by listing buckets
        response = s3_client.list_buckets()
        print("✅ Successfully connected to AWS S3")
        print(f"Found {len(response['Buckets'])} bucket(s) in your account")
        
        return s3_client
        
    except NoCredentialsError:
        print("❌ Invalid AWS credentials")
        return None
    except ClientError as e:
        print(f"❌ AWS Client Error: {e}")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def test_bucket_access(s3_client):
    """Test specific bucket access and permissions"""
    print("\n🪣 Testing Bucket Access...")
    
    bucket_name = os.getenv('S3_BUCKET_NAME')
    
    try:
        # Check if bucket exists and we have access
        s3_client.head_bucket(Bucket=bucket_name)
        print(f"✅ Bucket '{bucket_name}' exists and is accessible")
        
        # Test listing objects in bucket
        response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
        object_count = response.get('KeyCount', 0)
        print(f"📁 Bucket contains {object_count} object(s)")
        
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ Bucket '{bucket_name}' does not exist")
        elif error_code == '403':
            print(f"❌ Access denied to bucket '{bucket_name}'")
        else:
            print(f"❌ Error accessing bucket: {e}")
        return False

def test_upload_download():
    """Test upload and download functionality"""
    print("\n📤 Testing Upload/Download...")
    
    bucket_name = os.getenv('S3_BUCKET_NAME')
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    
    try:
        # Create a temporary test file
        test_content = "This is a test file for RAG system S3 configuration."
        test_key = "test-files/rag-system-test.txt"
        
        # Upload test file
        s3_client.put_object(
            Bucket=bucket_name,
            Key=test_key,
            Body=test_content,
            ContentType='text/plain'
        )
        print("✅ Successfully uploaded test file")
        
        # Download test file
        response = s3_client.get_object(Bucket=bucket_name, Key=test_key)
        downloaded_content = response['Body'].read().decode('utf-8')
        
        if downloaded_content == test_content:
            print("✅ Successfully downloaded and verified test file")
        else:
            print("❌ Downloaded content doesn't match uploaded content")
            return False
        
        # Clean up - delete test file
        s3_client.delete_object(Bucket=bucket_name, Key=test_key)
        print("✅ Successfully deleted test file")
        
        return True
        
    except Exception as e:
        print(f"❌ Upload/download test failed: {e}")
        return False

def show_bucket_info():
    """Show useful information about the bucket"""
    print("\n📊 Bucket Information:")
    
    bucket_name = os.getenv('S3_BUCKET_NAME')
    region = os.getenv('AWS_REGION')
    
    print(f"Bucket Name: {bucket_name}")
    print(f"Region: {region}")
    print(f"Console URL: https://s3.console.aws.amazon.com/s3/buckets/{bucket_name}")
    print(f"Bucket URL: https://{bucket_name}.s3.{region}.amazonaws.com/")

if __name__ == "__main__":
    print("🧪 Testing AWS S3 Configuration...\n")
    
    # Test credentials
    if not test_aws_credentials():
        print("\n❌ Fix your AWS environment variables first!")
        exit(1)
    
    # Test connection
    s3_client = test_s3_connection()
    if not s3_client:
        print("\n❌ Could not connect to AWS S3!")
        exit(1)
    
    # Test bucket access
    if not test_bucket_access(s3_client):
        print("\n❌ Could not access your S3 bucket!")
        exit(1)
    
    # Test upload/download
    if not test_upload_download():
        print("\n❌ Upload/download test failed!")
        exit(1)
    
    # Show summary
    show_bucket_info()
    print("\n🎉 All AWS S3 tests passed! Your configuration is ready!")