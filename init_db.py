from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import psycopg2
from app.database import Base, engine
from dotenv import load_dotenv
import time
import os

load_dotenv()

def create_database():
    max_retries = 5
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            conn = psycopg2.connect(
                dbname="postgres",
                user=os.getenv("POSTGRES_USER", "postgres"),
                password=os.getenv("POSTGRES_PASSWORD", "postgres"),
                host=os.getenv("POSTGRES_HOST", "localhost"),
                port=os.getenv("POSTGRES_PORT", "5432")
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # this code will create database if it doesn't exist
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'todo_db'")
            exists = cursor.fetchone()
            if not exists:
                cursor.execute("CREATE DATABASE todo_db")
                print("Database 'todo_db' created.")
            else:
                print("Database 'todo_db' already exists.")
            
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = 'todo_user'")
            user_exists = cursor.fetchone()
            if not user_exists:
                cursor.execute("CREATE USER todo_user WITH PASSWORD 'todo_password'")
                print("User 'todo_user' created.")
            cursor.execute("GRANT ALL PRIVILEGES ON DATABASE todo_db TO todo_user")
            print("Privileges granted to 'todo_user'.")
            
            cursor.close()
            conn.close()
            return
        except psycopg2.OperationalError as e:
            if attempt == max_retries - 1:
                raise
            print(f"Connection failed (attempt {attempt + 1}), retrying.")
            time.sleep(retry_delay)

def init_db():
    try:
        create_database()
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    init_db()