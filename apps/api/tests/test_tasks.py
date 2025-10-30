from __future__ import annotations

from datetime import datetime, timedelta, timezone
from http import HTTPStatus

from sqlalchemy.orm import Session

from apps.api.models import Task, User
from apps.api.models.enums import PlanTierEnum, PriorityEnum, StatusEnum, TaskTypeEnum


def _seed_task(db_session: Session) -> tuple[User, Task]:
    user = User(email="tasks@example.com", plan_tier=PlanTierEnum.FREE, status=StatusEnum.ACTIVE)
    task = Task(
        user=user,
        title="Follow up email",
        nudge_type=TaskTypeEnum.FOLLOW_UP,
        priority=PriorityEnum.NORMAL,
        due_at=datetime.now(timezone.utc),
    )
    db_session.add_all([user, task])
    db_session.commit()
    return user, task


def test_list_tasks_returns_results(client, db_session: Session):
    user, task = _seed_task(db_session)

    response = client.get("/tasks", headers={"X-User-Id": str(user.id)})
    assert response.status_code == HTTPStatus.OK
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == task.title


def test_complete_task_marks_completed(client, db_session: Session):
    user, task = _seed_task(db_session)
    response = client.patch(
        f"/tasks/{task.id}",
        json={"action": "complete"},
        headers={"X-User-Id": str(user.id)},
    )
    assert response.status_code == HTTPStatus.OK
    db_session.refresh(task)
    assert task.completed_at is not None


def test_defer_task_pushes_due_date(client, db_session: Session):
    user, task = _seed_task(db_session)
    original_due = task.due_at
    response = client.patch(
        f"/tasks/{task.id}",
        json={"action": "defer"},
        headers={"X-User-Id": str(user.id)},
    )
    assert response.status_code == HTTPStatus.OK
    db_session.refresh(task)
    assert task.due_at is not None
    assert task.due_at >= (original_due + timedelta(days=2))
