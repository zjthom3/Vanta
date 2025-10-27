AI Job Search — Product Requirements Document (PRD)

Last updated: Oct 27, 2025 (America/Toronto)

1) Overview & Purpose

Mission: Automate and optimize every step of the job-hunting process with OpenAI Agents—finding high-fit roles daily, tailoring applications, managing pipelines, and prompting smart follow-ups—so users spend time interviewing, not tab-hopping.

Goals

Deliver a daily, personalized job feed with high precision.

Auto-generate ATS-ready resumes/CVs and outreach in one click.

Track every application and surface next best actions that move offers forward.

Non-Goals (v1)

Automated application submission to sites that prohibit automation.

Negotiation copilot (planned future enhancement).

Multi-user collaboration (recruiter teams) beyond basic share/export.

2) Target Audience

Primary: Mid-career professionals (CSM, PM, Eng, Data, Design, Ops) seeking remote/hybrid roles in North America.

Secondary: Early-career and career-switchers who benefit from guided, automated application workflows.

Key Needs

Save time; reduce cognitive load.

Increase response/interview rates with tailored materials.

Stay organized with an end-to-end pipeline view and proactive nudges.

3) Core Features & User Stories
3.1 Daily AI Job Search

F1.1 Schedule & Search: System runs daily at user-set time to fetch roles from major boards/ATS aggregators via APIs (e.g., Greenhouse/Lever/Ashby/Workday connectors or compliant search APIs).

F1.2 Matching & Ranking: Agent scores roles against profile (skills, experience, preferences), explains “why fit,” and estimates salary if missing.

F1.3 Digest & Feed: New opportunities summarized in a clean dashboard with filters (seniority, compensation band, remote eligibility).

User Stories

As a user, I set my search schedule (e.g., 5:00 AM daily) and filters so I wake up to a curated list.

As a user, I want explanations for each match so I trust the recommendations.

3.2 Application Tracking

F2.1 Auto-Logging: One-click “Track” on any job saves posting, notes, and status.

F2.2 Pipeline: Columns (Prospect → Applied → Screen → Interview → Offer → Outcome) with drag-and-drop.

F2.3 Events & Notes: Interviews, recruiter calls, task history, attachments.

User Stories

As a user, I want applications auto-logged with company, role, source link, and date applied.

As a user, I want a visual pipeline to see progress and bottlenecks.

3.3 Follow-Up Task Suggestions

F3.1 Next Best Action (NBA): Agent suggests actions (e.g., “Follow up with recruiter,” “Send value add note,” “Prep with 3 role-specific stories”).

F3.2 Timing Intelligence: Uses application aging, stage patterns, and calendar to surface reminders.

User Stories

As a user, I receive time-boxed, high-impact suggestions to keep momentum.

3.4 Automated Resume & CV Generation

F4.1 Tailored Drafts: Given a job posting, the Resume Agent produces ATS-ready resume + optional CV variant aligned to keywords and responsibilities.

F4.2 Content Controls: Strength-meter, style toggles (concise/impactful/technical), quantify-impact helper.

User Stories

As a user, I upload a base resume once and get job-specific versions in one click.

3.5 LinkedIn Outreach Integration

F5.1 Employee Discovery: Identify hiring managers/recruiters and mutuals (via OAuth-based integration).

F5.2 Outreach Drafting: Personalized intro/follow-up notes with conversation hooks and calibrated tone.

User Stories

As a user, I want ready-to-send outreach that references my strengths and the role’s needs.

3.6 Resume Optimization

F6.1 Analysis & Score: AI returns clarity/impact/ATS compliance score with prioritized fixes.

F6.2 Rewrite Suggestions: Inline edits with acceptance toggles; before/after diff view.

4) Technical Architecture
4.1 Agent System (OpenAI Agents)

Agents

Orchestrator Agent — routes intents: {search_jobs, rank_jobs, tailor_resume, optimize_resume, outreach, track_update, suggest_tasks}

Job Scout Agent — sources roles, normalizes postings, enriches salary/location/eligibility, ranks & explains fit.

Resume Tailor Agent — generates ATS-ready resume/CV from base + job description; supports JSON schema IO for sections.

Optimizer Agent — evaluates resume, produces scorecard + diffs.

Outreach Agent — identifies prospects and drafts messages.

Tracker/Coach Agent — updates pipeline state and computes Next Best Actions.

Key Tools/Functions (exposed to Agents)

search_jobs(query, filters)

get_posting_details(url | ats_id)

rank_postings(profile, postings[]) -> ranked[]

generate_resume(profile, job_posting)

optimize_resume(resume_doc)

find_linkedin_contacts(company, role)

draft_outreach(profile, contact, role, stage)

update_application(job_id, stage, metadata)

suggest_tasks(applications[], calendar[])

Sequence (Daily Run)

