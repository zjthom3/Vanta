from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from apps.api.models.enums import StageEnum


class ApplicationCreateRequest(BaseModel):
    job_posting_id: str | None = None
    title: str | None = None
    company: str | None = None
    url: str | None = None


class ApplicationUpdateRequest(BaseModel):
    stage: StageEnum


class TaskSummary(BaseModel):
    id: str
    title: str
    task_type: str | None = Field(default=None, alias="type")
    due_at: str | None = None
    completed_at: str | None = None


class ApplicationResponse(BaseModel):
    id: str
    title: str
    company: str | None
    stage: StageEnum
    url: str | None
    tasks: list[TaskSummary] = []
    created_at: str
