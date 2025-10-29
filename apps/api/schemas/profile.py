from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class ProfileResponse(BaseModel):
    id: str
    headline: str | None
    summary: str | None
    skills: List[str] | None
    years_experience: int | None
    locations: List[str] | None
    work_auth: str | None
    salary_min_cents: int | None
    salary_max_cents: int | None
    remote_only: bool


class ProfileUpdateRequest(BaseModel):
    headline: str | None = Field(None, max_length=255)
    summary: str | None = Field(None, max_length=2000)
    skills: List[str] | None = None
    years_experience: int | None = Field(None, ge=0, le=60)
    locations: List[str] | None = None
    work_auth: str | None = Field(None, max_length=255)
    salary_min_cents: int | None = Field(None, ge=0)
    salary_max_cents: int | None = Field(None, ge=0)
    remote_only: bool | None = None
