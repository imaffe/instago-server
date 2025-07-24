import json
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.agents import ai_agent
from app.core.auth import get_current_user_id
from app.db.base import get_db
from app.models import Screenshot
from app.models.schemas import ScreenshotResponse, ScreenshotUpdate
from app.services.storage import storage_service
from app.services.vector_store import vector_service

router = APIRouter()
executor = ThreadPoolExecutor(max_workers=5)


@router.post("/screenshot", response_model=ScreenshotResponse, status_code=status.HTTP_201_CREATED)
async def upload_screenshot(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    content = await file.read()
    
    image_url, thumbnail_url, metadata = await storage_service.upload_screenshot(
        content, current_user_id, file.content_type
    )
    
    screenshot = Screenshot(
        user_id=current_user_id,
        image_url=image_url,
        thumbnail_url=thumbnail_url,
        width=metadata["width"],
        height=metadata["height"],
        file_size=metadata["file_size"]
    )
    
    db.add(screenshot)
    db.commit()
    db.refresh(screenshot)
    
    executor.submit(
        process_screenshot_async,
        str(screenshot.id),
        image_url,
        content
    )
    
    return screenshot


def process_screenshot_async(screenshot_id: str, image_url: str, content: bytes):
    try:
        from app.db.base import SessionLocal
        from app.agents.screenshot_agent import ScreenshotAgent
        db = SessionLocal()
        
        # Get screenshot to access user_id
        screenshot = db.query(Screenshot).filter(Screenshot.id == screenshot_id).first()
        if not screenshot:
            return
        
        result = ai_agent.process_screenshot(content)
        
        # Handle embedding generation
        embedding = ai_agent.generate_embedding(result["description"])
        
        # If the current agent doesn't generate embeddings (e.g., Gemini), use OpenAI
        if embedding is None:
            openai_agent = ScreenshotAgent()
            embedding = openai_agent.generate_embedding(result["description"])
        
        vector_id = vector_service.add_screenshot(screenshot_id, embedding, str(screenshot.user_id))
        
        # Update screenshot with AI results
        screenshot.ai_title = result["title"]
        screenshot.ai_description = result["description"]
        screenshot.ai_tags = json.dumps(result["tags"])
        screenshot.markdown_content = result["markdown"]
        screenshot.vector_id = vector_id
        
        db.commit()
        
    except Exception as e:
        print(f"Error processing screenshot {screenshot_id}: {e}")
    finally:
        db.close()


@router.get("/screenshot-note", response_model=List[ScreenshotResponse])
async def get_screenshots(
    skip: int = 0,
    limit: int = 20,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    screenshots = db.query(Screenshot).filter(
        Screenshot.user_id == current_user_id
    ).order_by(Screenshot.created_at.desc()).offset(skip).limit(limit).all()
    
    for screenshot in screenshots:
        if screenshot.ai_tags:
            screenshot.ai_tags = json.loads(screenshot.ai_tags)
    
    return screenshots


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
    
    if screenshot.ai_tags:
        screenshot.ai_tags = json.loads(screenshot.ai_tags)
    
    return screenshot


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
    
    if screenshot.ai_tags:
        screenshot.ai_tags = json.loads(screenshot.ai_tags)
    
    return screenshot


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
    
    await storage_service.delete_screenshot(screenshot.image_url, screenshot.thumbnail_url)
    
    if screenshot.vector_id:
        vector_service.delete_screenshot(screenshot.vector_id)
    
    db.delete(screenshot)
    db.commit()