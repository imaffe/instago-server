import json
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.llm_calls import ai_agent
from app.core.auth import get_current_user_id
from app.db.base import get_db
from app.models import Friendship, Screenshot, Query
from app.models.friendship import FriendshipStatus
from app.models.schemas import QueryRequest, QueryResult, ScreenshotResponse, QueryHistoryItem
from app.services.vector_store import vector_service

router = APIRouter()


@router.post("/query", response_model=List[QueryResult])
async def search_screenshots(
    query: QueryRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    user_ids = [current_user_id]
    
    if query.include_friends:
        friendships = db.query(Friendship).filter(
            or_(
                (Friendship.requester_id == current_user_id) & 
                (Friendship.status == FriendshipStatus.ACCEPTED),
                (Friendship.addressee_id == current_user_id) & 
                (Friendship.status == FriendshipStatus.ACCEPTED)
            )
        ).all()
        
        for friendship in friendships:
            if str(friendship.requester_id) == current_user_id:
                user_ids.append(str(friendship.addressee_id))
            else:
                user_ids.append(str(friendship.requester_id))
    
    query_embedding = ai_agent.generate_embedding(query.query)
    
    search_results = vector_service.search_screenshots(
        query_embedding,
        user_ids,
        limit=query.limit
    )
    
    # Store the query
    query_record = Query(
        user_id=current_user_id,
        query_text=query.query,
        results_count=len(search_results),
        include_friends=1 if query.include_friends else 0
    )
    db.add(query_record)
    db.commit()
    db.refresh(query_record)
    
    # Add query to vector store
    vector_id = vector_service.add_query(
        str(query_record.id),
        query_embedding,
        current_user_id
    )
    
    # Update query with vector ID
    query_record.vector_id = vector_id
    db.commit()
    
    results = []
    for result in search_results:
        screenshot = db.query(Screenshot).filter(
            Screenshot.id == result["screenshot_id"]
        ).first()
        
        if screenshot:
            if screenshot.ai_tags:
                screenshot.ai_tags = json.loads(screenshot.ai_tags)
            
            friend_name = None
            if str(screenshot.user_id) != current_user_id:
                from app.core.auth import auth_service
                try:
                    user_data = auth_service.supabase.auth.admin.get_user_by_id(
                        str(screenshot.user_id)
                    )
                    friend_name = user_data.user.email
                except:
                    friend_name = "Friend"
            
            results.append(QueryResult(
                screenshot=ScreenshotResponse.model_validate(screenshot),
                score=result["score"],
                friend_name=friend_name
            ))
    
    return results


@router.get("/query-history", response_model=List[QueryHistoryItem])
async def get_query_history(
    skip: int = 0,
    limit: int = 50,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    queries = db.query(Query).filter(
        Query.user_id == current_user_id
    ).order_by(Query.created_at.desc()).offset(skip).limit(limit).all()
    
    # Convert integer to boolean for include_friends
    for query in queries:
        query.include_friends = bool(query.include_friends)
    
    return queries