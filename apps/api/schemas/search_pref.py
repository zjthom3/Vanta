from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SearchPrefResponse(BaseModel):
    id: str
    name: str
    filters: dict[str, Any]
    schedule_cron: str
    timezone: str
    last_run_at: str | None


class SearchPrefCreateRequest(BaseModel):
    name: str = Field(..., max_length=120)
    filters: dict[str, Any] = Field(default_factory=dict)
    schedule_cron: str
    timezone: str


class SearchPrefUpdateRequest(BaseModel):
    name: str | None = Field(None, max_length=120)
    filters: dict[str, Any] | None = None
    schedule_cron: str | None = None
    timezone: str | None = None
