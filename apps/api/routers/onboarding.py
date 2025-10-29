from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import EmailStr
from pydantic import ValidationError
from sqlalchemy.orm import Session

from apps.api.db.session import get_session
from apps.api.schemas.onboarding import OnboardingPayload, OnboardingResponse, ResumeMetadata
from apps.api.services.onboarding import DEFAULT_CRON_SCHEDULE, DEFAULT_TIMEZONE, process_onboarding

router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/profile", response_model=OnboardingResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_profile(
    full_name: Annotated[str, Form(...)],
    email: Annotated[EmailStr, Form(...)],
    primary_role: Annotated[str, Form(...)],
    target_locations: Annotated[list[str], Form(...)],
    years_experience: Annotated[int, Form(...)],
    schedule_cron: Annotated[str, Form(...)] = DEFAULT_CRON_SCHEDULE,
    timezone: Annotated[str, Form(...)] = DEFAULT_TIMEZONE,
    resume: UploadFile | None = File(None),
    session: Session = Depends(get_session),
) -> OnboardingResponse:
    metadata = None
    if resume is not None:
        resume.file.seek(0, 2)
        size_bytes = resume.file.tell()
        resume.file.seek(0)
        metadata = ResumeMetadata(
            filename=resume.filename or "resume",
            content_type=resume.content_type or "application/octet-stream",
            size_bytes=size_bytes,
        )

    try:
        payload = OnboardingPayload(
            full_name=full_name,
            email=email,
            primary_role=primary_role,
            target_locations=target_locations,
            years_experience=years_experience,
            schedule_cron=schedule_cron,
            timezone=timezone,
            resume=metadata,
        )
    except ValidationError as exc:  # pragma: no cover - handled in tests
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.errors()) from exc

    response, _, _ = process_onboarding(session, payload, resume)
    return response
