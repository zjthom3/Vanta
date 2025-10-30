from __future__ import annotations

from sqlalchemy.orm import Session

from apps.api.models import JobPosting, PostingEnrichment, Profile, User
from apps.api.models.enums import PlanTierEnum, ProviderEnum, StatusEnum
from apps.api.services import matching


def test_compute_fit_score_uses_skill_overlap():
    user = User(email="match@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    profile = Profile(user=user, skills=["Python", "Leadership"], headline="Engineering Manager", locations=["Remote"])
    posting = JobPosting(
        source=ProviderEnum.GREENHOUSE,
        source_id="xyz",
        title="Senior Engineering Manager",
        url="https://example.com/roles/1",
        normalized_tags=["python", "management"],
        remote_flag=True,
        jd_clean="Lead Python engineering teams to deliver scalable services.",
    )

    result = matching.compute_fit_score(profile, posting)
    assert result.score > 50
    assert result.factors["skill_overlap"] > 0
    assert any("Shares skills" in reason for reason in result.reasons)


def test_update_posting_enrichment_persists(db_session: Session):
    user = User(email="persist@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    profile = Profile(user=user, skills=["Product"], headline="Product Manager", locations=["Remote"])
    posting = JobPosting(
        source=ProviderEnum.GREENHOUSE,
        source_id="pm-1",
        title="Product Manager",
        url="https://example.com/pm-1",
        remote_flag=True,
        normalized_tags=["product"],
    )
    db_session.add_all([user, profile, posting])
    db_session.commit()

    enrichment = matching.update_posting_enrichment(db_session, str(user.id), posting)
    assert enrichment.fit_score > 0
    stored = db_session.query(PostingEnrichment).filter_by(user_id=user.id, job_posting_id=posting.id).one()
    assert stored.fit_factors["skill_overlap"] == 1.0
    assert stored.rationale is not None
