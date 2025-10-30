from __future__ import annotations

from sqlalchemy.orm import Session

from apps.api.models import JobPosting, Notification, PostingEnrichment, User
from apps.api.models.enums import PlanTierEnum, ProviderEnum, StatusEnum
from apps.api.services import digest


def test_build_daily_digest_persists_notification(db_session: Session):
    user = User(email="digest@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    posting = JobPosting(
        source=ProviderEnum.GREENHOUSE,
        source_id="digest-1",
        title="Data Scientist",
        url="https://example.com/digest",
    )
    db_session.add_all([user, posting])
    db_session.flush()
    enrichment = PostingEnrichment(
        user_id=user.id,
        job_posting_id=posting.id,
        fit_score=88,
        fit_factors={"skill_overlap": 0.8},
        rationale="Matches core Python experience",
    )
    db_session.add(enrichment)
    db_session.commit()

    notification = digest.build_daily_digest(db_session, str(user.id), limit=5)
    assert notification.kind == "daily_digest"
    assert len(notification.payload["items"]) == 1
    item = notification.payload["items"][0]
    assert item["why_fit"] == "Matches core Python experience"
    stored = db_session.query(Notification).filter_by(user_id=user.id, kind="daily_digest").count()
    assert stored == 1
