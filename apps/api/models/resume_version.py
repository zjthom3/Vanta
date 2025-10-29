from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from apps.api.db.base import Base
from apps.api.db.types import ArrayType, JSONType, GuidType

if TYPE_CHECKING:
    from apps.api.models.job_posting import JobPosting
    from apps.api.models.user import User


class ResumeVersion(Base):
    __tablename__ = "resume_versions"

    id: Mapped[uuid.UUID] = mapped_column(GuidType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GuidType(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    job_posting_id: Mapped[uuid.UUID | None] = mapped_column(
        GuidType(as_uuid=True), ForeignKey("job_postings.id", ondelete="SET NULL"), nullable=True
    )
    base_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    doc_url: Mapped[str | None] = mapped_column(String, nullable=True)
    original_filename: Mapped[str | None] = mapped_column(String, nullable=True)
    content_type: Mapped[str | None] = mapped_column(String, nullable=True)
    sections_json: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    ats_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    keywords: Mapped[list[str] | None] = mapped_column(ArrayType(String), nullable=True)
    diff_from_base: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="resume_versions")
    job_posting: Mapped["JobPosting | None"] = relationship(back_populates="resume_versions")
