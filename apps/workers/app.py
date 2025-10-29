from __future__ import annotations

from celery import Celery

from apps.api.config import settings

celery_app = Celery(
    "vanta",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "apps.workers.tasks.resume",
        "apps.workers.tasks.search",
    ],
)

celery_app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"])


def run() -> None:  # pragma: no cover - convenience entrypoint
    celery_app.worker_main(["worker", "-l", "INFO"])