sequenceDiagram
  autonumber
  participant Scheduler
  participant Orchestrator
  participant JobScout
  participant DB
  participant User

  Scheduler->>Orchestrator: Trigger daily job search (cron)
  Orchestrator->>JobScout: search_jobs(filters, profile)
  JobScout->>JobScout: normalize, enrich, score, explain
  JobScout-->>Orchestrator: ranked_postings[]
  Orchestrator->>DB: upsert new postings, link to user
  Orchestrator-->>User: Daily digest (web + email push)

4.2 Services & Integrations

Job Data: Compliant APIs/feeds (e.g., Greenhouse/Lever/Ashby/Workday connectors via partner APIs; general job search APIs where ToS allows).

LinkedIn: OAuth + official API endpoints where permitted for people search/IDs; never scrape.

Email/Calendar (optional v1.1): Gmail/Outlook/Calendar read for interview detection and task timing.

Storage: Postgres (primary), S3/GCS for documents.

Embedding (optional v1): For JD/resume semantic matching (OpenAI text-embedding).

Auth: OAuth 2.0 + email/password, WebAuthn optional.

Hosting: Containerized (Docker) on managed PaaS (Render/Heroku/Fly) or K8s (EKS/GKE).

Background Jobs: Queue (RQ/Celery/Sidekiq-style) for scheduled search, generation, and webhooks.

4.3 Security & Compliance

PII encryption at rest (KMS) + in transit (TLS 1.2+).

Secret management (Vault/Parameter Store).

Role-based access (RBAC) for internal admin tools.

Data retention controls; user export/delete (GDPR/CCPA ready).

Audit log for all agent-writes and template generations.

Rate limits and circuit breakers for external APIs.

