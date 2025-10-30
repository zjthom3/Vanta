# Vanta
Automate and optimize every step of the job-hunting process with OpenAI Agents—finding high-fit roles daily, tailoring applications, managing pipelines, and prompting smart follow-ups—so users spend time interviewing, not tab-hopping.

## Repo Structure
- `apps/web` — Next.js 14 app (App Router) for the user experience.
- `apps/api` — FastAPI service exposing REST/JSON endpoints for agents and UI.
- `apps/workers` — Celery workers handling ingestion, resume parsing, matching, and notifications.
- `packages/ui` — Shared component library and styling primitives.
- `packages/types` — Shared OpenAPI/TypeScript schemas and Pydantic models.
- `infra/docker` — Dockerfiles and compose overrides for local dev + CI.
- `infra/db` — Alembic migrations, seeds, and data fixtures.
- `infra/ops` — Operational scripts, deployment manifests, and observability configs.
- `.devcontainer` — VS Code devcontainer configuration (optional for team parity).

Refer to `master_plan.md` for comprehensive product, data, and delivery plans.

## Getting Started
- Copy `.env.example` to `.env` and adjust secrets as needed.
- Install Python dependencies with `poetry install` and frontend dependencies via `npm install` inside `apps/web`.
- Launch the full stack using `make dev` (Docker Compose), or run `poetry run uvicorn apps.api.main:app --reload` and `npm --prefix apps/web run dev` locally.
- Helpful commands:
  - `make test` — Run FastAPI pytest suite and Vitest unit tests.
  - `make lint` — Ruff + Black + Next.js ESLint.
  - `make typecheck` — mypy and TypeScript compiler checks.
- The backend tests default to an on-disk SQLite database (`tests.db`). You can remove the file after runs; it is git-ignored. To exercise Postgres-specific behavior, set `POSTGRES_URL` before running `pytest`.
- The job feed (`/feed/jobs`) filters out hidden postings and returns simple pagination metadata for the `/feed` UI; creating an application (`POST /applications`) and moving stages (`PATCH /applications/{id}`) generates follow-up tasks that surface in the `/applications` Kanban view.

### Authentication (local dev)
- Sign in to the web app via `/sign-in` with any email address. The web app uses NextAuth Credentials provider and the API issues user IDs via `POST /auth/dev-login`.
- Requests from the frontend include an `X-User-Id` header so profile and search preference endpoints stay scoped to the authenticated user.

### Resume uploads (local dev)
- The API stores uploaded resumes in the S3-compatible bucket configured via `S3_*` env vars. The default Docker Compose stack ships with MinIO; ensure it is running (`docker compose up minio`) before testing uploads.

## Feature Highlights
- **Pipeline Kanban** – Drag-and-drop applications across stages and capture notes or attachments from the same board (`/applications`).
- **Task Inbox** – Action follow-ups and prep work with quick complete/defer actions (`/tasks`).
- **Daily Digest** – Review the latest ranked matches and “why fit” rationales in a dedicated digest view (`/digest`).
