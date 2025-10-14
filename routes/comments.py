from fastapi import APIRouter, HTTPException, Request, Depends, Query
from pydantic import BaseModel
from models.CommentModel import CommentModel
from helpers.auth import get_current_user
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

comment_router = APIRouter(
    prefix="/api/v1/comments",
    tags=["comments"],
)

class AddCommentRequest(BaseModel):
    post_id: int
    comment_text: str
    parent_comment_id: int = None

class CommentResponse(BaseModel):
    id: int
    comment_text: str
    user_id: int
    post_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

@comment_router.post("", response_model=CommentResponse)
async def add_comment(
    data: AddCommentRequest,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    comment_model = CommentModel(db_client)
    
    if not data.comment_text or len(data.comment_text.strip()) == 0:
        raise HTTPException(400, detail="Comment text cannot be empty")
    
    comment = await comment_model.add_comment(
        user_id=current_user["id"],
        post_id=data.post_id,
        comment_text=data.comment_text,
        parent_comment_id=data.parent_comment_id
    )
    
    if not comment:
        raise HTTPException(500, detail="Failed to add comment")
    
    return comment

@comment_router.get("/post/{post_id}")
async def get_comments(
    post_id: int,
    limit: int = Query(20, le=100),
    offset: int = Query(0, ge=0),
    request: Request = None
):
    db_client = request.app.db_client
    comment_model = CommentModel(db_client)
    
    comments = await comment_model.get_comments(post_id, limit, offset)
    
    return comments

@comment_router.delete("/{comment_id}")
async def remove_comment(
    comment_id: int,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    comment_model = CommentModel(db_client)
    
    success = await comment_model.remove_comment(comment_id, current_user["id"])
    
    if not success:
        raise HTTPException(404, detail="Comment not found or unauthorized")
    
    return {"message": "Comment deleted successfully"}
