from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_admin
from app.database.session import get_db
from app.models import User
from app.schemas.task import TaskCreate, TaskOut, TaskStatusUpdate, TaskUpdate
from app.services import task_service
from app.ai import service as ai_service
from app.schemas.ai import GenerateDescriptionRequest, GenerateDescriptionResponse, SummarizeResponse

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

@router.post("/generate-description", response_model=GenerateDescriptionResponse)
def generate_description(
    data: GenerateDescriptionRequest,
    current_user: User = Depends(get_current_user),
):
    description = ai_service.generate_description(data.title)
    return GenerateDescriptionResponse(title=data.title, description=description)


@router.post("/{task_id}/summarize", response_model=SummarizeResponse)
def summarize_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = task_service.get_task(db, task_id, current_user)  # also checks ownership
    summary = ai_service.summarize_task(task.title, task.description)
    return SummarizeResponse(task_id=task.id, summary=summary)