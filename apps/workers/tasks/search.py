from __future__ import annotations

import uuid

from loguru import logger
from sqlalchemy.orm import Session

from apps.api.db.session import SessionLocal
from apps.api.models import JobPosting, SearchPref
from apps.api.services import digest, ingestion, matching, providers

from apps.workers.app import celery_app


@celery_app.task(name="search.run")
def run_daily_search(user_id: str) -> None:
    logger.info("Running daily search", user_id=user_id)
    with SessionLocal() as session:
        prefs = _load_search_preferences(session, user_id)
        total_inserted = 0
        for pref in prefs:
            board_token = pref.filters.get("greenhouse_board_token")
            if not board_token:
                continue
            postings = providers.fetch_greenhouse_postings(board_token)
            normalized = [providers.normalize_greenhouse_posting(posting) for posting in postings]
            result = ingestion.upsert_job_postings(session, normalized)
            total_inserted += result.inserted
            for posting in result.postings:
                matching.update_posting_enrichment(session, user_id, posting)
        if total_inserted:
            digest.build_daily_digest(session, user_id)
        logger.info("Ingestion completed", user_id=user_id, inserted=total_inserted)


def _load_search_preferences(session: Session, user_id: str) -> list[SearchPref]:
    user_uuid = uuid.UUID(str(user_id))
    stmt = (
        session.query(SearchPref)
        .filter(SearchPref.user_id == user_uuid)
        .filter(SearchPref.filters.isnot(None))
    )
    return stmt.all()
