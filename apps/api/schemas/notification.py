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
