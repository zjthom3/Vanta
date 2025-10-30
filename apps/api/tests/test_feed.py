from __future__ import annotations

from http import HTTPStatus

from sqlalchemy.orm import Session

from apps.api.models import HiddenPosting, JobPosting, User
from apps.api.models.enums import PlanTierEnum, ProviderEnum, StatusEnum


def _seed_user(db: Session) -> User:
    user = User(email="feed@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    db.add(user)
    db.commit()
    return user


def _seed_posting(db: Session, title: str = "Engineer") -> JobPosting:
    posting = JobPosting(
        source=ProviderEnum.GREENHOUSE,
        source_id=title.lower(),
        title=title,
        url=f"https://example.com/{title}",
        remote_flag=True,
    )
    db.add(posting)
    db.commit()
    return posting


def test_feed_returns_items(client, db_session: Session):
    user = _seed_user(db_session)
    _seed_posting(db_session, "Engineer")

    response = client.get("/feed/jobs", headers={"X-User-Id": str(user.id)})
    assert response.status_code == HTTPStatus.OK
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Engineer"
    assert "fit_score" in data["items"][0]
    assert "why_fit" in data["items"][0]


def test_feed_hides_hidden_postings(client, db_session: Session):
    user = _seed_user(db_session)
    posting = _seed_posting(db_session, "Designer")
    hidden = HiddenPosting(user_id=user.id, job_posting_id=posting.id)
    db_session.add(hidden)
    db_session.commit()

    response = client.get("/feed/jobs", headers={"X-User-Id": str(user.id)})
    assert response.status_code == HTTPStatus.OK
    assert response.json()["total"] == 0


def test_feed_hide_endpoint_marks_posting(client, db_session: Session):
    user = _seed_user(db_session)
    posting = _seed_posting(db_session, "PM")

    hide_response = client.post(f"/feed/jobs/{posting.id}/hide", headers={"X-User-Id": str(user.id)})
    assert hide_response.status_code == HTTPStatus.OK

    response = client.get("/feed/jobs", headers={"X-User-Id": str(user.id)})
    assert response.json()["total"] == 0
