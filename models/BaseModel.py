from sqlalchemy.ext.asyncio import AsyncSession
from helpers.config import get_settings


class BaseModel:
    def __init__(self, db_client):
        self.settings = get_settings()
        self.db_client = db_client
