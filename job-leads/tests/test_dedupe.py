import os


def test_dedupe(tmp_path, monkeypatch):
    # Use a temporary sqlite file for this test
    dbfile = tmp_path / "test.sqlite"
    monkeypatch.setenv("JOB_LEADS_DB", str(dbfile))

    from job_agent.db import get_session, init_db, upsert_job
    from job_agent.models import Job

    init_db()
    j = {
        "id": "abc",
        "title": "Designer",
        "company": "Acme",
        "location": "Remote",
        "salary": "",
        "tags": "ux,ui",
        "posted_at": "",
        "url": "https://acme.test/jobs/1",
        "source": "test",
        "collected_at": "2024-01-01T00:00:00+00:00",
        "description": "",
    }
    with get_session() as s:
        upsert_job(s, j)
        upsert_job(s, j)

    with get_session() as s:
        rows = s.query(Job).all()
        assert len(rows) == 1

