from .social_media_base import SQLAlchemyBase, TimestampMixin
from sqlalchemy import Column, Integer, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class Comment(SQLAlchemyBase, TimestampMixin):
    
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_uuid = Column(
        UUID(as_uuid=True), 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
    )
    
    comment_text = Column(Text, nullable=False)
    
    # Foreign Keys
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    
    # Self-referential relationship
    replies = relationship("Comment", back_populates="parent", remote_side=[parent_comment_id], cascade="all, delete-orphan")
    parent = relationship("Comment", back_populates="replies", remote_side=[id])

    __table_args__ = (
        Index('idx_comment_uuid', 'comment_uuid'),
        Index('idx_comment_user_id', 'user_id'),
        Index('idx_comment_post_id', 'post_id'),
        Index('idx_comment_parent_id', 'parent_comment_id'),
        Index('idx_comment_post_created', 'post_id', 'created_at'),
    )
