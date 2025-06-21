from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError, ExpiredSignatureError
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from . import schemas, crud, auth
from .deps import get_db
from .database import engine, Base
from app.models import User, Task

app = FastAPI()

# Create database tables on startup
Base.metadata.create_all(bind=engine)


@app.get("/")
def read_root():
    """Returns a welcome message for the API.

    Returns:
        dict: A welcome message.
    """
    return {"message": "Welcome to ToDo API"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Creates a new user.

    Returns:
        User: The created user object.
    """
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered!")
    return crud.create_user(db=db, user=user)


@app.delete("/users/me", response_model=None)
def delete_user(
    token: str = Depends(auth.oauth2_scheme),
    db: Session = Depends(get_db),
):
    """Deletes the authenticated user's account.

    Returns:
        None
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Couldn't validate credentials!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise credentials_exception
    crud.delete_user(db=db, user_id=user_id)
    return None


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """Authenticates a user and returns a JWT token.

    Returns:
        dict: JWT access token and token type.
    """
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password!",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/tasks/", response_model=schemas.Task)
def create_task(
    task: schemas.TaskCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(auth.get_current_user),
):
    """Creates a new task for the authenticated user.

    Returns:
        Task: The created task object.
    """
    return crud.create_task(db=db, task=task, user_id=current_user.id)


@app.get("/tasks/", response_model=schemas.PaginatedTasks)
def read_tasks(
    skip: int = 0,
    limit: int = 10,
    status: Optional[schemas.TaskStatus] = None,
    db: Session = Depends(get_db),
):
    """Retrieves a paginated list of tasks with optional status filter.

    Returns:
        dict: Paginated tasks and metadata.
    """
    if skip < 0:
        raise HTTPException(status_code=400, detail="Skip must be non-negative!")
    if limit <= 0 or limit >= 100:
        raise HTTPException(
            status_code=400, detail="Limit must be between 1 and 100 (inclusive)!"
        )
    tasks, total = crud.get_tasks(db, skip=skip, limit=limit, status=status)
    if skip > 0 and skip >= total:
        raise HTTPException(
            status_code=400, detail=f"Skip value {skip} exceeds total tasks {total}"
        )
    return {"items": tasks, "total": total, "skip": skip, "limit": limit}


@app.get("/tasks/user/", response_model=schemas.PaginatedTasks)
def read_user_tasks(
    skip: int = 0,
    limit: int = 10,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves a paginated list of tasks for the authenticated user.

    Returns:
        dict: Paginated user tasks and metadata.
    """
    if skip < 0:
        raise HTTPException(status_code=400, detail="Skip must be non-negative!")
    if limit <= 0 or limit >= 100:
        raise HTTPException(
            status_code=400, detail="Limit must be between 1 and 100 (inclusive)!"
        )
    tasks, total = crud.get_user_tasks(
        db, user_id=current_user.id, skip=skip, limit=limit
    )
    if skip > 0 and skip >= total:
        raise HTTPException(
            status_code=400,
            detail=f"Skip value {skip} exceeds total user tasks {total}",
        )
    return {"items": tasks, "total": total, "skip": skip, "limit": limit}


@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
    """Retrieves a task by its ID.

    Returns:
        Task: The task object.
    """
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found!")
    return db_task


@app.put("/tasks/{task_id}", response_model=schemas.Task)
def update_task(
    task_id: int,
    task: schemas.TaskUpdate,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Updates a task for the authenticated user.

    Returns:
        Task: The updated task object.
    """
    db_task = crud.get_task(db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found!")
    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this task!"
        )
    if task.model_dump(exclude_unset=True) == {}:
        return db_task
    if task.title and (len(task.title.strip()) == 0 or len(task.title) > 100):
        raise HTTPException(
            status_code=422, detail="Title must be between 1 and 100 characters!"
        )
    if task.description and len(task.description) > 500:
        raise HTTPException(
            status_code=422, detail="Description cannot exceed 500 characters!"
        )
    return crud.update_task(db=db, task_id=task_id, task=task)


@app.patch("/tasks/{task_id}/complete", response_model=schemas.Task)
def complete_task(
    task_id: int,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Marks a task as completed for the authenticated user.

    Returns:
        Task: The updated task object.
    """
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found!")
    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this task!"
        )
    return crud.complete_task(db=db, task_id=task_id)


@app.delete("/tasks/{task_id}", response_model=None)
def delete_task(
    task_id: int,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes a task for the authenticated user.

    Returns:
        None
    """
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found!")
    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this task!"
        )
    crud.delete_task(db=db, task_id=task_id)
    return None
