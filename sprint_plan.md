0) Dev Environment & Repo Blueprint

Stack

Frontend: Next.js 15 + React Server Components, Tailwind, shadcn/ui, Zustand (state), React Query.

Backend: FastAPI, Pydantic, SQLAlchemy 2.0, Alembic, Celery + Redis (jobs), Postgres 15, S3-compatible storage.

Agents: OpenAI Agents (Orchestrator, JobScout, ResumeTailor, Optimizer, TrackerCoach).

Infra: Docker Compose, Makefile, pre-commit, Ruff + Black, mypy, ESLint.

Auth: NextAuth (email/Google) → JWT to FastAPI.

Analytics: PostHog or Amplitude SDK.

Repo structure

vanta/
  apps/
    web/                # Next.js app
    api/                # FastAPI app
    workers/            # Celery tasks (search, generation)
  packages/
    ui/                 # shared components (if needed)
    types/              # OpenAPI & shared TS types (or tRPC types)
  infra/
    docker/             # Dockerfiles
    db/                 # Alembic migrations & seeds
    ops/                # scripts, k8s manifests (later)
  .devcontainer/        # devcontainer.json (optional)
  Makefile
  docker-compose.yml
  README.md


VS Code essentials

Extensions: Python, Ruff, Pylance, Docker, EditorConfig, ESLint, Tailwind CSS IntelliSense, Prisma (if used), GitHub Copilot (optional).

launch.json targets: Next.js dev, FastAPI Uvicorn, Celery worker, Jest/Vitest, Pytest.

tasks.json recipes: make dev, make db.up, make migrate, make test.

Environment

# .env (root)
POSTGRES_URL=postgresql+psycopg://vanta:vanta@db:5432/vanta
REDIS_URL=redis://redis:6379/0
OPENAI_API_KEY=...
S3_ENDPOINT=...
S3_BUCKET=vanta
NEXTAUTH_SECRET=...
NEXTAUTH_URL=http://localhost:3000


Docker Compose (services)

db (postgres), redis, api (uvicorn hot reload), web (next dev), worker (celery), minio (optional S3 local).

Branching

main (protected), develop, feature branches feat/<epic>-<short>; conventional commits; PR template with checklist.

Sprint 1 — Auth, Onboarding, Resume Upload/Parse, Profiles, Search Prefs

Objective (MVP P0): User can sign up, upload resume, confirm skills, set filters & daily time.

Scope

Auth (email/Google), Profiles CRUD, Resume upload + parse (PDF/DOCX → JSON), Search Prefs model + cron preview.

Basic UI shell with Apple/Tesla/OpenAI minimal aesthetic.

Tasks

Scaffold apps (web, api, workers) + Docker Compose, Makefile, pre-commit.

DB setup: enums + tables from PRD (users, profiles, resume_versions, search_prefs).

Auth: NextAuth providers; GET /me on API; JWT handoff.

Resume Upload: S3 upload; worker parses file (PyPDF2/docx + heuristics) → sections_json, skills[].

Onboarding wizard (4 steps): Upload → Extract review → Skills/locations/salary → Daily time + timezone.

Search Prefs: JSON filters, cron string validation, “next run” preview badge.

DoD

New user completes onboarding ≤10 min.

Resume parsed with ≥80% fields; skills populated.

Search prefs saved with valid cron/timezone; preview updates.

Testing

Pytest for parsers; contract tests for /profiles, /search_prefs.

Cypress/Playwright: onboarding happy path.

Lint + type checks pass; CI green.

Codex Agent Prompts

Backend Model & Migrations

“Generate SQLAlchemy 2.0 models and Alembic migrations for users, profiles, resume_versions, search_prefs based on this schema: … Output code only.”

Resume Parser

“Write a Python parser that takes a PDF/DOCX resume and extracts summary, skills, experience bullets (•, -, *), education. Return Pydantic model ResumeSections. Include unit tests.”

Onboarding UI

“Create a Next.js 15 RSC onboarding wizard with 4 steps, Tailwind + shadcn/ui, persisting to /api endpoints. Include optimistic UI and form validation with Zod.”

Risks/Mitigations

Parsing variability → add manual edit UI and store parser confidence per section.

Auth complexity → start with email and Google only.

Sprint 2 — Ingestion, Normalization, Dedup, Feed (Basic)

Objective: Show a basic job feed sourced from 1–2 providers.

Scope

Provider clients (Greenhouse + Lever or an approved job API), normalization, deduplication, job_postings, companies.

Basic Feed UI (cards), filters, Hide/Save.

Tasks

DB: companies, job_postings (unique (source, source_id)), indexes (trigram, GIN).

