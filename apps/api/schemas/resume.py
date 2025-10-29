from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ResumeSummary(BaseModel):
    id: str
    base: bool
    original_filename: str | None
    created_at: datetime
    ats_score: int | None


class ResumeDetailResponse(BaseModel):
    id: str
    original_filename: str | None
    content_type: str | None
    sections: dict[str, Any] | None
    keywords: list[str] | None
    ats_score: int | None
    created_at: datetime


class TailorResumeRequest(BaseModel):
    job_posting_id: str | None = None


class OptimizeResumeRequest(BaseModel):
    emphasis: str | None = None
