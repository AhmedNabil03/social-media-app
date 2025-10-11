from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, func


class SQLAlchemyBase(DeclarativeBase):
    pass


class CreatedAtMixin:
    """Mixin for created_at only"""
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class TimestampMixin:
    """Mixin for created_at and updated_at"""
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
