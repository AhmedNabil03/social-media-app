from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint, Index
from sqlalchemy.orm import relationship
from .social_media_base import SQLAlchemyBase, CreatedAtMixin


class Follow(SQLAlchemyBase, CreatedAtMixin):
    __tablename__ = "follows"
    
    follower_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        primary_key=True
    )
    following_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        primary_key=True
    )
    
    # Relationships
    follower = relationship(
        "User",
        foreign_keys=[follower_id],
        backref="following"
    )
    following = relationship(
        "User",
        foreign_keys=[following_id],
        backref="followers"
    )
    
    __table_args__ = (
        PrimaryKeyConstraint('follower_id', 'following_id'),
        Index('idx_follower_id', 'follower_id'),
        Index('idx_following_id', 'following_id'),
    )
