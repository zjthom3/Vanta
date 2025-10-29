# Vanta Master Planning Document

_Last updated: Oct 27, 2025_

## 1. Mission & Vision
- **Mission:** Automate and optimize every step of the job-hunting process with OpenAI Agents so users spend time interviewing, not tab-hopping.
- **Vision:** Deliver a trusted AI copilot that curates high-fit roles, produces ATS-ready materials, and keeps candidates on track with proactive guidance.

## 2. Strategic Goals & Success Metrics
- **Daily Feed Precision:** ≥70% Precision@10 confirmed relevant roles.
- **Activation:** ≥80% of new users finish onboarding within 10 minutes and schedule their first daily run.
- **Engagement:** Daily digest open rate ≥60%; weekly active days ≥3.
- **Application Outcomes:** +25% response rate uplift versus baseline; ≥2 interviews per 10 applications; ≥1 offer per 50 applications.
- **Reliability & Performance:** Daily search success ≥99%; P95 resume generation latency ≤12s; job feed P95 latency <500ms; queue failures <1%.

## 3. Core Product Scope
### 3.1 Daily AI Job Search
- Scheduled runs fetch roles from compliant providers, normalize postings, and rank them.
- Matching includes hard filters, embedding similarity, skill overlap, salary alignment, and freshness scoring.
- Users receive daily digests (web + email) with “why fit” rationales and salary info (estimated when missing).

### 3.2 Application Tracking & Pipeline
- One-click tracking from the feed creates applications with company, role, source link, and timestamps.
- Kanban pipeline (Prospect → Applied → Screen → Interview → Offer → Outcome) with drag-and-drop updates and audit logs.
- Events, notes, and attachments provide full context per application.

### 3.3 Follow-Up Task Suggestions
- Tracker/Coach agent surfaces Next Best Actions using stage transitions, aging, and calendar context.
- Tasks inbox supports prioritization, due dates, and completion tracking.

### 3.4 Resume Tailoring & Optimization
- Users upload a base resume; Resume Tailor agent generates job-specific resumes/CVs with JSON-schema outputs.
- Optimizer agent scores clarity/impact/ATS compliance, suggests inline rewrites, and surfaces keyword coverage.
- Export flows provide resume/cover letter downloads.

### 3.5 Outreach & Networking
- Integrations (LinkedIn, email) discover hiring managers and mutual contacts.
- Outreach agent drafts personalized intros/follow-ups with configurable tone and safeguards (draft status until user approval).

### 3.6 Notifications & Analytics
- In-app and email notifications cover digests, tasks, and nudges with unsubscribe controls.
- Event tracking captures search_run, posting_view, apply_click, resume_generated, outreach_sent, task_completed.
- Analytics dashboards report funnel metrics, outcome rates, and match QA inputs.

## 4. Technical Architecture & Agents
- **Services:** Next.js 15 (RSC) frontend, FastAPI backend, Celery workers, Postgres 15, Redis, S3-compatible storage.
- **Agents:** Orchestrator (intent routing), Job Scout (ingestion, normalization, ranking), Resume Tailor, Optimizer, Outreach, Tracker/Coach.
- **Tool Contracts:** REST endpoints such as `search_jobs`, `rank_postings`, `generate_resume`, `optimize_resume`, `update_application`, `suggest_tasks`.
- **Sequence (Daily Run):** Scheduler → Orchestrator → Job Scout → DB upsert → Digest delivery.
- **Observability:** Logs, traces, metrics tagged by `model_run_id`; alerts for failure rates and queue depth.

## 5. Data Model Overview
### 5.1 Conventions
- Snake_case naming, UUID primary keys (`gen_random_uuid()`), `created_at`/`updated_at` timestamps.
- Monetary values stored as integer cents with currency codes.
- Soft deletes via `deleted_at` where required; JSONB for flexible preferences; text[] arrays with GIN indexes.

