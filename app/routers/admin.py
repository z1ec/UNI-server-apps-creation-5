from fastapi import APIRouter, Depends, HTTPException
from app.schemas import User
from app.dependencies import require_admin, get_storage
from app.storage import TaskStorage

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
def get_stats(
    current_user: User = Depends(require_admin),
    store: TaskStorage = Depends(get_storage),
):
    tasks = store.get_all()
    by_status = {"todo": 0, "in_progress": 0, "done": 0}
    for task in tasks:
        key = task.status.value if hasattr(task.status, "value") else str(task.status)
        if key in by_status:
            by_status[key] += 1
    return {"total_tasks": len(tasks), "by_status": by_status}


@router.delete("/tasks/{task_id}", status_code=204)
def admin_delete_task(
    task_id: int,
    current_user: User = Depends(require_admin),
    store: TaskStorage = Depends(get_storage),
):
    task = store.get_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    store.delete(task_id)
