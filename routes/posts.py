from fastapi import APIRouter, HTTPException, Request, Depends, Query
from pydantic import BaseModel
from models.PostModel import PostModel
from helpers.auth import get_current_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

post_router = APIRouter(
    prefix="/api/v1/posts",
    tags=["posts"],
)

class CreatePostRequest(BaseModel):
    post_text: str
    post_image: str = None

class PostResponse(BaseModel):
    id: int
    post_text: str
    post_image: str
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

@post_router.post("", response_model=PostResponse)
async def create_post(
    data: CreatePostRequest,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    post_model = PostModel(db_client)
    
    if not data.post_text or len(data.post_text.strip()) == 0:
        raise HTTPException(400, detail="Post text cannot be empty")
    
    post = await post_model.create_post(
        user_id=current_user["id"],
        post_text=data.post_text,
        post_image=data.post_image
    )
    
    if not post:
        raise HTTPException(500, detail="Failed to create post")
    
    return post

@post_router.get("/{post_id}", response_model=PostResponse)
async def get_post(post_id: int, request: Request):
    db_client = request.app.db_client
    post_model = PostModel(db_client)
    
    post = await post_model.get_post_by_id(post_id)
    
    if not post:
        raise HTTPException(404, detail="Post not found")
    
    return post

@post_router.get("/")
async def get_my_posts(
    limit: int = Query(10, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    post_model = PostModel(db_client)
    
    posts = await post_model.get_posts_by_user_id(current_user["id"], limit, offset)
    
    return posts

@post_router.delete("/{post_id}")
async def delete_post(
    post_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    post_model = PostModel(db_client)
    
    success = await post_model.delete_post(post_id, current_user["id"])
    
    if not success:
        raise HTTPException(404, detail="Post not found or unauthorized")
    
    return {"message": "Post deleted successfully"}
