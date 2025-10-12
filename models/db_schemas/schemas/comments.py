from .social_media_base import SQLAlchemyBase, TimestampMixin
from sqlalchemy import Column, Integer, Text, ForeignKey, PrimaryKeyConstraint, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class Comment(SQLAlchemyBase, TimestampMixin):
    
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    comment_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)

    comment_text = Column(Text, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
    replies = relationship("Comment", back_populates="parent", cascade="all, delete-orphan", remote_side=[id])
    parent = relationship("Comment", back_populates="replies", remote_side=[parent_comment_id], foreign_keys=[parent_comment_id])

    __table_args__ = (
        Index('idx_comment_uuid', 'comment_uuid'),
        Index('idx_comment_user_id', 'user_id'),
        Index('idx_comment_post_id', 'post_id'),
        Index('idx_comment_parent_comment_id', 'parent_comment_id'),
    )
