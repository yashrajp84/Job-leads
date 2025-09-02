from __future__ import annotations

import time
from typing import List

import requests

from ..utils import HEADERS, now_iso, safe_text, to_iso_date, url_hash


def make_record(item: dict, org: str) -> dict:
    url = safe_text(item.get("hostedUrl") or item.get("applyUrl") or item.get("url") or "")
    locs = item.get("categories", {})
    location = safe_text(locs.get("location") or item.get("location") or "")
    tags = ",".join(item.get("tags", []) or [])
    return {
        "id": url_hash(url),
        "title": safe_text(item.get("text") or item.get("title")),
        "company": org,
        "location": location,
        "salary": "",
        "tags": tags,
        "posted_at": to_iso_date(item.get("createdAt") or item.get("postedAt")),
        "url": url,
        "source": "lever",
        "collected_at": now_iso(),
        "description": safe_text(item.get("descriptionPlain") or item.get("description") or ""),
    }


def fetch_jobs(query: str, cfg: dict) -> List[dict]:
    # For Lever, `query` is org slug: jobs.lever.co/{org}.json
    org = query
    url = f"https://jobs.lever.co/{org}.json"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        jobs = [make_record(j, org) for j in data]
        time.sleep(0.6)
        return jobs
    except Exception:
        return []

