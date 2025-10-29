from __future__ import annotations

import uuid
from typing import Tuple

from fastapi import UploadFile

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.models import Profile, ResumeVersion, SearchPref, User
from apps.api.models.enums import PlanTierEnum, StatusEnum
from apps.api.schemas.onboarding import OnboardingPayload, OnboardingResponse
from apps.api.services import storage
from apps.workers.tasks import resume as resume_tasks

DEFAULT_SEARCH_PREF_NAME = "Daily Digest"
DEFAULT_CRON_SCHEDULE = "0 5 * * *"
DEFAULT_TIMEZONE = "UTC"


def enqueue_resume_parse(resume_id: uuid.UUID) -> None:
    """Best-effort enqueue of resume parsing task."""
    try:
        resume_tasks.parse_resume.delay(str(resume_id))
    except Exception as exc:  # pragma: no cover - network dependency
        logger.warning("Failed to enqueue resume parse", resume_id=str(resume_id), error=str(exc))


def ensure_user(session: Session, payload: OnboardingPayload) -> User:
    stmt = select(User).where(User.email == payload.email)
    user = session.scalar(stmt)
    if user:
        return user

    user = User(
        email=payload.email,
        plan_tier=PlanTierEnum.FREE,
        status=StatusEnum.ACTIVE,
    )
    session.add(user)
    session.flush()
    logger.debug("Created user", user_id=str(user.id))
    return user


def upsert_profile(session: Session, user: User, payload: OnboardingPayload) -> Profile:
    profile = user.profile
    remote_only = any(location.lower() == "remote" for location in payload.target_locations)

    if profile is None:
        profile = Profile(user_id=user.id)
        session.add(profile)

    profile.headline = payload.primary_role
    profile.summary = f"{payload.full_name} — {payload.primary_role}"
    profile.locations = payload.target_locations
    profile.remote_only = remote_only
    profile.years_experience = payload.years_experience
    profile.job_preferences = {
        "primary_role": payload.primary_role,
        "target_locations": payload.target_locations,
    }

    session.flush()
    logger.debug("Upserted profile", user_id=str(user.id), profile_id=str(profile.id))
    return profile


def ensure_search_pref(session: Session, user: User, payload: OnboardingPayload) -> SearchPref:
    stmt = (
        select(SearchPref)
        .where(SearchPref.user_id == user.id)
        .where(SearchPref.name == DEFAULT_SEARCH_PREF_NAME)
    )
    search_pref = session.scalar(stmt)
    schedule = payload.schedule_cron or DEFAULT_CRON_SCHEDULE
    timezone = payload.timezone or DEFAULT_TIMEZONE

    if search_pref:
        search_pref.filters = {
            "primary_role": payload.primary_role,
            "locations": payload.target_locations,
            "remote_only": any(loc.lower() == "remote" for loc in payload.target_locations),
        }
        search_pref.schedule_cron = schedule
        search_pref.timezone = timezone
        session.flush()
        return search_pref

    filters = {
        "primary_role": payload.primary_role,
        "locations": payload.target_locations,
        "remote_only": any(loc.lower() == "remote" for loc in payload.target_locations),
    }

    search_pref = SearchPref(
        user_id=user.id,
        name=DEFAULT_SEARCH_PREF_NAME,
        filters=filters,
        schedule_cron=schedule,
        timezone=timezone,
        last_run_at=None,
    )
    session.add(search_pref)
    session.flush()
    logger.debug("Created search pref", user_id=str(user.id), search_pref_id=str(search_pref.id))
    return search_pref


def persist_resume_upload(session: Session, user: User, file: UploadFile) -> ResumeVersion:
    resume_version = ResumeVersion(user_id=user.id, base_flag=True, doc_url=None)
    session.add(resume_version)
    session.flush()

    filename = file.filename or "resume"
    key = f"resumes/{resume_version.id}/{filename}"
    file.file.seek(0)
    content_type = file.content_type or "application/octet-stream"
    doc_url = storage.upload_stream(key, file.file, content_type)
    resume_version.doc_url = doc_url
    resume_version.original_filename = filename
    resume_version.content_type = content_type
    session.flush()

    logger.debug("Uploaded resume", resume_id=str(resume_version.id), key=key)
    return resume_version


def process_onboarding(
    session: Session, payload: OnboardingPayload, resume_file: UploadFile | None = None
) -> Tuple[OnboardingResponse, uuid.UUID | None, str | None]:
    user = ensure_user(session, payload)
    upsert_profile(session, user, payload)
    ensure_search_pref(session, user, payload)

    resume_id: uuid.UUID | None = None
    resume_url: str | None = None
    if resume_file is not None:
        resume = persist_resume_upload(session, user, resume_file)
        resume_id = resume.id
        resume_url = resume.doc_url
        enqueue_resume_parse(resume_id)
        # Perform an inline parse so the user sees extracted data immediately.
        try:
            resume_tasks.process_resume(str(resume_id))
        except Exception as exc:  # pragma: no cover - safety fallback
            logger.warning("Inline resume parse failed", resume_id=str(resume_id), error=str(exc))

    session.commit()

    response = OnboardingResponse(
        next_step="search_preferences",
        message=(
            "Profile received. We'll parse the resume, confirm your skills, and prompt you to configure daily searches."
        ),
        resume_version_id=resume_id,
        resume_doc_url=resume_url,
    )
    return response, resume_id, resume_url
