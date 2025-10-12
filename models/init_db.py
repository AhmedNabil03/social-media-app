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
        conn = psycopg2.connect(server_url)
        conn.autocommit = True
        
        with conn.cursor() as cursor:
            # Terminate all other connections to the database
            logger.info(f"Terminating other connections to '{db_name}'")
            terminate_query = sql.SQL(
                "SELECT pg_terminate_backend(pg_stat_activity.pid) "
                "FROM pg_stat_activity "
                "WHERE pg_stat_activity.datname = %s "
                "AND pid <> pg_backend_pid()"
            )
            cursor.execute(terminate_query, (db_name,))
            
            logger.info(f"Dropping database if exists: '{db_name}'")
            drop_query = sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name))
            cursor.execute(drop_query)
            
            logger.info(f"Creating database: '{db_name}'")
            create_query = sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db_name))
            cursor.execute(create_query)

            logger.info(f"Database '{db_name}' created successfully")
        
        conn.close()
        return True

    except Exception as e:
        logger.critical(f"Error creating database: {e}")
        return False

def generate_migrations(db_url: str, message: str = "Auto-generated migration") -> bool:
    base_dir = os.path.dirname(__file__)
    migrations_dir = os.path.join(base_dir, "db_schemas", "alembic")
    alembic_ini_path = os.path.join(base_dir, "db_schemas", "alembic.ini")
    
    if not os.path.exists(migrations_dir):
        logger.error(f"Migrations directory not found at: {migrations_dir}")
        return False
    
    if not os.path.exists(alembic_ini_path):
        logger.error(f"alembic.ini not found at: {alembic_ini_path}")
        return False
    
    config = Config(alembic_ini_path)
    config.set_main_option("sqlalchemy.url", db_url)
    config.set_main_option("script_location", migrations_dir)
    
    logger.info(f"Generating migration: '{message}'")
    
    try:
        command.revision(config, autogenerate=False, message=message)
    except Exception as e:
        logger.error(f"Error generating migration: {e}")
        return False

    logger.info("Migration generated successfully")
    
    return True

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
