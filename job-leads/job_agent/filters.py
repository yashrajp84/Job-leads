from __future__ import annotations

from typing import Iterable, List


def _contains_any(text: str, keywords: Iterable[str]) -> bool:
    t = text.lower()
    return any(k.lower() in t for k in keywords)


def filter_records(records: list[dict], include: list[str], exclude: list[str], locations: list[str]) -> list[dict]:
    out: List[dict] = []
    for r in records:
        text_blob = " ".join(
            [
                r.get("title", ""),
                r.get("company", ""),
                r.get("location", ""),
                r.get("tags", ""),
                r.get("description", ""),
            ]
        ).lower()

        # Include: if non-empty, require any include keyword
        if include:
            if not _contains_any(text_blob, include):
                continue

        # Exclude: if any exclude keyword, skip
        if exclude:
            if _contains_any(text_blob, exclude):
                continue

        # Locations: if provided, check location OR allow 'remote' match
        if locations:
            locs = [l.lower() for l in locations]
            job_loc = r.get("location", "").lower()
            if not any(l in job_loc for l in locs) and ("remote" not in locs or "remote" not in job_loc):
                continue

        out.append(r)
    return out

