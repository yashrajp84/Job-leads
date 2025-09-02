from __future__ import annotations

import hashlib
import os
import re
import sys
from datetime import datetime, timezone
from typing import Any

from dateutil import parser as dateparser


HEADERS = {
    "User-Agent": (
        "JobLeadsBot/0.1 (+https://example.local; contact=local)"
    )
}


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def url_hash(url: str) -> str:
    return hashlib.sha1(url.encode("utf-8")).hexdigest()


def safe_text(val: Any) -> str:
    if val is None:
        return ""
    return str(val).strip()


def to_iso_date(text: str | None) -> str:
    if not text:
        return ""
    try:
        dt = dateparser.parse(text)
        if not dt:
            return ""
        if not dt.tzinfo:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).isoformat()
    except Exception:
        return ""


def slugify(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s


def eprint(*args: Any, **kwargs: Any) -> None:
    print(*args, **kwargs, file=sys.stderr)