### 5.2 Key Entities
- **users:** email auth, plan tiers, status, login metadata.
- **profiles:** headline, summary, skills array, location preferences, salary bands, job preference JSON.
- **integration_accounts:** OAuth tokens encrypted via KMS, scopes, expiry.
- **companies & job_postings:** canonical company registry and deduplicated postings keyed by `(source, source_id)` with normalization fields.
- **posting_enrichments:** per-user fit scores, factors JSON, salary estimates, rationale text.
- **search_prefs:** cron schedule, filters JSON, timezone, next run preview.
- **applications, resume_versions, outreach, events, tasks:** pipeline artifacts with lifecycle tracking, attachments, and enums for stage, channel, status.
- **model_runs & model_io:** agent execution traces with token counts and success flags.
- **audit_logs & user_events:** compliance audit trail and analytics ingestion.

### 5.3 Relationships (High-Level)
- Users own profiles, search preferences, applications, resume versions, tasks, notifications, integrations, model runs, and user events.
- Job postings link to companies; applications reference postings; outreach/events/artifacts hang off applications.
- Posting enrichments tie users to postings and drive feed personalization.

## 6. Backlog & Roadmap
### 6.1 Epic Summary
- **Epic 1:** Account & Onboarding — auth, guided onboarding, resume import.
- **Epic 2:** Profiles & Search Preferences — profile editing, saved searches, multi-persona (later).
- **Epic 3:** Job Ingestion & Normalization — provider clients, normalization, deduplication, freshness.
- **Epic 4:** Matching, Scoring & Explanations — hard filters, embeddings, rationale, salary estimation.
- **Epic 5:** Daily Search & Digest — scheduler, digest generation, delivery, snooze.
- **Epic 6–7:** Feed UI & Applications — feed cards, filters, hide/save, application creation, Kanban, timeline.
- **Epic 8–12:** Resume Studio, ATS optimization, follow-ups, tasks, documents.
- **Epic 13–20:** Notifications, analytics, security/compliance, billing, admin ops, performance, accessibility, enrichment.

### 6.2 MVP Backlog (P0 Focus)
| ID | Story | Estimate | Depends |
| --- | --- | --- | --- |
| US1.1 | Account creation (email/SSO) | 3 pts | — |
| US1.2 | Guided onboarding (4 steps) | 5 pts | US1.1 |
| US1.3 | Resume import & parse | 5 pts | US1.2 |
| US2.1 | Edit profile | 3 pts | US1.2 |
| US2.2 | Manage saved searches | 3 pts | US2.1 |
| US3.1 | Provider ingestion (1–2 providers) | 8 pts | — |
| US3.2 | Normalize posting | 5 pts | US3.1 |
| US3.3 | Deduplication | 3 pts | US3.2 |
| US4.1 | Hard filters | 3 pts | US2.2, US3.* |
| US4.2 | Embedding similarity match | 5 pts | US4.1 |
| US4.3 | Why-fit rationale | 5 pts | US4.2 |
| US5.1 | Scheduler per user | 3 pts | US2.2, US4.* |
| US5.2 | Digest generation | 3 pts | US5.1 |
| US5.3 | In-app/email delivery | 5 pts | US5.2 |
| US6.1 | Feed list (cards) | 5 pts | US4.* |
| US6.2 | Filters & sort | 3 pts | US6.1 |
| US6.3 | Hide/Save | 3 pts | US6.1 |
| US7.1 | Create application from card | 3 pts | US6.* |
| US7.2 | Kanban board | 5 pts | US7.1 |
| US7.3 | Timeline & notes | 3 pts | US7.2 |
| US8.1 | Generate tailored resume | 8 pts | US1.3, US7.1 |
| US9.1 | ATS score & issues | 5 pts | US8.1 |
| US9.2 | Inline suggestions & diffs | 5 pts | US9.1 |
| US11.1 | Suggest follow-ups (rules) | 5 pts | US7.* |
| US11.2 | Task inbox | 3 pts | US11.1 |
| US12.1 | Upload base resume | 3 pts | US1.3 |
| US12.2 | Export resume/CL | 3 pts | US8.1 |
| US13.1 | In-app notifications | 3 pts | US5.* |
| US14.1 | Event tracking | 3 pts | All |
| US15.1 | Token encryption KMS | 3 pts | Integrations |
| US15.2 | Data export/delete | 5 pts | — |
| US17.2 | Observability baseline | 3 pts | — |
| US18.1 | Caching & pagination | 5 pts | US6.* |
| US18.2 | Queue resilience | 3 pts | US5.* |

