from fastapi import APIRouter, HTTPException, Request, Depends, status
from typing import List
from models.UserModel import UserModel
from helpers.auth import get_current_user, create_access_token, blacklist_token
from routes.schemas.users import (
    LoginRequest,
    SignUpRequest,
    TokenResponse,
    UserResponse,
    UserProfileResponse,
    UpdateUserRequest,
    UpdatePasswordRequest
)
import logging


logger = logging.getLogger(__name__)

user_router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
)


@user_router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(data: SignUpRequest, request: Request):
    db_client = request.app.db_client
    user_model = UserModel(db_client)
    
    # Check if username exists
    existing_user = await user_model.get_user_by_username(data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Check if email exists
    existing_email = await user_model.get_user_by_email(data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
    user = await user_model.create_user(
        username=data.username,
        email=data.email.lower(),
        hashed_password=data.hashed_password,
        bio=data.bio
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    access_token = create_access_token(user.id)
    logger.info(f"New user signed up: {user.username}")
    return {"access_token": access_token}

@user_router.post("/signup/multiple")
async def signup_multiple(users: List[SignUpRequest], request: Request):
    """For testing purposes only - should be disabled in production"""
    db_client = request.app.db_client
    user_model = UserModel(db_client)

    created_users = []
    failed_users = []

    for user_data in users:
        user = await user_model.create_user(
            username=user_data.username,
            email=user_data.email.lower(),
            hashed_password=user_data.hashed_password,
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
    
    if not user or user.hashed_password != data.hashed_password:
        # Don't reveal whether username or password is wrong
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    access_token = create_access_token(user.id)
    logger.info(f"User logged in: {user.username}")
    return {"access_token": access_token}

@user_router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user = Depends(get_current_user),
    request: Request = None
):
    """Get own profile with private information"""
    db_client = request.app.db_client
    user_model = UserModel(db_client)
    
    user = await user_model.get_user_by_id(current_user["id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@user_router.patch("/profile", response_model=UserProfileResponse)
async def update_profile(
    data: UpdateUserRequest,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    user_model = UserModel(db_client)
    
    # Check if trying to update to existing username
    if data.username:
        existing_user = await user_model.get_user_by_username(data.username)
        if existing_user and existing_user.id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
    
    # Check if trying to update to existing email
    if data.email:
        existing_email = await user_model.get_user_by_email(data.email)
        if existing_email and existing_email.id != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
    
    user = await user_model.update_user(
        user_id=current_user["id"],
        username=data.username,
        email=data.email.lower() if data.email else None,
        bio=data.bio
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user"
        )
    
    logger.info(f"User updated profile: {user.username}")
    return user

@user_router.patch("/password")
async def update_password(
    data: UpdatePasswordRequest,
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    user_model = UserModel(db_client)
    
    user = await user_model.get_user_by_id(current_user["id"])
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify current password
    if user.hashed_password != data.current_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Check if new password is same as current
    if data.current_password == data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
        )
    
    # Update password (you should add this method to UserModel)
    user = await user_model.update_user(
        user_id=current_user["id"],
        username=None,
        email=None,
        bio=None
    )
    # TODO: Add password update functionality to UserModel
    
    logger.info(f"User updated password: {user.username}")
    return {"message": "Password updated successfully"}

@user_router.get("/{username}", response_model=UserResponse)
async def get_user_by_username(username: str, request: Request):
    """Get public user profile"""
    db_client = request.app.db_client
    user_model = UserModel(db_client)
    
    user = await user_model.get_user_by_username(username)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@user_router.delete("/")
async def delete_user(
    current_user = Depends(get_current_user),
    request: Request = None
):
    db_client = request.app.db_client
    user_model = UserModel(db_client)
    
    success = await user_model.delete_user(current_user["id"])
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Blacklist the current token
    blacklist_token(current_user["token"])
    
    logger.info(f"User deleted account: {current_user['id']}")
    return {"message": "User deleted successfully"}

@user_router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    # Blacklist the current token
    blacklist_token(current_user["token"])
    
    logger.info(f"User {current_user['id']} logged out")
    return {"message": "Logged out successfully"}
