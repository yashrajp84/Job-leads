export const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {'Content-Type': 'application/json', ...(init?.headers||{})},
  })
  if (!r.ok) throw new Error(await r.text())
  return r.json() as Promise<T>
}

export const api = {
  feed: () => http<any[]>(`/feed`),
  search: (q: string) => http<any[]>(`/search?q=${encodeURIComponent(q)}`),
  clip: (body: any) => http(`/clip`, {method:'POST', body: JSON.stringify(body)}),
  suggest: (body: any) => http<{draft: string}>(`/llm/suggest`, {method:'POST', body: JSON.stringify(body)}),
}

