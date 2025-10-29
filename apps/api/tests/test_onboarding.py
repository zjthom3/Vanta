from __future__ import annotations

from http import HTTPStatus

from sqlalchemy import select

from apps.api.models import Profile, ResumeVersion, SearchPref, User
from apps.api.services import onboarding as onboarding_service


def test_submit_profile(monkeypatch, client, db_session):
    captured_resume_ids: list[str] = []

    monkeypatch.setattr(
        onboarding_service,
        "enqueue_resume_parse",
        lambda resume_id: captured_resume_ids.append(str(resume_id)),
    )

    inline_resume_ids: list[str] = []
    monkeypatch.setattr(
        onboarding_service.resume_tasks,
        "process_resume",
        lambda resume_id: inline_resume_ids.append(resume_id),
    )

    monkeypatch.setattr(
        onboarding_service.storage,
        "upload_stream",
        lambda key, body, content_type=None: f"https://storage.local/{key}",
    )

    data = {
        "full_name": "Ada Lovelace",
        "email": "ada@example.com",
        "primary_role": "Product Manager",
        "target_locations": ["Remote", "Toronto"],
        "years_experience": "6",
        "schedule_cron": "0 6 * * *",
        "timezone": "America/Toronto",
    }
    files = [
        ("resume", ("ada.pdf", b"resume content", "application/pdf")),
    ]

    response = client.post("/onboarding/profile", data=data, files=files)

    assert response.status_code == HTTPStatus.ACCEPTED
    body = response.json()
    assert body["next_step"] == "search_preferences"
    assert body["resume_version_id"] is not None
    assert body["resume_doc_url"] == f"https://storage.local/resumes/{body['resume_version_id']}/ada.pdf"
    assert captured_resume_ids, "resume parse should be enqueued"
    assert inline_resume_ids == captured_resume_ids

    user = db_session.execute(select(User).where(User.email == "ada@example.com")).scalar_one()
    profile = db_session.execute(select(Profile).where(Profile.user_id == user.id)).scalar_one()
    assert profile.locations == ["Remote", "Toronto"]
    assert profile.remote_only is True

    search_pref = db_session.execute(select(SearchPref).where(SearchPref.user_id == user.id)).scalar_one()
    assert search_pref.schedule_cron == "0 6 * * *"
    assert search_pref.timezone == "America/Toronto"

    resume = db_session.execute(select(ResumeVersion).where(ResumeVersion.user_id == user.id)).scalar_one()
    assert str(resume.id) == captured_resume_ids[0]
    assert resume.doc_url == f"https://storage.local/resumes/{captured_resume_ids[0]}/ada.pdf"
    assert resume.original_filename == "ada.pdf"
    assert resume.content_type == "application/pdf"


def test_submit_profile_validation(client):
    data = {
        "full_name": "Ada Lovelace",
        "email": "ada@example.com",
        "primary_role": "Product Manager",
        "target_locations": ["Remote", "Toronto"],
        "years_experience": "-1",
    }

    response = client.post("/onboarding/profile", data=data)
    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


def test_submit_profile_without_resume(monkeypatch, client, db_session):
    # Ensure resume upload helpers are not invoked when resume is omitted
    monkeypatch.setattr(onboarding_service, "enqueue_resume_parse", lambda resume_id: (_ for _ in ()).throw(AssertionError("should not enqueue")))
    monkeypatch.setattr(onboarding_service.resume_tasks, "process_resume", lambda resume_id: (_ for _ in ()).throw(AssertionError("should not process")))
    monkeypatch.setattr(onboarding_service.storage, "upload_stream", lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("should not upload")))

    data = {
        "full_name": "Ada Lovelace",
        "email": "ada-nofile@example.com",
        "primary_role": "Product Manager",
        "target_locations": ["Remote"],
        "years_experience": "5",
    }

    response = client.post("/onboarding/profile", data=data)
    assert response.status_code == HTTPStatus.ACCEPTED
    body = response.json()
    assert body["resume_version_id"] is None
    assert body["resume_doc_url"] is None

    user = db_session.execute(select(User).where(User.email == "ada-nofile@example.com")).scalar_one()
    assert user.profile is not None
