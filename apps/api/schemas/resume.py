from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ResumeDetailResponse(BaseModel):
    id: str
    original_filename: str | None
    content_type: str | None
    sections: dict[str, Any] | None
    keywords: list[str] | None
    ats_score: int | None
    created_at: datetime
