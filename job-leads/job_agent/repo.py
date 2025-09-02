from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List, Sequence, Set

from .supa import get_supa_client

JOBS = "jobs"
LEADS = "leads"
PEOPLE = "people"
POSTS = "posts"
INTERACTIONS = "interactions"
TEMPLATES = "templates"


def upsert_jobs_supa(records: Iterable[Dict], service: bool = True) -> List[str]:
    client = get_supa_client(service=service)
    up = []
    for r in records:
        up.append(
            {
                "id": r["id"],
                "title": r.get("title", ""),
                "company": r.get("company", ""),
                "location": r.get("location", ""),
                "salary": r.get("salary", ""),
                "tags": r.get("tags", ""),
                "posted_at": r.get("posted_at") or None,
                "url": r.get("url", ""),
                "source": r.get("source", ""),
                "collected_at": r.get("collected_at"),
                "description": r.get("description", ""),
            }
        )
    if not up:
        return []
    resp = client.table(JOBS).upsert(up, on_conflict="id").execute()
    return [row["id"] for row in (resp.data or [])]


def ensure_leads_supa(ids: List[str], service: bool = True) -> None:
    client = get_supa_client(service=service)
    if not ids:
        return
    existing = client.table(LEADS).select("id").in_("id", ids).execute()
    have = {row["id"] for row in (existing.data or [])}
    new_rows = [{"id": i} for i in ids if i not in have]
    if new_rows:
        client.table(LEADS).insert(new_rows).execute()


def bulk_status_supa(ids: List[str], status: str, service: bool = True) -> int:
    client = get_supa_client(service=service)
    if not ids:
        return 0
    ensure_leads_supa(ids, service=service)
    resp = (
        client.table(LEADS)
        .update({"status": status, "updated_at": datetime.utcnow().isoformat()})
        .in_("id", ids)
        .execute()
    )
    return len(resp.data or [])


def bulk_scores_supa(id_to_score: Dict[str, int], service: bool = True) -> int:
    client = get_supa_client(service=service)
    if not id_to_score:
        return 0
    ensure_leads_supa(list(id_to_score.keys()), service=service)
    count = 0
    items = list(id_to_score.items())
    for i in range(0, len(items), 500):
        batch = items[i : i + 500]
        for _id, sc in batch:
            client.table(LEADS).update(
                {"score": int(sc), "updated_at": datetime.utcnow().isoformat()}
            ).eq("id", _id).execute()
            count += 1
    return count


def get_jobs_by_ids_supa(ids: List[str], service: bool = False):
    client = get_supa_client(service=service)
    if not ids:
        return []
    resp = client.table(JOBS).select("*").in_("id", ids).execute()
    return resp.data or []


def get_existing_ids_supa(ids: List[str], service: bool = True) -> Set[str]:
    client = get_supa_client(service=service)
    if not ids:
        return set()
    resp = client.table(JOBS).select("id").in_("id", ids).execute()
    return {row["id"] for row in (resp.data or [])}


def query_jobs_supa(filters: dict, service: bool = False):
    client = get_supa_client(service=service)
    q = client.table(JOBS).select("*")
    if kw := filters.get("q"):
        pat = f"%{kw}%"
        # OR across several columns
        q = q.or_(f"title.ilike.{pat},company.ilike.{pat},tags.ilike.{pat},description.ilike.{pat}")
    if src := filters.get("source"):
        if isinstance(src, str):
            q = q.eq("source", src)
        elif isinstance(src, (list, tuple)):
            q = q.in_("source", src)
    if loc := filters.get("location"):
        q = q.ilike("location", f"%{loc}%")
    if date_from := filters.get("date_from"):
        q = q.gte("collected_at", date_from)
    if date_to := filters.get("date_to"):
        q = q.lte("collected_at", date_to)
    lim = int(filters.get("limit", 100))
    off = int(filters.get("offset", 0))
    resp = q.order("collected_at", desc=True).range(off, off + lim - 1).execute()
    return resp.data or []


def get_leads_supa(filters: dict | None = None, service: bool = False):
    client = get_supa_client(service=service)
    q = client.table(LEADS).select("*")
    if filters and (st := filters.get("status")):
        q = q.eq("status", st)
    resp = q.execute()
    return resp.data or []


def upsert_leads_fields_supa(id: str, fields: dict, service: bool = True):
    client = get_supa_client(service=service)
    ensure_leads_supa([id], service=service)
    fields = {**fields, "updated_at": datetime.utcnow().isoformat()}
    return client.table(LEADS).update(fields).eq("id", id).execute().data or []


# People/Posts/Interactions/Templates helpers
def upsert_person_supa(person: dict, service: bool = True):
    client = get_supa_client(service=service)
    data = {
        "id": person.get("id"),
        "platform": person.get("platform", "linkedin"),
        "full_name": person.get("full_name", ""),
        "headline": person.get("headline", ""),
        "company": person.get("company", ""),
        "location": person.get("location", ""),
        "profile_url": person.get("profile_url", ""),
        "tags": person.get("tags", ""),
        "source": person.get("source", "clipper"),
        "notes": person.get("notes", ""),
    }
    resp = client.table(PEOPLE).upsert(data).execute()
    return (resp.data or [])[0] if resp.data else data


def upsert_post_supa(post: dict, service: bool = True):
    client = get_supa_client(service=service)
    data = {
        "id": post.get("id"),
        "platform": post.get("platform", "linkedin"),
        "author_id": post.get("author_id"),
        "url": post.get("url", ""),
        "text": post.get("text", ""),
        "hashtags": post.get("hashtags", ""),
        "posted_at": post.get("posted_at"),
        "meta": post.get("meta", {}),
    }
    resp = client.table(POSTS).upsert(data).execute()
    return (resp.data or [])[0] if resp.data else data


def upsert_interaction_supa(data: dict, service: bool = True):
    client = get_supa_client(service=service)
    payload = {k: v for k, v in data.items() if k in {
        "id","entity_type","entity_id","status","score","pinned","next_action","next_action_date","notes"
    }}
    if payload.get("id"):
        resp = client.table(INTERACTIONS).update(payload).eq("id", payload["id"]).execute()
    else:
        resp = client.table(INTERACTIONS).insert(payload).execute()
    return (resp.data or [])[0] if resp.data else None


def bulk_interaction_status_supa(ids: List[str], status: str, service: bool = True) -> int:
    client = get_supa_client(service=service)
    if not ids:
        return 0
    resp = client.table(INTERACTIONS).update({"status": status}).in_("id", ids).execute()
    return len(resp.data or [])


def list_latest_people_supa(limit: int = 50, service: bool = False):
    client = get_supa_client(service=service)
    return client.table(PEOPLE).select("*").order("updated_at", desc=True).limit(limit).execute().data or []


def list_latest_posts_supa(limit: int = 50, service: bool = False):
    client = get_supa_client(service=service)
    return client.table(POSTS).select("*").order("created_at", desc=True).limit(limit).execute().data or []


def list_latest_jobs_supa(limit: int = 50, service: bool = False):
    client = get_supa_client(service=service)
    return client.table(JOBS).select("*").order("collected_at", desc=True).limit(limit).execute().data or []


def search_all_supa(q: str, limit: int = 50, service: bool = False):
    client = get_supa_client(service=service)
    resp = client.rpc("search_all", {"q": q, "lim": limit}).execute()
    return resp.data or []
