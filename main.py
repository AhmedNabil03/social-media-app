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
    logger.info("Starting application...")
    
    settings = get_settings()
    
    create_database(settings.SERVER_URL)
    run_migrations()
    
    yield
    
    logger.info("Shutting down application...")

app = FastAPI(
    title="Social Media App",
    description="A simple social media application built with FastAPI and PostgreSQL",
    lifespan=lifespan
)

app.include_router(base_router)
