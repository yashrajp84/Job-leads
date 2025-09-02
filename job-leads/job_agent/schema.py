from __future__ import annotations

from typing import Optional

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
    q: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    location: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    limit: int = 100
    offset: int = 0


class UpsertLead(BaseModel):
    status: Optional[str] = None
    score: Optional[int] = None
    favourite: Optional[bool] = None
    resume_url: Optional[str] = None
    cover_letter_url: Optional[str] = None
    next_action: Optional[str] = None
    next_action_date: Optional[str] = None
    notes: Optional[str] = None
