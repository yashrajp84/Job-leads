from types import SimpleNamespace

import pytest


class FakeTable:
    def __init__(self, name):
        self.name = name
        self.ops = []
        self._data = []
        self._filter = None

    # Chainable builders
    def upsert(self, rows, on_conflict=None):
        self.ops.append(("upsert", rows, on_conflict))
        self._data = rows
        return self

    def insert(self, rows):
        self.ops.append(("insert", rows))
        self._data = rows
        return self

    def update(self, fields):
        self.ops.append(("update", fields))
        self._update_fields = fields
        return self

    def select(self, cols="*"):
        self.ops.append(("select", cols))
        return self

    # Filters
    def in_(self, col, ids):
        self._filter = ("in", col, list(ids))
        return self

    def eq(self, col, val):
        self._filter = ("eq", col, val)
        return self

    def execute(self):
        # Minimal simulation based on ops for tests
        if self.name == "leads" and self.ops and self.ops[0][0] == "select" and self._filter and self._filter[0] == "in":
            # Return only the ids requested that we pretend exist (empty by default)
            return SimpleNamespace(data=[])
        if self.name == "jobs" and self.ops and self.ops[0][0] == "select" and self._filter and self._filter[0] == "in":
            return SimpleNamespace(data=[{"id": i} for i in self._filter[2]])
        # For insert/upsert/update just echo back rows
        return SimpleNamespace(data=self._data)


class FakeClient:
    def __init__(self):
        self.tables = {"jobs": FakeTable("jobs"), "leads": FakeTable("leads")}

    def table(self, name):
        return self.tables[name]


def test_upsert_jobs_calls_table(monkeypatch):
    from job_agent import repo

    fake = FakeClient()
    monkeypatch.setattr(repo, "get_supa_client", lambda service=True: fake)
    ids = repo.upsert_jobs_supa([
        {"id": "a", "title": "t", "company": "c", "url": "u", "source": "s", "collected_at": "now"}
    ])
    assert ids == ["a"]
    assert fake.tables["jobs"].ops[0][0] == "upsert"


def test_ensure_leads_inserts_missing(monkeypatch):
    from job_agent import repo

    fake = FakeClient()
    monkeypatch.setattr(repo, "get_supa_client", lambda service=True: fake)
    repo.ensure_leads_supa(["a", "b"], service=True)
    # Should attempt to insert 2 ids because select returns empty
    ops = fake.tables["leads"].ops
    assert any(op[0] == "insert" for op in ops)


def test_bulk_status_updates(monkeypatch):
    from job_agent import repo

    fake = FakeClient()
    monkeypatch.setattr(repo, "get_supa_client", lambda service=True: fake)
    updated = repo.bulk_status_supa(["a", "b"], "Applied", service=True)
    assert updated >= 0
    # Update op recorded
    assert any(op[0] == "update" for op in fake.tables["leads"].ops)

