from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
import jwt
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

# JWT configuration
SECRET_KEY = "secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Token blacklist - Redis
token_blacklist = set()


def create_access_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "sub": str(user_id),
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[int]:
    """Verify JWT token and return user_id"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        
        if user_id is None:
            return None
        
        return user_id
    
    except jwt.ExpiredSignatureError:
        logger.error("Token has expired")
        return None
    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        return None


def blacklist_token(token: str):
    """Add token to blacklist"""
    token_blacklist.add(token)
    logger.info(f"Token blacklisted")


def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    return token in token_blacklist


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current user from JWT token (for API routes)
    Expects Bearer token in Authorization header
    """
    token = credentials.credentials
    
    # Check if token is blacklisted
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"id": user_id, "token": token}


async def get_current_user_from_cookie(request: Request) -> dict:
    """
    Dependency to get current user from cookie (for web routes)
    Expects access_token in cookies
    """
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - please login",
        )
    
    # Check if token is blacklisted
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked - please login again",
        )
    
    user_id = verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token - please login again",
        )
    
    return {"id": user_id, "token": token}


def get_current_user_optional(request: Request) -> Optional[dict]:
    """
    Get current user from cookie without raising exception
    Returns None if not authenticated (for optional auth)
    """
    token = request.cookies.get("access_token")
    
    if not token:
        return None
    
    if is_token_blacklisted(token):
        return None
    
    user_id = verify_token(token)
    
    if user_id is None:
        return None
    
    return {"id": user_id, "token": token}


# Optional: If you want to store user object instead of just ID
async def get_current_user_with_db(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db_client = None
) -> dict:
    """
    Get current user from JWT and fetch from database
    Use this if you need full user details
    """
    token = credentials.credentials
    user_id = verify_token(token)
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # If you need to fetch from DB:
    # from models.UserModel import UserModel
    # user_model = UserModel(db_client)
    # user = await user_model.get_user_by_id(user_id)
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found")
    # return user
    
    return {"id": user_id}
