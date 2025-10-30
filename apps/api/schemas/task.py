from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

from apps.api.models.enums import PriorityEnum, TaskTypeEnum


class TaskResponse(BaseModel):
    id: str
    title: str
    type: TaskTypeEnum | None = None
    priority: PriorityEnum
    due_at: datetime | None = None
    completed_at: datetime | None = None
    application_id: str | None = None
    application_title: str | None = None


class TaskActionRequest(BaseModel):
    action: Literal["complete", "defer", "undo"]
