from __future__ import annotations

from http import HTTPStatus

from sqlalchemy.orm import Session

from apps.api.models import SearchPref, User
from apps.api.models.enums import PlanTierEnum, StatusEnum


def _seed_user(db_session: Session) -> User:
    user = User(email="search-pref@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    db_session.add(user)
    db_session.commit()
    return user


def test_search_pref_crud_flow(client, db_session: Session):
    user = _seed_user(db_session)
    headers = {"X-User-Id": str(user.id)}

    list_response = client.get("/search-preferences/", headers=headers)
    assert list_response.status_code == HTTPStatus.OK
    assert list_response.json() == []

    create_payload = {
        "name": "Morning Run",
        "filters": {"role": "PM"},
        "schedule_cron": "0 6 * * *",
        "timezone": "America/Toronto",
    }

    create_response = client.post("/search-preferences/", json=create_payload, headers=headers)
    assert create_response.status_code == HTTPStatus.CREATED
    pref_id = create_response.json()["id"]

    update_payload = {"name": "Morning Search", "filters": {"role": "PM", "remote": True}}
    update_response = client.put(f"/search-preferences/{pref_id}", json=update_payload, headers=headers)
    assert update_response.status_code == HTTPStatus.OK
    assert update_response.json()["filters"]["remote"] is True

    delete_response = client.delete(f"/search-preferences/{pref_id}", headers=headers)
    assert delete_response.status_code == HTTPStatus.NO_CONTENT

    list_after_delete = client.get("/search-preferences/", headers=headers)
    assert list_after_delete.json() == []


def test_search_pref_name_conflict(client, db_session: Session):
    user = _seed_user(db_session)
    headers = {"X-User-Id": str(user.id)}

    pref = SearchPref(
        user_id=user.id,
        name="Existing",
        filters={"role": "PM"},
        schedule_cron="0 7 * * *",
        timezone="UTC",
    )
    db_session.add(pref)
    db_session.commit()

    payload = {
        "name": "Existing",
        "filters": {},
        "schedule_cron": "0 8 * * *",
        "timezone": "UTC",
    }
    response = client.post("/search-preferences/", json=payload, headers=headers)
    assert response.status_code == HTTPStatus.CONFLICT
