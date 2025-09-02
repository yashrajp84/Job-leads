from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)  # hash of URL
    title: Mapped[str] = mapped_column(String(300), default="")
    company: Mapped[str] = mapped_column(String(200), default="")
    location: Mapped[str] = mapped_column(String(200), default="")
    salary: Mapped[str] = mapped_column(String(200), default="")
    tags: Mapped[str] = mapped_column(String(400), default="")
    posted_at: Mapped[str] = mapped_column(String(64), default="")  # ISO string or empty
    url: Mapped[str] = mapped_column(Text, default="")
    source: Mapped[str] = mapped_column(String(64), default="")
    collected_at: Mapped[str] = mapped_column(String(64), default="")
    description: Mapped[str] = mapped_column(Text, default="")


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)  # job id
    status: Mapped[str] = mapped_column(String(40), default="new")
    score: Mapped[int] = mapped_column(Integer, default=0)
    favourite: Mapped[bool] = mapped_column(Boolean, default=False)
    resume_url: Mapped[str] = mapped_column(Text, default="")
    cover_letter_url: Mapped[str] = mapped_column(Text, default="")
    next_action: Mapped[str] = mapped_column(String(120), default="")
    next_action_date: Mapped[str] = mapped_column(String(64), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[str] = mapped_column(String(64), default="")

