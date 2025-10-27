0) Conventions

snake_case tables/columns, singular table names.

Primary keys: id UUID DEFAULT gen_random_uuid().

Timestamps: created_at, updated_at (timestamptz).

Soft delete (select tables): deleted_at timestamptz NULL.

Monetary: integer cents (amount_cents int4, currency char(3)).

Arrays: text[] with GIN; JSON: jsonb.

Multi-tenant: user-scoped but global catalogs (companies, job_postings).

1) ER Diagram (High-Level)
erDiagram
  USER ||--o{ PROFILE : has
  USER ||--o{ INTEGRATION_ACCOUNT : connects
  USER ||--o{ SEARCH_PREF : sets
  USER ||--o{ APPLICATION : tracks
  USER ||--o{ RESUME_VERSION : owns
  USER ||--o{ TASK : has
  USER ||--o{ NOTIFICATION : receives
  USER ||--o{ MODEL_RUN : triggers
  USER ||--o{ USER_EVENT : generates

  COMPANY ||--o{ JOB_POSTING : offers
  JOB_POSTING ||--o{ APPLICATION : referencedBy
  APPLICATION ||--o{ OUTREACH : includes
  APPLICATION ||--o{ EVENT : includes
  APPLICATION ||--o{ ARTIFACT : attaches

  JOB_POSTING ||--o{ POSTING_ENRICHMENT : enrichedBy

  MODEL_RUN ||--o{ MODEL_IO : records
  AUDIT_LOG ||--|| USER : actor (nullable system)

2) Enums
create type stage_enum as enum ('prospect','applied','screen','interview','offer','rejected','accepted');
create type outreach_channel_enum as enum ('linkedin','email');
create type outreach_status_enum as enum ('draft','queued','sent','replied','bounced');
create type event_type_enum as enum ('interview','phone_screen','assessment','deadline','offer_call','other');
create type task_type_enum as enum ('follow_up','research','prep','apply','referral','thank_you');
create type priority_enum as enum ('low','normal','high','urgent');
create type provider_enum as enum ('linkedin','gmail','outlook','google_calendar','greenhouse','lever','ashby','workday','indeed','other');
create type plan_tier_enum as enum ('free','pro','team','enterprise');
create type agent_enum as enum ('orchestrator','job_scout','resume_tailor','optimizer','outreach','tracker_coach');
create type status_enum as enum ('active','inactive');

3) Core Tables
3.1 users
column	type	constraints
id	uuid	pk
email	citext	unique not null
password_hash	text	null if SSO
auth_provider	text	null
plan_tier	plan_tier_enum	default 'free'
status	status_enum	default 'active'
last_login_at	timestamptz	
created_at / updated_at	timestamptz	not null

Indexes: unique(email)

3.2 profiles

User professional profile & preferences.

column	type	constraints
id	uuid	pk
user_id	uuid	fk → users(id) on delete cascade
headline	text	
summary	text	
skills	text[]	GIN
years_experience	int	
locations	text[]	preferred geos
work_auth	text	e.g., "US citizen; Canadian resident"
salary_min_cents / salary_max_cents	int	
remote_only	bool	default true
job_preferences	jsonb	{levels, functions, industries}
created_at / updated_at	timestamptz	

Index: GIN on skills, job_preferences

3.3 integration_accounts

OAuth tokens & scopes.

column	type	constraints
id	uuid	pk
user_id	uuid	fk → users(id) on delete cascade
provider	provider_enum	not null
external_user_id	text	
scopes	text[]	
token_encrypted	text	KMS-sealed
refresh_token_encrypted	text	
expires_at	timestamptz	
created_at / updated_at	timestamptz	

Unique: (user_id, provider)

3.4 companies

Canonical company registry.

column	type	constraints
id	uuid	pk
name	text	not null
domain	citext	unique nullable
linkedin_company_id	text	unique nullable
size_range	text	
industry	text	
created_at / updated_at	timestamptz	

Index: lower(name)

3.5 job_postings

Normalized job postings (de-duplicated by source).

column	type	constraints
id	uuid	pk
company_id	uuid	fk → companies(id)
source	provider_enum	e.g., greenhouse/lever/indeed/other
source_id	text	nullable but unique with source
url	text	not null
title	text	not null
jd_raw	text	
jd_clean	text	
location	text	
remote_flag	bool	default false
eligibility_notes	text	
salary_min_cents / salary_max_cents	int	nullable
currency	char(3)	default 'USD'
normalized_tags	text[]	skills/keywords
posted_at	timestamptz	
scraped_at	timestamptz	
created_at / updated_at	timestamptz	

Unique: (source, source_id) (when source_id not null)
Indexes: GIN on normalized_tags, trigram on title

3.6 posting_enrichments

System-computed fit & explanations per user & posting.

column	type
id	uuid pk
user_id	uuid fk users
job_posting_id	uuid fk job_postings on delete cascade
fit_score	int check (between 0..100)
fit_factors	jsonb (top features w/ weights)
salary_estimate_cents	int nullable
rationale	text
created_at	timestamptz

Unique: (user_id, job_posting_id)

3.7 applications

User’s pipeline items.

column	type
id	uuid pk
user_id	uuid fk users on delete cascade
job_posting_id	uuid fk job_postings
stage	stage_enum default 'prospect'
status_notes	text
source_label	text (e.g., “Daily Digest”, “Manual add”)
applied_at	timestamptz
updated_at	timestamptz
created_at	timestamptz

Indexes: (user_id, stage), (user_id, job_posting_id) unique

3.8 resume_versions

Generated & user-authored doc versions.

column	type
id	uuid pk
user_id	uuid fk users on delete cascade
base_flag	bool default false
job_posting_id	uuid fk job_postings nullable
doc_url	text (S3/GCS)
sections_json	jsonb (schema-controlled)
ats_score	int
keywords	text[]
diff_from_base	jsonb
created_at / updated_at	timestamptz

Index: (user_id, base_flag) partial where base_flag = true

3.9 outreach

Contact drafts & statuses.

column	type
id	uuid pk
application_id	uuid fk applications on delete cascade
contact_name	text
contact_role	text
contact_profile_url	text
channel	outreach_channel_enum
status	outreach_status_enum default 'draft'
message_body	text
sent_at	timestamptz
created_at / updated_at	timestamptz
3.10 events

Application-related calendar events.

column	type
id	uuid pk
application_id	uuid fk applications on delete cascade
type	event_type_enum
start_at / end_at	timestamptz
location	text
notes	text
created_at / updated_at	timestamptz
3.11 tasks

Next-Best-Actions (NBA).

column	type
id	uuid pk
user_id	uuid fk users on delete cascade
application_id	uuid fk applications nullable
title	text not null
nudge_type	task_type_enum
priority	priority_enum default 'normal'
due_at	timestamptz
completed_at	timestamptz nullable
created_at / updated_at	timestamptz

Indexes: (user_id, completed_at nulls first), (due_at)

3.12 artifacts

Generated files (resumes, cover letters, notes).

column	type
id	uuid pk
application_id	uuid fk applications on delete cascade
kind	text (resume_pdf, resume_docx, cover_letter, notes)
storage_url	text
metadata	jsonb (mime, size, hash)
created_at	timestamptz
3.13 search_prefs

Saved searches & schedules.

column	type
id	uuid pk
user_id	uuid fk users on delete cascade
name	text
filters	jsonb (titles, skills[], levels, industries, salary range, remote_only, geo)
schedule_cron	text (e.g., "0 5 * * *")
timezone	text
last_run_at	timestamptz
created_at / updated_at	timestamptz

Unique: (user_id, name)

3.14 notifications

In-app & email pushes.

column	type
id	uuid pk
user_id	uuid fk users
kind	text (daily_digest, task_due, status_update, resume_ready)
payload	jsonb
read_at	timestamptz
created_at	timestamptz
3.15 model_runs & model_io

Traceability for agent actions.

model_runs

column	type
id	uuid pk
user_id	uuid fk users
agent	agent_enum
tool	text
input_ref	text (fk or opaque)
output_ref	text
tokens_in	int
tokens_out	int
latency_ms	int
success_flag	bool
created_at	timestamptz

model_io

column	type
id	uuid pk
model_run_id	uuid fk model_runs on delete cascade
role	text (system
content	jsonb
created_at	timestamptz
3.16 audit_logs

Every state-changing action.

column	type
id	uuid pk
actor_type	text ('user','agent','system')
actor_id	uuid nullable
action	text
entity	text
entity_id	uuid
diff	jsonb (before/after)
ip	inet nullable
created_at	timestamptz

Index: (entity, entity_id, created_at)

3.17 Billing (Optional v1)

subscriptions (user_id, plan_tier, status, renews_at, cancel_at, provider_customer_id, provider_sub_id, created_at)

4) Search & Matching Aids

Full-text: pg_trgm on job_postings.title, companies.name

Tag/skill overlap: GIN on arrays (profiles.skills, job_postings.normalized_tags)

Materialized views (optional):

mv_recent_postings (last 14 days with computed freshness score)

mv_user_fit_scores (denormalized top-N for dashboard)

5) JSON Schemas
5.1 Resume Sections (stored in resume_versions.sections_json)
{
  "summary": "Customer Success leader ...",
  "skills": ["Customer Success","AI Systems","Django","SQL"],
  "experience": [
    {
      "company": "TechSmart",
      "role": "Customer Success Manager",
      "start": "2022-03",
      "end": null,
      "bullets": [
        "Drove 35% YoY retention uplift across 161 districts",
        "Built AI workflows for onboarding; -28% TTV"
      ]
    }
  ],
  "education": [{"school":"...", "degree":"...", "year":"..."}],
  "certifications": ["PMP","CSM"],
  "keywords_covered": ["renewals","playbooks","LMS"],
  "ats_score": 86
}

5.2 posting_enrichments.fit_factors
{
  "title_similarity": 0.82,
  "skill_overlap": {"count": 9, "ratio": 0.6, "skills": ["renewals","playbooks","ai"]},
  "seniority_match": true,
  "salary_alignment": 0.9,
  "recency_boost": 0.7
}

5.3 search_prefs.filters
{
  "titles": ["Customer Success Manager","Customer Experience Lead"],
  "skills": ["LMS","AI","Change Management"],
  "levels": ["IC","Lead"],
  "industries": ["EdTech","AI"],
  "remote_only": true,
  "geo": ["Canada","US"],
  "salary_min_cents": 12000000
}

6) Referential Integrity & Constraints

applications.user_id must equal resume_versions.user_id when linked via job_posting_id.

outreach.application_id fk ensures cascade deletes when application removed.

Unique guards:

applications (user_id, job_posting_id)

posting_enrichments (user_id, job_posting_id)

job_postings (source, source_id) (nullable source_id handled by partial unique index).

Check constraints: non-negative cents; fit_score 0..100; dates logical (end_at > start_at).

7) Index Strategy (Practical)

create index idx_postings_tags on job_postings using gin (normalized_tags);

create index idx_profiles_skills on profiles using gin (skills);

create index idx_applications_user_stage on applications (user_id, stage);

create index idx_tasks_due on tasks (user_id, completed_at, due_at);

create index idx_enrich_user_posting on posting_enrichments (user_id, job_posting_id);

create index idx_runs_user_time on model_runs (user_id, created_at desc);

Trigram:

create extension if not exists pg_trgm;

create index idx_postings_title_trgm on job_postings using gin (title gin_trgm_ops);

8) Security & PII Classification

PII columns: users.email, profiles.summary, resume_versions.sections_json, outreach.contact_*, events.location.

Encryption at rest: App-level KMS for integration_accounts.*token*.

Row-level access: Enforce via service layer; optional RLS policies for applications, resume_versions, tasks, notifications, model_runs, audit_logs.

Data retention:

Soft-delete applications, resume_versions, outreach (keep for 30 days).

Hard-delete OAuth tokens on integration disconnect.

9) Migration Seeds (MVP)

Seed plan_tier_enum, provider_enum values.

Insert default search_prefs after onboarding (based on uploaded resume parsing).

Backfill posting_enrichments nightly for recent postings.

10) Example DDL (Selected)
-- users
create table users (
  id uuid primary key default gen_random_uuid(),
  email citext unique not null,
  password_hash text,
  auth_provider text,
  plan_tier plan_tier_enum not null default 'free',
  status status_enum not null default 'active',
  last_login_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- profiles
create table profiles (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  headline text,
  summary text,
  skills text[] default '{}',
  years_experience int,
  locations text[] default '{}',
  work_auth text,
  salary_min_cents int,
  salary_max_cents int,
  remote_only boolean not null default true,
  job_preferences jsonb not null default '{}',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- companies
create table companies (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  domain citext unique,
  linkedin_company_id text unique,
  size_range text,
  industry text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- job_postings
create table job_postings (
  id uuid primary key default gen_random_uuid(),
  company_id uuid references companies(id),
  source provider_enum,
  source_id text,
  url text not null,
  title text not null,
  jd_raw text,
  jd_clean text,
  location text,
  remote_flag boolean not null default false,
  eligibility_notes text,
  salary_min_cents int,
  salary_max_cents int,
  currency char(3) not null default 'USD',
  normalized_tags text[] not null default '{}',
  posted_at timestamptz,
  scraped_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);
create unique index if not exists ux_posting_source_id on job_postings(source, source_id) where source_id is not null;

-- applications
create table applications (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  job_posting_id uuid references job_postings(id),
  stage stage_enum not null default 'prospect',
  status_notes text,
  source_label text,
  applied_at timestamptz,
  updated_at timestamptz not null default now(),
  created_at timestamptz not null default now(),
  unique(user_id, job_posting_id)
);

-- resume_versions
create table resume_versions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  base_flag boolean not null default false,
  job_posting_id uuid references job_postings(id),
  doc_url text,
  sections_json jsonb not null default '{}',
  ats_score int,
  keywords text[] not null default '{}',
  diff_from_base jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- outreach
create table outreach (
  id uuid primary key default gen_random_uuid(),
  application_id uuid not null references applications(id) on delete cascade,
  contact_name text,
  contact_role text,
  contact_profile_url text,
  channel outreach_channel_enum not null,
  status outreach_status_enum not null default 'draft',
  message_body text,
  sent_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- events
create table events (
  id uuid primary key default gen_random_uuid(),
  application_id uuid not null references applications(id) on delete cascade,
  type event_type_enum not null,
  start_at timestamptz,
  end_at timestamptz,
  location text,
  notes text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (end_at is null or start_at is null or end_at > start_at)
);

-- tasks
create table tasks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  application_id uuid references applications(id),
  title text not null,
  nudge_type task_type_enum,
  priority priority_enum not null default 'normal',
  due_at timestamptz,
  completed_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

-- posting_enrichments
create table posting_enrichments (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  job_posting_id uuid not null references job_postings(id) on delete cascade,
  fit_score int not null,
  fit_factors jsonb not null default '{}',
  salary_estimate_cents int,
  rationale text,
  created_at timestamptz not null default now(),
  unique(user_id, job_posting_id)
);

-- model_runs & model_io
create table model_runs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references users(id) on delete cascade,
  agent agent_enum not null,
  tool text,
  input_ref text,
  output_ref text,
  tokens_in int,
  tokens_out int,
  latency_ms int,
  success_flag boolean not null default true,
  created_at timestamptz not null default now()
);
create table model_io (
  id uuid primary key default gen_random_uuid(),
  model_run_id uuid not null references model_runs(id) on delete cascade,
  role text not null,
  content jsonb not null,
  created_at timestamptz not null default now()
);

-- audit_logs
create table audit_logs (
  id uuid primary key default gen_random_uuid(),
  actor_type text not null,
  actor_id uuid,
  action text not null,
  entity text not null,
  entity_id uuid not null,
  diff jsonb,
  ip inet,
  created_at timestamptz not null default now()
);

11) Data Flows (Key Joins)

Daily Feed:
job_postings ⟵ companies + left join posting_enrichments on (user_id, job_posting_id) to show fit_score, salary est., rationale.

Pipeline Board:
applications ⟵ job_postings ⟵ companies + counts by stage.

Resume Studio:
resume_versions (latest per application_id or base_flag = true) + job_postings.jd_clean → display ats_score, keywords.

Outreach:
outreach by application_id + status funnel.

12) Analytics Events (Minimal)

Table: user_events
(id, user_id, name text, props jsonb, created_at timestamptz)
Examples: search_run, posting_view, apply_click, resume_generated, outreach_sent, task_completed.

13) Backups & Retention

PITR enabled; daily snapshots kept 30 days (free/pro), 90 days (team/enterprise).

Export endpoint for user data (GDPR/CCPA); hard delete within 30 days of request.

14) What Ships in MVP

Tables: users, profiles, companies, job_postings, posting_enrichments, applications, resume_versions, outreach, events, tasks, search_prefs, model_runs, model_io, audit_logs, notifications (optional).

Indexes noted in §7.

Seeds: enums, a default search_prefs, and a base resume_versions from uploaded file.
