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
        "source": "remoteok",
        "collected_at": now_iso(),
        "description": safe_text(row.get("description")),
    }


def fetch_jobs(query: str, cfg: dict) -> List[dict]:
    # HTML page: https://remoteok.com/remote-{query}-jobs
    q = query.replace(" ", "-")
    url = f"https://remoteok.com/remote-{q}-jobs"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        out: List[dict] = []
        for tr in soup.select("tr.job"):
            try:
                title_el = tr.select_one("h2")
                company_el = tr.select_one("h3")
                link_el = tr.select_one("a.preventLink") or tr.select_one("a")
                tags = [t.get_text(strip=True) for t in tr.select("div.tags > a")]
                location_el = tr.select_one("div.location")
                date_el = tr.select_one("time")
                desc_el = tr.select_one("div.description")

                row = {
                    "title": title_el.get_text(strip=True) if title_el else "",
                    "company": company_el.get_text(strip=True) if company_el else "",
                    "url": ("https://remoteok.com" + link_el.get("href")) if link_el and link_el.get("href") else "",
                    "tags": tags,
                    "location": location_el.get_text(strip=True) if location_el else "",
                    "posted_at": to_iso_date(date_el.get("datetime")) if date_el else "",
                    "salary": "",
                    "description": desc_el.get_text(strip=True) if desc_el else "",
                }
                out.append(make_record(row))
            except Exception:
                continue
        time.sleep(0.6)
        return out
    except Exception:
        return []

