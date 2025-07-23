from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.auth import auth_service, get_current_user_id
from app.db.base import get_db
from app.models import Friendship
from app.models.friendship import FriendshipStatus
from app.models.schemas import FriendGrantRequest, FriendRequest, FriendshipResponse

router = APIRouter()


@router.post("/friend-request", response_model=FriendshipResponse, status_code=status.HTTP_201_CREATED)
async def send_friend_request(
    request: FriendRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        user_data = auth_service.supabase.auth.admin.list_users()
        addressee_user = None
        
        for user in user_data:
            if user.email == request.email:
                addressee_user = user
                break
        
        if not addressee_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if str(addressee_user.id) == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot send friend request to yourself"
            )
        
        existing_friendship = db.query(Friendship).filter(
            or_(
                (Friendship.requester_id == current_user_id) & 
                (Friendship.addressee_id == addressee_user.id),
                (Friendship.requester_id == addressee_user.id) & 
                (Friendship.addressee_id == current_user_id)
            )
        ).first()
        
        if existing_friendship:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Friend request already exists"
            )
        
        friendship = Friendship(
            requester_id=current_user_id,
            addressee_id=str(addressee_user.id),
            status=FriendshipStatus.PENDING
        )
        
        db.add(friendship)
        db.commit()
        db.refresh(friendship)
        
        return friendship
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/friend-grant", response_model=FriendshipResponse)
async def accept_friend_request(
    request: FriendGrantRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    friendship = db.query(Friendship).filter(
        Friendship.id == request.friendship_id,
        Friendship.addressee_id == current_user_id,
        Friendship.status == FriendshipStatus.PENDING
    ).first()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friend request not found"
        )
    
    friendship.status = FriendshipStatus.ACCEPTED
    db.commit()
    db.refresh(friendship)
    
    return friendship


@router.get("/friends", response_model=List[FriendshipResponse])
async def get_friends(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    friendships = db.query(Friendship).filter(
        or_(
            (Friendship.requester_id == current_user_id),
            (Friendship.addressee_id == current_user_id)
        )
    ).all()
    
    for friendship in friendships:
        try:
            requester_data = auth_service.supabase.auth.admin.get_user_by_id(
                str(friendship.requester_id)
            )
            friendship.requester_email = requester_data.user.email
            
            addressee_data = auth_service.supabase.auth.admin.get_user_by_id(
                str(friendship.addressee_id)
            )
            friendship.addressee_email = addressee_data.user.email
        except:
            pass
    
    return friendships


@router.delete("/friend/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_friend(
    friend_id: UUID,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    friendship = db.query(Friendship).filter(
        Friendship.id == friend_id,
        or_(
            Friendship.requester_id == current_user_id,
            Friendship.addressee_id == current_user_id
        )
    ).first()
    
    if not friendship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Friendship not found"
        )
    
    db.delete(friendship)
    db.commit()