from sqlalchemy import select
from models.BaseModel import BaseModel
from models.db_schemas.schemas.comment import Comment
import logging

logger = logging.getLogger(__name__)


class CommentModel(BaseModel):
    
    async def add_comment(self, user_id: int, post_id: int, comment_text: str, parent_comment_id: int = None) -> Comment | None:
        try:
            async with self.db_client() as session:
                comment = Comment(
                    user_id=user_id,
                    post_id=post_id,
                    comment_text=comment_text,
                    parent_comment_id=parent_comment_id
                )
                session.add(comment)
                await session.commit()
                await session.refresh(comment)
                logger.info(f"Comment created: {comment.id}")
                return comment
        except Exception as e:
            logger.error(f"Error adding comment: {e}")
            return None
    
    async def get_comment_by_id(self, comment_id: int) -> Comment | None:
        try:
            async with self.db_client() as session:
                return await session.get(Comment, comment_id)
        except Exception as e:
            logger.error(f"Error getting comment by id: {e}")
            return None
    
    async def get_comment_by_uuid(self, comment_uuid: str) -> Comment | None:
        try:
            async with self.db_client() as session:
                result = await session.execute(
                    select(Comment).where(Comment.comment_uuid == comment_uuid)
                )
                return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting comment by uuid: {e}")
            return None
    
    async def update_comment(self, comment_id: int, user_id: int, comment_text: str) -> Comment | None:
        try:
            async with self.db_client() as session:
                comment = await session.get(Comment, comment_id)
                if not comment or comment.user_id != user_id:
                    logger.warning(f"Comment not found or unauthorized: {comment_id}")
                    return None
                
                comment.comment_text = comment_text
                await session.commit()
                await session.refresh(comment)
                logger.info(f"Comment updated: {comment_id}")
                return comment
        except Exception as e:
            logger.error(f"Error updating comment: {e}")
            return None
    
    async def remove_comment(self, comment_id: int, user_id: int) -> bool:
        try:
            async with self.db_client() as session:
                comment = await session.get(Comment, comment_id)
                if not comment or comment.user_id != user_id:
                    logger.warning(f"Comment not found or unauthorized: {comment_id}")
                    return False
                await session.delete(comment)
                await session.commit()
                logger.info(f"Comment deleted: {comment_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting comment: {e}")
            return False
    
    async def get_comments(self, post_id: int, limit: int = 20, offset: int = 0, parent_comment_id: int = None) -> list[Comment]:
        try:
            async with self.db_client() as session:
                query = select(Comment).where(Comment.post_id == post_id)
                
                if parent_comment_id is not None:
                    query = query.where(Comment.parent_comment_id == parent_comment_id)
                else:
                    query = query.where(Comment.parent_comment_id == None)
                
                query = query.order_by(Comment.created_at.desc()).limit(limit).offset(offset)
                
                result = await session.execute(query)
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting comments: {e}")
            return []
    
    async def get_replies(self, parent_comment_id: int, limit: int = 20, offset: int = 0) -> list[Comment]:
        try:
            async with self.db_client() as session:
                result = await session.execute(
                    select(Comment)
                    .where(Comment.parent_comment_id == parent_comment_id)
                    .order_by(Comment.created_at.asc())
                    .limit(limit)
                    .offset(offset)
                )
                return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting replies: {e}")
            return []
