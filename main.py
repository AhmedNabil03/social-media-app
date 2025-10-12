from fastapi import FastAPI
from helpers.config import get_settings
from routes import base_router
from models.init_db import create_database, run_migrations

app = FastAPI()

async def startup_span():
    
    settings = get_settings()
        
    create_database(settings.SERVER_URL)
    run_migrations()
    
async def shutdown_span():
    pass

app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base_router)
