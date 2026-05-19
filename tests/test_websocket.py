import pytest
from fastapi.testclient import TestClient
from app.main import app, room_manager


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_rooms():
    room_manager._rooms.clear()
    yield
    room_manager._rooms.clear()


def test_connect_with_valid_username(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        data = ws.receive_json()
        assert data["type"] == "connect"
        assert data["username"] == "alice"


def test_send_and_receive_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # connect event
        ws.send_json({"type": "message", "text": "Всем привет"})
        data = ws.receive_json()
        assert data["type"] == "message"
        assert data["text"] == "Всем привет"
        assert data["username"] == "alice"
        assert data["room_id"] == "python"


def test_two_clients_same_room_receive_same_message(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws1:
        ws1.receive_json()  # alice connect
        with client.websocket_connect("/ws/rooms/python?username=bob") as ws2:
            ws1.receive_json()  # bob connect event in ws1
            ws2.receive_json()  # bob connect event in ws2
            ws1.send_json({"type": "message", "text": "Hi everyone"})
            msg1 = ws1.receive_json()
            msg2 = ws2.receive_json()
            assert msg1["text"] == "Hi everyone"
            assert msg2["text"] == "Hi everyone"


def test_different_rooms_isolation(client):
    with client.websocket_connect("/ws/rooms/room1?username=alice") as ws1:
        ws1.receive_json()  # alice connect
        with client.websocket_connect("/ws/rooms/room2?username=bob") as ws2:
            ws2.receive_json()  # bob connect

            users1 = client.get("/rooms/room1/users").json()
            users2 = client.get("/rooms/room2/users").json()

            assert "alice" in users1["users"]
            assert "bob" not in users1["users"]
            assert "bob" in users2["users"]
            assert "alice" not in users2["users"]


def test_long_message_returns_error(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # connect event
        ws.send_json({"type": "message", "text": "x" * 301})
        data = ws.receive_json()
        assert data["type"] == "error"
        assert data["detail"] == "Message is too long"


def test_disconnect_removes_user(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()  # connect event

    response = client.get("/rooms/python/users")
    assert "alice" not in response.json()["users"]
