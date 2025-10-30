from __future__ import annotations

from datetime import UTC, datetime, timedelta
from http import HTTPStatus

from sqlalchemy.orm import Session

from apps.api.models import Notification, User
from apps.api.models.enums import PlanTierEnum, StatusEnum


def _seed_user(db_session: Session) -> User:
    user = User(email="notifications@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    db_session.add(user)
    db_session.commit()
    return user


def test_list_notifications_returns_descending_order(client, db_session: Session):
    user = _seed_user(db_session)
    older = Notification(
        user_id=user.id,
        kind="resume_tailored",
        payload={"message": "Older"},
        created_at=datetime.now(UTC) - timedelta(days=1),
    )
    newer = Notification(
        user_id=user.id,
        kind="daily_digest",
        payload={"message": "Newer"},
    )
    db_session.add_all([older, newer])
    db_session.commit()

    response = client.get("/notifications", headers={"X-User-Id": str(user.id)})
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert len(body) == 2
    assert body[0]["kind"] == "daily_digest"
    assert body[1]["kind"] == "resume_tailored"


def test_mark_notification_read_sets_timestamp(client, db_session: Session):
    user = _seed_user(db_session)
    notification = Notification(user_id=user.id, kind="daily_digest", payload={"items": []})
    db_session.add(notification)
    db_session.commit()

    response = client.post(f"/notifications/{notification.id}/read", headers={"X-User-Id": str(user.id)})
    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == "read"

    db_session.refresh(notification)
    assert notification.read_at is not None


def test_mark_all_notifications_read(client, db_session: Session):
    user = _seed_user(db_session)
    unread = Notification(user_id=user.id, kind="resume_tailored", payload={"resume_id": "abc"})
    read = Notification(user_id=user.id, kind="resume_optimized", payload={}, read_at=datetime.now(UTC))
    db_session.add_all([unread, read])
    db_session.commit()

    response = client.post("/notifications/read-all", headers={"X-User-Id": str(user.id)})
    assert response.status_code == HTTPStatus.OK
    assert response.json()["status"] == "read_all"

    db_session.refresh(unread)
    db_session.refresh(read)
    assert unread.read_at is not None
    # previously read notifications remain read (timestamp untouched beyond existing value)
    assert read.read_at is not None