Total MVP size: ~135–150 pts for a 3–4 person team over ~6–8 weeks.

### 6.3 Post-MVP Highlights
- Salary estimation, snooze/pauses, feed detail drawer, outcome capture.
- Resume style controls and cover letters, outreach/contact integrations, calendar sync.
- Advanced analytics, billing/paywalls, admin console, rate limiting, accessibility, company enrichment.

## 7. Delivery & Execution Plan
### 7.1 Repo & Tooling
- Monorepo structure with `apps/` (web, api, workers), `packages/` (ui, types), and `infra/` (docker, db, ops).
- Docker Compose orchestrates Postgres, Redis, API, web, Celery worker, and optional MinIO.
- Makefile targets: `dev`, `db.up`, `db.migrate`, `test`, `lint`, `typecheck`, `seed`.
- Dev tooling: pre-commit, Ruff, Black, mypy, ESLint, VS Code launch/tasks for Next.js, Uvicorn, Celery.
- Environment variables stored in root `.env` (database, Redis, OpenAI key, S3, NextAuth).

### 7.2 Sprint Roadmap
- **Sprint 1:** Auth + onboarding flow, resume upload/parse, profiles, search preferences. Deliver onboarding wizard, parsers, cron preview, passing tests.
- **Sprint 2:** Provider ingestion, normalization, deduplication, feed UI with filters and hide/save. Import ≥100 postings with <3% duplicates.
- **Sprint 3:** Hard filters, embedding match, why-fit explanations, scheduler, digest generation/delivery, in-app notifications.
- **Sprint 4:** Applications (create, Kanban, timeline/notes), follow-up rules, task inbox, document upload baseline.
- **Sprint 5:** Resume tailoring, ATS optimization, inline suggestions, export flows, notification polish.
- **Sprint 6:** Performance, resilience, security/privacy, analytics instrumentation, beta readiness.

### 7.3 Release & Rollout
- **Release Plan:** Sprint sequencing aligns to MVP completion; Beta checklist includes seed data, admin guardrails, observability, legal/privacy review, kill switches, backup verification.
- **Definition of Ready:** Clear user value, designs or agreed low-fi, API contracts, non-functional requirements, dependencies identified, data model fields confirmed.
- **Definition of Done:** Acceptance criteria met, unit/integration tests ≥80%, observability hooks, security review, feature flags, docs + analytics events updated, staging demo and PM/Design/Eng sign-off.

## 8. Risks & Mitigations
- **Provider Compliance:** Use approved APIs, respect ToS, maintain kill switches.
- **PII Handling:** Encrypt tokens with KMS, enforce data export/delete within SLA, limit analytics PII.
- **Model Hallucination:** Provide provenance tags, confidence scores, and allow user review before sending outputs.
- **Over-Automation:** Offer manual overrides, undo, and user-configurable toggles.
- **Parsing Variability:** Include manual edit UI, store parser confidence per section, expand test fixture coverage.
- **Queue Reliability:** Implement retries, dead-letter queues, and monitor queue depth.

## 9. Next Actions
1. Bootstrap monorepo and Docker-based dev environment; configure linting, testing, and CI.
2. Implement SQLAlchemy models and Alembic migrations for core tables and enums; seed baseline data.
3. Deliver Sprint 1 scope end-to-end to validate onboarding, resume parsing, and search preference storage.
4. Prototype ingestion with one compliant provider to test normalization, dedup, and feed performance.
5. Formalize agent tool contracts and observability to prepare for orchestrated workflows.

