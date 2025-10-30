from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.deps.auth import get_current_user
from apps.api.db.session import get_session
from apps.api.models import Application, Task, User
from apps.api.schemas.task import TaskActionRequest, TaskResponse

router = APIRouter(prefix="/tasks", tags=["tasks"])


def _serialize_task(task: Task) -> TaskResponse:
    application = task.application
    return TaskResponse(
        id=str(task.id),
        title=task.title,
        type=task.nudge_type,
        priority=task.priority,
        due_at=task.due_at,
        completed_at=task.completed_at,
        application_id=str(application.id) if application else None,
        application_title=application.job_posting.title if application and application.job_posting else None,
    )


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[TaskResponse]:
    stmt = (
        select(Task)
        .where(Task.user_id == user.id)
        .order_by(Task.completed_at.is_(None).desc(), Task.due_at.asc().nullslast(), Task.created_at.desc())
    )
    tasks = session.scalars(stmt).all()
    return [_serialize_task(task) for task in tasks]


@router.patch("/{task_id}", response_model=TaskResponse)
def act_on_task(
    task_id: uuid.UUID,
    payload: TaskActionRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> TaskResponse:
    task = session.get(Task, task_id)
    if task is None or task.user_id != user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    if payload.action == "complete":
        task.completed_at = datetime.now(timezone.utc)
    elif payload.action == "undo":
        task.completed_at = None
    elif payload.action == "defer":
        base = task.due_at or datetime.now(timezone.utc)
        task.due_at = base + timedelta(days=2)
    else:  # pragma: no cover - defensive
        raise HTTPException(status_code=400, detail="Unknown action")

    session.add(task)
    session.commit()
    session.refresh(task)
    return _serialize_task(task)
