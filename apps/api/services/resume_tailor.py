from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from apps.api.models import JobPosting, Notification, ResumeVersion


def _build_sections(base: ResumeVersion, job: JobPosting | None) -> dict[str, object]:
    sections = dict(base.sections_json or {})
    summary = sections.get("summary") or base.original_filename or "Resume"
    job_phrase = job.title if job else "target roles"
    sections["summary"] = f"Tailored for {job_phrase}: {summary}" if summary else f"Tailored for {job_phrase}"
    highlights = sections.get("highlights")
    if isinstance(highlights, list) and job and job.normalized_tags:
        sections["highlights"] = list(dict.fromkeys(highlights + job.normalized_tags))
    return sections


def tailor_resume(session: Session, base: ResumeVersion, job: JobPosting | None) -> ResumeVersion:
    resume = ResumeVersion(
        user_id=base.user_id,
        job_posting_id=job.id if job else None,
        base_flag=False,
        original_filename=f"tailored-{uuid.uuid4().hex[:8]}.{(base.original_filename or 'pdf').split('.')[-1]}",
        content_type=base.content_type,
        sections_json=_build_sections(base, job),
        keywords=list(dict.fromkeys((base.keywords or []) + (job.normalized_tags if job and job.normalized_tags else []))),
        ats_score=min((base.ats_score or 60) + 5, 100),
        diff_from_base={"notes": f"Tailored for {job.title if job else 'generic use'}"},
    )
    session.add(resume)
    session.flush()
    notification = Notification(
        user_id=base.user_id,
        kind="resume_tailored",
        payload={
            "resume_id": str(resume.id),
            "job_posting_id": str(job.id) if job else None,
            "created_at": datetime.now(UTC).isoformat(),
        },
    )
    session.add(notification)
    session.commit()
    session.refresh(resume)
    return resume


def optimize_resume(session: Session, resume: ResumeVersion, emphasis: str | None = None) -> ResumeVersion:
    current = resume.ats_score or 60
    resume.ats_score = min(current + 10, 100)
    diff = dict(resume.diff_from_base or {})
    diff["optimization"] = emphasis or "General ATS improvements"
    resume.diff_from_base = diff
    notification = Notification(
        user_id=resume.user_id,
        kind="resume_optimized",
        payload={
            "resume_id": str(resume.id),
            "ats_score": resume.ats_score,
        },
    )
    session.add(resume)
    session.add(notification)
    session.commit()
    session.refresh(resume)
    return resume
