from sqlalchemy import Column, Integer, String, Text
from .database import Base
import enum

class TaskStatus(enum.Enum):
    NEW = "New"
    IN_PROGRESS = "In progress"
    COMPLETED = "Completed"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(Text, nullable=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)