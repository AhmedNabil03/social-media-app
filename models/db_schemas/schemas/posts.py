from .social_media_base import SQLAlchemyBase, TimestampMixin
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class Post(SQLAlchemyBase, TimestampMixin):
    
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    post_text = Column(Text, nullable=False)
    post_image = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="posts")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_post_user_id', 'user_id'),
        Index('idx_post_uuid', 'post_uuid'),
        Index('idx_post_created_at', 'created_at'),
    )
