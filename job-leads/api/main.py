from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import and_, select

from job_agent.db import get_session, init_db, upsert_job, upsert_lead
from job_agent.models import Job, Lead
from job_agent.orchestrator import load_config, run_scrape
from job_agent.schema import FilterQuery, JobModel, LeadModel, UpsertLead
from job_agent.utils import now_iso, url_hash

app = FastAPI(title="Job Leads API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    init_db()
    with get_session() as session:
        stmt = select(Job)
        conditions = []
        if q:
            pattern = f"%{q.lower()}%"
            # SQLite lower() works on ASCII; acceptable for our case.
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

        # Join with leads if available
        lead_rows = {l.id: l for l in session.execute(select(Lead)).scalars().all()}

        if status:
            rows = [r for r in rows if (lead_rows.get(r.id) and lead_rows[r.id].status == status)]

        out = []
        for j in rows:
            jd = {c: getattr(j, c) for c in JobModel.model_fields.keys()}
            ld = lead_rows.get(j.id)
            if ld:
                jd.update({
                    "lead": {
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
                })
            out.append(jd)
        return out


@app.get("/leads")
def get_leads():
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
    init_db()
    with get_session() as session:
        data = (payload.model_dump(exclude_unset=True) if payload else {})
        lead = upsert_lead(session, lead_id, data)
        return {"ok": True, "id": lead.id}


@app.patch("/leads/{lead_id}")
def patch_lead(lead_id: str, payload: UpsertLead):
    init_db()
    with get_session() as session:
        data = payload.model_dump(exclude_unset=True)
        lead = upsert_lead(session, lead_id, data)
        return {"ok": True, "id": lead.id}


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
    id: str | None = None
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
    init_db()
    data = payload.model_dump()
    if not data.get("id"):
        data["id"] = url_hash(data.get("url", ""))
    data.setdefault("collected_at", now_iso())
    with get_session() as session:
        job = upsert_job(session, data)
        return {"ok": True, "id": job.id}
