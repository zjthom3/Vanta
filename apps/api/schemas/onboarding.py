from __future__ import annotations

from typing import List

from pydantic import BaseModel, EmailStr, Field

from uuid import UUID


class ResumeMetadata(BaseModel):
    filename: str
    content_type: str = Field(examples=["application/pdf"])
    size_bytes: int


class OnboardingPayload(BaseModel):
    full_name: str
    email: EmailStr
    primary_role: str
    target_locations: List[str] = Field(min_length=1)
    years_experience: int = Field(ge=0, le=60)
    schedule_cron: str | None = None
    timezone: str | None = None
    resume: ResumeMetadata | None = None


class OnboardingResponse(BaseModel):
    next_step: str
    message: str
    resume_version_id: UUID | None = None
    resume_doc_url: str | None = None
