from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.deps.auth import get_current_user
from apps.api.db.session import get_session
from apps.api.models import Application, JobPosting, User
from apps.api.models.enums import StageEnum
from apps.api.schemas.application import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationUpdateRequest,
    TaskSummary,
)
from apps.api.services import task_rules

router = APIRouter(prefix="/applications", tags=["applications"])


def _serialize_application(application: Application) -> ApplicationResponse:
    tasks = []
    for task in application.tasks:
        tasks.append(
            TaskSummary(
                id=str(task.id),
                title=task.title,
                type=task.nudge_type.value if task.nudge_type else None,
                due_at=task.due_at.isoformat() if task.due_at else None,
                completed_at=task.completed_at.isoformat() if task.completed_at else None,
            )
        )
    job = application.job_posting
    return ApplicationResponse(
        id=str(application.id),
        title=job.title if job else application.job_posting_id or "",
        company=job.company.name if job and job.company else None,
        stage=application.stage,
        url=job.url if job else None,
        tasks=tasks,
        created_at=application.created_at.isoformat(),
    )


@router.get("/", response_model=list[ApplicationResponse])
def list_applications(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[ApplicationResponse]:
    stmt = select(Application).where(Application.user_id == user.id).order_by(Application.created_at.desc())
    applications = session.scalars(stmt).all()
    return [_serialize_application(app) for app in applications]


@router.post("/", response_model=ApplicationResponse, status_code=HTTPStatus.CREATED)
def create_application(
    payload: ApplicationCreateRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ApplicationResponse:
    job_posting = None
    if payload.job_posting_id:
        job_uuid = uuid.UUID(payload.job_posting_id)
        job_posting = session.get(JobPosting, job_uuid)
        if job_posting is None:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Job posting not found")
        duplicate_stmt = select(Application).where(Application.user_id == user.id, Application.job_posting_id == job_uuid)
        if session.scalars(duplicate_stmt).first():
            raise HTTPException(status_code=HTTPStatus.CONFLICT, detail="Application already exists for this posting")

    application = Application(user_id=user.id, job_posting=job_posting)
    if not job_posting:
        application.job_posting_id = payload.job_posting_id
    session.add(application)
    session.flush()
    session.refresh(application)
    return _serialize_application(application)


@router.patch("/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: uuid.UUID,
    payload: ApplicationUpdateRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ApplicationResponse:
    application = session.get(Application, application_id)
    if application is None or application.user_id != user.id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Application not found")

    if application.stage != payload.stage:
        application.stage = payload.stage
        task_rules.handle_stage_change(session, application, payload.stage)

    session.add(application)
    session.commit()
    session.refresh(application)
    return _serialize_application(application)
