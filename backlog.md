EPIC 1 — Account & Onboarding

Goal: Get users activated within minutes with a usable profile and a scheduled daily search.
Success: ≥80% complete onboarding in ≤10 min; first daily run scheduled.

Dependencies: Auth, Profiles, Search Prefs, Resume Upload.

User Stories

US1.1 Create account (P0)
As a visitor, I create an account with email/SSO.
AC: Given valid email/SSO → When I sign up → Then account is created, verification sent, session established.

US1.2 Guided onboarding (P0)
As a new user, I’m guided through 4 steps: upload resume → confirm skills → set preferences → set daily time.
AC: Progress saved per step; can resume; default search prefs created.

US1.3 Resume import parse (P0)
As a user, I upload a resume and see extracted skills/experience prefilled.
AC: Supported formats PDF/DOCX; parse ≥ 80% sections; show review screen.

US1.4 Quickstart templates (P1)
As a user, I can pick a role template (e.g., CSM, PM) to seed prefs.
AC: Applying template updates filters with undo.

EPIC 2 — Profiles & Search Preferences

Goal: Accurate professional profile + reusable searches.
Success: Profile completion ≥70% for active users.

Dependencies: Onboarding.

User Stories

US2.1 Edit profile (P0)
Headline, summary, skills[], locations[], work auth, salary range.
AC: Validation; autosave; audit log entry on save.

US2.2 Manage saved searches (P0)
Create/update/delete named searches with filters JSON.
AC: Unique per user+name; cron/timezone set; next run preview.

US2.3 Multi-persona profiles (P2)
Switchable persona presets (e.g., CSM vs PM).
AC: Switching updates ranking weights.

EPIC 3 — Job Ingestion & Normalization

Goal: Pull fresh postings compliantly; de-dupe; normalize.
Success: Daily run success ≥99%; duplicates <3%.

Dependencies: Integrations, Companies, Job Postings.

User Stories

US3.1 Ingest via providers (P0)
As the system, I fetch jobs from providers (Greenhouse/Lever/Ashby/Workday/partner APIs).
AC: Provider client with retries/backoff; ToS respected; source+source_id stored.

US3.2 Normalize posting (P0)
Map title, location, remote, compensation (if present), tags.
AC: Minimum fields present; normalization rules covered by tests.

US3.3 Deduplication (P0)
Merge by (source, source_id) or semantic URL match.
AC: Unique constraint enforcement; idempotent upsert.

US3.4 Freshness scoring (P1)
Compute recency/freshness score for ranking.
AC: Materialized view updated nightly.

EPIC 4 — Matching, Scoring & Explanations

Goal: High-precision Top-N ranking with transparent “why fit.”
Success: Precision@10 ≥70% (user-confirmed relevant).

Dependencies: Profiles, Postings.

User Stories

US4.1 Hard filters (P0)
Eligibility, geo, remote, seniority filters applied first.
AC: No violating postings pass.

US4.2 Embedding similarity (P0)
Profile↔JD semantic score; skill overlap.
AC: Scores stored in posting_enrichments.fit_score; deterministic seed.

US4.3 Why-fit rationale (P0)
Show top features (skills, title sim, salary alignment).
AC: Human-readable bullet list; cached with posting+user pair.

US4.4 Salary estimation (P1)
Estimate range if missing; mark as “estimated.”
AC: Confidence band + provenance note.

EPIC 5 — Daily Search & Digest

Goal: Scheduled runs create a daily digest + push.
Success: ≥60% daily open rate; errors <1%.

Dependencies: Search Prefs, Matching, Notifications.

User Stories

US5.1 Scheduler (P0)
Cron per user/timezone; enqueue search:user_id.
AC: P95 job time < 2 min per user; failures retried.

US5.2 Digest generation (P0)
Compile Top-N (e.g., 20) new matches since last run.
AC: Excludes seen/hidden; includes why-fit + salary/eligibility.

US5.3 Delivery (in-app + email) (P0)
Inbox card + optional email summary with deep links.
AC: Email unsubscribe; notification record stored.

