#!/usr/bin/env bash
set -euo pipefail

cd /workspace
if [ -f poetry.lock ]; then
  poetry install --no-root > /tmp/poetry-install.log 2>&1 || (cat /tmp/poetry-install.log && exit 1)
fi

cd /workspace/apps/workers
poetry run celery -A apps.workers.app:celery_app worker -l INFO

