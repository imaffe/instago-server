import os
import uuid
from io import BytesIO
from typing import Tuple

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
            
            image_url = blob.public_url
            thumbnail_url = thumb_blob.public_url
            
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
    
    async def delete_screenshot(self, image_url: str, thumbnail_url: str) -> bool:
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