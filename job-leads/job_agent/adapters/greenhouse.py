from __future__ import annotations

import time
from typing import List

import requests

from ..utils import HEADERS, now_iso, safe_text, to_iso_date, url_hash


def make_record(item: dict, org: str) -> dict:
    url = safe_text(item.get("absolute_url") or item.get("url") or "")
    return {
        "id": url_hash(url),
        "title": safe_text(item.get("title")),
        "company": org,
        "location": safe_text((item.get("location") or {}).get("name")),
        "salary": "",
        "tags": ",".join([t.get("name", "") for t in item.get("metadata", []) if t.get("name")]),
        "posted_at": to_iso_date(item.get("updated_at") or item.get("created_at")),
        "url": url,
        "source": "greenhouse",
        "collected_at": now_iso(),
        "description": safe_text(item.get("content") or item.get("description") or ""),
    }


def fetch_jobs(query: str, cfg: dict) -> List[dict]:
    # For Greenhouse, `query` is expected to be the org slug: boards.greenhouse.io/{org}.json
    org = query
    url = f"https://boards.greenhouse.io/{org}.json"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        jobs = [make_record(j, org) for j in data.get("jobs", [])]
        time.sleep(0.6)
        return jobs
    except Exception:
        return []

