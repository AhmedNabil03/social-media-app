from .social_media_base import SQLAlchemyBase, CreatedAtMixin
from sqlalchemy import Column, Integer, ForeignKey, Index
from sqlalchemy.orm import relationship

class Follow(SQLAlchemyBase, CreatedAtMixin):
    
    __tablename__ = "follows"
    
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True, nullable=False)
    following_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True, nullable=False)
    
    # Relationships
    follower = relationship("User", foreign_keys=[follower_id], back_populates="following")
    following = relationship("User", foreign_keys=[following_id], back_populates="followers")
    
    __table_args__ = (
        Index('idx_follow_follower_id', 'follower_id'), 
        Index('idx_follow_following_id', 'following_id'), 
        Index('idx_follow_created_at', 'created_at'), 
    )
