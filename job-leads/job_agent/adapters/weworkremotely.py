from __future__ import annotations

import time
from typing import List

import requests
from bs4 import BeautifulSoup

from ..utils import HEADERS, now_iso, safe_text, to_iso_date, url_hash


def make_record(row: dict) -> dict:
    url = row.get("url", "")
    return {
        "id": url_hash(url),
        "title": safe_text(row.get("title")),
        "company": safe_text(row.get("company")),
        "location": safe_text(row.get("location")),
        "salary": safe_text(row.get("salary")),
        "tags": ",".join(row.get("tags", [])),
        "posted_at": safe_text(row.get("posted_at", "")),
        "url": url,
        "source": "weworkremotely",
        "collected_at": now_iso(),
        "description": safe_text(row.get("description")),
    }


def fetch_jobs(query: str, cfg: dict) -> List[dict]:
    # HTML search: https://weworkremotely.com/remote-jobs/search?term={query}
    url = "https://weworkremotely.com/remote-jobs/search?term=" + requests.utils.quote(query)
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        out: List[dict] = []
        for section in soup.select("section.jobs"):  # sections contain lists
            for li in section.select("li"):  # individual jobs or header dividers
                a = li.select_one("a")
                if not a or not a.get("href") or "/remote-jobs/" not in a.get("href"):
                    continue
                url = "https://weworkremotely.com" + a.get("href")
                company = li.select_one("span.company")
                title = li.select_one("span.title")
                region = li.select_one("span.region.company") or li.select_one("span.region")
                tags = [t.get_text(strip=True) for t in li.select("span.tag")]
                row = {
                    "title": title.get_text(strip=True) if title else "",
                    "company": company.get_text(strip=True) if company else "",
                    "url": url,
                    "tags": tags,
                    "location": region.get_text(strip=True) if region else "",
                    "posted_at": "",
                    "salary": "",
                    "description": "",
                }
                out.append(make_record(row))
        time.sleep(0.6)
        return out
    except Exception:
        return []

