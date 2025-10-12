from fastapi import FastAPI
from contextlib import asynccontextmanager
from helpers.config import get_settings
from routes import base_router, user_router
from models.init_db import create_database, run_migrations
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting application...")
        
        settings = get_settings()
        logger.info(f"Database host: {settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}")

        create_database(server_url=settings.SERVER_URL, db_name=settings.POSTGRES_MAIN_DATABASE)
        run_migrations(db_url=settings.DATABASE_URL)
        
        logger.info("Application started and database initialized")
        
        app.db_engine = create_async_engine(settings.DATABASE_ASYNC_URL, echo=False)
        app.db_client = sessionmaker(app.db_engine, class_=AsyncSession, expire_on_commit=False)
        
        logger.info("Database sessionmaker created")

    except Exception as e:
        logger.critical(f"Error during startup: {e}")
        raise e
    
    yield
    
    try:
        logger.info("Shutting down application...")
        
        app.db_engine.dispose()
        
        logger.info("Application shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

app = FastAPI(
    title="Social Media App",
    description="A simple social media application built with FastAPI and PostgreSQL",
    lifespan=lifespan
)

app.include_router(base_router)
app.include_router(user_router)
