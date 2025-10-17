from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, func


class SQLAlchemyBase(DeclarativeBase):
    pass


class CreatedAtMixin:
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class TimestampMixin:
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )
