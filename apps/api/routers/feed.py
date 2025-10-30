from __future__ import annotations

import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.deps.auth import get_current_user
from apps.api.db.session import get_session
from apps.api.models import HiddenPosting, JobPosting, User
from apps.api.services import matching

router = APIRouter(prefix="/feed", tags=["feed"])


def _hidden_ids(session: Session, user_id: uuid.UUID) -> set[uuid.UUID]:
    stmt = select(HiddenPosting.job_posting_id).where(HiddenPosting.user_id == user_id)
    return {row[0] for row in session.execute(stmt)}


@router.get("/jobs")
def job_feed(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    location: str | None = Query(None),
    remote_only: bool | None = Query(None),
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> dict[str, object]:
    stmt = select(JobPosting).order_by(JobPosting.created_at.desc())
    if location:
        stmt = stmt.where(JobPosting.location.ilike(f"%{location}%"))
    if remote_only:
        stmt = stmt.where(JobPosting.remote_flag.is_(True))

    postings = session.scalars(stmt).all()
    hidden = _hidden_ids(session, user.id)
    visible = [posting for posting in postings if posting.id not in hidden]

    start = (page - 1) * limit
    end = start + limit
    items = visible[start:end]

    serialized = []
    for posting in items:
        enrichment = matching.update_posting_enrichment(session, str(user.id), posting)
        serialized.append(
            {
                "id": str(posting.id),
                "title": posting.title,
                "company": posting.company.name if posting.company else None,
                "location": posting.location,
                "remote": posting.remote_flag,
                "url": posting.url,
                "tags": posting.normalized_tags or [],
                "fit_score": enrichment.fit_score if enrichment else None,
                "fit_factors": enrichment.fit_factors if enrichment else {},
                "why_fit": enrichment.rationale,
            }
        )

    return {
        "items": serialized,
        "page": page,
        "limit": limit,
        "total": len(visible),
    }


@router.post("/jobs/{posting_id}/hide")
def hide_job(
    posting_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> dict[str, str]:
    posting = session.get(JobPosting, posting_id)
    if posting is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Job posting not found")

    stmt = select(HiddenPosting).where(
        HiddenPosting.user_id == user.id,
        HiddenPosting.job_posting_id == posting_id,
    )
    hidden = session.scalars(stmt).first()
    if hidden is None:
        hidden = HiddenPosting(user_id=user.id, job_posting_id=posting_id)
        session.add(hidden)
        session.flush()
    session.commit()
    return {"status": "hidden"}
