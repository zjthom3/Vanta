from __future__ import annotations

import uuid
from datetime import datetime, timezone
from http import HTTPStatus

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.deps.auth import get_current_user
from apps.api.db.session import get_session
from apps.api.models import Application, ApplicationNote, AuditLog, JobPosting, User
from apps.api.models.enums import StageEnum
from apps.api.schemas.application import (
    ApplicationCreateRequest,
    ApplicationNoteResponse,
    ApplicationResponse,
    ApplicationUpdateRequest,
    TaskSummary,
)
from apps.api.services import storage, task_rules

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
        notes_count=len(application.notes),
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
        previous_stage = application.stage
        application.stage = payload.stage
        if payload.stage == StageEnum.APPLIED and application.applied_at is None:
            application.applied_at = datetime.now(timezone.utc)
        task_rules.handle_stage_change(session, application, payload.stage)
        log = AuditLog(
            actor_type="user",
            actor_id=user.id,
            action="application.stage_changed",
            entity="application",
            entity_id=application.id,
            diff={"from": previous_stage.value, "to": payload.stage.value},
        )
        session.add(log)

    session.add(application)
    session.commit()
    session.refresh(application)
    return _serialize_application(application)


def _serialize_note(note: ApplicationNote) -> ApplicationNoteResponse:
    return ApplicationNoteResponse(
        id=str(note.id),
        body=note.body,
        attachment_url=note.attachment_url,
        attachment_name=note.attachment_name,
        attachment_content_type=note.attachment_content_type,
        created_at=note.created_at.isoformat(),
    )


@router.get("/{application_id}/notes", response_model=list[ApplicationNoteResponse])
def list_application_notes(
    application_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[ApplicationNoteResponse]:
    application = session.get(Application, application_id)
    if application is None or application.user_id != user.id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Application not found")

    notes_stmt = (
        select(ApplicationNote)
        .where(ApplicationNote.application_id == application.id)
        .order_by(ApplicationNote.created_at.desc())
    )
    notes = session.scalars(notes_stmt).all()
    return [_serialize_note(note) for note in notes]


@router.post("/{application_id}/notes", response_model=ApplicationNoteResponse, status_code=HTTPStatus.CREATED)
async def create_application_note(
    application_id: uuid.UUID,
    body: str | None = Form(default=None),
    attachment: UploadFile | None = File(default=None),
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ApplicationNoteResponse:
    application = session.get(Application, application_id)
    if application is None or application.user_id != user.id:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Application not found")

    if (body is None or not body.strip()) and attachment is None:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Provide note text or an attachment")

    attachment_url = None
    attachment_name = None
    attachment_content_type = None
    if attachment is not None:
        filename = attachment.filename or "attachment"
        key = f"applications/{application_id}/notes/{uuid.uuid4()}-{filename}"
        attachment.file.seek(0)
        attachment_url = storage.upload_stream(key, attachment.file, attachment.content_type)
        attachment_name = filename
        attachment_content_type = attachment.content_type

    note = ApplicationNote(
        application_id=application.id,
        user_id=user.id,
        body=body.strip() if body and body.strip() else None,
        attachment_url=attachment_url,
        attachment_name=attachment_name,
        attachment_content_type=attachment_content_type,
    )
    session.add(note)
    session.commit()
    session.refresh(note)
    return _serialize_note(note)
