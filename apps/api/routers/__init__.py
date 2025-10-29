"""API router modules."""

from apps.api.routers import auth, feed, onboarding, profiles, resumes, search_prefs, system

__all__ = [
    "auth",
    "feed",
    "onboarding",
    "profiles",
    "resumes",
    "search_prefs",
    "system",
]
