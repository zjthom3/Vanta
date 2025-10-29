from __future__ import annotations

from sqlalchemy.orm import Session

from apps.api.models import SearchPref, User
from apps.api.models.enums import PlanTierEnum, StatusEnum
from apps.workers.tasks import scheduler, search


def test_scheduler_tick_enqueues_runs(monkeypatch, db_session: Session):
    user = User(email="schedule@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    pref = SearchPref(
        user=user,
        name="Daily",
        filters={"greenhouse_board_token": "token"},
        schedule_cron="0 5 * * *",
        timezone="UTC",
    )
    db_session.add_all([user, pref])
    db_session.commit()

    dispatched: list[str] = []

    def fake_delay(user_id: str) -> None:  # noqa: ANN001
        dispatched.append(user_id)

    monkeypatch.setattr(search.run_daily_search, "delay", fake_delay)

    scheduler.scheduler_tick()

    assert dispatched == [str(user.id)]
