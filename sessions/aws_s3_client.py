import boto3
from config import settings

class AWSS3Client:
    """
    Low-level client for AWS S3.
    """
    def __init__(self):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    def upload_file(self, file_path: str, object_name: str) -> str:
        """
        Uploads a file to S3 and returns the URL.
        """
        self.client.upload_file(file_path, self.bucket_name, object_name)
        
        # Return the S3 URI or URL
        return f"s3://{self.bucket_name}/{object_name}"

# Singleton instance
s3_client = AWSS3Client()
