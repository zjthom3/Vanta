FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /workspace

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential curl libpq-dev \
    && pip install --no-cache-dir poetry==1.8.3 \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/workspace

COPY pyproject.toml poetry.lock* README.md ./
RUN if [ -f pyproject.toml ]; then poetry install --no-root; fi

COPY . .

CMD ["bash", "/workspace/infra/docker/start-api.sh"]
