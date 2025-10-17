from fastapi import APIRouter, HTTPException, Request, Depends, Query, status
from models.PostModel import PostModel
from models.UserModel import UserModel
from routes.schemas.posts import (
    CreatePostRequest,
    UpdatePostRequest,
    PostAuthorResponse,
    PostResponse,
    PostDetailResponse
)
from helpers.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

post_router = APIRouter(
    prefix="/api/v1/posts",
    tags=["posts"],
)


@post_router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: CreatePostRequest,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    post_model = PostModel(db_client)
    
    if not data.post_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post text cannot be empty"
        )
    
    post = await post_model.create_post(
        user_id=current_user["id"],
        post_text=data.post_text.strip(),
        post_image=data.post_image,
        is_published=data.is_published
    )
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create post"
        )
    
    logger.info(f"Post created by user {current_user['id']}: post_id={post.id}")
    return post

@post_router.get("/{post_id}", response_model=PostDetailResponse)
async def get_post(
    post_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    post_model = PostModel(db_client)
    user_model = UserModel(db_client)
    
    post = await post_model.get_post_by_id(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Only show unpublished posts to the owner
    if not post.is_published and post.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Get author information
    author = await user_model.get_user_by_id(post.user_id)
    
    post_dict = {
        "id": post.id,
        "post_text": post.post_text,
        "post_image": post.post_image,
        "user_id": post.user_id,
        "is_published": post.is_published,
        "created_at": post.created_at,
        "author": author if author else None
    }
    
    return post_dict

@post_router.get("/", response_model=list[PostResponse])
async def get_my_posts(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    include_unpublished: bool = Query(True),
    current_user = Depends(get_current_user),
    request: Request = None
):
    """Get current user's posts"""
    db_client = request.app.db_client
    post_model = PostModel(db_client)
    
    posts = await post_model.get_posts_by_user_id(
        current_user["id"], 
        limit, 
        offset,
        include_unpublished=include_unpublished
    )
    
    return posts

@post_router.get("/user/{user_id}", response_model=list[PostResponse])
async def get_user_posts(
    user_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    request: Request = None
):
    """Get another user's published posts"""
    db_client = request.app.db_client
    post_model = PostModel(db_client)
    
    # Only show published posts for other users
    posts = await post_model.get_posts_by_user_id(
        user_id, 
        limit, 
        offset,
        include_unpublished=False
    )
    
    return posts

@post_router.get("/feed/all", response_model=list[PostResponse])
async def get_feed_posts(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user = Depends(get_current_user),
    request: Request = None
):
    """Get feed of posts from other users"""
    db_client = request.app.db_client
    post_model = PostModel(db_client)

    posts = await post_model.get_feed_posts(
        current_user["id"], 
        limit, 
        offset,
        include_unpublished=False
    )
    return posts

@post_router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    data: UpdatePostRequest,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    post_model = PostModel(db_client)
    
    # Verify post ownership
    existing_post = await post_model.get_post_by_user_id_and_post_id(
        current_user["id"], 
        post_id
    )
    
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or unauthorized"
        )
    
    if data.post_text is not None and not data.post_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post text cannot be empty"
        )
    
    post = await post_model.update_post(
        post_id=post_id,
        user_id=current_user["id"],
        post_text=data.post_text.strip() if data.post_text else None,
        post_image=data.post_image,
        is_published=data.is_published
    )
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update post"
        )
    
    logger.info(f"Post updated by user {current_user['id']}: post_id={post_id}")
    return post

@post_router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    post_model = PostModel(db_client)
    
    success = await post_model.delete_post(post_id, current_user["id"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or unauthorized"
        )
    
    logger.info(f"Post deleted by user {current_user['id']}: post_id={post_id}")
    return None
