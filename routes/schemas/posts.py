from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Request Models
class CreatePostRequest(BaseModel):
    post_text: str = Field(..., min_length=1, max_length=5000)
    post_image: Optional[str] = Field(None, max_length=500)
    is_published: bool = True

class UpdatePostRequest(BaseModel):
    post_text: Optional[str] = Field(None, min_length=1, max_length=5000)
    post_image: Optional[str] = Field(None, max_length=500)
    is_published: Optional[bool] = None

# Response Models
class PostAuthorResponse(BaseModel):
    id: int
    username: str
    bio: Optional[str]
    
    class Config:
        from_attributes = True

class PostResponse(BaseModel):
    id: int
    post_text: str
    post_image: Optional[str]
    user_id: int
    is_published: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class PostDetailResponse(PostResponse):
    author: Optional[PostAuthorResponse] = None
