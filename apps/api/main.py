from __future__ import annotations

from fastapi import FastAPI

from apps.api.routers import auth, feed, onboarding, profiles, resumes, search_prefs, system

app = FastAPI(title="Vanta API", version="0.1.0")

app.include_router(system.router)
app.include_router(auth.router)
app.include_router(feed.router)
app.include_router(onboarding.router)
app.include_router(profiles.router)
app.include_router(resumes.router)
app.include_router(search_prefs.router)


def run() -> None:  # pragma: no cover - convenience entrypoint
    import uvicorn

    uvicorn.run("apps.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run()
