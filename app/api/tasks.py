from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin
from app.database.session import get_db
from app.models import User
from app.schemas.task import TaskCreate, TaskOut, TaskStatusUpdate, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.post("", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
def create_task(
    data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.create_task(db, data, current_user)


@router.get("", response_model=list[TaskOut])
def list_tasks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.list_tasks(db, current_user)


@router.get("/{task_id}", response_model=TaskOut)
def view_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.get_task(db, task_id, current_user)


@router.put("/{task_id}", response_model=TaskOut)
def update_task(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return task_service.update_task(db, task_id, data, current_user)


@router.patch("/{task_id}/status", response_model=TaskOut)
def update_task_status(
    task_id: int,
    data: TaskStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return task_service.update_task_status(db, task_id, data)