import os
import boto3
from botocore.exceptions import ClientError
from typing import Optional
import uuid


class StorageService:
    """S3-compatible storage service"""
    
    def __init__(self):
        self.enabled = os.getenv("S3_ENABLED", "false").lower() == "true"
        self.endpoint = os.getenv("S3_ENDPOINT", "localhost:9000")
        self.access_key = os.getenv("S3_ACCESS_KEY", "minioadmin")
        self.secret_key = os.getenv("S3_SECRET_KEY", "minioadmin")
        self.bucket = os.getenv("S3_BUCKET", "smartclean")
        self.public_url = os.getenv("S3_PUBLIC_URL", f"http://{self.endpoint}/{self.bucket}")
        
        if self.enabled:
            self.client = boto3.client(
                's3',
                endpoint_url=f"http://{self.endpoint}",
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key
            )
            self._create_bucket()
    
    def _create_bucket(self):
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except ClientError:
            self.client.create_bucket(Bucket=self.bucket)
    
    async def upload_file(self, file_data: bytes, filename: str, folder: str = "uploads") -> str:
        """Upload file and return URL"""
        key = f"{folder}/{filename}"
        
        if self.enabled:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=file_data,
                ContentType=self._get_content_type(filename)
            )
            return f"{self.public_url}/{key}"
        else:
            # Local storage
            local_path = os.path.join("uploads", folder, filename)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                f.write(file_data)
            return f"/uploads/{folder}/{filename}"
    
    def _get_content_type(self, filename: str) -> str:
        ext = filename.split('.')[-1].lower()
        types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp',
            'webm': 'audio/webm',
            'mp3': 'audio/mpeg'
        }
        return types.get(ext, 'application/octet-stream')


storage = StorageService()
