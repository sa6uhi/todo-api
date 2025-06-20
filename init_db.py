from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from app.database import Base, engine
from app.models import User, Task
from dotenv import load_dotenv
import psycopg2
import time
import os

load_dotenv()

def create_database():
    """Create database for local setup with retry logic"""
    IS_DOCKER = os.getenv("IS_DOCKER", "false").lower() == "true"
    if IS_DOCKER:
        print("Running in Docker, skipping database creation.")
        return

    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=os.getenv("POSTGRES_ADMIN_USER", "postgres"),
                password=os.getenv("POSTGRES_ADMIN_PASSWORD", "postgres"),
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", "5432")
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (os.getenv("POSTGRES_DB", "todo_db"),))
            exists = cursor.fetchone()
            if not exists:
                cursor.execute(f"CREATE DATABASE {os.getenv('POSTGRES_DB', 'todo_db')}")
                print(f"Database '{os.getenv('POSTGRES_DB', 'todo_db')}' created.")
            else:
                print(f"Database '{os.getenv('POSTGRES_DB', 'todo_db')}' already exists.")
            
            cursor.close()
            conn.close()
            return
        except psycopg2.OperationalError as e:
            if attempt == max_retries - 1:
                print(f"Failed to connect after {max_retries} attempts: {e}")
                raise
            print(f"Connection failed (attempt {attempt + 1}), retrying.")
            time.sleep(retry_delay)

def init_db():
    """Initialize database tables"""
    try:
        create_database()
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_db()