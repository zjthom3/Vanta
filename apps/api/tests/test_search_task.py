from __future__ import annotations

from sqlalchemy.orm import Session

from apps.api.models import Notification, Profile, SearchPref, User
from apps.api.models.enums import PlanTierEnum, StatusEnum
from apps.workers.tasks import search


def test_run_daily_search_creates_enrichments_and_digest(monkeypatch, db_session: Session):
    user = User(email="task@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    profile = Profile(user=user, skills=["python", "management"], headline="Engineering Manager", locations=["Remote"])
    pref = SearchPref(
        user=user,
        name="Daily",
        filters={"greenhouse_board_token": "demo"},
        schedule_cron="0 7 * * *",
        timezone="UTC",
    )
    db_session.add_all([user, profile, pref])
    db_session.commit()

    monkeypatch.setattr(
        search.providers,
        "fetch_greenhouse_postings",
        lambda board_token: [
            {
                "id": 1,
                "title": "Senior Engineering Manager",
                "absolute_url": "https://example.com/jobs/1",
                "location": {"name": "Remote"},
                "departments": [{"name": "Engineering"}],
            }
        ],
    )

    search.run_daily_search(str(user.id))

    digest_notifications = db_session.query(Notification).filter_by(user_id=user.id, kind="daily_digest").all()
    assert len(digest_notifications) == 1
    payload = digest_notifications[0].payload
    assert payload["items"][0]["title"] == "Senior Engineering Manager"
    assert payload["items"][0]["fit_score"] > 0
