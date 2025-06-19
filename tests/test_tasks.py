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
    if response.status_code != status.HTTP_200_OK:
        print(f"Create task failed: {response.json()}")  # debugging
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
    if response.status_code != status.HTTP_200_OK:
        print(f"Read user tasks failed: {response.json()}")  # debugging
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
    if create_response.status_code != status.HTTP_200_OK:
        # debugging
        print(f"Create task for read failed: {create_response.json()}")
    assert create_response.status_code == status.HTTP_200_OK
    task_id = create_response.json()["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["title"] == "Task to Read"


def test_update_task(client, token):
    task_data = {"title": "Task to Update", "description": "Update Test"}
    create_response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    if create_response.status_code != status.HTTP_200_OK:
        # debugging
        print(f"Create task for update failed: {create_response.json()}")
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
    task_data = {"title": "Task to Complete", "description": "Complete Test"}
    create_response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    if create_response.status_code != status.HTTP_200_OK:
        # debugging
        print(f"Create task for complete failed: {create_response.json()}")
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
    task_data = {"title": "Task to Delete", "description": "Delete Test"}
    create_response = client.post(
        "/tasks/",
        json=task_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    if create_response.status_code != status.HTTP_200_OK:
        # debugging
        print(f"Create task for delete failed: {create_response.json()}")
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
    create_response1 = client.post(
        "/tasks/",
        json={"title": "Task 1", "status": "NEW"},
        headers={"Authorization": f"Bearer {token}"},
    )
    if create_response1.status_code != status.HTTP_200_OK:
        print(f"Create task 1 failed: {create_response1.json()}")  # debugging
    create_response2 = client.post(
        "/tasks/",
        json={"title": "Task 2", "status": "IN_PROGRESS"},
        headers={"Authorization": f"Bearer {token}"},
    )
    if create_response2.status_code != status.HTTP_200_OK:
        print(f"Create task 2 failed: {create_response2.json()}")  # debugging
    response = client.get("/tasks/?skip=0&limit=1&status=NEW")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["status"] == "NEW"
    assert data["total"] >= 1