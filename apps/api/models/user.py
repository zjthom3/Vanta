from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from apps.api.db.base import Base
from apps.api.db.types import GuidType
from apps.api.models.enums import PlanTierEnum, StatusEnum

if TYPE_CHECKING:
    from apps.api.models.application import Application
    from apps.api.models.audit_log import AuditLog
    from apps.api.models.application_note import ApplicationNote
    from apps.api.models.integration_account import IntegrationAccount
    from apps.api.models.model_run import ModelRun
    from apps.api.models.notification import Notification
    from apps.api.models.posting_enrichment import PostingEnrichment
    from apps.api.models.profile import Profile
    from apps.api.models.resume_version import ResumeVersion
    from apps.api.models.search_pref import SearchPref
    from apps.api.models.task import Task
    from apps.api.models.user_event import UserEvent

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        GuidType(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(320), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    auth_provider: Mapped[str | None] = mapped_column(String, nullable=True)
    plan_tier: Mapped[PlanTierEnum] = mapped_column(
        Enum(PlanTierEnum, name="plan_tier_enum"), nullable=False, default=PlanTierEnum.FREE
    )
    status: Mapped[StatusEnum] = mapped_column(
        Enum(StatusEnum, name="status_enum"), nullable=False, default=StatusEnum.ACTIVE
    )
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    profile: Mapped["Profile"] = relationship(back_populates="user", uselist=False)
    search_prefs: Mapped[list["SearchPref"]] = relationship(back_populates="user")
    resume_versions: Mapped[list["ResumeVersion"]] = relationship(back_populates="user")
    applications: Mapped[list["Application"]] = relationship(back_populates="user")
    tasks: Mapped[list["Task"]] = relationship(back_populates="user")
    notifications: Mapped[list["Notification"]] = relationship(back_populates="user")
    integration_accounts: Mapped[list["IntegrationAccount"]] = relationship(back_populates="user")
    posting_enrichments: Mapped[list["PostingEnrichment"]] = relationship(back_populates="user")
    model_runs: Mapped[list["ModelRun"]] = relationship(back_populates="user")
    user_events: Mapped[list["UserEvent"]] = relationship(back_populates="user")
    audit_logs: Mapped[list["AuditLog"]] = relationship(back_populates="actor")
    application_notes: Mapped[list["ApplicationNote"]] = relationship(back_populates="author")
