from __future__ import annotations

from http import HTTPStatus

from sqlalchemy.orm import Session

from apps.api.models import Profile, User
from apps.api.models.enums import PlanTierEnum, StatusEnum


def _seed_user(db_session: Session) -> User:
    user = User(email="profile@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    profile = Profile(user=user)
    db_session.add_all([user, profile])
    db_session.commit()
    return user


def test_get_my_profile(client, db_session: Session):
    user = _seed_user(db_session)

    response = client.get("/profile/me", headers={"X-User-Id": str(user.id)})
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["id"] is not None
    assert body["remote_only"] is True


def test_update_profile(client, db_session: Session):
    user = _seed_user(db_session)

    payload = {
        "headline": "Product Manager",
        "summary": "Drives cross-functional alignment.",
        "skills": ["Product Strategy", "Roadmaps"],
        "remote_only": False,
    }

    response = client.put("/profile/me", json=payload, headers={"X-User-Id": str(user.id)})
    assert response.status_code == HTTPStatus.OK

    updated = response.json()
    assert updated["headline"] == "Product Manager"
    assert updated["remote_only"] is False
