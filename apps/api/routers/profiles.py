from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from apps.api.deps.auth import get_current_user
from apps.api.db.session import get_session
from apps.api.models import Profile, User
from apps.api.schemas.profile import ProfileResponse, ProfileUpdateRequest

router = APIRouter(prefix="/profile", tags=["profile"])


def _ensure_profile(session: Session, user: User) -> Profile:
    profile = user.profile
    if profile is None:
        profile = Profile(user_id=user.id)
        session.add(profile)
        session.flush()
    return profile


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ProfileResponse:
    profile = _ensure_profile(session, user)
    session.refresh(profile)
    return ProfileResponse(
        id=str(profile.id),
        headline=profile.headline,
        summary=profile.summary,
        skills=profile.skills,
        years_experience=profile.years_experience,
        locations=profile.locations,
        work_auth=profile.work_auth,
        salary_min_cents=profile.salary_min_cents,
        salary_max_cents=profile.salary_max_cents,
        remote_only=profile.remote_only,
    )


@router.put("/me", response_model=ProfileResponse, status_code=status.HTTP_200_OK)
def update_my_profile(
    payload: ProfileUpdateRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> ProfileResponse:
    profile = _ensure_profile(session, user)

    if payload.headline is not None:
        profile.headline = payload.headline
    if payload.summary is not None:
        profile.summary = payload.summary
    if payload.skills is not None:
        profile.skills = payload.skills
    if payload.years_experience is not None:
        profile.years_experience = payload.years_experience
    if payload.locations is not None:
        profile.locations = payload.locations
    if payload.work_auth is not None:
        profile.work_auth = payload.work_auth
    if payload.salary_min_cents is not None:
        profile.salary_min_cents = payload.salary_min_cents
    if payload.salary_max_cents is not None:
        profile.salary_max_cents = payload.salary_max_cents
    if payload.remote_only is not None:
        profile.remote_only = payload.remote_only

    session.flush()
    session.refresh(profile)

    return ProfileResponse(
        id=str(profile.id),
        headline=profile.headline,
        summary=profile.summary,
        skills=profile.skills,
        years_experience=profile.years_experience,
        locations=profile.locations,
        work_auth=profile.work_auth,
        salary_min_cents=profile.salary_min_cents,
        salary_max_cents=profile.salary_max_cents,
        remote_only=profile.remote_only,
    )
