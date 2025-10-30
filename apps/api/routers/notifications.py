from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from apps.api.deps.auth import get_current_user
from apps.api.db.session import get_session
from apps.api.models import Notification, User
from apps.api.schemas.notification import (
    DailyDigestItem,
    DailyDigestResponse,
    NotificationReadResponse,
    NotificationResponse,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=list[NotificationResponse])
def list_notifications(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> list[NotificationResponse]:
    stmt = (
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
    )
    notifications = session.scalars(stmt).all()
    return [
        NotificationResponse(
            id=str(notification.id),
            kind=notification.kind,
            payload=notification.payload,
            read_at=notification.read_at,
            created_at=notification.created_at,
        )
        for notification in notifications
    ]


@router.post("/{notification_id}/read", response_model=NotificationReadResponse)
def mark_notification_read(
    notification_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> NotificationReadResponse:
    notification = session.get(Notification, notification_id)
    if notification is None or notification.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")

    if notification.read_at is None:
        notification.read_at = datetime.now(timezone.utc)
        session.add(notification)
        session.commit()

    return NotificationReadResponse(status="read")


@router.post("/read-all", response_model=NotificationReadResponse)
def mark_all_notifications_read(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> NotificationReadResponse:
    now = datetime.now(timezone.utc)
    stmt = select(Notification).where(Notification.user_id == user.id, Notification.read_at.is_(None))
    updated = False
    for notification in session.scalars(stmt):
        notification.read_at = now
        updated = True
    if updated:
        session.commit()
    return NotificationReadResponse(status="read_all")


@router.get("/latest/digest", response_model=DailyDigestResponse)
def latest_digest(
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
) -> DailyDigestResponse:
    stmt = (
        select(Notification)
        .where(Notification.user_id == user.id, Notification.kind == "daily_digest")
        .order_by(Notification.created_at.desc())
        .limit(1)
    )
    notification = session.scalars(stmt).first()
    if notification is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No digest available")

    payload = notification.payload or {}
    generated_raw = payload.get("generated_at")
    try:
        generated_at = datetime.fromisoformat(generated_raw) if generated_raw else None
    except Exception:  # pragma: no cover - defensive
        generated_at = None
    generated_at = generated_at or notification.created_at

    items_payload = payload.get("items") or []
    items: list[DailyDigestItem] = []
    for raw_item in items_payload:
        items.append(
            DailyDigestItem(
                job_id=str(raw_item.get("job_id")),
                title=raw_item.get("title") or "Untitled role",
                company=raw_item.get("company"),
                location=raw_item.get("location"),
                remote=bool(raw_item.get("remote")),
                url=raw_item.get("url"),
                fit_score=raw_item.get("fit_score"),
                why_fit=raw_item.get("why_fit"),
            )
        )

    return DailyDigestResponse(generated_at=generated_at, items=items)
