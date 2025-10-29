#!/usr/bin/env bash
set -euo pipefail

cd /workspace
if [ -f poetry.lock ]; then
  poetry install --no-root > /tmp/poetry-install.log 2>&1 || (cat /tmp/poetry-install.log && exit 1)
else
  echo "poetry.lock not found; skipping dependency install"
fi

cd /workspace/apps/api
if [ -f alembic.ini ]; then
  poetry run alembic upgrade head
fi

poetry run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
