from fastapi import APIRouter, HTTPException, Request, Depends
from models.FollowModel import FollowModel
from helpers.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

follow_router = APIRouter(
    prefix="/api/v1/follows",
    tags=["follows"],
)

@follow_router.post("/{following_id}")
async def follow_user(
    following_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    follow_model = FollowModel(db_client)
    
    success = await follow_model.follow_user(current_user["id"], following_id)
    
    if not success:
        raise HTTPException(400, detail="Failed to follow user or already following")
    
    return {"message": "User followed successfully"}

@follow_router.delete("/{following_id}")
async def unfollow_user(
    following_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    follow_model = FollowModel(db_client)
    
    success = await follow_model.unfollow_user(current_user["id"], following_id)
    
    if not success:
        raise HTTPException(404, detail="Follow not found")
    
    return {"message": "User unfollowed successfully"}

@follow_router.get("/{following_id}/check")
async def check_follow(
    following_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    follow_model = FollowModel(db_client)
    
    is_following = await follow_model.is_following(current_user["id"], following_id)
    
    return {"following": is_following}

@follow_router.get("/stats/{user_id}")
async def get_follow_stats(user_id: int, request: Request):
    """Get followers and following count for a user"""
    db_client = request.app.db_client
    follow_model = FollowModel(db_client)
    
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
    
    count = await follow_model.get_followers_count(user_id)
    
    return {"user_id": user_id, "followers_count": count}

@follow_router.get("/user/{user_id}/following")
async def get_following_count(user_id: int, request: Request):
    """Get number of users this user is following"""
    db_client = request.app.db_client
    follow_model = FollowModel(db_client)
    
    count = await follow_model.get_following_count(user_id)
    
    return {"user_id": user_id, "following_count": count}
