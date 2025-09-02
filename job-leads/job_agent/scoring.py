from __future__ import annotations

from typing import Dict, Iterable, List, Tuple


def score_record(record: dict, rules: dict | None) -> int:
    if not rules:
        return 0
    text = " ".join(
        [
            record.get("title", ""),
            record.get("company", ""),
            record.get("location", ""),
            record.get("tags", ""),
            record.get("description", ""),
        ]
    ).lower()

    score = 0
    for term, weight in rules.get("plus", []) or []:
        if term.lower() in text:
            score += int(weight)
    for term, weight in rules.get("minus", []) or []:
        if term.lower() in text:
            score -= int(weight)
    return score

