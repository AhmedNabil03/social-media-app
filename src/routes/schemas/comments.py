from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Request Models
class AddCommentRequest(BaseModel):
    post_id: int
    comment_text: str = Field(..., min_length=1, max_length=2000)
    parent_comment_id: Optional[int] = None

class UpdateCommentRequest(BaseModel):
    comment_text: str = Field(..., min_length=1, max_length=2000)

# Response Models
class CommentAuthorResponse(BaseModel):
    id: int
    username: str
    
    class Config:
        from_attributes = True

class CommentResponse(BaseModel):
    id: int
    comment_text: str
    user_id: int
    post_id: int
    parent_comment_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True

class CommentDetailResponse(CommentResponse):
    author: Optional[CommentAuthorResponse] = None
