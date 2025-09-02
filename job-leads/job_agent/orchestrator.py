from __future__ import annotations

import argparse
import os
from typing import Dict, List, Tuple

import pandas as pd
from dotenv import load_dotenv
import yaml

from .adapters import ADAPTERS
from .db import get_session, init_db, upsert_job
from .filters import filter_records
from .models import Job
from .schema import JobModel
from .scoring import score_record
from .utils import now_iso, url_hash
from .repo import (
    upsert_jobs_supa,
    ensure_leads_supa,
    get_existing_ids_supa,
)


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def run_scrape(cfg: dict) -> tuple[int, int, int, list[JobModel]]:
    # Initialize local DB only if using sqlite
    if cfg.get("use_sqlite"):
        init_db()
    sites: List[str] = cfg.get("sites", [])
    includes: List[str] = cfg.get("include", [])
    excludes: List[str] = cfg.get("exclude", [])
    locations: List[str] = cfg.get("locations", [])

    # queries: for JSON org adapters, treat includes as org slugs if looks like one; otherwise treat includes as search terms
    # Here we take a simple approach: for greenhouse/lever we expect include to be org slugs; for HTML adapters we use include as search terms.
    results: List[dict] = []
    for site in sites:
        fetch = ADAPTERS.get(site)
        if not fetch:
            continue
        terms = includes or [""]
        for term in terms:
            try:
                jobs = fetch(term, cfg)
            except Exception:
                jobs = []
            for j in jobs:
                # compute score early
                j["score"] = score_record(j, cfg.get("score_rules"))
            results.extend(jobs)

    all_count = len(results)
    filtered = filter_records(results, includes, excludes, locations)
    filtered_count = len(filtered)

    # dedupe by id
    unique_map: Dict[str, dict] = {}
    for r in filtered:
        unique_map[r["id"]] = r
    unique = list(unique_map.values())
    unique_count = len(unique)

    # Decide storage target based on env/config
    supa_ok = bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))

    # Always assign ids and collected_at
    ids = [r.get("id") or url_hash(r.get("url", "")) for r in unique]
    for r, _id in zip(unique, ids):
        r["id"] = _id
        r.setdefault("collected_at", now_iso())

    new_jobs: List[JobModel] = []

    if supa_ok:
        existing = get_existing_ids_supa(ids, service=True)
        upserted_ids = upsert_jobs_supa(unique, service=True)
        ensure_leads_supa(upserted_ids, service=True)
        new_ids = [i for i in upserted_ids if i not in existing]
        new_jobs = [
            JobModel(**{k: v for k, v in r.items() if k in JobModel.model_fields})
            for r in unique
            if r["id"] in new_ids
        ]
    # Local writes: if configured or Supabase not available
    if cfg.get("use_sqlite") or not supa_ok:
        with get_session() as session:
            for r in unique:
                existed = session.get(Job, r["id"]) is not None
                job = upsert_job(session, r)
                if not supa_ok and not existed:
                    new_jobs.append(
                        JobModel(
                            **{c: getattr(job, c) for c in JobModel.model_fields.keys()}
                        )
                    )

        out_csv = cfg.get("output_csv", "out/jobs.csv")
        os.makedirs(os.path.dirname(out_csv), exist_ok=True)
        df = pd.DataFrame(unique)
        cols = [
            "id",
            "title",
            "company",
            "location",
            "salary",
            "tags",
            "posted_at",
            "url",
            "source",
            "collected_at",
            "description",
            "score",
        ]
        for c in cols:
            if c not in df.columns:
                df[c] = ""
        df[cols].to_csv(out_csv, index=False)

    return all_count, filtered_count, unique_count, new_jobs


def main() -> None:
    load_dotenv()
    parser = argparse.ArgumentParser(description="Job leads scraper orchestrator")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--include", nargs="*", default=None)
    parser.add_argument("--exclude", nargs="*", default=None)
    parser.add_argument("--locations", nargs="*", default=None)
    parser.add_argument("--sites", nargs="*", default=None)
    args = parser.parse_args()

    cfg = load_config(args.config)
    if args.include is not None:
        cfg["include"] = args.include
    if args.exclude is not None:
        cfg["exclude"] = args.exclude
    if args.locations is not None:
        cfg["locations"] = args.locations
    if args.sites is not None:
        cfg["sites"] = args.sites

    all_c, filt_c, uniq_c, new_jobs = run_scrape(cfg)
    print(f"Scrape done: all={all_c} filtered={filt_c} unique={uniq_c} new={len(new_jobs)}")


if __name__ == "__main__":
    main()