Provider clients: typed clients with retries, rate limits, ToS compliance.

Normalizer: title/location/remote/salary/tags; tests with fixtures.

Dedup: upsert logic + partial unique index; idempotent ETL worker.

Feed UI: infinite list, filters, Hide/Save buckets (per user).

Company link: resolve domain/name to companies row.

DoD

Import ≥100 postings via seed; duplicates <3%.

Feed renders in <500ms P95 with pagination.

Hide excludes from future views.

Testing

ETL unit tests; DB property tests for uniqueness.

Playwright: feed filters, hide/save.

Codex Prompts

“Implement a Greenhouse jobs fetcher with pagination and backoff. Input: board token. Output: normalized postings list. Include unit tests with VCR-like cassettes.”

“Create Next.js job card component with Why Fit placeholder, actions (Track, Tailor disabled), and responsive layout.”

Risks

API limits → add per-provider backoff + internal cache layer.

Sprint 3 — Matching (Embeddings), Why-Fit, Scheduler & Daily Digest

Objective: Personalized ranking + daily run that compiles Top-N digest.

Scope

Embedding-based match, fit score, posting_enrichments, Why-Fit rationale, per-user cron scheduler, in-app & email digest.

Tasks

Embedding service: OpenAI embeddings; profile+JD vectorization; caching.

Scoring: Hard filters → semantic score → rerank by recency/skill overlap/salary alignment; write posting_enrichments.

Why-Fit: factor breakdown + human-readable rationale bullets.

Scheduler: per-user cron enqueues search:user_id; digest creation storing notifications.

Digest UI/Email: in-app inbox + email template with deep links.

DoD

Precision@10 ≥70% in internal QA (tag 50 samples, measure).

Daily job runs succeed ≥99% with retries.

Digest shows only new (not hidden/saved) postings.

Testing

Offline eval dataset + scoring tests.

Email rendering snapshot tests.

Codex Prompts

“Write a scoring function that takes Profile, JobPosting, and returns fit_score (0..100) plus factors: title_similarity, skill_overlap, salary_alignment, recency_boost.”

“Build a Next.js in-app notification center with unread counts and pagination.”

Risks

Hallucinated salary estimates → mark estimated with confidence; no assertive statements.

Sprint 4 — Applications (Track, Kanban, Notes) + Tasks (NBAs)

Objective: One-click track to pipeline; Kanban; Next-Best-Actions rules + Task Inbox.

Scope

applications, Kanban board, notes & attachments, task rules engine, task inbox.

Tasks

DB: applications, tasks, events, audit_logs.

Track from card: creates prospect, links posting.

Kanban: drag-drop updates stage + audit trail.

Notes/attachments: rich text + S3 uploads; versioning.

NBA rules: rule set (e.g., follow-up 5d after applied; prep tasks on interview).

Task Inbox: Do/Defer/Done; reminders.

DoD

Drag-drop persists and logs action.

NBA tasks create with due dates + reason.

Task completion shows in dashboard.

Testing

API contract tests for stage changes and audit logs.

E2E: Track → move → tasks created.

Codex Prompts

“Implement a Kanban board with React DnD and server actions to patch /applications/:id. Include optimistic updates and rollback on error.”

“Write a rule engine that accepts Application state and returns suggested tasks with due dates and reasons. Unit tests for edge cases.”

Risks

Over-notification → bundle NBAs per day; snooze.

Sprint 5 — Resume Tailor (Gen), Optimizer (Score + Diff), Notifications

Objective: Generate tailored resume; show ATS score & inline suggestions; notify user.

Scope

ResumeTailor agent → schema’d resume JSON + PDF/DOCX; Optimizer agent → score & suggestions; Diff UI; notifications.

Tasks

Agent endpoints: /resumes/generate, /resumes/optimize (async job + polling).

Renderer: server PDF via Paged.js/Playwright or WeasyPrint; DOCX using python-docx.

ATS scoring: keyword coverage, clarity heuristics.

Diff view: side-by-side base vs tailored; accept/reject per section.

Notifications: “resume ready” & Task creation (“Apply now”).

DoD

P95 generation ≤12s; JSON schema validated; PDF/DOCX downloadable.

Score & suggestions visible; accept → new version created & logged.

Testing

Golden file tests for renderer.

Heuristic unit tests for scoring.

Codex Prompts

“Create a FastAPI route /resumes/generate that accepts {profile_id, job_posting_id} and returns a job id. Worker composes a tailored resume JSON and renders to PDF/DOCX. Include schema validators and tests.”

“Build a diff editor UI for JSON-backed resume sections: show changes with accept/reject per bullet.”

Risks

PDF rendering flakiness → lock fonts, use known-good CSS print stack.

