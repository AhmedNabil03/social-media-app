from fastapi import FastAPI
from contextlib import asynccontextmanager
from helpers.config import get_settings
from routes import base_router
from models.init_db import create_database, run_migrations
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
        
        logger.info("Application startup complete")

    except Exception as e:
        logger.critical(f"Error during startup: {e}")
        raise e
    
    yield
    
    try:
        logger.info("Shutting down application...")
        logger.info("Application shutdown complete")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

app = FastAPI(
    title="Social Media App",
    description="A simple social media application built with FastAPI and PostgreSQL",
    lifespan=lifespan
)

app.include_router(base_router)
