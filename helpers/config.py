from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    
    """Database configuration"""
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str
    
    model_config = SettingsConfigDict(    
        env_file='.env',
        env_file_encoding='utf-8',
    )

@lru_cache()
def get_settings() -> Settings:
    return Settings()
