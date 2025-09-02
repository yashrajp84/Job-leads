from __future__ import annotations

import os
from typing import List, Optional
from dotenv import load_dotenv

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import and_, select

from job_agent.orchestrator import load_config, run_scrape
from job_agent.schema import FilterQuery, JobModel, LeadModel, UpsertLead
from job_agent.utils import now_iso, url_hash
from job_agent.db import get_session, init_db, upsert_job, upsert_lead
from job_agent.models import Job, Lead
from job_agent.repo import (
    query_jobs_supa,
    get_leads_supa,
    upsert_leads_fields_supa,
    upsert_jobs_supa,
    get_jobs_by_ids_supa,
    bulk_scores_supa,
    bulk_status_supa,
    upsert_person_supa,
    upsert_post_supa,
    upsert_interaction_supa,
    list_latest_people_supa,
    list_latest_posts_supa,
    list_latest_jobs_supa,
    search_all_supa,
)
from job_agent.scoring import score_record
from job_agent.notify import send_slack
from backend.llm import get_default_provider
from backend.prompts import INVITE_TMPL, COMMENT_TMPL, COVER_LETTER_TMPL, RESUME_BULLETS_TMPL

load_dotenv()
app = FastAPI(title="Job Leads API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def supa_available() -> bool:
    # Require service role for server-side usage to ensure consistency with writes
    return bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_SERVICE_ROLE_KEY"))


@app.get("/jobs")
def get_jobs(
    q: Optional[str] = None,
    status: Optional[str] = None,
    source: Optional[str] = None,
    location: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
):
    if supa_available():
        filters = {
            "q": q,
            "source": source,
            "location": location,
            "date_from": date_from,
            "date_to": date_to,
            "limit": limit,
            "offset": offset,
        }
        jobs = query_jobs_supa(filters, service=False)
        leads = get_leads_supa({"status": status} if status else None, service=False)
        lead_map = {l["id"]: l for l in leads}
        out = []
        for j in jobs:
            jd = {k: j.get(k, "") for k in JobModel.model_fields.keys()}
            ld = lead_map.get(jd["id"]) if status is None or (lead_map.get(jd["id"]) and lead_map[jd["id"]]["status"] == status) else None
            if status and not ld:
                continue
            if ld:
                jd["lead"] = ld
            out.append(jd)
        return out
    # Fallback: local SQLite
    init_db()
    with get_session() as session:
        stmt = select(Job)
        conditions = []
        if q:
            pattern = f"%{q.lower()}%"
            conditions.append(
                (Job.title.ilike(pattern))
                | (Job.company.ilike(pattern))
                | (Job.description.ilike(pattern))
                | (Job.tags.ilike(pattern))
            )
        if source:
            conditions.append(Job.source == source)
        if location:
            conditions.append(Job.location.ilike(f"%{location}%"))
        if date_from:
            conditions.append(Job.collected_at >= date_from)
        if date_to:
            conditions.append(Job.collected_at <= date_to)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        stmt = stmt.offset(offset).limit(limit)
        rows = session.execute(stmt).scalars().all()
        lead_rows = {l.id: l for l in session.execute(select(Lead)).scalars().all()}
        if status:
            rows = [r for r in rows if (lead_rows.get(r.id) and lead_rows[r.id].status == status)]
        out = []
        for j in rows:
            jd = {c: getattr(j, c) for c in JobModel.model_fields.keys()}
            ld = lead_rows.get(j.id)
            if ld:
                jd["lead"] = {
                    "id": ld.id,
                    "status": ld.status,
                    "score": ld.score,
                    "favourite": ld.favourite,
                    "resume_url": ld.resume_url,
                    "cover_letter_url": ld.cover_letter_url,
                    "next_action": ld.next_action,
                    "next_action_date": ld.next_action_date,
                    "notes": ld.notes,
                    "updated_at": ld.updated_at,
                }
            out.append(jd)
        return out


@app.get("/leads")
def get_leads():
    if supa_available():
        return get_leads_supa(None, service=False)
    init_db()
    with get_session() as session:
        rows = session.execute(select(Lead)).scalars().all()
        return [
            {
                "id": l.id,
                "status": l.status,
                "score": l.score,
                "favourite": l.favourite,
                "resume_url": l.resume_url,
                "cover_letter_url": l.cover_letter_url,
                "next_action": l.next_action,
                "next_action_date": l.next_action_date,
                "notes": l.notes,
                "updated_at": l.updated_at,
            }
            for l in rows
        ]


@app.post("/leads/{lead_id}")
def post_lead(lead_id: str, payload: UpsertLead | None = None):
    data = (payload.model_dump(exclude_unset=True) if payload else {})
    if supa_available():
        upsert_leads_fields_supa(lead_id, data, service=True)
    else:
        init_db()
        with get_session() as session:
            upsert_lead(session, lead_id, data)
    return {"ok": True, "id": lead_id}


@app.patch("/leads/{lead_id}")
def patch_lead(lead_id: str, payload: UpsertLead):
    data = payload.model_dump(exclude_unset=True)
    if supa_available():
        upsert_leads_fields_supa(lead_id, data, service=True)
    else:
        init_db()
        with get_session() as session:
            upsert_lead(session, lead_id, data)
    return {"ok": True, "id": lead_id}


@app.post("/run-scrape")
def run_scrape_now():
    cfg = load_config("config.yaml")
    all_c, filt_c, uniq_c, new_jobs = run_scrape(cfg)
    return {
        "all": all_c,
        "filtered": filt_c,
        "unique": uniq_c,
        "new": len(new_jobs),
    }


class UpsertJob(BaseModel):
    id: Optional[str] = None
    title: str = ""
    company: str = ""
    location: str = ""
    salary: str = ""
    tags: str = ""
    posted_at: str = ""
    url: str = ""
    source: str = "manual"
    description: str = ""


@app.post("/jobs")
def create_or_update_job(payload: UpsertJob):
    data = payload.model_dump()
    if not data.get("id"):
        data["id"] = url_hash(data.get("url", ""))
    data.setdefault("collected_at", now_iso())
    if supa_available():
        upsert_jobs_supa([data], service=True)
    else:
        init_db()
        with get_session() as session:
            upsert_job(session, data)
    return {"ok": True, "id": data["id"]}


# Actions API
@app.post("/actions/scrape_now")
def actions_scrape_now():
    return run_scrape_now()


class RescorePayload(BaseModel):
    ids: list[str] | None = None


@app.post("/actions/rescore")
def actions_rescore(payload: RescorePayload | None = None):
    cfg = load_config("config.yaml")
    rules = cfg.get("score_rules")
    ids = (payload.ids if payload else None) or []
    if supa_available():
        jobs = get_jobs_by_ids_supa(ids, service=True) if ids else query_jobs_supa({"limit": 1000}, service=True)
        id_to_score = {}
        for j in jobs:
            sc = score_record(j, rules)
            id_to_score[j["id"]] = sc
        updated = bulk_scores_supa(id_to_score, service=True)
        return {"updated": updated}
    # Local fallback
    init_db()
    updated = 0
    with get_session() as session:
        q = select(Job)
        if ids:
            from sqlalchemy import bindparam
            q = q.where(Job.id.in_(ids))
        jobs = session.execute(q).scalars().all()
        for j in jobs:
            sc = score_record({c: getattr(j, c) for c in JobModel.model_fields.keys()}, rules)
            upsert_lead(session, j.id, {"score": sc})
            updated += 1
    return {"updated": updated}


class BulkStatusPayload(BaseModel):
    ids: list[str]
    status: str


@app.post("/actions/bulk_status")
def actions_bulk_status(payload: BulkStatusPayload):
    if supa_available():
        updated = bulk_status_supa(payload.ids, payload.status, service=True)
        return {"updated": updated}
    init_db()
    with get_session() as session:
        for _id in payload.ids:
            upsert_lead(session, _id, {"status": payload.status})
    return {"updated": len(payload.ids)}


class SlackDigestPayload(BaseModel):
    ids: list[str]


@app.post("/actions/slack_digest")
def actions_slack_digest(payload: SlackDigestPayload):
    jobs = get_jobs_by_ids_supa(payload.ids, service=False)
    lines = [f"Digest: {len(jobs)} jobs"] + [f"• {j['title']} — {j['company']} — {j['url']}" for j in jobs[:5]]
    ok = send_slack("\n".join(lines), webhook_url=os.getenv("SLACK_WEBHOOK_URL"))
    return {"ok": ok}


class CreateRemindersPayload(BaseModel):
    items: list[dict]


@app.post("/actions/create_reminders")
def actions_create_reminders(payload: CreateRemindersPayload):
    count = 0
    for it in payload.items:
        _id = it.get("id")
        if not _id:
            continue
        fields = {k: v for k, v in it.items() if k in {"next_action", "next_action_date", "notes"}}
        upsert_leads_fields_supa(_id, fields, service=True)
        count += 1
    return {"updated": count}


class ImportCsvPayload(BaseModel):
    csv_text: str


@app.post("/actions/import_csv")
def actions_import_csv(payload: ImportCsvPayload):
    import csv
    import io

    reader = csv.DictReader(io.StringIO(payload.csv_text))
    rows = list(reader)
    # Map to job records
    to_upsert = []
    for r in rows:
        if not r.get("url"):
            continue
        _id = r.get("id") or url_hash(r["url"])
        to_upsert.append(
            {
                "id": _id,
                "title": r.get("title", ""),
                "company": r.get("company", ""),
                "location": r.get("location", ""),
                "salary": r.get("salary", ""),
                "tags": r.get("tags", ""),
                "posted_at": r.get("posted_at") or None,
                "url": r.get("url", ""),
                "source": r.get("source", "import"),
                "collected_at": r.get("collected_at") or now_iso(),
                "description": r.get("description", ""),
            }
        )
    ids = upsert_jobs_supa(to_upsert, service=True)
    return {"upserted": len(ids)}


# ---------- Net-Leads additions ----------

class SuggestPayload(BaseModel):
    type: str
    payload: dict
    style: str | None = None


@app.post("/llm/suggest")
async def llm_suggest(body: SuggestPayload):
    prov = get_default_provider()
    kind = body.type
    style = body.style or "short"
    p = body.payload
    if kind == "invite":
        prompt = INVITE_TMPL.format(full_name=p.get("full_name",""), company=p.get("company",""), headline=p.get("headline",""), shared=p.get("shared_context",""), style=style)
    elif kind == "comment":
        prompt = COMMENT_TMPL.format(excerpt=p.get("excerpt",""), persona=p.get("persona",""), style=style)
    elif kind == "cover_letter":
        prompt = COVER_LETTER_TMPL.format(title=p.get("title",""), company=p.get("company",""), description=p.get("description",""), strengths=p.get("strengths",""), keywords=p.get("keywords",""), style=style)
    elif kind == "resume_bullets":
        prompt = RESUME_BULLETS_TMPL.format(title=p.get("title",""), company=p.get("company",""), keywords=p.get("keywords",""))
    else:
        return {"draft": ""}
    text = await prov.suggest(kind, prompt)
    # Try to extract JSON {draft: ...}
    import json
    try:
        data = json.loads(text)
        return {"draft": data.get("draft", text)}
    except Exception:
        return {"draft": text}


class ClipPayload(BaseModel):
    kind: str
    url: str
    title: str | None = None
    text: str | None = None
    meta: dict | None = None


@app.post("/clip")
def clip(body: ClipPayload):
    # never automate actions on platforms; just store references
    if supa_available():
        if body.kind == "person":
            upsert_person_supa({
                "platform": "linkedin" if "linkedin.com" in body.url else "website",
                "full_name": body.title or body.url,
                "profile_url": body.url,
                "notes": body.text or "",
                "source": "clipper",
            }, service=True)
            upsert_interaction_supa({"entity_type": "person", "entity_id": "", "status": "Saved"}, service=True)
        elif body.kind == "post":
            upsert_post_supa({
                "platform": "linkedin" if "linkedin.com" in body.url else "website",
                "url": body.url,
                "text": (body.text or "")[:1000],
            }, service=True)
            upsert_interaction_supa({"entity_type": "post", "entity_id": "", "status": "Saved"}, service=True)
        else:  # job
            # Quick add as job when scraping adapter isn't available here
            jid = url_hash(body.url)
            upsert_jobs_supa([{
                "id": jid,
                "title": body.title or "Job",
                "company": "",
                "url": body.url,
                "source": "clipper",
                "description": body.text or "",
                "collected_at": now_iso(),
            }], service=True)
            upsert_interaction_supa({"entity_type": "job", "entity_id": jid, "status": "Saved"}, service=True)
        return {"ok": True}
    # Fallback: local only supports jobs
    jid = url_hash(body.url)
    init_db()
    with get_session() as s:
        upsert_job(s, {
            "id": jid,
            "title": body.title or "Job",
            "company": "",
            "url": body.url,
            "source": "clipper",
            "description": body.text or "",
            "collected_at": now_iso(),
        })
    return {"ok": True}


@app.get("/feed")
def get_feed():
    if supa_available():
        people = list_latest_people_supa(50, service=False)
        posts = list_latest_posts_supa(50, service=False)
        jobs = list_latest_jobs_supa(50, service=False)
        # Tag and merge by timestamps (best-effort without full schema consistency)
        def tag(arr, kind, ts_key):
            for a in arr:
                a["kind"] = kind
                a["_ts"] = a.get(ts_key) or a.get("created_at") or a.get("updated_at") or ""
            return arr
        items = tag(people, "person", "updated_at") + tag(posts, "post", "created_at") + tag(jobs, "job", "collected_at")
        items.sort(key=lambda x: x.get("_ts", ""), reverse=True)
        for a in items:
            a.pop("_ts", None)
        return items[:100]
    # Local fallback: jobs only
    return get_jobs(q=None, status=None, source=None, location=None, date_from=None, date_to=None, limit=50, offset=0)


class BulkStatusInteractions(BaseModel):
    ids: list[str]
    status: str


@app.post("/status/bulk")
def status_bulk(body: BulkStatusInteractions):
    if supa_available():
        updated = bulk_interaction_status_supa(body.ids, body.status, service=True)
        return {"updated": updated}
    return {"updated": 0}


@app.get("/search")
def search(q: str, limit: int = 50):
    if supa_available():
        return search_all_supa(q, limit, service=False)
    return []
