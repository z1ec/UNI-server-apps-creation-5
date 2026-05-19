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


def test_users_me_returns_current_user(client):
    response = client.get("/users/me", headers={"X-User-Id": "10", "X-User-Role": "user"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 10
    assert data["role"] == "user"


def test_no_user_id_returns_401(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_regular_user_gets_403_on_admin_stats(client):
    response = client.get("/admin/stats", headers={"X-User-Id": "10", "X-User-Role": "user"})
    assert response.status_code == 403


def test_admin_gets_stats(client):
    client.post(
        "/tasks",
        json={"title": "Task one", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"},
    )
    client.post(
        "/tasks",
        json={"title": "Task two", "status": "done", "priority": 2},
        headers={"X-User-Id": "10"},
    )

    response = client.get("/admin/stats", headers={"X-User-Id": "1", "X-User-Role": "admin"})
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 2
    assert data["by_status"]["todo"] == 1
    assert data["by_status"]["done"] == 1


def test_regular_user_cannot_delete_foreign_task(client):
    create_resp = client.post(
        "/tasks",
        json={"title": "Owner task", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"},
    )
    task_id = create_resp.json()["id"]

    response = client.delete(f"/tasks/{task_id}", headers={"X-User-Id": "20"})
    assert response.status_code == 404


def test_admin_can_delete_any_task(client):
    create_resp = client.post(
        "/tasks",
        json={"title": "Owner task", "status": "todo", "priority": 1},
        headers={"X-User-Id": "10"},
    )
    task_id = create_resp.json()["id"]

    response = client.delete(
        f"/admin/tasks/{task_id}",
        headers={"X-User-Id": "1", "X-User-Role": "admin"},
    )
    assert response.status_code == 204


def test_swagger_routes_grouped_by_tags(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    spec = response.json()
    tags_used = set()
    for path_data in spec["paths"].values():
        for method_data in path_data.values():
            tags_used.update(method_data.get("tags", []))
    assert "tasks" in tags_used
    assert "users" in tags_used
    assert "admin" in tags_used


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "env" in data