US5.4 Snooze/pauses (P1)
Pause all runs for X days.
AC: Resume date shown.

EPIC 6 — Job Feed & Search UI

Goal: Sleek feed with filters, save, hide, quick actions.
Success: Time-to-apply < 2 min from feed.

Dependencies: Matching, Applications.

User Stories

US6.1 Feed list (P0)
Job cards (title/company/tags/why fit/actions).
AC: Infinite scroll; loading skeletons; keyboard nav.

US6.2 Filters & sort (P0)
Filter by seniority, comp band, remote, provider; sort by score/recency.
AC: URL-synced state.

US6.3 Hide/Save (P0)
Hide postings permanently; save for later.
AC: Hidden excluded from future digests.

US6.4 Detail drawer (P1)
Right-side drawer with full JD, eligibility, salary, company info.
AC: One-click “Track” & “Tailor Resume.”

EPIC 7 — Application Tracking (Pipeline)

Goal: Visual Kanban; drag-drop across stages; history.
Success: ≥90% of apps created via one click from feed.

Dependencies: Applications, Audit Logs, Tasks.

User Stories

US7.1 Create application (P0)
From job card → “Track.”
AC: Application row created with prospect stage; source label.

US7.2 Kanban board (P0)
Columns: Prospect → Applied → Screen → Interview → Offer → Outcome.
AC: Drag-drop updates stage, writes audit log.

US7.3 Timeline & notes (P0)
Application detail view with notes & attachments.
AC: Rich text; versioned edits.

US7.4 Outcome capture (P1)
Accepted/Rejected with reason tags.
AC: Reports use outcomes.

EPIC 8 — Resume Tailoring (Generation)

Goal: One-click, ATS-ready resume per posting.
Success: Median ATS score uplift ≥ +15.

Dependencies: Resume Versions, Job Posting, Agents.

User Stories

US8.1 Generate tailored resume (P0)
As a user, I click “Tailor” to create a resume version aligned to the posting.
AC: Output JSON schema + downloadable PDF/DOCX; P95 ≤ 12s.

US8.2 Style controls (P1)
Concise/impactful/technical tone toggles.
AC: Diff view vs base.

US8.3 Cover letter (optional) (P1)
Generate role-specific cover letter.
AC: Stored in artifacts.

EPIC 9 — Resume Optimization (Analysis)

Goal: Score, pinpoint fixes, apply one-click rewrites.
Success: ≥70% users apply ≥1 suggestion.

Dependencies: Resume Versions, Optimizer Agent.

User Stories

US9.1 ATS score & issues (P0)
Show score with prioritized checklist.
AC: Issues grouped (clarity, impact, keywords).

US9.2 Inline suggestions (P0)
Accept/reject edits per section; before/after diff.
AC: Accept writes new version; audit logged.

US9.3 Keyword coverage (P1)
Heatmap of JD→resume coverage.
AC: Missing “must-have” flagged.

EPIC 10 — Outreach & LinkedIn

Goal: Identify people + draft personalized outreach.
Success: Outreach send rate ≥40% for applied apps.

Dependencies: LinkedIn integration, Outreach table.

User Stories

US10.1 Discover contacts (P1)
Hiring manager/recruiter suggestions (where API permits).
AC: Show 1–3 contacts with titles and profiles.

US10.2 Draft outreach (P1)
Personalized message under 700 chars with hooks.
AC: Uses profile & JD; editable; saved as draft.

US10.3 Send status tracking (P2)
Mark sent/replied manually or via webhook.
AC: Status funnel visible.

EPIC 11 — Tasks & Next-Best-Actions (Coach)

Goal: Keep momentum via smart, timed nudges.
Success: ≥3 NBAs completed/user/week.

Dependencies: Applications, Events, Calendar (opt), Tasks.

User Stories

US11.1 Suggest follow-ups (P0)
Generate tasks when stages/aging match patterns (e.g., 5 days after applied).
AC: Tasks created with due dates; explain “why.”

