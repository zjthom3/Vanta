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
    from apps.api.models.user import User


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(GuidType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(
        GuidType(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    headline: Mapped[str | None] = mapped_column(String, nullable=True)
    summary: Mapped[str | None] = mapped_column(String, nullable=True)
    skills: Mapped[list[str] | None] = mapped_column(ArrayType(String), nullable=True)
    years_experience: Mapped[int | None] = mapped_column(Integer, nullable=True)
    locations: Mapped[list[str] | None] = mapped_column(ArrayType(String), nullable=True)
    work_auth: Mapped[str | None] = mapped_column(String, nullable=True)
    salary_min_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_max_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    remote_only: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    job_preferences: Mapped[dict | None] = mapped_column(JSONType, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="profile")
