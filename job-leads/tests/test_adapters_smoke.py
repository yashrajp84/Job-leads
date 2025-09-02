import os
from types import SimpleNamespace

import pytest


class DummyResp:
    def __init__(self, text=None, json_data=None, status_code=200):
        self.text = text
        self._json = json_data
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception("error")

    def json(self):
        return self._json


def test_greenhouse_smoke(monkeypatch):
    from job_agent.adapters import greenhouse

    def fake_get(url, headers=None, timeout=None):
        return DummyResp(json_data={
            "jobs": [
                {
                    "absolute_url": "https://boards.greenhouse.io/org/jobs/1",
                    "title": "Designer",
                    "location": {"name": "Remote"},
                    "metadata": [],
                    "updated_at": "2024-01-01",
                    "content": "desc",
                }
            ]
        })

    monkeypatch.setattr(greenhouse.requests, "get", fake_get)
    out = greenhouse.fetch_jobs("org", {})
    assert isinstance(out, list) and out and set(
        ["id", "title", "company", "location", "url", "source", "collected_at", "description"]
    ).issubset(out[0].keys())


def test_lever_smoke(monkeypatch):
    from job_agent.adapters import lever

    def fake_get(url, headers=None, timeout=None):
        return DummyResp(json_data=[
            {
                "hostedUrl": "https://jobs.lever.co/org/1",
                "text": "Designer",
                "categories": {"location": "Remote"},
                "tags": ["ux"],
                "createdAt": "2024-01-01",
                "descriptionPlain": "desc",
            }
        ])

    monkeypatch.setattr(lever.requests, "get", fake_get)
    out = lever.fetch_jobs("org", {})
    assert isinstance(out, list) and out and out[0]["source"] == "lever"


def test_remoteok_smoke(monkeypatch):
    from job_agent.adapters import remoteok

    html = """
    <table><tr class="job">
      <td><a class="preventLink" href="/r/123">link</a></td>
      <td><h2>Designer</h2></td>
      <td><h3>Acme</h3></td>
      <td><div class="location">Remote</div></td>
      <td><div class="tags"><a>ux</a></div></td>
      <td><time datetime="2024-01-01"></time></td>
    </tr></table>
    """

    def fake_get(url, headers=None, timeout=None):
        return DummyResp(text=html)

    monkeypatch.setattr(remoteok.requests, "get", fake_get)
    out = remoteok.fetch_jobs("designer", {})
    assert isinstance(out, list) and out and out[0]["source"] == "remoteok"


def test_wwr_smoke(monkeypatch):
    from job_agent.adapters import weworkremotely as wwr

    html = """
    <section class="jobs">
      <li>
        <a href="/remote-jobs/123"></a>
        <span class="company">Acme</span>
        <span class="title">Designer</span>
        <span class="region">Remote</span>
        <span class="tag">ux</span>
      </li>
    </section>
    """

    def fake_get(url, headers=None, timeout=None):
        return DummyResp(text=html)

    monkeypatch.setattr(wwr.requests, "get", fake_get)
    out = wwr.fetch_jobs("designer", {})
    assert isinstance(out, list) and out and out[0]["source"] == "weworkremotely"

