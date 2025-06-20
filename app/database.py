from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

IS_DOCKER = os.getenv("IS_DOCKER", "false").lower() == "true"
POSTGRES_USER = os.getenv("POSTGRES_USER") if IS_DOCKER else os.getenv("POSTGRES_ADMIN_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD") if IS_DOCKER else os.getenv("POSTGRES_ADMIN_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_DB = os.getenv("POSTGRES_DB", "todo_db")

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)

if not all([POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DB]):
    raise ValueError("One or more database environment variables are not set.")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()