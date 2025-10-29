from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from apps.api.db.base import Base
from apps.api.db.types import JSONType, GuidType

if TYPE_CHECKING:
    from apps.api.models.job_posting import JobPosting
    from apps.api.models.user import User


class PostingEnrichment(Base):
    __tablename__ = "posting_enrichments"
    __table_args__ = (
        UniqueConstraint("user_id", "job_posting_id", name="uq_enrichment_user_posting"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GuidType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GuidType(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    job_posting_id: Mapped[uuid.UUID] = mapped_column(
        GuidType(as_uuid=True), ForeignKey("job_postings.id", ondelete="CASCADE"), nullable=False
    )
    fit_score: Mapped[int] = mapped_column(Integer, nullable=False)
    fit_factors: Mapped[dict] = mapped_column(JSONType, nullable=False, default=dict)
    salary_estimate_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rationale: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="posting_enrichments")
    job_posting: Mapped["JobPosting"] = relationship(back_populates="posting_enrichments")
