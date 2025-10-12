from fastapi import APIRouter, HTTPException, Request
from models.UserModel import UserModel
from pydantic import BaseModel

user_router = APIRouter(
    prefix="/api/v1/user",
    tags=["api_v1"],
)

class SignUpRequest(BaseModel):
    username: str
    email: str
    hashed_password: str
    salt: str
    bio: str = None
    
@user_router.post("/signup")
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
        raise HTTPException(400, "Failed to create user")
    
    return user
