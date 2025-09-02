import { Filters, Job, Lead } from "./types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}

export async function fetchJobs(filters: Filters): Promise<Job[]> {
  const params = new URLSearchParams();
  if (filters.q) params.set("q", filters.q);
  if (filters.source) params.set("source", filters.source);
  if (filters.location) params.set("location", filters.location);
  if (filters.status) params.set("status", filters.status);
  params.set("limit", "500");
  return http<Job[]>(`/jobs?${params.toString()}`);
}

export async function updateLead(id: string, fields: Partial<Lead>): Promise<void> {
  await http(`/leads/${id}`, { method: "POST", body: JSON.stringify(fields) });
}

export async function runScrape(): Promise<void> {
  await http(`/run-scrape`, { method: "POST", body: JSON.stringify({}) });
}

export async function bulkStatus(ids: string[], status: string): Promise<number> {
  const res = await http<{ updated: number }>(`/actions/bulk_status`, {
    method: "POST",
    body: JSON.stringify({ ids, status }),
  });
  return res.updated;
}

export async function rescore(ids?: string[]): Promise<number> {
  const res = await http<{ updated: number }>(`/actions/rescore`, {
    method: "POST",
    body: JSON.stringify({ ids }),
  });
  return res.updated;
}

