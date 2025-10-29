from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Iterable, List

from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.models import Company, JobPosting
from apps.api.models.enums import ProviderEnum


@dataclass
class UpsertResult:
    inserted: int
    postings: List[JobPosting]


def _get_or_create_company(session: Session, payload: dict[str, str | None]) -> Company | None:
    name = payload.get("name")
    domain = payload.get("domain")
    if not name and not domain:
        return None

    stmt = select(Company)
    if domain:
        stmt = stmt.where(Company.domain == domain)
    elif name:
        stmt = stmt.where(Company.name == name)

    company = session.scalars(stmt).first()
    if company:
        return company

    company = Company(name=name or domain or "Unknown", domain=domain)
    session.add(company)
    session.flush()
    return company


def upsert_job_postings(session: Session, normalized_postings: Iterable[dict[str, object]]) -> UpsertResult:
    inserted = 0
    affected: list[JobPosting] = []
    for payload in normalized_postings:
        source_value = payload.get("source", "greenhouse")
        try:
            source = ProviderEnum(source_value)
        except ValueError:
            logger.warning("Unsupported provider", provider=source_value)
            continue

        source_id = payload.get("source_id")
        if not source_id:
            logger.warning("Skipping posting with no source_id", payload=payload)
            continue

        stmt = select(JobPosting).where(JobPosting.source == source, JobPosting.source_id == str(source_id))
        posting = session.scalars(stmt).first()
        if posting:
            posting.title = str(payload.get("title") or posting.title)
            posting.url = str(payload.get("url") or posting.url)
            posting.location = payload.get("location_raw") or posting.location
            posting.remote_flag = bool(payload.get("is_remote"))
            metadata = payload.get("metadata_json")
            if isinstance(metadata, dict):
                posting.normalized_tags = metadata.get("departments")
            affected.append(posting)
            continue

        company = None
        company_payload = payload.get("company")
        if isinstance(company_payload, dict):
            company = _get_or_create_company(session, company_payload)

        metadata = payload.get("metadata_json") if isinstance(payload.get("metadata_json"), dict) else {}

        posting = JobPosting(
            source=source,
            source_id=str(source_id),
            url=str(payload.get("url") or ""),
            title=str(payload.get("title") or "Untitled"),
            location=payload.get("location_raw"),
            remote_flag=bool(payload.get("is_remote")),
            salary_min_cents=payload.get("salary_min"),
            salary_max_cents=payload.get("salary_max"),
            currency=str(payload.get("salary_currency") or "USD"),
            normalized_tags=metadata.get("departments") if isinstance(metadata, dict) else None,
            scraped_at=datetime.now(UTC),
        )

        if company:
            posting.company_id = company.id

        session.add(posting)
        inserted += 1
        affected.append(posting)

    session.commit()
    return UpsertResult(inserted=inserted, postings=affected)
