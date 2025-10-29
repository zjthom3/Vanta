from __future__ import annotations

import uuid
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.models import JobPosting, PostingEnrichment, Profile


def _normalize_tokens(values: Iterable[str] | None) -> set[str]:
    if not values:
        return set()
    return {value.strip().lower() for value in values if value and value.strip()}


def _skill_score(profile: Profile | None, posting: JobPosting) -> tuple[int, dict[str, float]]:
    profile_skills = _normalize_tokens(profile.skills if profile else None)
    posting_tags = _normalize_tokens(posting.normalized_tags)

    if not profile_skills or not posting_tags:
        return 20, {"skill_overlap": 0.0}

    overlap = profile_skills & posting_tags
    ratio = len(overlap) / len(profile_skills)
    return int(20 + ratio * 60), {"skill_overlap": ratio}


def _remote_score(profile: Profile | None, posting: JobPosting) -> tuple[int, dict[str, float]]:
    if not profile:
        return 10, {"remote_match": 0.0}

    prefers_remote = any(location.lower() == "remote" for location in profile.locations or [])
    if prefers_remote and posting.remote_flag:
        return 15, {"remote_match": 1.0}
    if not prefers_remote:
        return 15, {"remote_match": 0.5}
    return 5, {"remote_match": 0.0}


def _title_similarity(profile: Profile | None, posting: JobPosting) -> tuple[int, dict[str, float]]:
    if not profile or not profile.headline:
        return 10, {"title_similarity": 0.0}
    profile_title = profile.headline.lower()
    posting_title = posting.title.lower()
    overlap = len(set(profile_title.split()) & set(posting_title.split()))
    ratio = overlap / max(len(posting_title.split()), 1)
    return int(10 + ratio * 20), {"title_similarity": ratio}


def _clamp(score: int) -> int:
    return max(0, min(100, score))


def compute_fit_score(profile: Profile | None, posting: JobPosting) -> tuple[int, dict[str, float]]:
    skill_score, skill_factors = _skill_score(profile, posting)
    remote_score, remote_factors = _remote_score(profile, posting)
    title_score, title_factors = _title_similarity(profile, posting)

    total = skill_score + remote_score + title_score
    return _clamp(total), {**skill_factors, **remote_factors, **title_factors}


def update_posting_enrichment(session: Session, user_id: str, posting: JobPosting) -> PostingEnrichment:
    user_uuid = uuid.UUID(str(user_id))
    profile = session.execute(select(Profile).where(Profile.user_id == user_uuid)).scalar_one_or_none()

    fit_score, factors = compute_fit_score(profile, posting)

    stmt = select(PostingEnrichment).where(
        PostingEnrichment.user_id == user_uuid,
        PostingEnrichment.job_posting_id == posting.id,
    )
    enrichment = session.scalars(stmt).first()
    if enrichment is None:
        enrichment = PostingEnrichment(
            user_id=user_uuid,
            job_posting_id=posting.id,
            fit_score=fit_score,
            fit_factors=factors,
        )
        session.add(enrichment)
    else:
        enrichment.fit_score = fit_score
        enrichment.fit_factors = factors
    session.commit()
    return enrichment