5) Data Model Overview
erDiagram
  USER ||--o{ PROFILE : has
  USER ||--o{ INTEGRATION_ACCOUNT : connects
  USER ||--o{ APPLICATION : tracks
  USER ||--o{ RESUME_VERSION : owns
  USER ||--o{ TASK : has
  COMPANY ||--o{ JOB_POSTING : offers
  JOB_POSTING ||--o{ APPLICATION : referencedBy
  APPLICATION ||--o{ OUTREACH : includes
  APPLICATION ||--o{ EVENT : includes

Key Entities (v1)

User: id, email, auth_provider, created_at, plan_tier

Profile: user_id(FK), headline, summary, skills[], years_experience, locations[], salary_min, salary_max, work_auth, job_preferences{}

IntegrationAccount: user_id, provider, oauth_token_ref, scopes[]

Company: id, name, domain, linkedin_company_id, size_range, industry

JobPosting: id, company_id, title, jd_raw, jd_clean, source, source_id, url, location, remote_flag, salary_min, salary_max, currency, eligibility_notes, normalized_tags[]

Application: id, user_id, job_posting_id, stage(enum: prospect|applied|screen|interview|offer|rejected|accepted), status_notes, created_at, updated_at

ResumeVersion: id, user_id, base_flag, job_posting_id?, doc_url, sections_json, ats_score, keywords[], diff_from_base

Outreach: id, application_id, contact_name, contact_role, contact_profile_url, message_body, channel(enum: linkedin|email), status(enum: draft|sent|replied)

Event: id, application_id, type(enum: interview|phone_screen|assessment|deadline), start_at, end_at, notes

Task: id, user_id, application_id?, title, nudge_type(enum: follow_up|research|prep), due_at, completed_at

ModelRun: id, agent, tool, input_ref, output_ref, tokens_in, tokens_out, latency_ms, success_flag

AuditLog: id, actor(enum: user|agent|system), action, entity, entity_id, timestamp, metadata

Indexes

job_posting(source, source_id) unique

GIN on Profile.skills[] / JobPosting.normalized_tags[]

Partial index on Application(stage) for pipeline queries

6) UX / UI Principles

Aesthetic: Apple/Tesla/OpenAI—clean typography, ample white space, soft gradients, tasteful motion.

Foundations

Typography: Large, legible headings; compact body; consistent rhythm.

Motion: Micro-interactions (hover, drag, save) at 120–200ms; easing for perceived speed.

Colors: Minimal neutral palette with an accent color for status and CTAs.

Components:

Job Cards: title, company, badge chips, fit-reason, quick actions (Track, Tailor).

Pipeline Board: columns with counts; drag-and-drop with haptic feedback.

Resume Studio: left sidebar sections, central diff editor, right panel scorecard.

Outreach Composer: recipient chips, templates, personalization hints.

Tasks: inbox with “Do, Defer, Delegate” quick triage.

Key Screens

Onboarding: import resume → set preferences → connect LinkedIn → set daily time.

Dashboard: Today’s matches, pipeline snapshot, tasks due, quick actions.

Job Feed: Filters, saved searches, explanation modals (“Why this role”).

Application Detail: timeline, attached docs, outreach, tasks, events.

Resume Studio: live ATS score, keyword coverage, one-click quantification.

Outreach: contact discovery, draft variants, compliance checklist.

Settings: integrations, privacy, export/delete data.

Accessibility

WCAG 2.1 AA; keyboard navigable; reduced motion option; color-contrast safe.

7) Success Metrics

Acquisition/Activation

A1: % users completing onboarding within 10 minutes.

A2: Time to first tracked application (TTA) < 24h.

Quality

Q1: Match Precision @Top-10 ≥ 70% (user-confirmed relevant).

Q2: Resume ATS score uplift median ≥ +15 points vs. base.

Engagement

E1: Daily job open rate ≥ 60%; weekly active days ≥ 3.

E2: Average NBAs completed/user/week ≥ 3.

Outcome

O1: Response rate uplift vs. user’s baseline ≥ +25%.

O2: Interview rate per 10 applications ≥ 2.0.

O3: Offer rate per 50 applications ≥ 1.0.

Reliability

R1: Daily search completion success ≥ 99%.

R2: P95 resume generation latency ≤ 12s.

8) Technical Details (Implementable)
8.1 API Surface (example, REST+Webhooks)

POST /v1/search/runs — trigger search (admin/batch)

GET /v1/jobs?filters=... — paginated feed

POST /v1/applications — create from posting

PATCH /v1/applications/{id} — update stage/notes

POST /v1/resumes/generate — {profile_id, job_posting_id}

POST /v1/resumes/optimize — {resume_id}

POST /v1/outreach/draft — {application_id, contact}

POST /v1/tasks/suggest — derive NBAs

Webhooks: /webhooks/integrations/* for ATS/LinkedIn events

8.2 Schedulers & Queues

Cron: user-specific schedule → enqueue search:user_id

Workers: search, generate_resume, optimize_resume, outreach, suggest_tasks

Retry & DLQ for transient external failures

8.3 Matching/Reranking (baseline)

Hard filters: eligibility, location, seniority.

Semantic match: embeddings(profile ⟷ JD).

Rerank features: skill overlap, title similarity, salary band fit, company size preference, recency.

Explainability: expose top features as “Why this fits.”

8.4 Document Generation

JSON-schema controlled outputs for resume sections:

{
  "summary": "...",
  "skills": ["..."],
  "experience": [{"company":"...", "role":"...", "bullets":["..."]}],
  "education": [{"school":"...", "degree":"..."}],
  "certifications": ["..."],
  "keywords_covered": ["..."],
  "ats_score": 86
}

9) Future Enhancements

Offer Maximizer: negotiation prep, alternative packages, counter-offer drafts.

Interview Copilot: calendar-aware prep packs, mock interviews, STAR library.

Market Intel: comp ranges by geo/company/level; trend dashboards.

Multi-Persona Profiles: switch personas (CSM vs PM) with separated resumes/feeds.

Referrals Graph: map 2nd-degree contacts and draft intro asks.

Multi-Region Compliance: EU/UK job boards and data residency controls.

10) Risks & Mitigations

API/ToS Compliance: Use approved APIs; no scraping. Mitigation: vendor partnerships; ToS reviews; kill-switches.

Data Sensitivity: Resumes and outreach contain PII. Mitigation: encryption, scoped tokens, explicit consent flows.

Model Hallucination: Incorrect salary/eligibility. Mitigation: provenance tags, confidence scores, user-visible citations where available.

Over-automation Fatigue: Users want control. Mitigation: “Review before send,” granular toggles, undo.

11) Rollout Plan (High-Level)

M0 (2 wks): Skeleton app, auth, Postgres schema, manual import of resume, basic job feed via one API, track apps.

M1 (3–4 wks): Orchestrator + Job Scout; daily search; resume tailor MVP; pipeline board; tasks.

M2 (3–4 wks): Outreach integration; optimizer scoring; explanations; performance hardening; metrics.

12) Appendix — Acceptance Criteria (Samples)

Daily Search

Given a user with preferences, when the scheduler runs, then the system stores ≥10 unique postings if available, each with fit reason and (if present) salary.

Resume Tailoring

Given a job posting linked to an application, when “Generate Resume” is clicked, then a downloadable resume version with ≥80% keyword coverage is created in ≤12s P95.

Pipeline

Dragging an application between columns updates stage, creates an AuditLog entry, and triggers Task suggestions when entering screen or interview.

Outreach

When a user chooses a contact, a draft < 700 chars with personalization tokens is produced, and status is draft until user confirmation.

13) Appendix — Monitoring & Analytics

Product Analytics: Amplitude event streams (search_run, posting_view, apply_click, resume_generated, outreach_sent, task_completed).

Observability: Traces tagged by ModelRun.id, external API latencies, error budgets.

Privacy: Analytics events scrub PII by default; config-based allow-list for necessary fields.
