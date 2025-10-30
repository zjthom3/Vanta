from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from apps.api.db.base import Base
from apps.api.db.types import GuidType
from apps.api.models.enums import StageEnum

if TYPE_CHECKING:
    from apps.api.models.job_posting import JobPosting
    from apps.api.models.outreach import Outreach
    from apps.api.models.task import Task
    from apps.api.models.user import User
    from apps.api.models.event import Event
    from apps.api.models.application_note import ApplicationNote


class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("user_id", "job_posting_id", name="uq_application_user_posting"),
    )

    id: Mapped[uuid.UUID] = mapped_column(GuidType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GuidType(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    job_posting_id: Mapped[uuid.UUID | None] = mapped_column(
        GuidType(as_uuid=True), ForeignKey("job_postings.id", ondelete="SET NULL"), nullable=True
    )
    stage: Mapped[StageEnum] = mapped_column(
        Enum(StageEnum, name="stage_enum"), nullable=False, default=StageEnum.PROSPECT
    )
    status_notes: Mapped[str | None] = mapped_column(String, nullable=True)
    source_label: Mapped[str | None] = mapped_column(String, nullable=True)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="applications")
    job_posting: Mapped["JobPosting | None"] = relationship(back_populates="applications")
    outreaches: Mapped[list["Outreach"]] = relationship(back_populates="application")
    tasks: Mapped[list["Task"]] = relationship(back_populates="application")
    events: Mapped[list["Event"]] = relationship(back_populates="application")
    notes: Mapped[list["ApplicationNote"]] = relationship(
        back_populates="application", order_by="desc(ApplicationNote.created_at)"
    )
