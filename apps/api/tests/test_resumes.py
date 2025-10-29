from __future__ import annotations

from http import HTTPStatus

from sqlalchemy.orm import Session

from apps.api.models import ResumeVersion, User
from apps.api.models.enums import PlanTierEnum, StatusEnum


def _seed_resume(db: Session) -> tuple[User, ResumeVersion]:
    user = User(email="resume-owner@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    resume = ResumeVersion(
        user=user,
        base_flag=True,
        doc_url="https://storage.local/resumes/sample",
        original_filename="resume.docx",
        content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        sections_json={"summary": "Product leader", "experience": ["Built roadmap"]},
        keywords=["Product", "Roadmaps"],
        ats_score=78,
    )
    db.add_all([user, resume])
    db.commit()
    db.refresh(user)
    db.refresh(resume)
    return user, resume


def test_get_resume_details(client, db_session: Session):
    user, resume = _seed_resume(db_session)

    response = client.get(f"/resumes/{resume.id}", headers={"X-User-Id": str(user.id)})
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert body["original_filename"] == "resume.docx"
    assert body["sections"]["summary"] == "Product leader"
    assert body["ats_score"] == 78


def test_get_resume_details_unauthorized(client, db_session: Session):
    user, resume = _seed_resume(db_session)
    other = User(email="other@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    db_session.add(other)
    db_session.commit()

    response = client.get(f"/resumes/{resume.id}", headers={"X-User-Id": str(other.id)})
    assert response.status_code == HTTPStatus.NOT_FOUND