Sprint 6 — Perf/Resilience, Security/Privacy, Analytics, Polish & Beta

Objective: Harden, measure, and prepare for private beta.

Scope

Caching, pagination tuning, DLQs and retries, token encryption (KMS), data export/delete, analytics, A11y polish.

Tasks

Perf: Redis caching on feed queries; index audit; P95 <500ms.

Reliability: Celery retries & DLQ dashboards; alerting on queue depth/failures.

Security: KMS-sealed tokens; secrets rotation; scopes audit.

Privacy: user data export & account deletion (soft-delete 30d + token hard-delete).

Analytics: event schema (search_run, posting_view, apply_click, resume_generated, task_completed), funnels, dashboards.

A11y & UX polish: focus order, contrasts, reduced motion, hover states.

Beta checklist: seed data, admin guardrails, Sentry/Datadog wired.

DoD

Error budget: daily run success ≥99%; feed P95 <500ms.

Security checks pass; export/delete flows verified.

Analytics charts show full funnel.

Testing

Load tests (k6/Locust) for feed and generation endpoints.

Security linting (Bandit), dependency audit.

Codex Prompts

“Add Redis caching to the job feed endpoint with cache keys derived from filter params and user id, TTL 300s, cache-busting on new ingests.”

“Implement GDPR-compliant export as a ZIP with JSON + files; delete flow with 30-day soft delete and immediate OAuth token revocation.”

Risks

Over-caching stale data → tag cache with updated_at watermark per table.

Daily Cadence (per Sprint)

Mon: Kickoff, scope lock, create tickets, Codex prompts prepared.

Tue–Wed: Feature dev; PRs merged daily; staging deploy nightly.

Thu: E2E tests, accessibility/perf checks; bug bash.

Fri: Demo, metrics review, retro, next sprint planning.

Makefile Targets (copy-paste)
.PHONY: dev db.up db.migrate test api web worker lint typecheck seed

dev:                   ## run all services
\tdocker compose up --build

db.up:
\tdocker compose up -d db redis
\tpoetry run alembic upgrade head

db.migrate:
\tpoetry run alembic revision --autogenerate -m "$(m)"
\tpoetry run alembic upgrade head

api:
\tdocker compose up api

web:
\tdocker compose up web

worker:
\tdocker compose up worker

test:
\tdocker compose exec api pytest -q
\tnpm --prefix apps/web test

lint:
\truff check .
\teslint apps/web --max-warnings=0

typecheck:
\tmypy apps/api
\tts-node -v >/dev/null

seed:
\tpython infra/db/seed.py

VS Code launch.json (snippets)
{
  "version": "0.2.0",
  "configurations": [
    {"name":"Next.js dev","type":"node","request":"launch","runtimeExecutable":"npm","runtimeArgs":["run","dev"],"cwd":"${workspaceFolder}/apps/web","console":"integratedTerminal"},
    {"name":"API (Uvicorn)","type":"python","request":"launch","module":"uvicorn","args":["main:app","--reload","--host","0.0.0.0","--port","8000"],"cwd":"${workspaceFolder}/apps/api"},
    {"name":"Celery worker","type":"python","request":"launch","module":"celery","args":["-A","worker.app","worker","-l","INFO"],"cwd":"${workspaceFolder}/apps/workers"}
  ]
}

OpenAI Agents — Minimal Config (MVP)

Orchestrator

Goal: route intents {search_jobs, rank_jobs, tailor_resume, optimize_resume, track_update, suggest_tasks}

Tools: your REST endpoints above.

System Prompt (excerpt):
“You are the Vanta Orchestrator. For each user request or scheduled event, call exactly the minimal set of tools… Return JSON with action, inputs, and next_step.”

JobScout

Consumes search_prefs, calls provider clients (internal tools), writes job_postings, computes posting_enrichments.

ResumeTailor / Optimizer / TrackerCoach

Each bound to a small, typed toolset. Enforce JSON schema output.

QA & Acceptance per Sprint (mapping to Backlog)

S1: US1.1–1.3, US2.1–2.2 ✅

S2: US3.1–3.3, US6.1–6.3 ✅

S3: US4.1–4.3, US5.1–5.3, US13.1 ✅

S4: US7.1–7.3, US11.1–11.2, US12.1 ✅

S5: US8.1, US9.1–9.2, US12.2, US13.1 ✅

S6: US18.1–18.2, US15.1–15.2, US14.1 + polish ✅

Rollout Checklist (Beta)

 Seed test users & postings; sample digests.

 Legal/ToS, privacy policy, provider ToS review.

 Observability dashboards & alerts.

 Admin kill-switches for providers and agents.

 Backup & PITR verified.
