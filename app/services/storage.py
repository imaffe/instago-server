import os
import uuid
from datetime import timedelta
from io import BytesIO
from typing import Tuple, Optional

from google.cloud import storage
from PIL import Image

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class StorageService:
    def __init__(self):
        if settings.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
        
        self.client = storage.Client()
        self.bucket = self.client.bucket(settings.GCS_BUCKET_NAME)
    
    async def upload_screenshot(
        self, 
        file_content: bytes, 
        user_id: str,
        content_type: str = "image/png"
    ) -> Tuple[str, str, dict]:
        try:
            file_id = str(uuid.uuid4())
            file_path = f"screenshots/{user_id}/{file_id}.png"
            thumbnail_path = f"screenshots/{user_id}/{file_id}_thumb.png"
            
            blob = self.bucket.blob(file_path)
            blob.upload_from_string(file_content, content_type=content_type)
            
            image = Image.open(BytesIO(file_content))
            width, height = image.size
            file_size = len(file_content)
            
            thumbnail = image.copy()
            thumbnail.thumbnail((400, 400), Image.Resampling.LANCZOS)
            
            thumb_buffer = BytesIO()
            thumbnail.save(thumb_buffer, format='PNG')
            thumb_content = thumb_buffer.getvalue()
            
            thumb_blob = self.bucket.blob(thumbnail_path)
            thumb_blob.upload_from_string(thumb_content, content_type="image/png")
            
            # Generate signed URLs that expire in 7 days
            image_url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=7),
                method="GET"
            )
            thumbnail_url = thumb_blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=7),
                method="GET"
            )
            
            metadata = {
                "width": width,
                "height": height,
                "file_size": file_size
            }
            
            logger.info(f"Uploaded screenshot {file_id} for user {user_id}")
            
            return image_url, thumbnail_url, metadata
            
        except Exception as e:
            logger.error(f"Error uploading screenshot: {e}")
            raise
    
    def generate_signed_url(self, blob_name: str, expiration_days: int = 7) -> str:
        """Generate a signed URL for a blob in the bucket."""
        try:
            blob = self.bucket.blob(blob_name)
            return blob.generate_signed_url(
                version="v4",
                expiration=timedelta(days=expiration_days),
                method="GET"
            )
        except Exception as e:
            logger.error(f"Error generating signed URL for {blob_name}: {e}")
            return ""
    
    def refresh_signed_url(self, old_url: str) -> str:
        """Refresh a signed URL by extracting the blob name and generating a new signed URL."""
        try:
            # Extract blob name from URL
            # Format: https://storage.googleapis.com/bucket-name/path/to/file?X-Goog-Signature=...
            # or: https://bucket-name.storage.googleapis.com/path/to/file?X-Goog-Signature=...
            if "storage.googleapis.com" in old_url:
                # Remove query parameters
                base_url = old_url.split("?")[0]
                # Extract path after bucket name
                if f"/{settings.GCS_BUCKET_NAME}/" in base_url:
                    blob_name = base_url.split(f"/{settings.GCS_BUCKET_NAME}/")[1]
                else:
                    # Try alternative format
                    blob_name = base_url.split(".storage.googleapis.com/")[1]
                
                return self.generate_signed_url(blob_name)
            else:
                # If it's already a blob name or path, use it directly
                return self.generate_signed_url(old_url)
        except Exception as e:
            logger.error(f"Error refreshing signed URL: {e}")
            return old_url
    
    async def delete_screenshot(self, image_url: str, thumbnail_url: Optional[str] = None) -> bool:
        try:
            image_path = image_url.split(f"{settings.GCS_BUCKET_NAME}/")[1]
            blob = self.bucket.blob(image_path)
            blob.delete()
            
            if thumbnail_url:
                thumb_path = thumbnail_url.split(f"{settings.GCS_BUCKET_NAME}/")[1]
                thumb_blob = self.bucket.blob(thumb_path)
                thumb_blob.delete()
            
            logger.info(f"Deleted screenshot from GCS: {image_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting screenshot: {e}")
            return False


storage_service = StorageService()