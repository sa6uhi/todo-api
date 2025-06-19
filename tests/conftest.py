import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.deps import get_db
from app import models, schemas
from passlib.context import CryptContext

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def session():
    models.Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    models.Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]


@pytest_asyncio.fixture
async def test_user(session):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("sabuhi123")
    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "username": "testuser",
        "password": hashed_password,
    }
    db_user = models.User(**user_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    print(f"Created test user: {db_user.username}, ID: {db_user.id}")
    return schemas.User(**user_data, id=db_user.id).model_dump()


@pytest_asyncio.fixture
async def token(client, test_user):
    response = client.post(
        "/token",
        data={"username": test_user["username"], "password": "sabuhi123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token
