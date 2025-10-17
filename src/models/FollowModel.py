from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from models.BaseModel import BaseModel
from models.db_schemas.schemas.follower import Follow
import logging

logger = logging.getLogger(__name__)


class FollowModel(BaseModel):
    
    async def follow_user(self, follower_id: int, following_id: int) -> bool:
        try:
            if follower_id == following_id:
                logger.warning(f"User cannot follow themselves: {follower_id}")
                return False
            
            async with self.db_client() as session:
                follow = Follow(follower_id=follower_id, following_id=following_id)
                session.add(follow)
                await session.commit()
                logger.info(f"Follow added: {follower_id} -> {following_id}")
                return True
        except IntegrityError:
            logger.warning(f"Already following: {follower_id} -> {following_id}")
            return False
        except Exception as e:
            logger.error(f"Error following user: {e}")
            return False
    
    async def unfollow_user(self, follower_id: int, following_id: int) -> bool:
        try:
            async with self.db_client() as session:
                result = await session.execute(
                    select(Follow).where(
                        (Follow.follower_id == follower_id) & (Follow.following_id == following_id)
                    )
                )
                follow = result.scalar_one_or_none()
                if not follow:
                    logger.warning(f"Follow not found: {follower_id} -> {following_id}")
                    return False
                await session.delete(follow)
                await session.commit()
                logger.info(f"Follow removed: {follower_id} -> {following_id}")
                return True
        except Exception as e:
            logger.error(f"Error unfollowing user: {e}")
            return False
    
    async def is_following(self, follower_id: int, following_id: int) -> bool:
        try:
            async with self.db_client() as session:
                result = await session.execute(
                    select(Follow).where(
                        (Follow.follower_id == follower_id) & (Follow.following_id == following_id)
                    )
                )
                return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Error checking follow: {e}")
            return False
    
    async def get_followers_count(self, user_id: int) -> int:
        """Get number of followers for a user"""
        try:
            async with self.db_client() as session:
                result = await session.execute(
                    select(func.count(Follow.follower_id)).where(
                        Follow.following_id == user_id
                    )
                )
                count = result.scalar()
                return count if count else 0
        except Exception as e:
            logger.error(f"Error getting followers count: {e}")
            return 0
    
    async def get_following_count(self, user_id: int) -> int:
        """Get number of users this user is following"""
        try:
            async with self.db_client() as session:
                result = await session.execute(
                    select(func.count(Follow.following_id)).where(
                        Follow.follower_id == user_id
                    )
                )
                count = result.scalar()
                return count if count else 0
        except Exception as e:
            logger.error(f"Error getting following count: {e}")
            return 0
