from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models.BaseModel import BaseModel
from models.db_schemas.schemas.like import Like
import logging

logger = logging.getLogger(__name__)


class LikeModel(BaseModel):
    
    async def add_like(self, user_id: int, post_id: int) -> bool:
        try:
            async with self.db_client() as session:
                like = Like(user_id=user_id, post_id=post_id)
                session.add(like)
                await session.commit()
                logger.info(f"Like added: user {user_id} -> post {post_id}")
                return True
        except IntegrityError:
            logger.warning(f"Like already exists: user {user_id} -> post {post_id}")
            return False
        except Exception as e:
            logger.error(f"Error adding like: {e}")
            return False
    
    async def remove_like(self, user_id: int, post_id: int) -> bool:
        try:
            async with self.db_client() as session:
                result = await session.execute(
                    select(Like).where(
                        (Like.user_id == user_id) & (Like.post_id == post_id)
                    )
                )
                like = result.scalar_one_or_none()
                if not like:
                    logger.warning(f"Like not found: user {user_id} -> post {post_id}")
                    return False
                await session.delete(like)
                await session.commit()
                logger.info(f"Like removed: user {user_id} -> post {post_id}")
                return True
        except Exception as e:
            logger.error(f"Error removing like: {e}")
            return False
    
    async def check_like(self, user_id: int, post_id: int) -> bool:
        try:
            async with self.db_client() as session:
                result = await session.execute(
                    select(Like).where(
                        (Like.user_id == user_id) & (Like.post_id == post_id)
                    )
                )
                return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Error checking like: {e}")
            return False
    
    async def get_likes(self, post_id: int) -> int:
        try:
            async with self.db_client() as session:
                result = await session.execute(
                    select(Like).where(Like.post_id == post_id)
                )
                return len(result.scalars().all())
        except Exception as e:
            logger.error(f"Error getting likes: {e}")
            return 0
