from __future__ import annotations

from loguru import logger

from apps.api.db.session import SessionLocal
from apps.api.models import SearchPref
from apps.workers.app import celery_app
from apps.workers.tasks import search


@celery_app.task(name="scheduler.tick")
def scheduler_tick() -> None:
    with SessionLocal() as session:
        prefs = session.query(SearchPref).all()
        for pref in prefs:
            logger.debug("Queueing search run", user_id=str(pref.user_id), search_pref=str(pref.id))
            search.run_daily_search.delay(str(pref.user_id))
