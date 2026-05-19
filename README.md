# Task Manager API

FastAPI-приложение для управления задачами с поддержкой WebSocket-чата.

## Запуск локально

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Тесты

```bash
pytest
```

## Docker

```bash
docker compose up --build
```

Проверка после запуска:

```bash
curl http://localhost:8000/tasks -H "X-User-Id: 10"
curl http://localhost:8000/health
```

## Структура проекта

```
app/
    main.py          — точка входа, WebSocket, /health
    schemas.py       — Pydantic-модели
    storage.py       — in-memory хранилище задач
    dependencies.py  — зависимости FastAPI (auth, admin, storage)
    routers/
        tasks.py     — CRUD задач (/tasks)
        users.py     — пользователи (/users)
        admin.py     — административные маршруты (/admin)
tests/
    test_tasks.py                       — тесты REST API задач
    test_websocket.py                   — тесты WebSocket-чата
    test_dependencies_and_routing.py    — тесты зависимостей и маршрутизации
```

## API

| Метод  | Маршрут                    | Описание                        |
|--------|----------------------------|---------------------------------|
| POST   | /tasks                     | Создать задачу (201)            |
| GET    | /tasks                     | Список своих задач              |
| GET    | /tasks/{id}                | Получить задачу (404 если чужая)|
| PATCH  | /tasks/{id}/status         | Изменить статус задачи          |
| DELETE | /tasks/{id}                | Удалить задачу (204)            |
| GET    | /users/me                  | Текущий пользователь            |
| GET    | /admin/stats               | Статистика (только admin)       |
| DELETE | /admin/tasks/{id}          | Удалить любую задачу (admin)    |
| GET    | /health                    | Проверка состояния              |
| WS     | /ws/rooms/{room_id}        | WebSocket-чат (?username=alice) |
| GET    | /rooms/{room_id}/users     | Активные пользователи комнаты   |

Авторизация: заголовок `X-User-Id: <int>`, для admin дополнительно `X-User-Role: admin`.
# UNI-server-apps-creation-5