US11.2 Task inbox (P0)
Do/Defer/Done quick triage; reminders.
AC: Keyboard actions; due-soon badge.

US11.3 Calendar sync (optional) (P1)
Detect interviews from email/calendar, create events/tasks.
AC: Two-way link to app event.

EPIC 12 — Documents & Artifacts

Goal: Secure storage of generated files with versions.
Success: 0% broken links; virus-scan pass 100%.

Dependencies: S3/GCS, Artifacts.

User Stories

US12.1 Upload base resume (P0)
Store file + parsed JSON.
AC: Hash stored; mime validated; size limit enforced.

US12.2 Export resume/CL (P0)
Download PDF/DOCX.
AC: Filenames standardized.

EPIC 13 — Notifications & Digest Delivery

Goal: Timely in-app/email notifications.
Success: Bounce <1%; unsubscribe honored.

Dependencies: Notifications, Email provider.

User Stories

US13.1 In-app notifications (P0)
New digest, task due, resume ready.
AC: Mark read/unread; persisted list.

US13.2 Email summary (P0)
Daily digest email with top 10; deep links.
AC: Per-user toggle; unsubscribe link.

EPIC 14 — Analytics & Reporting

Goal: Product + user outcome metrics.
Success: Dashboards for funnel and outcomes.

Dependencies: User events, Model runs.

User Stories

US14.1 Event tracking (P0)
Track search_run, posting_view, apply_click, resume_generated, task_completed.
AC: PII scrubbed; schema documented.

US14.2 Outcome report (P1)
Interviews/applications, offers/50 apps per user.
AC: Date range filters; CSV export.

US14.3 Match precision QA (P1)
Collect “relevant/not” feedback to tune ranking.
AC: Feedback pipeline updates weights.

EPIC 15 — Security, Privacy & Compliance

Goal: Protect PII and tokens; user trust.
Success: No P0 security issues; data export/delete works.

Dependencies: All.

User Stories

US15.1 Token encryption (P0)
Store OAuth tokens encrypted with KMS; rotate keys.
AC: Vaulted; decrypt only in worker.

US15.2 Data export/delete (P0)
Self-serve export and account deletion.
AC: Hard-delete tokens; soft-delete data with 30-day window; notify user.

US15.3 RBAC admin (P1)
Admin UI with least-privilege roles.
AC: Actions logged.

EPIC 16 — Billing & Plans (Optional for Private Beta)

Goal: Monetize post-beta.
Dependencies: Subscriptions.

User Stories

US16.1 Stripe integration (P1)
Subscribe/upgrade/cancel; proration.
AC: Webhooks reconcile state.

US16.2 Paywalled features (P1)
Limit saved searches, resume versions for Free tier.
AC: Friendly upsell.

EPIC 17 — Admin & Ops

Goal: Operate the product safely.
Dependencies: Audit logs, Monitoring.

User Stories

US17.1 Admin console (P1)
Search users, reset runs, view errors.
AC: Access restricted; actions logged.

US17.2 Observability (P0)
Logs, traces, metrics; model latency dashboards.
AC: Alerts for failure rates, queue depth.

EPIC 18 — Performance & Reliability

Goal: Fast, reliable UX.
Dependencies: Infra.

User Stories

US18.1 Caching & pagination (P0)
Server-side pagination; Redis cache for feed.
AC: P95 feed < 500ms.

US18.2 Queue resilience (P0)
Retry & dead-letter queues for providers.
AC: Message visibility timeout tuned; metrics visible.

US18.3 Rate limiting (P1)
Per-user/per-IP API throttles.
AC: Friendly errors; no provider bans.

EPIC 19 — Accessibility & Internationalization

Goal: Inclusive, future-proof UI.
Dependencies: UI.

User Stories

US19.1 WCAG 2.1 AA (P1)
Keyboard navigation, contrast, reduced motion.
AC: Lighthouse ≥ 90 accessibility.

US19.2 i18n plumbing (P2)
Locale files support; dates/currency formats.
AC: English default; structure present.

