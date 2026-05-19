import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.storage import storage


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_storage():
    storage.clear()
    yield
    storage.clear()


def test_create_task_success(client):
    response = client.post(
        "/tasks",
        json={"title": "Подготовить тесты", "status": "todo", "priority": 4},
        headers={"X-User-Id": "10"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Подготовить тесты"
    assert data["owner_id"] == 10
    assert data["id"] == 1


def test_create_task_title_too_short(client):
    response = client.post(
        "/tasks",
        json={"title": "AB", "status": "todo", "priority": 3},
        headers={"X-User-Id": "10"},
    )
    assert response.status_code == 422


def test_create_task_no_auth(client):
    response = client.post(
        "/tasks",
        json={"title": "Test task", "status": "todo", "priority": 3},
    )
    assert response.status_code == 401


def test_user_sees_only_own_tasks(client):
    client.post(
        "/tasks",
        json={"title": "Task user 10", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"},
    )
    client.post(
        "/tasks",
        json={"title": "Task user 20", "status": "todo", "priority": 1},
        headers={"X-User-Id": "20"},
    )

    response = client.get("/tasks", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["owner_id"] == 10


def test_filter_by_status(client):
    client.post(
        "/tasks",
        json={"title": "Todo task", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"},
    )
    client.post(
        "/tasks",
        json={"title": "Done task", "status": "done", "priority": 1},
        headers={"X-User-Id": "10"},
    )

    response = client.get("/tasks?status=todo", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["status"] == "todo"


def test_filter_by_min_priority(client):
    client.post(
        "/tasks",
        json={"title": "Low priority", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"},
    )
    client.post(
        "/tasks",
        json={"title": "High priority", "status": "todo", "priority": 4},
        headers={"X-User-Id": "10"},
    )

    response = client.get("/tasks?min_priority=3", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["priority"] == 4


def test_update_task_status(client):
    create_resp = client.post(
        "/tasks",
        json={"title": "Test task", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"},
    )
    task_id = create_resp.json()["id"]

    response = client.patch(
        f"/tasks/{task_id}/status",
        json={"status": "done"},
        headers={"X-User-Id": "10"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_get_foreign_task_returns_404(client):
    create_resp = client.post(
        "/tasks",
        json={"title": "Test task", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"},
    )
    task_id = create_resp.json()["id"]

    response = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "20"})
    assert response.status_code == 404


def test_delete_task_success(client):
    create_resp = client.post(
        "/tasks",
        json={"title": "Test task", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"},
    )
    task_id = create_resp.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert response.status_code == 204

    get_resp = client.get(f"/tasks/{task_id}", headers={"X-User-Id": "10"})
    assert get_resp.status_code == 404
