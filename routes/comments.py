from fastapi import APIRouter, HTTPException, Request, Depends, Query, status
from models.CommentModel import CommentModel
from models.PostModel import PostModel
from models.UserModel import UserModel
from routes.schemas.comments import (
    AddCommentRequest,
    UpdateCommentRequest,
    CommentAuthorResponse,
    CommentResponse,
    CommentDetailResponse
)
from helpers.auth import get_current_user
import logging

logger = logging.getLogger(__name__)

comment_router = APIRouter(
    prefix="/api/v1/comments",
    tags=["comments"],
)


@comment_router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(
    data: AddCommentRequest,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    comment_model = CommentModel(db_client)
    post_model = PostModel(db_client)
    
    if not data.comment_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment text cannot be empty"
        )
    
    # Verify post exists and is published
    post = await post_model.get_post_by_id(data.post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    if not post.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # If replying to a comment, verify parent exists
    if data.parent_comment_id:
        parent_comment = await comment_model.get_comment_by_id(data.parent_comment_id)
        if not parent_comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found"
            )
        # Verify parent comment is on the same post
        if parent_comment.post_id != data.post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent comment is not on this post"
            )
    
    comment = await comment_model.add_comment(
        user_id=current_user["id"],
        post_id=data.post_id,
        comment_text=data.comment_text.strip(),
        parent_comment_id=data.parent_comment_id
    )
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add comment"
        )
    
    logger.info(f"Comment added by user {current_user['id']} on post {data.post_id}")
    return comment

@comment_router.get("/post/{post_id}", response_model=list[CommentDetailResponse])
async def get_comments(
    post_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    request: Request = None
):
    """Get top-level comments for a post"""
    db_client = request.app.db_client
    comment_model = CommentModel(db_client)
    post_model = PostModel(db_client)
    user_model = UserModel(db_client)
    
    # Verify post exists and is published
    post = await post_model.get_post_by_id(post_id)
    if not post or not post.is_published:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Get only top-level comments
    comments = await comment_model.get_comments(post_id, limit, offset, parent_comment_id=None)
    
    # Add author information
    comments_with_authors = []
    for comment in comments:
        author = await user_model.get_user_by_id(comment.user_id)
        comment_dict = {
            "id": comment.id,
            "comment_text": comment.comment_text,
            "user_id": comment.user_id,
            "post_id": comment.post_id,
            "parent_comment_id": comment.parent_comment_id,
            "created_at": comment.created_at,
            "author": author if author else None
        }
        comments_with_authors.append(comment_dict)
    
    return comments_with_authors

@comment_router.get("/{comment_id}/replies", response_model=list[CommentDetailResponse])
async def get_comment_replies(
    comment_id: int,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    request: Request = None
):
    """Get replies to a comment"""
    db_client = request.app.db_client
    comment_model = CommentModel(db_client)
    user_model = UserModel(db_client)
    
    # Verify parent comment exists
    parent_comment = await comment_model.get_comment_by_id(comment_id)
    if not parent_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    replies = await comment_model.get_replies(comment_id, limit, offset)
    
    # Add author information
    replies_with_authors = []
    for reply in replies:
        author = await user_model.get_user_by_id(reply.user_id)
        reply_dict = {
            "id": reply.id,
            "comment_text": reply.comment_text,
            "user_id": reply.user_id,
            "post_id": reply.post_id,
            "parent_comment_id": reply.parent_comment_id,
            "created_at": reply.created_at,
            "author": author if author else None
        }
        replies_with_authors.append(reply_dict)
    
    return replies_with_authors

@comment_router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    data: UpdateCommentRequest,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    comment_model = CommentModel(db_client)
    
    # Verify comment exists and user is the owner
    existing_comment = await comment_model.get_comment_by_id(comment_id)
    if not existing_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if existing_comment.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this comment"
        )
    
    if not data.comment_text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment text cannot be empty"
        )
    
    comment = await comment_model.update_comment(
        comment_id=comment_id,
        user_id=current_user["id"],
        comment_text=data.comment_text.strip()
    )
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update comment"
        )
    
    logger.info(f"Comment {comment_id} updated by user {current_user['id']}")
    return comment

@comment_router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_comment(
    comment_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    comment_model = CommentModel(db_client)
    
    # Verify comment exists and user is the owner
    existing_comment = await comment_model.get_comment_by_id(comment_id)
    if not existing_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    if existing_comment.user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this comment"
        )
    
    success = await comment_model.remove_comment(comment_id, current_user["id"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete comment"
        )
    
    logger.info(f"Comment {comment_id} deleted by user {current_user['id']}")
    return None
