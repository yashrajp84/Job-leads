from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterable, Sequence

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from .models import Base, Job, Lead
from .utils import ensure_dir, now_iso


DEFAULT_DB_PATH = os.environ.get("JOB_LEADS_DB", "out/jobs.sqlite")
ensure_dir(os.path.dirname(DEFAULT_DB_PATH))

engine = create_engine(f"sqlite:///{DEFAULT_DB_PATH}", future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    Base.metadata.create_all(engine)


@contextmanager
def get_session() -> Iterable[Session]:
    init_db()
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def upsert_job(session: Session, data: dict) -> Job:
    job = session.get(Job, data["id"])  # type: ignore
    if job is None:
        job = Job(**data)
        session.add(job)
    else:
        # Update fields that belong to the job record only
        for k in [
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
        ]:
            setattr(job, k, data.get(k, getattr(job, k)))
    return job


def upsert_lead(session: Session, lead_id: str, data: dict) -> Lead:
    lead = session.get(Lead, lead_id)  # type: ignore
    if lead is None:
        lead = Lead(id=lead_id, updated_at=now_iso(), **data)
        session.add(lead)
    else:
        for k, v in data.items():
            setattr(lead, k, v)
        lead.updated_at = now_iso()
    return lead


def get_new_job_ids_since(session: Session, iso_timestamp: str) -> Sequence[str]:
    stmt = select(Job.id).where(Job.collected_at > iso_timestamp)
    rows = session.execute(stmt).scalars().all()
    return rows

