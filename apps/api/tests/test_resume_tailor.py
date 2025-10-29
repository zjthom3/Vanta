from __future__ import annotations

from http import HTTPStatus

from sqlalchemy.orm import Session

from apps.api.models import JobPosting, Notification, ResumeVersion, User
from apps.api.models.enums import PlanTierEnum, ProviderEnum, StatusEnum


def _seed_user(db_session: Session) -> User:
    user = User(email="tailor@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    db_session.add(user)
    db_session.commit()
    return user


def _seed_resume(db_session: Session, user: User) -> ResumeVersion:
    resume = ResumeVersion(
        user_id=user.id,
        base_flag=True,
        original_filename="base.pdf",
        content_type="application/pdf",
        sections_json={"summary": "Experienced leader", "highlights": ["Strategy"]},
        keywords=["Leadership"],
        ats_score=70,
    )
    db_session.add(resume)
    db_session.commit()
    return resume


def _seed_job(db_session: Session) -> JobPosting:
    job = JobPosting(
        source=ProviderEnum.GREENHOUSE,
        source_id="job-1",
        title="Engineering Manager",
        url="https://example.com/jobs/1",
        normalized_tags=["Leadership", "Python"],
    )
    db_session.add(job)
    db_session.commit()
    return job


def test_tailor_resume_endpoint(client, db_session: Session):
    user = _seed_user(db_session)
    resume = _seed_resume(db_session, user)
    job = _seed_job(db_session)

    response = client.post(
        f"/resumes/{resume.id}/tailor",
        json={"job_posting_id": str(job.id)},
        headers={"X-User-Id": str(user.id)},
    )
    assert response.status_code == HTTPStatus.CREATED
    body = response.json()
    assert "Tailored for Engineering Manager" in body["sections"]["summary"]

    notification = db_session.query(Notification).filter_by(user_id=user.id, kind="resume_tailored").one()
    assert notification.payload["resume_id"] == body["id"]


def test_optimize_resume_endpoint(client, db_session: Session):
    user = _seed_user(db_session)
    resume = _seed_resume(db_session, user)

    response = client.post(
        f"/resumes/{resume.id}/optimize",
        json={"emphasis": "ATS"},
        headers={"X-User-Id": str(user.id)},
    )
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["ats_score"] >= resume.ats_score


def test_list_resumes(client, db_session: Session):
    user = _seed_user(db_session)
    resume = _seed_resume(db_session, user)

    response = client.get("/resumes", headers={"X-User-Id": str(user.id)})
    assert response.status_code == HTTPStatus.OK
    items = response.json()
    assert items[0]["id"] == str(resume.id)
