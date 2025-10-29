from __future__ import annotations

from http import HTTPStatus

from sqlalchemy.orm import Session

from apps.api.models import Application, JobPosting, Task, User
from apps.api.models.enums import PlanTierEnum, ProviderEnum, StageEnum, StatusEnum


def _seed_user_and_posting(db_session: Session):
    user = User(email="app@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    posting = JobPosting(
        source=ProviderEnum.GREENHOUSE,
        source_id="abc",
        title="Product Designer",
        url="https://example.com/jobs/abc",
    )
    db_session.add_all([user, posting])
    db_session.commit()
    return user, posting


def test_create_application_from_job(client, db_session: Session):
    user, posting = _seed_user_and_posting(db_session)

    response = client.post(
        "/applications/",
        json={"job_posting_id": str(posting.id)},
        headers={"X-User-Id": str(user.id)},
    )
    assert response.status_code == HTTPStatus.CREATED
    body = response.json()
    assert body["title"] == "Product Designer"


def test_update_stage_creates_task(client, db_session: Session):
    user, posting = _seed_user_and_posting(db_session)
    application = Application(user_id=user.id, job_posting=posting)
    db_session.add(application)
    db_session.commit()

    response = client.patch(
        f"/applications/{application.id}",
        json={"stage": StageEnum.APPLIED.value},
        headers={"X-User-Id": str(user.id)},
    )
    assert response.status_code == HTTPStatus.OK

    tasks = db_session.query(Task).filter_by(user_id=user.id).all()
    assert len(tasks) == 1
    assert "follow up" in tasks[0].title.lower()
