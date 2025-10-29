from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.routers import (
    applications,
    auth,
    feed,
    notifications,
    onboarding,
    profiles,
    resumes,
    search_prefs,
    system,
)

app = FastAPI(title="Vanta API", version="0.1.0")

allowed_origins = {
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    os.getenv("NEXTAUTH_URL", "http://localhost:3000"),
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in allowed_origins if origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router)
app.include_router(auth.router)
app.include_router(feed.router)
app.include_router(applications.router)
app.include_router(notifications.router)
app.include_router(onboarding.router)
app.include_router(profiles.router)
app.include_router(resumes.router)
app.include_router(search_prefs.router)


def run() -> None:  # pragma: no cover - convenience entrypoint
    import uvicorn

    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()
