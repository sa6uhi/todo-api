from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    password = pwd_context.hash(user.password)
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        password=password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user