from __future__ import annotations

import time
from typing import Any

import httpx
from loguru import logger


class ProviderError(RuntimeError):
    """Raised when a provider request fails after retries."""


def fetch_greenhouse_postings(board_token: str) -> list[dict[str, Any]]:
    """Fetch all jobs for a public Greenhouse board.

    Uses basic exponential backoff for transient failures and follows the meta.next
    cursor implemented by the Greenhouse Board API.
    """

    base_url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    jobs: list[dict[str, Any]] = []

    with httpx.Client(headers={"User-Agent": "VantaJobScout/0.1"}) as client:
        next_url: str | None = base_url
        while next_url:
            logger.debug("Fetching Greenhouse payload", url=next_url)
            payload = _request_with_backoff(client, next_url)
            jobs.extend(payload.get("jobs", []))
            next_url = payload.get("meta", {}).get("next")

    return jobs


def _request_with_backoff(client: httpx.Client, url: str, retries: int = 3) -> dict[str, Any]:
    for attempt in range(retries + 1):
        try:
            response = client.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            should_retry = exc.response.status_code >= 500 and attempt < retries
            logger.warning(
                "Greenhouse request failed",
                status=exc.response.status_code,
                url=url,
                attempt=attempt,
                retrying=should_retry,
            )
            if should_retry:
                time.sleep(0.5 * (2**attempt))
                continue
            raise ProviderError(f"Greenhouse returned {exc.response.status_code}") from exc
        except httpx.RequestError as exc:
            logger.warning("Greenhouse network error", error=str(exc), attempt=attempt)
            if attempt < retries:
                time.sleep(0.5 * (2**attempt))
                continue
            raise ProviderError("Failed to reach Greenhouse") from exc
    raise ProviderError("Exhausted retries talking to Greenhouse")


def normalize_greenhouse_posting(raw: dict[str, Any]) -> dict[str, Any]:
    location = raw.get("location") or {}
    location_name = location.get("name") if isinstance(location, dict) else None
    is_remote = bool(location_name and "remote" in location_name.lower())

    departments = [dept.get("name") for dept in raw.get("departments", []) if dept.get("name")]
    company = raw.get("company") or {}

    salary = raw.get("salary") or {}
    salary_min = salary.get("min") if isinstance(salary.get("min"), (int, float)) else None
    salary_max = salary.get("max") if isinstance(salary.get("max"), (int, float)) else None

    return {
        "source": "greenhouse",
        "source_id": str(raw.get("id")),
        "title": raw.get("title") or "Untitled",
        "url": raw.get("absolute_url") or raw.get("job_post_url") or "",
        "location_raw": location_name,
        "is_remote": is_remote,
        "metadata_json": {
            "departments": departments,
            "offices": raw.get("offices") or [],
        },
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": salary.get("currency") or "USD",
        "company": {
            "name": company.get("name") if isinstance(company, dict) else None,
            "domain": company.get("url") if isinstance(company, dict) else None,
        },
    }
