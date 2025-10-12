import os
import psycopg2
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database(server_conn):
    conn = psycopg2.connect(server_conn)
    conn.autocommit = True
    
    cursor = conn.cursor()        
    
    cursor.execute("DROP DATABASE IF EXISTS socialmedia")
    cursor.execute("CREATE DATABASE socialmedia")
    
    logger.info("Database created")
    
    cursor.close()
    conn.close()
    
    return True

def run_migrations() -> bool:
    alembic_dir = os.path.join(os.path.dirname(__file__), "db_schemas")
    
    if not alembic_dir or not os.path.exists(os.path.join(alembic_dir, "alembic.ini")):
        logger.error("Alembic configuration not found.")
        return False
    
    logger.info(f"Running migrations in {alembic_dir}")
    
    # Run alembic upgrade
    result = subprocess.run(
        ["alembic", "upgrade", "head"],
        cwd=str(alembic_dir),
        capture_output=True,
        text=True,
        timeout=30
    )
    
    if result.returncode == 0:
        logger.info("Database migrations applied successfully.")
        
    return True
