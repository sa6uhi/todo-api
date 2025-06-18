from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import List
from . import models, schemas, crud, auth
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
    # return schemas.Token(access_token=access_token, token_type="bearer") TODO


@app.get("/tasks/", response_model=List[schemas.Task])
def read_tasks(db: Session = Depends(get_db)):
    tasks = crud.get_tasks(db)
    return tasks


@app.get("/tasks/user/", response_model=List[schemas.Task])
def read_user_tasks(current_user: schemas.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    tasks = crud.get_user_tasks(db, user_id=current_user.id)
    return tasks
