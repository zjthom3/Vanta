from __future__ import annotations

import math
import re
import uuid
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.models import JobPosting, PostingEnrichment, Profile

STOPWORDS = {
    "a",
    "an",
    "and",
    "for",
    "in",
    "of",
    "on",
    "the",
    "to",
    "with",
}


@dataclass
class FitComputation:
    score: int
    factors: dict[str, float]
    reasons: list[str]


def _normalize_tokens(values: Iterable[str] | None) -> set[str]:
    if not values:
        return set()
    return {value.strip().lower() for value in values if value and value.strip()}


def _tokenize(text: str | None) -> list[str]:
    if not text:
        return []
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return [token for token in tokens if token and token not in STOPWORDS]


def _vectorize(tokens: Iterable[str]) -> Counter[str]:
    counter: Counter[str] = Counter()
    for token in tokens:
        if token:
            counter[token] += 1
    return counter


def _cosine_similarity(vec_a: Counter[str], vec_b: Counter[str]) -> float:
    if not vec_a or not vec_b:
        return 0.0
    dot = sum(vec_a[token] * vec_b[token] for token in vec_a if token in vec_b)
    if dot == 0:
        return 0.0
    norm_a = math.sqrt(sum(value * value for value in vec_a.values()))
    norm_b = math.sqrt(sum(value * value for value in vec_b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def _build_profile_vector(profile: Profile | None) -> Counter[str]:
    if profile is None:
        return Counter()
    tokens: list[str] = []
    if profile.headline:
        tokens.extend(_tokenize(profile.headline))
    if profile.summary:
        tokens.extend(_tokenize(profile.summary))
    if profile.skills:
        tokens.extend(_tokenize(" ".join(profile.skills)))
    if profile.locations:
        tokens.extend(_tokenize(" ".join(profile.locations)))
    return _vectorize(tokens)


def _build_posting_vector(posting: JobPosting) -> Counter[str]:
    tokens: list[str] = []
    tokens.extend(_tokenize(posting.title))
    if posting.company and posting.company.name:
        tokens.extend(_tokenize(posting.company.name))
    if posting.normalized_tags:
        tokens.extend(_tokenize(" ".join(posting.normalized_tags)))
    if posting.jd_clean:
        tokens.extend(_tokenize(posting.jd_clean))
    elif posting.jd_raw:
        tokens.extend(_tokenize(posting.jd_raw))
    if posting.location:
        tokens.extend(_tokenize(posting.location))
    return _vectorize(tokens)


def _skill_score(profile: Profile | None, posting: JobPosting) -> tuple[int, dict[str, float], list[str]]:
    profile_skills = _normalize_tokens(profile.skills if profile else None)
    posting_tags = _normalize_tokens(posting.normalized_tags)

    if not profile_skills or not posting_tags:
        return 20, {"skill_overlap": 0.0}, []

    overlap = profile_skills & posting_tags
    ratio = len(overlap) / len(profile_skills)
    reason = []
    if overlap:
        top_overlap = ", ".join(sorted(overlap)[:5])
        reason.append(f"Shares skills: {top_overlap}")
    return int(20 + ratio * 60), {"skill_overlap": ratio}, reason


def _embedding_score(profile: Profile | None, posting: JobPosting) -> tuple[int, dict[str, float], list[str]]:
    profile_vec = _build_profile_vector(profile)
    posting_vec = _build_posting_vector(posting)
    similarity = _cosine_similarity(profile_vec, posting_vec)
    score = int(similarity * 30)
    reason = []
    if similarity >= 0.2:
        reason.append("Title and summary resemble the job description")
    return score, {"semantic_similarity": similarity}, reason


def _remote_score(profile: Profile | None, posting: JobPosting) -> tuple[int, dict[str, float], list[str]]:
    if not profile:
        return 10, {"remote_match": 0.0}, []

    prefers_remote = any(location.lower() == "remote" for location in profile.locations or [])
    reason = []
    if prefers_remote and posting.remote_flag:
        reason.append("Remote role matches preference")
        return 15, {"remote_match": 1.0}, reason
    if not prefers_remote:
        return 15, {"remote_match": 0.5}, reason
    return 5, {"remote_match": 0.0}, reason


def _location_score(profile: Profile | None, posting: JobPosting) -> tuple[int, dict[str, float], list[str]]:
    if not profile or not profile.locations:
        return 10, {"location_match": 0.0}, []

    profile_locations = _normalize_tokens(profile.locations)
    posting_location_tokens = _normalize_tokens([posting.location] if posting.location else None)

    overlap = profile_locations & posting_location_tokens
    reason = []
    if overlap:
        reason.append(f"Location match: {', '.join(sorted(overlap))}")
        return 15, {"location_match": 1.0}, reason
    return 8, {"location_match": 0.0}, reason


def _title_similarity(profile: Profile | None, posting: JobPosting) -> tuple[int, dict[str, float], list[str]]:
    if not profile or not profile.headline:
        return 10, {"title_similarity": 0.0}, []
    profile_title = profile.headline.lower()
    posting_title = posting.title.lower()
    profile_tokens = profile_title.split()
    posting_tokens = posting_title.split()
    overlap = len(set(profile_tokens) & set(posting_tokens))
    ratio = overlap / max(len(posting_tokens), 1)
    reason = []
    if ratio >= 0.3:
        reason.append("Similar title to your profile headline")
    return int(10 + ratio * 20), {"title_similarity": ratio}, reason


def _clamp(score: int) -> int:
    return max(0, min(100, score))


def compute_fit_score(profile: Profile | None, posting: JobPosting) -> FitComputation:
    skill_score, skill_factors, skill_reasons = _skill_score(profile, posting)
    embedding_score, embedding_factors, embedding_reasons = _embedding_score(profile, posting)
    remote_score, remote_factors, remote_reasons = _remote_score(profile, posting)
    location_score, location_factors, location_reasons = _location_score(profile, posting)
    title_score, title_factors, title_reasons = _title_similarity(profile, posting)

    total = skill_score + embedding_score + remote_score + location_score + title_score
    factors = {
        **skill_factors,
        **embedding_factors,
        **remote_factors,
        **location_factors,
        **title_factors,
    }
    reasons = skill_reasons + embedding_reasons + remote_reasons + location_reasons + title_reasons
    return FitComputation(score=_clamp(total), factors=factors, reasons=reasons)


def update_posting_enrichment(session: Session, user_id: str, posting: JobPosting) -> PostingEnrichment:
    user_uuid = uuid.UUID(str(user_id))
    profile = session.execute(select(Profile).where(Profile.user_id == user_uuid)).scalar_one_or_none()

    result = compute_fit_score(profile, posting)

    stmt = select(PostingEnrichment).where(
        PostingEnrichment.user_id == user_uuid,
        PostingEnrichment.job_posting_id == posting.id,
    )
    enrichment = session.scalars(stmt).first()
    rationale = " • ".join(result.reasons[:3]) if result.reasons else None
    if enrichment is None:
        enrichment = PostingEnrichment(
            user_id=user_uuid,
            job_posting_id=posting.id,
            fit_score=result.score,
            fit_factors=result.factors,
            rationale=rationale,
        )
        session.add(enrichment)
    else:
        enrichment.fit_score = result.score
        enrichment.fit_factors = result.factors
        enrichment.rationale = rationale
    session.commit()
    return enrichment
