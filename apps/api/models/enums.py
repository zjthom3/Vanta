from enum import StrEnum


class StageEnum(StrEnum):
    PROSPECT = "prospect"
    APPLIED = "applied"
    SCREEN = "screen"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


class OutreachChannelEnum(StrEnum):
    LINKEDIN = "linkedin"
    EMAIL = "email"


class OutreachStatusEnum(StrEnum):
    DRAFT = "draft"
    QUEUED = "queued"
    SENT = "sent"
    REPLIED = "replied"
    BOUNCED = "bounced"


class EventTypeEnum(StrEnum):
    INTERVIEW = "interview"
    PHONE_SCREEN = "phone_screen"
    ASSESSMENT = "assessment"
    DEADLINE = "deadline"
    OFFER_CALL = "offer_call"
    OTHER = "other"


class TaskTypeEnum(StrEnum):
    FOLLOW_UP = "follow_up"
    RESEARCH = "research"
    PREP = "prep"
    APPLY = "apply"
    REFERRAL = "referral"
    THANK_YOU = "thank_you"


class PriorityEnum(StrEnum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ProviderEnum(StrEnum):
    LINKEDIN = "linkedin"
    GMAIL = "gmail"
    OUTLOOK = "outlook"
    GOOGLE_CALENDAR = "google_calendar"
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    WORKDAY = "workday"
    INDEED = "indeed"
    OTHER = "other"


class PlanTierEnum(StrEnum):
    FREE = "free"
    PRO = "pro"
    TEAM = "team"
    ENTERPRISE = "enterprise"


class AgentEnum(StrEnum):
    ORCHESTRATOR = "orchestrator"
    JOB_SCOUT = "job_scout"
    RESUME_TAILOR = "resume_tailor"
    OPTIMIZER = "optimizer"
    OUTREACH = "outreach"
    TRACKER_COACH = "tracker_coach"


class StatusEnum(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
