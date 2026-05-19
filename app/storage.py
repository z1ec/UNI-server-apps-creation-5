from typing import Dict, List, Optional
from app.schemas import Task, TaskStatus


class TaskStorage:
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._counter = 0

    def add(self, task: Task) -> Task:
        self._counter += 1
        saved = task.model_copy(update={"id": self._counter})
        self._tasks[self._counter] = saved
        return saved

    def get_all(self) -> List[Task]:
        return list(self._tasks.values())

    def get_by_id(self, task_id: int) -> Optional[Task]:
        return self._tasks.get(task_id)

    def update_status(self, task_id: int, status: TaskStatus) -> Optional[Task]:
        task = self._tasks.get(task_id)
        if task is None:
            return None
        updated = task.model_copy(update={"status": status})
        self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: int) -> bool:
        if task_id in self._tasks:
            del self._tasks[task_id]
            return True
        return False

    def clear(self):
        self._tasks.clear()
        self._counter = 0


storage = TaskStorage()
