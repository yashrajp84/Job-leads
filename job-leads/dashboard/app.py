from __future__ import annotations

import os
import sqlite3
from typing import Any, Dict, List

import httpx
import pandas as pd
import streamlit as st

DB_PATH = os.environ.get("JOB_LEADS_DB", "out/jobs.sqlite")
API_URL = os.environ.get("JOB_LEADS_API", "http://localhost:8000")


def load_jobs_via_api(params: dict) -> List[dict] | None:
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(f"{API_URL}/jobs", params=params)
            if r.status_code == 200:
                return r.json()
    except Exception:
        return None
    return None


def load_jobs_via_db() -> List[dict]:
    try:
        con = sqlite3.connect(DB_PATH)
        jobs = pd.read_sql_query("SELECT * FROM jobs ORDER BY collected_at DESC", con).to_dict(
            orient="records"
        )
        con.close()
        return jobs
    except Exception:
        return []


def api_post(path: str, json: dict) -> bool:
    try:
        r = httpx.post(f"{API_URL}{path}", json=json, timeout=10.0)
        return r.status_code // 100 == 2
    except Exception:
        return False


st.set_page_config(page_title="Job Leads", layout="wide")
st.title("Job Leads Dashboard")

with st.sidebar:
    st.header("Filters")
    q = st.text_input("Keywords")
    source = st.selectbox("Source", ["", "greenhouse", "lever", "remoteok", "weworkremotely"], index=0)
    location = st.text_input("Location contains")
    status = st.selectbox("Status", ["", "new", "applied", "interview", "offer", "archived"], index=0)
    st.divider()
    st.write("Data actions")
    if st.button("Run scrape now"):
        ok = api_post("/run-scrape", json={})
        st.success("Scrape triggered" if ok else "Failed to trigger scrape")

params = {
    "q": q or None,
    "source": source or None,
    "location": location or None,
    "status": status or None,
    "limit": 500,
}

jobs = load_jobs_via_api(params)
if jobs is None:
    st.warning("API not reachable; reading DB directly.")
    jobs = load_jobs_via_db()

df = pd.DataFrame(jobs)
if df.empty:
    st.info("No jobs yet. Try running a scrape.")
    st.stop()

# Simple table view
cols = ["id", "title", "company", "location", "source", "posted_at", "url"]
for c in cols:
    if c not in df.columns:
        df[c] = ""

st.dataframe(df[cols], height=400)

# Select a job to edit lead
st.subheader("Lead Details")
selected_id = st.selectbox("Select job", df["id"].tolist())
selected_row = df[df["id"] == selected_id].iloc[0].to_dict()
st.write(f"Selected: {selected_row['title']} — {selected_row['company']}")

with st.form("lead_form"):
    status_val = st.selectbox("Status", ["new", "applied", "interview", "offer", "archived"], index=0)
    score_val = st.number_input("Score", value=0)
    fav_val = st.checkbox("Favourite", value=False)
    resume_url = st.text_input("Resume URL", value="")
    cover_url = st.text_input("Cover Letter URL", value="")
    next_action = st.text_input("Next Action", value="")
    next_action_date = st.text_input("Next Action Date (ISO)", value="")
    notes = st.text_area("Notes", value="")
    submitted = st.form_submit_button("Save Lead")
    if submitted:
        payload = {
            "status": status_val,
            "score": int(score_val),
            "favourite": bool(fav_val),
            "resume_url": resume_url,
            "cover_letter_url": cover_url,
            "next_action": next_action,
            "next_action_date": next_action_date,
            "notes": notes,
        }
        ok = api_post(f"/leads/{selected_id}", json=payload)
        st.success("Saved" if ok else "Failed to save")

st.subheader("Add Manual Lead")
with st.form("manual_lead"):
    m_title = st.text_input("Title")
    m_company = st.text_input("Company")
    m_url = st.text_input("URL")
    m_location = st.text_input("Location")
    m_source = st.text_input("Source", value="manual")
    add = st.form_submit_button("Add")
    if add and m_url:
        mid = __import__("hashlib").sha1(m_url.encode()).hexdigest()
        # Create/update stub job then create lead
        ok_job = api_post(
            "/jobs",
            json={
                "id": mid,
                "title": m_title,
                "company": m_company,
                "url": m_url,
                "location": m_location,
                "source": m_source or "manual",
            },
        )
        ok = ok_job and api_post(f"/leads/{mid}", json={"status": "new"})
        if ok:
            st.success("Manual lead added (lead created)")
        else:
            st.warning("Could not add via API. Consider adding via DB.")

st.subheader("Export CSV")
export_cols = [c for c in df.columns if c in [
    "id","title","company","location","salary","tags","posted_at","url","source","collected_at","description"
]]
st.download_button(
    label="Download current jobs.csv",
    data=df[export_cols].to_csv(index=False).encode("utf-8"),
    file_name="jobs.csv",
    mime="text/csv",
)
