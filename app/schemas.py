from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from enum import Enum


class TaskStatus(str, Enum):
    NEW = "NEW"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class UserBase(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: Optional[str] = None
    username: str = Field(..., min_length=1)


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class User(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    status: TaskStatus = TaskStatus.NEW


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None


class Task(TaskBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class PaginatedTasks(BaseModel):
    items: List[Task]
    total: int
    skip: int
    limit: int