EPIC 20 — Company Intelligence (Enrichment)

Goal: Add company context (size, industry).
Dependencies: Companies.

User Stories

US20.1 Company enrichment (P1)
Pull domain/size/industry via partner API.
AC: Rate-limited; cached; shown on card.

MVP Backlog (P0 Only)
ID	Story	Estimate	Depends
US1.1	Account creation (email/SSO)	3 pts	—
US1.2	Guided onboarding (4 steps)	5 pts	US1.1
US1.3	Resume import & parse	5 pts	US1.2
US2.1	Edit profile	3 pts	US1.2
US2.2	Manage saved searches	3 pts	US2.1
US3.1	Provider ingestion (1–2 providers)	8 pts	—
US3.2	Normalize posting	5 pts	US3.1
US3.3	Deduplication	3 pts	US3.2
US4.1	Hard filters	3 pts	US2.2, US3.*
US4.2	Embedding similarity match	5 pts	US4.1
US4.3	Why-fit rationale	5 pts	US4.2
US5.1	Scheduler per user	3 pts	US2.2, US4.*
US5.2	Digest generation	3 pts	US5.1
US5.3	In-app/email delivery	5 pts	US5.2
US6.1	Feed list (cards)	5 pts	US4.*
US6.2	Filters & sort	3 pts	US6.1
US6.3	Hide/Save	3 pts	US6.1
US7.1	Create application from card	3 pts	US6.*
US7.2	Kanban board	5 pts	US7.1
US7.3	Timeline & notes	3 pts	US7.2
US8.1	Generate tailored resume	8 pts	US1.3, US7.1
US9.1	ATS score & issues	5 pts	US8.1
US9.2	Inline suggestions & diffs	5 pts	US9.1
US11.1	Suggest follow-ups (rules)	5 pts	US7.*
US11.2	Task inbox	3 pts	US11.1
US12.1	Upload base resume	3 pts	US1.3
US12.2	Export resume/CL	3 pts	US8.1
US13.1	In-app notifications	3 pts	US5.*
US14.1	Event tracking	3 pts	All
US15.1	Token encryption KMS	3 pts	Integrations
US15.2	Data export/delete	5 pts	—
US17.2	Observability baseline	3 pts	—
US18.1	Caching & pagination	5 pts	US6.*
US18.2	Queue resilience	3 pts	US5.*

Total MVP ~135–150 pts (team of 3–4 over ~6–8 weeks).

Post-MVP Backlog Highlights (P1)

US4.4 Salary estimation

US5.4 Snooze/pauses

US6.4 Detail drawer

US7.4 Outcome capture

US8.2 Style controls / US8.3 Cover letters

US10.1–10.2 Outreach & contacts

US11.3 Calendar sync

US14.2 Outcome reports, US14.3 Match QA loop

US16.1–16.2 Billing & paywalls

US17.1 Admin console

US18.3 Rate limiting

US19.1 Accessibility AA

US20.1 Company enrichment

Definition of Ready (DoR)

Clear user problem & value.

Designs/wireframes available or agreed low-fi.

API contracts drafted.

Non-functional requirements (perf, security) listed.

Dependencies identified; data model fields confirmed.

Definition of Done (DoD)

All ACs met; unit/integration tests ≥80% for module.

Observability: logs/metrics/traces.

Security review passed; feature flags where needed.

Docs updated; analytics events firing and verified.

Demo in staging; sign-off from PM/Design/Eng.

Release Plan (High-Level)

Sprint 1: Auth + Onboarding + Resume Upload/Parse + Profiles + Search Prefs

Sprint 2: Ingestion + Normalization + Dedup + Hard Filters + Feed (basic)

Sprint 3: Embedding Match + Why-Fit + Scheduler + Digest Delivery

Sprint 4: Applications (Create + Kanban + Notes) + Tasks (Rules + Inbox)

Sprint 5: Resume Tailor + Optimization (Score + Inline Edits) + Notifications

Sprint 6: Perf/Resilience + Security + Analytics + Polishing + Beta
