import pytest
from fastapi import status


def test_create_task(client, token):
    task_data = {"title": "Test Task",
                 "description": "Test Description", "status": "NEW"}
    response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Test Task"
    assert data["status"] == "NEW"
    assert "id" in data
    assert "user_id" in data


def test_read_tasks(client):
    response = client.get("/tasks/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data


def test_read_user_tasks(client, token):
    response = client.get(
        "/tasks/user/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_read_task(client, token):
    task_data = {"title": "Task to Read", "description": "Read Test"}
    create_response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    task_id = create_response.json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Task to Read"
