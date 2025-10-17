from .social_media_base import SQLAlchemyBase, TimestampMixin
from sqlalchemy import Column, Integer, String, Text, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class User(SQLAlchemyBase, TimestampMixin):

    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_uuid = Column(
        UUID(as_uuid=True), 
        default=uuid.uuid4, 
        unique=True, 
        nullable=False
    )
    
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    bio = Column(Text, nullable=True)
    
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    
    following = relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower", cascade="all, delete-orphan", lazy="dynamic")
    followers = relationship("Follow", foreign_keys="Follow.following_id", back_populates="following", cascade="all, delete-orphan", lazy="dynamic")

    __table_args__ = (
        Index('idx_user_uuid', 'user_uuid'),
        Index('idx_user_username', 'username'),
        Index('idx_user_email', 'email'),
    )
