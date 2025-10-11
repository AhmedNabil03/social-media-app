from .social_media_base import SQLAlchemyBase, CreatedAtMixin
from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint, Index
from sqlalchemy.orm import relationship


class Like(SQLAlchemyBase, CreatedAtMixin):
    
    __tablename__ = "likes"
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    # Relationships
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'post_id'),
        Index('idx_like_post_id', 'post_id'),
        Index('idx_like_user_id', 'user_id'),
    )
