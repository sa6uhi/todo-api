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
