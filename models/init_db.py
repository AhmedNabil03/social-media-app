import os
import psycopg2
from psycopg2 import sql
from alembic.config import Config
from alembic import command
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database(server_url: str, db_name: str) -> bool:
    try:
        with psycopg2.connect(server_url, autocommit=True) as conn:
            with conn.cursor() as cursor:

                logger.info(f"Dropping database if exists: '{db_name}'")
                drop_query = sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name))
                cursor.execute(drop_query)
                
                logger.info(f"Creating database: '{db_name}'")
                create_query = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name))
                cursor.execute(create_query)

                logger.info(f"Database '{db_name}' created successfully")
                return True

    except Exception as e:
        logger.critical(f"Error creating database: {e}")
        return False

def run_migrations(db_url: str) -> bool:
    base_dir = os.path.dirname(__file__)
    migrations_dir = os.path.join(base_dir, "db_schemas", "alembic")
    alembic_ini_path = os.path.join(base_dir, "db_schemas", "alembic.ini")

    if not os.path.exists(migrations_dir):
        logger.error(f"Migrations directory not found at: {migrations_dir}")
        return False

    if not os.path.exists(alembic_ini_path):
        logger.error(f"alembic.ini not found at: {alembic_ini_path}")
        return False
    
    config = Config()
    config.set_main_option("script_location", migrations_dir)
    config.set_main_option("sqlalchemy.url", db_url)

    logger.info(f"Running migrations from: {migrations_dir}")
    
    try:
        command.upgrade(config, "head")
    except Exception as e:
        logger.error(f"Error running migrations: {e}")
        return False
    
    logger.info("Database migrations applied successfully")
    
    return True
