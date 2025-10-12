from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models.BaseModel import BaseModel
from models.db_schemas.schemas.users import User
import logging

logger = logging.getLogger(__name__)


class UserModel(BaseModel):
    
    async def create_user(self, 
                          username: str, 
                          email: str, 
                          hashed_password: str, 
                          salt: str, 
                          bio: str = None
                    ) -> User:
        try:
            async with self.db_client() as session:
                user = User(
                    username=username,
                    email=email,
                    hashed_password=hashed_password,
                    salt=salt,
                    bio=bio
                )
                session.add(user)
                await session.commit()
                await session.refresh(user)
                logger.info(f"User created: {user.id}")
                return user
        except IntegrityError as e:
            logger.error(f"User already exists: {e}")
            return None
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return None
    
    async def get_user_by_username(self, username: str) -> User | None:
        try:
            async with self.db_client() as session:
                result = await session.execute(
                    select(User).where(User.username == username)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting user by username: {e}")
            return None
    
    async def get_user_by_id(self, user_id: int) -> User | None:
        try:
            async with self.db_client() as session:
                return await session.get(User, user_id)
        except Exception as e:
            logger.error(f"Error getting user by id: {e}")
            return None
