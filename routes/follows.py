from fastapi import APIRouter, HTTPException, Request, Depends, status
from models.FollowModel import FollowModel
from models.UserModel import UserModel
from helpers.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

follow_router = APIRouter(
    prefix="/api/v1/follows",
    tags=["follows"],
)

@follow_router.post("/{following_id}", status_code=status.HTTP_201_CREATED)
async def follow_user(
    following_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    follow_model = FollowModel(db_client)
    user_model = UserModel(db_client)
    
    # Check if trying to follow self
    if current_user["id"] == following_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself"
        )
    
    # Verify user exists and is active
    user_to_follow = await user_model.get_user_by_id(following_id)
    if not user_to_follow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user_to_follow.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = await follow_model.follow_user(current_user["id"], following_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already following this user"
        )
    
    logger.info(f"User {current_user['id']} followed user {following_id}")
    return {"message": "User followed successfully"}

@follow_router.delete("/{following_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unfollow_user(
    following_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    follow_model = FollowModel(db_client)
    
    success = await follow_model.unfollow_user(current_user["id"], following_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow relationship not found"
        )
    
    logger.info(f"User {current_user['id']} unfollowed user {following_id}")
    return None

@follow_router.get("/{user_id}/check")
async def check_follow(
    user_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    """Check if current user is following the specified user"""
    db_client = request.app.db_client
    follow_model = FollowModel(db_client)
    user_model = UserModel(db_client)
    
    # Verify user exists
    user = await user_model.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    is_following = await follow_model.is_following(current_user["id"], user_id)
    
    return {"following": is_following}

@follow_router.get("/stats/{user_id}")
async def get_follow_stats(user_id: int, request: Request):
    """Get followers and following count for a user"""
    db_client = request.app.db_client
    follow_model = FollowModel(db_client)
    user_model = UserModel(db_client)
    
    # Verify user exists and is active
    user = await user_model.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    followers_count = await follow_model.get_followers_count(user_id)
    following_count = await follow_model.get_following_count(user_id)
    
    return {
        "user_id": user_id,
        "followers_count": followers_count,
        "following_count": following_count
    }

@follow_router.get("/user/{user_id}/followers")
async def get_followers_count(user_id: int, request: Request):
    """Get number of followers for a user"""
    db_client = request.app.db_client
    follow_model = FollowModel(db_client)
    user_model = UserModel(db_client)
    
    # Verify user exists and is active
    user = await user_model.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    count = await follow_model.get_followers_count(user_id)
    
    return {"user_id": user_id, "followers_count": count}

@follow_router.get("/user/{user_id}/following")
async def get_following_count(user_id: int, request: Request):
    """Get number of users this user is following"""
    db_client = request.app.db_client
    follow_model = FollowModel(db_client)
    user_model = UserModel(db_client)
    
    # Verify user exists and is active
    user = await user_model.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    count = await follow_model.get_following_count(user_id)
    
    return {"user_id": user_id, "following_count": count}
