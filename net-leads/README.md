# Net-Leads

React (Vite + TS + Tailwind + shadcn-style components) frontend for networking + jobs, backed by your existing FastAPI API and Supabase.

Env
- Create `apps/web/.env.local` with:

```
VITE_SUPABASE_URL=<your Supabase URL>
VITE_SUPABASE_ANON_KEY=<your anon key>
VITE_API_BASE=http://localhost:8000
```

Run
- Backend: `uvicorn api.main:app --reload --port 8000` (from job-leads)
- Frontend:
  - `cd apps/web`
  - `npm i`
  - `npm run dev`

Ollama
- Install Ollama; `ollama pull llama3:8b`

