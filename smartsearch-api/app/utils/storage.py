"""
Storage client utility.
Handles file uploads/downloads using MinIO/S3 with a local filesystem fallback for offline testing.
"""

import os
import logging
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from app.core.config import settings

logger = logging.getLogger(__name__)

class StorageClient:
    def __init__(self):
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.local_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "uploads"))
        self.use_fallback = False
        self.s3 = None

        # Try to initialize boto3 S3 client
        try:
            # We configure MinIO as an S3 compatible service
            self.s3 = boto3.client(
                "s3",
                endpoint_url=f"http://{settings.MINIO_ENDPOINT}" if not settings.MINIO_USE_SSL else f"https://{settings.MINIO_ENDPOINT}",
                aws_access_key_id=settings.MINIO_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_SECRET_KEY,
                config=Config(signature_version="s3v4"),
                verify=False
            )
            # Test connection by listing buckets or checking head
            self.s3.list_buckets()
            logger.info("MinIO/S3 connection established successfully.")
            
            # Ensure bucket exists
            try:
                self.s3.create_bucket(Bucket=self.bucket_name)
                logger.info(f"Created MinIO bucket: '{self.bucket_name}'")
            except ClientError as e:
                # If bucket already exists, that's fine
                if e.response['Error']['Code'] not in ('BucketAlreadyExists', 'BucketAlreadyOwnedByYou'):
                    raise e
        except Exception as e:
            logger.warning(f"Could not connect to MinIO ({e}). Falling back to local filesystem storage.")
            self.use_fallback = True
            os.makedirs(self.local_dir, exist_ok=True)

    def upload_file(self, file_data: bytes, file_name: str) -> str:
        """
        Upload file data and return the file_key/path.
        """
        # Generate a unique directory/prefix structure or use direct name
        file_key = f"uploads/{file_name}"
        
        if self.use_fallback:
            local_path = os.path.join(self.local_dir, file_name)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(file_data)
            logger.info(f"Stored file locally at: {local_path}")
            return file_key

        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_data
            )
            logger.info(f"Uploaded file '{file_key}' to MinIO bucket '{self.bucket_name}'.")
            return file_key
        except Exception as e:
            logger.error(f"Error uploading file to MinIO: {e}. Attempting local write...")
            # Emergency fallback write
            local_path = os.path.join(self.local_dir, file_name)
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, "wb") as f:
                f.write(file_data)
            return f"fallback://{file_name}"

    def download_file(self, file_key: str) -> bytes:
        """
        Download file content by file_key.
        """
        # If it was saved via fallback or is a fallback URL
        if self.use_fallback or file_key.startswith("fallback://"):
            file_name = file_key.replace("fallback://", "").replace("uploads/", "")
            local_path = os.path.join(self.local_dir, file_name)
            if not os.path.exists(local_path):
                raise FileNotFoundError(f"File not found on local storage: {local_path}")
            with open(local_path, "rb") as f:
                return f.read()

        try:
            response = self.s3.get_object(Bucket=self.bucket_name, Key=file_key)
            return response["Body"].read()
        except Exception as e:
            logger.error(f"Error downloading file '{file_key}' from MinIO: {e}")
            # Try to read local fallback as emergency
            file_name = file_key.replace("uploads/", "")
            local_path = os.path.join(self.local_dir, file_name)
            if os.path.exists(local_path):
                with open(local_path, "rb") as f:
                    return f.read()
            raise e

# Global storage client singleton
storage_client = StorageClient()
