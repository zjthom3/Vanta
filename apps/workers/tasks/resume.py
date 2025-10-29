from __future__ import annotations

import uuid

from loguru import logger

from apps.api.db.session import SessionLocal
from apps.api.models import ResumeVersion, User
from apps.api.services import resume_parser, storage
from apps.workers.app import celery_app


def _resolve_storage_key(doc_url: str | None) -> str | None:
    if not doc_url:
        return None
    return storage.key_from_url(doc_url)


def process_resume(resume_id: str) -> None:
    parsed_resume_id: uuid.UUID
    try:
        parsed_resume_id = uuid.UUID(resume_id)
    except ValueError:
        logger.warning("Invalid resume id", resume_id=resume_id)
        return

    with SessionLocal() as session:
        resume: ResumeVersion | None = session.get(ResumeVersion, parsed_resume_id)
        if resume is None:
            logger.warning("Resume not found", resume_id=resume_id)
            return

        storage_key = _resolve_storage_key(resume.doc_url)
        if storage_key is None:
            logger.warning("Resume missing storage key", resume_id=resume_id, doc_url=resume.doc_url)
            return

        try:
            raw_bytes = storage.download_bytes(storage_key)
        except Exception as exc:  # pragma: no cover - external service
            logger.exception("Failed to download resume from storage", resume_id=resume_id, error=str(exc))
            return

        parsed = resume_parser.parse_resume_bytes(
            raw_bytes, content_type=resume.content_type, filename=resume.original_filename
        )

        resume.sections_json = parsed.to_dict()
        resume.keywords = parsed.skills
        resume.ats_score = resume_parser.estimate_ats_score(parsed)
        resume.base_flag = True

        # Mark the owning user as having at least one parsed resume for downstream onboarding steps.
        if resume.user_id is not None:
            user = session.get(User, resume.user_id)
            if user and user.profile:
                # Populate skills from resume if profile is currently empty.
                if not user.profile.skills and parsed.skills:
                    user.profile.skills = parsed.skills

        session.commit()
        logger.info("Parsed resume successfully", resume_id=resume_id)


@celery_app.task(name="resume.parse")
def parse_resume(resume_id: str) -> None:
    process_resume(resume_id)


@celery_app.task(name="resume.generate")
def generate_resume(resume_id: str, job_posting_id: str) -> None:
    logger.info(
        "Generating tailored resume", resume_id=resume_id, job_posting_id=job_posting_id
    )
