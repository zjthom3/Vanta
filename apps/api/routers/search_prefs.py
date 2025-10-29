from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.deps.auth import get_current_user
from apps.api.db.session import get_session
from apps.api.models import SearchPref, User
from apps.api.schemas.search_pref import (
    SearchPrefCreateRequest,
    SearchPrefResponse,
    SearchPrefUpdateRequest,
)

router = APIRouter(prefix="/search-preferences", tags=["search-preferences"])


def _serialize(pref: SearchPref) -> SearchPrefResponse:
    return SearchPrefResponse(
        id=str(pref.id),
        name=pref.name,
        filters=pref.filters or {},
        schedule_cron=pref.schedule_cron,
        timezone=pref.timezone,
        last_run_at=pref.last_run_at.isoformat() if pref.last_run_at else None,
    )


def _get_pref(session: Session, user: User, pref_id: uuid.UUID) -> SearchPref:
    pref = session.get(SearchPref, pref_id)
    if pref is None or pref.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Search preference not found")
    return pref


@router.get("/", response_model=list[SearchPrefResponse])
def list_search_prefs(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[SearchPrefResponse]:
    stmt = select(SearchPref).where(SearchPref.user_id == user.id).order_by(SearchPref.created_at.asc())
    prefs = session.scalars(stmt).all()
    return [_serialize(pref) for pref in prefs]


@router.post("/", response_model=SearchPrefResponse, status_code=status.HTTP_201_CREATED)
def create_search_pref(
    payload: SearchPrefCreateRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> SearchPrefResponse:
    existing_stmt = select(SearchPref).where(SearchPref.user_id == user.id, SearchPref.name == payload.name)
    if session.scalar(existing_stmt):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Search preference name already exists")

    pref = SearchPref(
        user_id=user.id,
        name=payload.name,
        filters=payload.filters,
        schedule_cron=payload.schedule_cron,
        timezone=payload.timezone,
    )
    session.add(pref)
    session.flush()
    session.refresh(pref)
    return _serialize(pref)


@router.put("/{pref_id}", response_model=SearchPrefResponse)
def update_search_pref(
    pref_id: uuid.UUID,
    payload: SearchPrefUpdateRequest,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> SearchPrefResponse:
    pref = _get_pref(session, user, pref_id)

    if payload.name and payload.name != pref.name:
        conflict_stmt = select(SearchPref).where(SearchPref.user_id == user.id, SearchPref.name == payload.name)
        if session.scalar(conflict_stmt):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Search preference name already exists")
        pref.name = payload.name
    if payload.filters is not None:
        pref.filters = payload.filters
    if payload.schedule_cron is not None:
        pref.schedule_cron = payload.schedule_cron
    if payload.timezone is not None:
        pref.timezone = payload.timezone

    session.flush()
    session.refresh(pref)
    return _serialize(pref)


@router.delete("/{pref_id}")
def delete_search_pref(
    pref_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> None:
    pref = _get_pref(session, user, pref_id)
    session.delete(pref)
    session.flush()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
