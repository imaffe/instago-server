import json
import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status, Query
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.core.logging import get_logger
from app.db.base import get_db
from app.models import Screenshot
from app.models.schemas import ScreenshotResponse, ScreenshotUpdate, ScreenshotCreate
from app.services.storage import storage_service
from app.services.vector_store import vector_service
from app.services.screenshot import screenshot_processing_service

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=5)
logger = get_logger(__name__)


@router.post("/screenshot", status_code=status.HTTP_200_OK)
async def upload_screenshot(
    screenshot_data: ScreenshotCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    # Decode base64 image to validate it
    try:
        content = base64.b64decode(screenshot_data.screenshotFileBlob)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid base64 image data"
        )

    # Submit to executor for async processing
    executor.submit(
        screenshot_processing_service.process_screenshot_async,
        current_user_id,
        screenshot_data
    )

    # Return immediately with 200 OK
    return {"status": "accepted"}



@router.get("/screenshot-note", response_model=List[ScreenshotResponse])
async def get_screenshots(
    skip: int = 0,
    limit: int = 20,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    logger.info(f"Fetching screenshots for user: {current_user_id}, skip: {skip}, limit: {limit}")
    screenshots = db.query(Screenshot).filter(
        Screenshot.user_id == current_user_id
    ).order_by(Screenshot.created_at.desc()).offset(skip).limit(limit).all()

    # Refresh signed URLs for each screenshot
    responses = []
    for screenshot in screenshots:
        response = ScreenshotResponse.from_db(screenshot)
        # Refresh the signed URL if it exists
        if response.image_url:
            response.image_url = storage_service.refresh_signed_url(response.image_url)
        responses.append(response)

    return responses


@router.get("/screenshot-note/{screenshot_id}", response_model=ScreenshotResponse)
async def get_screenshot(
    screenshot_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    screenshot = db.query(Screenshot).filter(
        Screenshot.id == screenshot_id,
        Screenshot.user_id == current_user_id
    ).first()

    if not screenshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screenshot not found"
        )

    response = ScreenshotResponse.from_db(screenshot)

    # Refresh the signed URL if it exists
    if response.image_url:
        response.image_url = storage_service.refresh_signed_url(response.image_url)

    return response


@router.put("/screenshot-note/{screenshot_id}", response_model=ScreenshotResponse)
async def update_screenshot(
    screenshot_id: UUID,
    update_data: ScreenshotUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    screenshot = db.query(Screenshot).filter(
        Screenshot.id == screenshot_id,
        Screenshot.user_id == current_user_id
    ).first()

    if not screenshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screenshot not found"
        )

    if update_data.user_note is not None:
        screenshot.user_note = update_data.user_note

    if update_data.ai_tags is not None:
        screenshot.ai_tags = json.dumps(update_data.ai_tags)

    db.commit()
    db.refresh(screenshot)

    return ScreenshotResponse.from_db(screenshot)


@router.delete("/screenshot/{screenshot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_screenshot(
    screenshot_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    screenshot = db.query(Screenshot).filter(
        Screenshot.id == screenshot_id,
        Screenshot.user_id == current_user_id
    ).first()

    if not screenshot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Screenshot not found"
        )

    # Delete from vector database if vector_id exists
    if screenshot.vector_id:
        try:
            vector_service.delete_screenshot(screenshot.vector_id)
        except Exception as e:
            logger.warning(f"Failed to delete from vector store: {e}")
            # Continue with database deletion even if vector deletion fails
    
    # Delete from database
    db.delete(screenshot)
    db.commit()
