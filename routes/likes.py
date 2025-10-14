from fastapi import APIRouter, HTTPException, Request, Depends
from models.LikeModel import LikeModel
from helpers.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

like_router = APIRouter(
    prefix="/api/v1/likes",
    tags=["likes"],
)

@like_router.post("/{post_id}")
async def add_like(
    post_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    like_model = LikeModel(db_client)
    
    success = await like_model.add_like(current_user["id"], post_id)
    
    if not success:
        raise HTTPException(400, detail="Failed to like post or already liked")
    
    return {"message": "Post liked successfully"}

@like_router.delete("/{post_id}")
async def remove_like(
    post_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    like_model = LikeModel(db_client)
    
    success = await like_model.remove_like(current_user["id"], post_id)
    
    if not success:
        raise HTTPException(404, detail="Like not found")
    
    return {"message": "Like removed successfully"}

@like_router.get("/{post_id}/check")
async def check_like(
    post_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    like_model = LikeModel(db_client)
    
    is_liked = await like_model.check_like(current_user["id"], post_id)
    
    return {"liked": is_liked}

@like_router.get("/{post_id}/count")
async def get_likes_count(post_id: int, request: Request):
    db_client = request.app.db_client
    like_model = LikeModel(db_client)
    
    count = await like_model.get_likes(post_id)
    
    return {"likes_count": count}
