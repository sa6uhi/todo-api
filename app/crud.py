from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Tuple
from . import models, schemas
from passlib.context import CryptContext
from .auth import pwd_context


def get_user_by_username(db: Session, username: str):
    """Retrieves a user by their username.

    Returns:
        User or None: The user object if found, None otherwise.
    """
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    """Creates a new user with hashed password.

    Returns:
        User: The created user object.
    """
    try:
        hashed_password = pwd_context.hash(user.password)
        db_user = models.User(
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            password=hashed_password,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Username already registered!"
        )


def delete_user(db: Session, user_id: int):
    """Deletes a user by their ID.

    Returns:
        None
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found!")
    db.delete(user)
    db.commit()


def get_task(db: Session, task_id: int):
    """Retrieves a task by its ID.

    Returns:
        Task or None: The task object if found, None otherwise.
    """
    return db.query(models.Task).filter(models.Task.id == task_id).first()


def get_tasks(db: Session, skip: int = 0, limit: int = 10, status: Optional[schemas.TaskStatus] = None) -> Tuple[List[models.Task], int]:
    """Retrieves a list of tasks with pagination and optional status filter.

    Returns:
        tuple: List of tasks and total count.
    """
    query = db.query(models.Task)
    if status:
        query = query.filter(models.Task.status == status)
    total = query.count()
    tasks = query.offset(skip).limit(limit).all()
    return tasks, total


def get_user_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 10) -> Tuple[List[models.Task], int]:
    """Retrieves a list of tasks for a specific user with pagination.

    Returns:
        tuple: List of user tasks and total count.
    """
    query = db.query(models.Task).filter(models.Task.user_id == user_id)
    total = query.count()
    tasks = query.offset(skip).limit(limit).all()
    return tasks, total


def create_task(db: Session, task: schemas.TaskCreate, user_id: int):
    """Creates a new task for a user.

    Returns:
        Task: The created task object.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"User with id {user_id} not found"
        )
    db_task = models.Task(**task.model_dump(), user_id=user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task: schemas.TaskUpdate):
    """Updates an existing task.

    Returns:
        Task: The updated task object.
    """
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found!")
    update_data = task.model_dump(exclude_unset=True)
    if not update_data:
        return db_task
    for key, value in update_data.items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task


def complete_task(db: Session, task_id: int):
    """Marks a task as completed.

    Returns:
        Task: The updated task object.
    """
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found!")
    if task.status == models.TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail="Task is already completed!"
        )
    task.status = models.TaskStatus.COMPLETED
    db.commit()
    db.refresh(task)
    return task


def delete_task(db: Session, task_id: int):
    """Deletes a task by its ID.

    Returns:
        None
    """
    db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task