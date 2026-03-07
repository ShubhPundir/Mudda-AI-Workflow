from sessions.aws_s3_client import s3_client
import os

class S3Service:
    """
    Service for handling S3 operations.
    """
    @staticmethod
    async def upload_document(file_path: str, object_name: str = None) -> str:
        """
        Uploads a generated document to S3.
        """
        if object_name is None:
            object_name = os.path.basename(file_path)
            
        print(f"Uploading {file_path} to S3 as {object_name}...")
        # Note: Boto3 is synchronous, but in a production async app 
        # we might wrap this in run_in_executor if performance is a concern.
        s3_url = s3_client.upload_file(file_path, object_name)
        return s3_url
