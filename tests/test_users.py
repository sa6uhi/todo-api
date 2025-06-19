import pytest
from fastapi import status


def test_create_user(client):
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
    response = client.post(
        "/token",
        data={"username": test_user["username"], "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["detail"] == "Incorrect username or password!"