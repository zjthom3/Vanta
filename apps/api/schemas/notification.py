from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class NotificationResponse(BaseModel):
    id: str
    kind: str
    payload: dict | None = None
    read_at: datetime | None = None
    created_at: datetime


class NotificationReadResponse(BaseModel):
    status: str


class DailyDigestItem(BaseModel):
    job_id: str
    title: str
    company: str | None
    location: str | None
    remote: bool
    url: str | None
    fit_score: int | None = None
    why_fit: str | None = None


class DailyDigestResponse(BaseModel):
    generated_at: datetime
    items: list[DailyDigestItem]
