import json
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.core.logging import get_logger
from app.db.base import get_db
from app.models import Screenshot, Query
from app.models.schemas import (
    QueryRequest,
    QueryResult,
    ScreenshotResponse,
    QueryHistoryItem,
    ScreenshotDTO
)
from app.services.vector_store import vector_service
from app.services.embedding import embedding_service
from app.services.reranking import reranking_service
from app.services.storage import storage_service

router = APIRouter()
logger = get_logger(__name__)


@router.post("/query", response_model=List[QueryResult])
async def search_screenshots(
    query: QueryRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Search screenshots with semantic search and reranking.
    Returns reranked screenshot results.
    """
    logger.info(f"Processing query: '{query.query}' for user {current_user_id}")

    # Step 1: Only search current user's screenshots
    user_ids = [current_user_id]

    # Step 2: Generate embedding for the query
    try:
        query_embedding = embedding_service.generate_embedding(query.query)
    except Exception as e:
        logger.error(f"Failed to generate embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process query"
        )

    # Step 3: Search vector store
    search_results = vector_service.search_screenshots(
        query_embedding,
        user_ids,
        limit=query.limit * 2  # Get more results for reranking
    )

    if not search_results:
        # No results found
        return []

    # Step 4: Store the query in database
    query_record = Query(
        user_id=current_user_id,
        query_text=query.query,
        results_count=len(search_results),
        include_friends=0  # Always 0 since we only search user's own screenshots
    )
    db.add(query_record)
    db.commit()
    db.refresh(query_record)

    # Step 5: Fetch screenshot data
    screenshot_ids = [result["screenshot_id"] for result in search_results]
    screenshots = db.query(Screenshot).filter(
        Screenshot.id.in_(screenshot_ids)
    ).all()

    # Create mapping for quick lookup
    screenshot_map = {str(s.id): s for s in screenshots}

    # Step 6: Prepare screenshots with metadata
    screenshot_data_list = []
    for result in search_results:
        screenshot = screenshot_map.get(result["screenshot_id"])
        if screenshot:
            # Parse JSON fields
            ai_tags = []
            if screenshot.ai_tags:
                try:
                    ai_tags = json.loads(screenshot.ai_tags) if isinstance(screenshot.ai_tags, str) else screenshot.ai_tags
                except:
                    ai_tags = []

            screenshot_dto = ScreenshotDTO(
                id=str(screenshot.id),
                user_id=str(screenshot.user_id),
                ai_title=screenshot.ai_title or "",
                ai_description=screenshot.ai_description or "",
                markdown_content=screenshot.markdown_content or "",
                ai_tags=ai_tags,
                vector_score=result["score"]
            )
            screenshot_data_list.append(screenshot_dto)

    # Step 7: Always apply reranking
    if not screenshot_data_list:
        return []
    
    # Rerank results
    reranked_results = reranking_service.rerank_screenshots(
        query.query,
        screenshot_data_list,
        top_k=query.limit
    )

    # Step 8: Build final response
    results = []
    for screenshot_data, score in reranked_results:
        # Get the original screenshot from the map using the DTO id
        screenshot = screenshot_map.get(screenshot_data.id)
        if not screenshot:
            continue

        # Create response object
        screenshot_response = ScreenshotResponse.from_db(screenshot)

        # Refresh signed URLs
        if screenshot_response.image_url:
            screenshot_response.image_url = storage_service.refresh_signed_url(screenshot_response.image_url)
        if screenshot_response.thumbnail_url:
            screenshot_response.thumbnail_url = storage_service.refresh_signed_url(screenshot_response.thumbnail_url)

        results.append(QueryResult(
            screenshot=screenshot_response,
            score=float(score)
        ))

    return results


@router.post("/query-simple", response_model=List[QueryResult])
async def search_screenshots_simple(
    query: QueryRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Simple query endpoint that returns just the screenshot results.
    For backward compatibility - extracts results from the main endpoint.
    """
    # Call main endpoint
    return await search_screenshots(query, current_user_id, db)


@router.get("/query-history", response_model=List[QueryHistoryItem])
async def get_query_history(
    skip: int = 0,
    limit: int = 50,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get user's query history"""
    queries = db.query(Query).filter(
        Query.user_id == current_user_id
    ).order_by(Query.created_at.desc()).offset(skip).limit(limit).all()

    return queries


