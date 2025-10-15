from sqlalchemy import select
from models.BaseModel import BaseModel
from models.db_schemas.schemas.post import Post
import logging

logger = logging.getLogger(__name__)


class PostModel(BaseModel):
    
    async def create_post(self, user_id: int, post_text: str, post_image: str | None = None) -> Post | None:
        try:
            async with self.db_client() as session:
                post = Post(
                    user_id=user_id,
                    post_text=post_text,
                    post_image=post_image
                )
                session.add(post)
                await session.commit()
                await session.refresh(post)
                logger.info(f"Post created: {post.id}")
                return post
        except Exception as e:
            logger.error(f"Error creating post: {e}")
            return None
    
    async def get_post_by_id(self, post_id: int) -> Post | None:
        try:
            async with self.db_client() as session:
                return await session.get(Post, post_id)
        except Exception as e:
            logger.error(f"Error getting post by id: {e}")
            return None
        
    async def get_feed_posts(self, user_id: int, limit: int = 10, offset: int = 0) -> list[Post]:
        try:
            async with self.db_client() as session:
                result = await session.execute(
                    select(Post)
                    .where(Post.user_id != user_id)
                    .order_by(Post.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting feed posts: {e}")
            return []
    
    async def get_posts_by_user_id(self, user_id: int, limit: int = 10, offset: int = 0) -> list[Post]:
        try:
            async with self.db_client() as session:
                result = await session.execute(
                    select(Post)
                    .where(Post.user_id == user_id)
                    .order_by(Post.created_at.desc())
                    .limit(limit)
                    .offset(offset)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting posts by user: {e}")
            return []
    
    async def get_post_by_user_id_and_post_id(self, user_id: int, post_id: int) -> Post | None:
        try:
            async with self.db_client() as session:
                result = await session.execute(
                    select(Post).where(
                        (Post.user_id == user_id) & (Post.id == post_id)
                    )
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting post: {e}")
            return None
    
    async def delete_post(self, post_id: int, user_id: int) -> bool:
        try:
            async with self.db_client() as session:
                post = await session.get(Post, post_id)
                if not post or post.user_id != user_id:
                    logger.warning(f"Post not found or unauthorized: {post_id}")
                    return False
                await session.delete(post)
                await session.commit()
                logger.info(f"Post deleted: {post_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting post: {e}")
            return False
