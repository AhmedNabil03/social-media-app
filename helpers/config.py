from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    
    # Database configuration
    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str
    
    # Server configuration
    JWT_SECRET_KEY: str
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
    )
    
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_MAIN_DATABASE}"
        )
    
    @property
    def DATABASE_ASYNC_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_MAIN_DATABASE}"
        )
    
    @property
    def SERVER_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/postgres"
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
