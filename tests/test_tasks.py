import pytest
from fastapi import status

def test_create_task(client, token):
    task_data = {"title": "Test Task", "description": "Test Description", "status": "NEW"}
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