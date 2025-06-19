from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from . import schemas, crud, auth
from .deps import get_db

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": "Welcome to ToDo API"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400, detail="Username already registered!")
    return crud.create_user(db=db, user=user)


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
    return crud.create_task(db=db, task=task, user_id=current_user.id)


@app.get("/tasks/", response_model=schemas.PaginatedTasks)
def read_tasks(
    skip: int = 0,
    limit: int = 10,
    status: Optional[schemas.TaskStatus] = None,
    db: Session = Depends(get_db),
):
    if skip < 0:
        raise HTTPException(
            status_code=400,
            detail="Skip must be non-negative!"
        )
    if limit <= 0 or limit > 100:  # example limit range
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100!"
        )
    tasks, total = crud.get_tasks(db, skip=skip, limit=limit, status=status)
    return {"items": tasks, "total": total, "skip": skip, "limit": limit}


@app.get("/tasks/user/", response_model=schemas.PaginatedTasks)
def read_user_tasks(
    skip: int = 0,
    limit: int = 10,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    if skip < 0:
        raise HTTPException(
            status_code=400,
            detail="Skip must be non-negative!"
        )
    if limit <= 0 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100!"
        )
    tasks, total = crud.get_user_tasks(
        db, user_id=current_user.id, skip=skip, limit=limit)
    return {"items": tasks, "total": total, "skip": skip, "limit": limit}


@app.get("/tasks/{task_id}", response_model=schemas.Task)
def read_task(task_id: int, db: Session = Depends(get_db)):
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
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found!")
    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this task!")
    return crud.update_task(db=db, task_id=task_id, task=task)


@app.patch("/tasks/{task_id}/complete", response_model=schemas.Task)
def complete_task(
    task_id: int,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found!")
    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this task!")
    return crud.complete_task(db=db, task_id=task_id)


@app.delete("/tasks/{task_id}", response_model=None)
def delete_task(
    task_id: int,
    current_user: schemas.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db),
):
    db_task = crud.get_task(db, task_id=task_id)
    if db_task is None:
        raise HTTPException(status_code=404, detail="Task not found!")
    if db_task.user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this task!")
    crud.delete_task(db=db, task_id=task_id)
    return None
