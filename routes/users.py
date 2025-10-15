from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
from models.UserModel import UserModel
from helpers.auth import get_current_user, create_access_token
import logging

logger = logging.getLogger(__name__)

user_router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
)

class SignUpRequest(BaseModel):
    username: str
    email: str
    hashed_password: str
    salt: str
    bio: str = None

class LoginRequest(BaseModel):
    username: str
    hashed_password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    bio: str
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

@user_router.post("/signup", response_model=TokenResponse)
async def signup(data: SignUpRequest, request: Request):
    db_client = request.app.db_client
    user_model = UserModel(db_client)
    
    user = await user_model.create_user(
        username=data.username,
        email=data.email,
        hashed_password=data.hashed_password,
        salt=data.salt,
        bio=data.bio
    )
    
    if not user:
        raise HTTPException(400, detail="Failed to create user or user already exists")
    
    access_token = create_access_token(user.id)
    return {"access_token": access_token}

### For Testing: Signup multiple users at once
from typing import List
@user_router.post("/signup/multiple")
async def signup_multiple(users: List[SignUpRequest], request: Request):
    db_client = request.app.db_client
    user_model = UserModel(db_client)

    created_users = []
    failed_users = []

    for user_data in users:
        user = await user_model.create_user(
            username=user_data.username,
            email=user_data.email,
            hashed_password=user_data.hashed_password,
            salt=user_data.salt,
            bio=user_data.bio
        )

        if user:
            access_token = create_access_token(user.id)
            created_users.append({
                "username": user_data.username,
                "access_token": access_token
            })
        else:
            failed_users.append(user_data.username)

    return {
        "created_count": len(created_users),
        "failed_count": len(failed_users),
        "created_users": created_users,
        "failed_users": failed_users
    }

@user_router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, request: Request):
    db_client = request.app.db_client
    user_model = UserModel(db_client)
    
    user = await user_model.get_user_by_username(data.username)
    
    if not user:
        raise HTTPException(401, detail="Invalid credentials")
    
    if user.hashed_password != data.hashed_password:
        raise HTTPException(401, detail="Invalid credentials")
    
    access_token = create_access_token(user.id)
    return {"access_token": access_token}

@user_router.get("/profile", response_model=UserResponse)
async def get_profile(current_user = Depends(get_current_user), request: Request = None):
    db_client = request.app.db_client
    user_model = UserModel(db_client)
    
    user = await user_model.get_user_by_id(current_user["id"])
    
    if not user:
        raise HTTPException(404, detail="User not found")
    
    return user

@user_router.get("/{username}", response_model=UserResponse)
async def get_user_by_username(username: str, request: Request):
    db_client = request.app.db_client
    user_model = UserModel(db_client)
    
    user = await user_model.get_user_by_username(username)
    
    if not user:
        raise HTTPException(404, detail="User not found")
    
    return user

@user_router.delete("/")
async def delete_user(current_user = Depends(get_current_user), request: Request = None):
    db_client = request.app.db_client
    user_model = UserModel(db_client)
    
    success = await user_model.delete_user(current_user["id"])
    
    if not success:
        raise HTTPException(404, detail="User not found")
    
    return {"message": "User deleted successfully"}

@user_router.post("/logout")
async def logout(current_user = Depends(get_current_user)):

    logger.info(f"User {current_user['id']} logged out")
    return {"message": "Logged out successfully"}
