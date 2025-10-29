from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from apps.api.db.base import Base
from apps.api.db.types import GuidType
from apps.api.models.enums import OutreachChannelEnum, OutreachStatusEnum

if TYPE_CHECKING:
    from apps.api.models.application import Application


class Outreach(Base):
    __tablename__ = "outreach"

    id: Mapped[uuid.UUID] = mapped_column(GuidType(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(
        GuidType(as_uuid=True), ForeignKey("applications.id", ondelete="CASCADE"), nullable=False
    )
    contact_name: Mapped[str | None] = mapped_column(String, nullable=True)
    contact_role: Mapped[str | None] = mapped_column(String, nullable=True)
    contact_profile_url: Mapped[str | None] = mapped_column(String, nullable=True)
    channel: Mapped[OutreachChannelEnum] = mapped_column(
        Enum(OutreachChannelEnum, name="outreach_channel_enum"), nullable=False
    )
    status: Mapped[OutreachStatusEnum] = mapped_column(
        Enum(OutreachStatusEnum, name="outreach_status_enum"), nullable=False, default=OutreachStatusEnum.DRAFT
    )
    message_body: Mapped[str | None] = mapped_column(String, nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )

    application: Mapped["Application"] = relationship(back_populates="outreaches")
