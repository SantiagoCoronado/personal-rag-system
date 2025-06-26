# app/services/s3_service.py
import boto3
from botocore.exceptions import ClientError
from app.config import settings
import os

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        self.bucket_name = settings.s3_bucket_name
    
    def upload_file(self, file_path: str, s3_key: str) -> str:
        """Upload file to S3 and return URL"""
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, s3_key)
            return f"https://{self.bucket_name}.s3.{settings.aws_region}.amazonaws.com/{s3_key}"
        except Exception as e:
            raise Exception(f"Failed to upload to S3: {e}")
    
    def download_file(self, s3_key: str, local_path: str):
        """Download file from S3 to local path"""
        try:
            self.s3_client.download_file(self.bucket_name, s3_key, local_path)
        except Exception as e:
            raise Exception(f"Failed to download from S3: {e}")
    
    def delete_file(self, s3_key: str):
        """Delete file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
        except Exception as e:
            raise Exception(f"Failed to delete from S3: {e}")