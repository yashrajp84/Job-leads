import os
from supabase import create_client, Client


def get_supa_client(service: bool = False) -> Client:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY" if service else "SUPABASE_ANON_KEY")
    if not url or not key:
        raise RuntimeError("Missing SUPABASE_URL or key env")
    return create_client(url, key)

