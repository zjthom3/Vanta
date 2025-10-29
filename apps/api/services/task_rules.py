from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from apps.api.models import Application, Task
from apps.api.models.enums import StageEnum, TaskTypeEnum, PriorityEnum


def create_default_task(session: Session, application: Application, *, reason: str) -> Task:
    task = Task(
        user_id=application.user_id,
        application_id=application.id,
        title=reason,
        nudge_type=TaskTypeEnum.FOLLOW_UP,
        priority=PriorityEnum.NORMAL,
        due_at=datetime.now(UTC) + timedelta(days=3),
    )
    session.add(task)
    session.flush()
    return task


def handle_stage_change(session: Session, application: Application, new_stage: StageEnum) -> None:
    if new_stage == StageEnum.APPLIED:
        create_default_task(session, application, reason="Follow up on applied role")
    elif new_stage == StageEnum.INTERVIEW:
        create_default_task(session, application, reason="Interview prep")
