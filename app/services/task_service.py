from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Role, Task, TaskStatus, User
from app.schemas.task import TaskCreate, TaskStatusUpdate, TaskUpdate


def get_task_or_404(db: Session, task_id: int) -> Task:
    task = db.get(Task, task_id)
    if task is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Task not found")
    return task


def check_access(task: Task, user: User) -> None:
    # Admins can access any task. Normal users only their own.
    if user.role != Role.ADMIN.value and task.user_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have access to this task")


def create_task(db: Session, data: TaskCreate, user: User) -> Task:
    task = Task(
        user_id=user.id,
        title=data.title,
        description=data.description,
        status=TaskStatus.PENDING.value,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def list_tasks(db: Session, user: User) -> list[Task]:
    query = select(Task).order_by(Task.id)
    if user.role != Role.ADMIN.value:
        query = query.where(Task.user_id == user.id)
    return list(db.scalars(query).all())


def get_task(db: Session, task_id: int, user: User) -> Task:
    task = get_task_or_404(db, task_id)
    check_access(task, user)
    return task


def update_task(db: Session, task_id: int, data: TaskUpdate, user: User) -> Task:
    task = get_task(db, task_id, user)
    if data.title is not None:
        task.title = data.title
    if data.description is not None:
        task.description = data.description
    db.commit()
    db.refresh(task)
    return task


def update_task_status(db: Session, task_id: int, data: TaskStatusUpdate) -> Task:
    task = get_task_or_404(db, task_id)
    task.status = data.status.value
    db.commit()
    db.refresh(task)
    return task