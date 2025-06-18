from passlib.context import CryptContext
from . import models
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(
        models.User.username == username).first()
    if not user or not verify_password(password, user.password):
        return False
    return user
