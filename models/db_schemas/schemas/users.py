from .social_media_base import SQLAlchemyBase
from sqlalchemy import Column, Integer, String, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class User(SQLAlchemyBase):
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    bio = Column(Text, nullable=True)
    
    salt = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    
    # Relationships
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_user_uuid', 'user_uuid'),
        Index('idx_username', 'username'),
        Index('idx_email', 'email'),
    )
