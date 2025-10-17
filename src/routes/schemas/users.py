from pydantic import BaseModel, Field, validator
from typing import Optional, List
import re

# Validation helpers
def validate_username(username: str) -> str:
    if not re.match(r'^[a-zA-Z0-9_-]{3,30}$', username):
        raise ValueError('Username must be 3-30 characters and contain only letters, numbers, underscores, and hyphens')
    return username

def validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError('Password must be at least 8 characters long')
    return password

# Request Models
class SignUpRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: str = Field(..., min_length=5, max_length=255)
    hashed_password: str = Field(..., min_length=8)
    bio: Optional[str] = Field(None, max_length=500)
    
    @validator('username')
    def validate_username_format(cls, v):
        return validate_username(v)
    
    @validator('email')
    def validate_email_format(cls, v):
        # Basic email validation
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v.lower()

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3)
    hashed_password: str = Field(..., min_length=8)

class UpdateUserRequest(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=30)
    email: Optional[str] = Field(None, min_length=5, max_length=255)
    bio: Optional[str] = Field(None, max_length=500)
    
    @validator('username')
    def validate_username_format(cls, v):
        if v is not None:
            return validate_username(v)
        return v
    
    @validator('email')
    def validate_email_format(cls, v):
        if v is not None:
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
                raise ValueError('Invalid email format')
            return v.lower()
        return v

class UpdatePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)
    
    @validator('new_password')
    def validate_new_password(cls, v):
        return validate_password(v)

# Response Models
class UserResponse(BaseModel):
    id: int
    username: str
    bio: Optional[str]
    
    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str
    bio: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
