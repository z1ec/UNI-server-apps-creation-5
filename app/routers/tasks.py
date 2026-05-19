from fastapi import APIRouter, Depends, HTTPException
from typing import Optional, List
from app.schemas import Task, TaskCreate, TaskStatusUpdate, User
from app.dependencies import get_current_user, get_storage
from app.storage import TaskStorage

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=Task, status_code=201)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    store: TaskStorage = Depends(get_storage),
):
    task = Task(
        id=0,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        owner_id=current_user.id,
    )
    return store.add(task)


@router.get("", response_model=List[Task])
def get_tasks(
    status: Optional[str] = None,
    min_priority: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    store: TaskStorage = Depends(get_storage),
):
    tasks = [t for t in store.get_all() if t.owner_id == current_user.id]
    if status is not None:
        tasks = [t for t in tasks if t.status == status]
    if min_priority is not None:
        tasks = [t for t in tasks if t.priority >= min_priority]
    return tasks


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    store: TaskStorage = Depends(get_storage),
):
    task = store.get_by_id(task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}/status", response_model=Task)
def update_task_status(
    task_id: int,
    status_update: TaskStatusUpdate,
    current_user: User = Depends(get_current_user),
    store: TaskStorage = Depends(get_storage),
):
    task = store.get_by_id(task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    return store.update_status(task_id, status_update.status)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    store: TaskStorage = Depends(get_storage),
):
    task = store.get_by_id(task_id)
    if task is None or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")
    store.delete(task_id)
