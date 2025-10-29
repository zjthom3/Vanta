from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from apps.api.db.base import Base
from apps.api.db.types import ArrayType, GuidType
from apps.api.models.enums import ProviderEnum

if TYPE_CHECKING:
    from apps.api.models.application import Application
    from apps.api.models.company import Company
    from apps.api.models.posting_enrichment import PostingEnrichment
    from apps.api.models.resume_version import ResumeVersion


class JobPosting(Base):
    __tablename__ = "job_postings"
    __table_args__ = (
        UniqueConstraint("source", "source_id", name="uq_job_posting_source_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GuidType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id: Mapped[uuid.UUID | None] = mapped_column(
        GuidType(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True
    )
    source: Mapped[ProviderEnum] = mapped_column(Enum(ProviderEnum, name="provider_enum"), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String, nullable=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    jd_raw: Mapped[str | None] = mapped_column(String, nullable=True)
    jd_clean: Mapped[str | None] = mapped_column(String, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    remote_flag: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    eligibility_notes: Mapped[str | None] = mapped_column(String, nullable=True)
    salary_min_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="USD")
    normalized_tags: Mapped[list[str] | None] = mapped_column(ArrayType(String), nullable=True)
    posted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    company: Mapped["Company | None"] = relationship(back_populates="job_postings")
    applications: Mapped[list["Application"]] = relationship(back_populates="job_posting")
    posting_enrichments: Mapped[list["PostingEnrichment"]] = relationship(back_populates="job_posting")
    resume_versions: Mapped[list["ResumeVersion"]] = relationship(back_populates="job_posting")
