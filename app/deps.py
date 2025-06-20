from sqlalchemy.orm import Session
from .database import SessionLocal

def get_db():
    """Provides a database session for dependency injection.

    Yields:
        Session: A SQLAlchemy database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()