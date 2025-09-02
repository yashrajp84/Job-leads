from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from typing import Iterable, List

import requests

from .schema import JobModel


def send_slack(text: str, webhook_url: str | None) -> bool:
    if not webhook_url:
        return False
    try:
        resp = requests.post(webhook_url, json={"text": text}, timeout=20)
        return resp.status_code // 100 == 2
    except Exception:
        return False


def send_email(subject: str, body: str, to_email: str | None, *, host: str | None, port: int | None, user: str | None, password: str | None, from_email: str | None) -> bool:
    if not to_email or not host or not from_email:
        return False
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email
    msg.set_content(body)
    try:
        with smtplib.SMTP(host, port or 587, timeout=20) as s:
            s.starttls()
            if user and password:
                s.login(user, password)
            s.send_message(msg)
        return True
    except Exception:
        return False


def notify_new_jobs(new_jobs: list[JobModel], cfg: dict, env: dict | None = None) -> dict:
    env = env or os.environ
    webhook = env.get("SLACK_WEBHOOK_URL")
    notify_email = env.get("NOTIFY_EMAIL")
    smtp_host = env.get("SMTP_HOST")
    smtp_port = int(env.get("SMTP_PORT", "587")) if env.get("SMTP_PORT") else None
    smtp_user = env.get("SMTP_USER")
    smtp_pass = env.get("SMTP_PASS")
    smtp_from = env.get("SMTP_FROM")

    total = len(new_jobs)
    if total == 0:
        return {"slack": False, "email": False}

    top = new_jobs[:5]
    lines = [f"New jobs: {total}"] + [f"• {j.title} — {j.company} — {j.url}" for j in top]
    text = "\n".join(lines)

    slack_ok = send_slack(text, webhook)

    email_ok = send_email(
        subject=f"Job Leads: {total} new",
        body=text,
        to_email=notify_email,
        host=smtp_host,
        port=smtp_port,
        user=smtp_user,
        password=smtp_pass,
        from_email=smtp_from,
    )

    return {"slack": slack_ok, "email": email_ok}

