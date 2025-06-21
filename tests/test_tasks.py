import pytest
from app import models, schemas
from fastapi import status


def test_create_task(client, token):
    """Tests creating a task with valid data."""
    task_data = {"title": "Test Task",
                 "description": "Test Description"}
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


def test_create_task_invalid_title(client, token):
    """Tests creating a task with an invalid title."""
    task_data = {"title": "", "description": "Invalid"}
    response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "title" in response.json()["detail"][0]["loc"]


def test_create_task_without_token(client):
    """Tests creating a task without authentication."""
    task_data = {"title": "Test Task Without Token",
                 "description": "Test Description"}
    response = client.post("/tasks/", json=task_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"] == "Not authenticated"


def test_create_task_with_invalid_token(client):
    """Tests creating a task with an invalid token."""
    task_data = {"title": "Test Task With Invalid Token",
                 "description": "Test Description"}
    response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert data["detail"] == "Couldn't validate credentials!"


def test_read_tasks(client):
    """Tests retrieving a paginated list of tasks."""
    response = client.get("/tasks/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data


def test_read_user_tasks(client, token):
    """Tests retrieving a paginated list of user tasks."""
    response = client.get(
        "/tasks/user/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_read_task(client, token):
    """Tests retrieving a task by ID."""
    task_data = {"title": "Task to Read", "description": "Read Test"}
    create_response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK
    task_id = create_response.json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Task to Read"


def test_update_task(client, token):
    """Tests updating a task with valid data."""
    task_data = {"title": "Task to Update", "description": "Update Test"}
    create_response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK
    task_id = create_response.json()["id"]
    update_data = {"title": "Updated Task", "status": "IN_PROGRESS"}
    response = client.put(
        f"/tasks/{task_id}",
        json=update_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Updated Task"
    assert data["status"] == "IN_PROGRESS"


def test_complete_task(client, token):
    """Tests marking a task as completed."""
    task_data = {"title": "Task to Complete", "description": "Complete Test"}
    create_response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK
    task_id = create_response.json()["id"]
    response = client.patch(
        f"/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "COMPLETED"


def test_delete_task(client, token):
    """Tests deleting a task."""
    task_data = {"title": "Task to Delete", "description": "Delete Test"}
    create_response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK
    task_id = create_response.json()["id"]
    response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_read_tasks_with_pagination_and_status(client, token):
    """Tests retrieving tasks with pagination and status filter."""
    create_response1 = client.post(
        "/tasks/",
        json={"title": "Task 1", "status": "NEW"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response1.status_code == status.HTTP_200_OK
    create_response2 = client.post(
        "/tasks/",
        json={"title": "Task 2", "status": "IN_PROGRESS"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response2.status_code == status.HTTP_200_OK
    response = client.get("/tasks/?skip=0&limit=1&status=NEW")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "NEW"
    assert data["total"] >= 1


def test_read_tasks_invalid_skip(client):
    """Tests retrieving tasks with an invalid skip value."""
    response = client.get("/tasks/?skip=-1")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Skip must be non-negative!"


def test_read_tasks_invalid_limit(client):
    """Tests retrieving tasks with an invalid limit value."""
    response1 = client.get("/tasks/?limit=0")
    assert response1.status_code == status.HTTP_400_BAD_REQUEST
    assert response1.json()["detail"] == "Limit must be between 1 and 100 (inclusive)!"

    response2 = client.get("/tasks/?limit=101")
    assert response2.status_code == status.HTTP_400_BAD_REQUEST
    assert response2.json()["detail"] == "Limit must be between 1 and 100 (inclusive)!"


def test_update_task_empty_update(client, token):
    """Tests updating a task with no fields provided."""
    task_data = {"title": "Task to Update", "description": "Update Test"}
    create_response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK
    task_id = create_response.json()["id"]
    response = client.put(
        f"/tasks/{task_id}",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Task to Update"
    assert data["description"] == "Update Test"


def test_update_task_invalid_status(client, token):
    """Tests updating a task with an invalid status."""
    task_data = {"title": "Task to Update", "description": "Update Test"}
    create_response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK
    task_id = create_response.json()["id"]
    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Updated Task", "status": "INVALID"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_create_task_max_length(client, token):
    """Tests creating a task with maximum title and description lengths."""
    max_title = "x" * 100
    max_description = "x" * 500
    task_data = {"title": max_title, "description": max_description}
    response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == max_title
    assert data["description"] == max_description


def test_create_task_exceed_max_length(client, token):
    """Tests creating a task with title and description exceeding maximum lengths."""
    max_title = "x" * 101
    max_description = "x" * 501
    task_data = {"title": max_title, "description": max_description}
    response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_read_tasks_invalid_status(client):
    """Tests retrieving tasks with an invalid status filter."""
    response = client.get("/tasks/?status=INVALID")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = client.get("/tasks/?status=new")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    response = client.get("/tasks/?status=In_Progress")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_update_task_redundant_status(client, token):
    """Tests updating a task with the same status."""
    task_data = {"title": "Task", "status": "COMPLETED"}
    create_response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK
    task_id = create_response.json()["id"]
    response = client.put(
        f"/tasks/{task_id}",
        json={"status": "COMPLETED"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "COMPLETED"


def test_update_task_unauthorized(client, token, session):
    """Tests updating a task owned by another user."""
    second_user = {"username": "otheruser", "password": "sabuhi123", "first_name": "Other", "last_name": "User"}
    client.post("/users/", json=second_user)
    second_user_token_response = client.post(
        "/token",
        data={"username": "otheruser", "password": "sabuhi123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert second_user_token_response.status_code == status.HTTP_200_OK
    second_user_token = second_user_token_response.json()["access_token"]
    
    task_data = {"title": "Task"}
    create_response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK
    task_id = create_response.json()["id"]
    
    response = client.put(
        f"/tasks/{task_id}",
        json={"title": "Unauthorized Update"},
        headers={"Authorization": f"Bearer {second_user_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized to update this task!"


def test_read_tasks_pagination_boundaries(client, token):
    """Tests retrieving tasks with boundary pagination values."""

    for i in range(3):
        client.post(
            "/tasks/",
            json={"title": f"Task {i}"},
            headers={"Authorization": f"Bearer {token}"},
        )

    response = client.get("/tasks/?skip=0&limit=100")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) >= 3
    assert data["total"] >= 3
    assert data["skip"] == 0
    assert data["limit"] == 100

    response = client.get("/tasks/?skip=0&limit=1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    assert data["total"] >= 3
    assert data["skip"] == 0
    assert data["limit"] == 1


def test_complete_task_unauthorized(client, token, session):
    """Tests marking a task as completed by a non-owner."""

    second_user = {"username": "otheruser2", "password": "sabuhi123", "first_name": "Other2", "last_name": "User2"}
    client.post("/users/", json=second_user)
    second_user_token_response = client.post(
        "/token",
        data={"username": "otheruser2", "password": "sabuhi123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert second_user_token_response.status_code == status.HTTP_200_OK
    second_user_token = second_user_token_response.json()["access_token"]
    
    task_data = {"title": "Task"}
    create_response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK
    task_id = create_response.json()["id"]
    
    response = client.patch(
        f"/tasks/{task_id}/complete",
        headers={"Authorization": f"Bearer {second_user_token}"},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized to update this task!"

def test_delete_task_unauthorized(client, token, session):
    """Tests deleting a task owned by another user."""

    second_user = {"username": "otheruser3", "password": "sabuhi123", "first_name": "Other3", "last_name": "User3"}
    client.post("/users/", json=second_user)
    second_user_token_response = client.post(
        "/token",
        data={"username": "otheruser3", "password": "sabuhi123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert second_user_token_response.status_code == status.HTTP_200_OK
    second_user_token = second_user_token_response.json()["access_token"]
    
    task_data = {"title": "Task"}
    create_response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == status.HTTP_200_OK
    task_id = create_response.json()["id"]
    
    response = client.delete(
        f"/tasks/{task_id}",
        headers={"Authorization": f"Bearer {second_user_token}"},
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json()["detail"] == "Not authorized to delete this task!"