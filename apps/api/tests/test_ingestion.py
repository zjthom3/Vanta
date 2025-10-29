from __future__ import annotations

from sqlalchemy.orm import Session

from apps.api.models import Company, JobPosting
from apps.api.models.enums import ProviderEnum
from apps.api.services import ingestion, providers


def test_normalize_greenhouse_posting_sets_remote_flag():
    raw = {
        "id": 42,
        "title": "Staff Engineer",
        "absolute_url": "https://example.com/42",
        "location": {"name": "Remote - North America"},
        "departments": [{"name": "Engineering"}],
    }

    normalized = providers.normalize_greenhouse_posting(raw)

    assert normalized["source_id"] == "42"
    assert normalized["is_remote"] is True
    assert normalized["metadata_json"]["departments"] == ["Engineering"]


def test_upsert_job_postings_creates_and_updates(db_session: Session):
    payloads = [
        {
            "source": "greenhouse",
            "source_id": "abc",
            "title": "Product Manager",
            "url": "https://example.com/jobs/abc",
            "location_raw": "Remote",
            "is_remote": True,
            "metadata_json": {"departments": ["Product"]},
            "company": {"name": "Acme", "domain": "acme.com"},
        }
    ]

    inserted = ingestion.upsert_job_postings(db_session, payloads)
    assert inserted == 1

    posting = db_session.query(JobPosting).filter_by(source=ProviderEnum.GREENHOUSE, source_id="abc").one()
    assert posting.remote_flag is True
    assert posting.company is not None
    assert posting.company.name == "Acme"

    update_payload = [
        {
            "source": "greenhouse",
            "source_id": "abc",
            "title": "Principal Product Manager",
            "url": "https://example.com/jobs/abc",
            "location_raw": "Toronto",
            "is_remote": False,
        }
    ]

    updated = ingestion.upsert_job_postings(db_session, update_payload)
    assert updated == 0

    db_session.refresh(posting)
    assert posting.title == "Principal Product Manager"
    assert posting.remote_flag is False


def test_upsert_job_postings_skips_invalid_provider(db_session: Session):
    payload = [{"source": "unknown", "source_id": "1"}]
    inserted = ingestion.upsert_job_postings(db_session, payload)
    assert inserted == 0
    assert db_session.query(JobPosting).count() == 0
