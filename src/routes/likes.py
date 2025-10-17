from fastapi import APIRouter, HTTPException, Request, Depends, status
from models.LikeModel import LikeModel
from models.PostModel import PostModel
from helpers.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

like_router = APIRouter(
    prefix="/api/v1/likes",
    tags=["likes"],
)


@like_router.post("/{post_id}", status_code=status.HTTP_201_CREATED)
async def add_like(
    post_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    like_model = LikeModel(db_client)
    post_model = PostModel(db_client)
    
    # Verify post exists
    post = await post_model.get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if post is published
    if not post.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    success = await like_model.add_like(current_user["id"], post_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post already liked"
        )
    
    logger.info(f"User {current_user['id']} liked post {post_id}")
    return {"message": "Post liked successfully"}

@like_router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_like(
    post_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    like_model = LikeModel(db_client)
    
    success = await like_model.remove_like(current_user["id"], post_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found"
        )
    
    logger.info(f"User {current_user['id']} unliked post {post_id}")
    return None

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
    post_model = PostModel(db_client)
    
    # Verify post exists and is published
    post = await post_model.get_post_by_id(post_id)
    if not post or not post.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    count = await like_model.get_likes(post_id)
    
    return {"post_id": post_id, "likes_count": count}
