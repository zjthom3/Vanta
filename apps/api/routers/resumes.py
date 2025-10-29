from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.api.deps.auth import get_current_user
from apps.api.db.session import get_session
from apps.api.models import JobPosting, Notification, ResumeVersion, User
from apps.api.schemas.resume import OptimizeResumeRequest, ResumeDetailResponse, ResumeSummary, TailorResumeRequest
from apps.api.services import resume_tailor

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _load_resume(session: Session, resume_id: uuid.UUID, user: User) -> ResumeVersion:
    resume = session.get(ResumeVersion, resume_id)
    if resume is None or resume.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume


@router.get("/", response_model=list[ResumeSummary])
def list_resumes(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[ResumeSummary]:
    stmt = (
        session.query(ResumeVersion)
        .filter(ResumeVersion.user_id == user.id)
        .order_by(ResumeVersion.created_at.desc())
    )
    items = stmt.all()
    return [
        ResumeSummary(
            id=str(resume.id),
            base=resume.base_flag,
            original_filename=resume.original_filename,
            created_at=resume.created_at,
            ats_score=resume.ats_score,
        )
        for resume in items
    ]


@router.get("/{resume_id}", response_model=ResumeDetailResponse)
def get_resume_details(
    resume_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ResumeDetailResponse:
    resume = _load_resume(session, resume_id, user)
    return ResumeDetailResponse(
        id=str(resume.id),
        original_filename=resume.original_filename,
        content_type=resume.content_type,
        sections=resume.sections_json,
        keywords=resume.keywords,
        ats_score=resume.ats_score,
        created_at=resume.created_at,
    )


@router.post("/{resume_id}/tailor", response_model=ResumeDetailResponse, status_code=status.HTTP_201_CREATED)
def tailor_resume(
    resume_id: uuid.UUID,
    payload: TailorResumeRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ResumeDetailResponse:
    base_resume = _load_resume(session, resume_id, user)
    job_posting = None
    if payload.job_posting_id:
        job_posting = session.get(JobPosting, uuid.UUID(payload.job_posting_id))
        if job_posting is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job posting not found")

    tailored_resume = resume_tailor.tailor_resume(session, base_resume, job_posting)
    return ResumeDetailResponse(
        id=str(tailored_resume.id),
        original_filename=tailored_resume.original_filename,
        content_type=tailored_resume.content_type,
        sections=tailored_resume.sections_json,
        keywords=tailored_resume.keywords,
        ats_score=tailored_resume.ats_score,
        created_at=tailored_resume.created_at,
    )


@router.post("/{resume_id}/optimize", response_model=ResumeDetailResponse)
def optimize_resume(
    resume_id: uuid.UUID,
    payload: OptimizeResumeRequest | None = None,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ResumeDetailResponse:
    resume = _load_resume(session, resume_id, user)
    optimized = resume_tailor.optimize_resume(session, resume, emphasis=payload.emphasis if payload else None)
    return ResumeDetailResponse(
        id=str(optimized.id),
        original_filename=optimized.original_filename,
        content_type=optimized.content_type,
        sections=optimized.sections_json,
        keywords=optimized.keywords,
        ats_score=optimized.ats_score,
        created_at=optimized.created_at,
    )
