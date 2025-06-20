import pytest
from fastapi import status
from app import models


def test_create_user(client):
    """Tests creating a user with valid data."""
    user_data = {
        "first_name": "Sabuhi",
        "last_name": "Nazarov",
        "username": "sabuhinazarov",
        "password": "sabuhi123",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "sabuhinazarov"
    assert data["first_name"] == "Sabuhi"
    assert data["last_name"] == "Nazarov"
    assert "password" not in data


def test_create_user_empty_username(client):
    """Tests creating a user with an empty username."""
    user_data = {
        "first_name": "Sabuhi",
        "last_name": "Nazarov",
        "username": "",
        "password": "sabuhi123"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "username" in response.json()["detail"][0]["loc"]


def test_create_user_short_password(client):
    """Tests creating a user with a short password."""
    user_data = {
        "first_name": "Sabuhi",
        "last_name": "Nazarov",
        "username": "sabuhinazarov",
        "password": "short"
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "password" in response.json()["detail"][0]["loc"]


def test_create_user_duplicate_username(client, test_user):
    """Tests creating a user with a duplicate username."""
    user_data = {
        "first_name": "Sabuhi",
        "last_name": "Nazarov",
        "username": test_user["username"],
        "password": "sabuhi123",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Username already registered!"


def test_login_success(client, test_user):
    """Tests successful user login."""
    response = client.post(
        "/token",
        data={"username": test_user["username"], "password": "sabuhi123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client, test_user):
    """Tests login with invalid credentials."""
    response = client.post(
        "/token",
        data={"username": test_user["username"], "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password!"


def test_delete_user(client, token, test_user):
    """Tests deleting the authenticated user."""
    response = client.delete(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK

    response = client.post(
        "/token",
        data={"username": test_user["username"], "password": "sabuhi123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_delete_user_nonexistent(client, token, test_user, session):
    """Tests deleting a user after manual deletion from database."""
    session.query(models.User).filter(models.User.id == test_user["id"]).delete()
    session.commit()
    response = client.delete(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "User not found!"