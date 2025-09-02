from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class JobModel(BaseModel):
    id: str
    title: str = ""
    company: str = ""
    location: str = ""
    salary: str = ""
    tags: str = ""
    posted_at: str = ""
    url: str = ""
    source: str = ""
    collected_at: str = ""
    description: str = ""


class LeadModel(BaseModel):
    id: str
    status: str = "new"
    score: int = 0
    favourite: bool = False
    resume_url: str = ""
    cover_letter_url: str = ""
    next_action: str = ""
    next_action_date: str = ""
    notes: str = ""
    updated_at: str = ""


class FilterQuery(BaseModel):
    q: str | None = None
    status: str | None = None
    source: str | None = None
    location: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    limit: int = 100
    offset: int = 0


class UpsertLead(BaseModel):
    status: str | None = None
    score: int | None = None
    favourite: bool | None = None
    resume_url: str | None = None
    cover_letter_url: str | None = None
    next_action: str | None = None
    next_action_date: str | None = None
    notes: str | None = None

