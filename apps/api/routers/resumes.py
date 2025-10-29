from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from apps.api.deps.auth import get_current_user
from apps.api.db.session import get_session
from apps.api.models import ResumeVersion, User
from apps.api.schemas.resume import ResumeDetailResponse

router = APIRouter(prefix="/resumes", tags=["resumes"])


def _load_resume(session: Session, resume_id: uuid.UUID, user: User) -> ResumeVersion:
    resume = session.get(ResumeVersion, resume_id)
    if resume is None or resume.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return resume


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
