from __future__ import annotations

from datetime import UTC, datetime
import uuid
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.models import JobPosting, Notification, PostingEnrichment


def build_daily_digest(session: Session, user_id: str, limit: int = 10) -> Notification:
    user_uuid = uuid.UUID(str(user_id))
    stmt = (
        select(PostingEnrichment)
        .where(PostingEnrichment.user_id == user_uuid)
        .order_by(PostingEnrichment.fit_score.desc())
        .limit(limit)
    )
    enrichments = session.scalars(stmt).all()

    items: List[dict[str, object]] = []
    for enrichment in enrichments:
        posting: JobPosting | None = enrichment.job_posting
        if posting is None:
            continue
        items.append(
            {
                "job_id": str(posting.id),
                "title": posting.title,
                "company": posting.company.name if posting.company else None,
                "location": posting.location,
                "remote": posting.remote_flag,
                "url": posting.url,
                "fit_score": enrichment.fit_score,
            }
        )

    payload = {
        "generated_at": datetime.now(UTC).isoformat(),
        "items": items,
    }

    notification = Notification(user_id=user_uuid, kind="daily_digest", payload=payload)
    session.add(notification)
    session.commit()
    return notification
