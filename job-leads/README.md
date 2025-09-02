# Job Leads — Scraper, API, and Dashboard

Job Leads is a local-first toolkit to scrape job boards, normalize and score results, track leads, and browse/edit them via a small API and Streamlit dashboard. It now supports Supabase Postgres as the primary datastore with RLS-enabled read-only public access and server-side writes using the Service Role key.

This project targets Python 3.11 on macOS/Linux. No Docker required.

## Quick Start

1) Create and activate a virtualenv, then install deps:

```
make -C job-leads setup
```

2) Set environment variables (copy `.env.example` → `.env`) and fill in Supabase keys. The Service Role key must only be set in the API/scheduler environment.

```
cp .env.example .env
# Fill SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY (server only)
```

3) Apply Supabase schema (via SQL editor or CLI) using `supabase/migrations/001_init.sql`.

4) Run a scrape once (writes to Supabase; local CSV/SQLite only if `use_sqlite: true` in config):

```
make -C job-leads run-scrape
```

5) Start the API (http://localhost:8000):

```
make -C job-leads run-api
```

6) Start the Streamlit dashboard:

```
make -C job-leads run-dashboard
```

7) (Optional) Run the scheduler that scrapes on an interval and sends notifications for new jobs:

```
make -C job-leads run-scheduler
```

## Configuration

Adjust `job-leads/config.yaml` to set:

- sites: which adapters to use
- include/exclude keywords and locations
- score rules
- outputs: CSV and SQLite path
- schedule cron
 - use_sqlite: dual-write to local CSV/SQLite if true

Set secrets in `.env` (copy `.env.example`):

- `SLACK_WEBHOOK_URL`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`, `NOTIFY_EMAIL`
- `SUPABASE_URL`, `SUPABASE_ANON_KEY` (safe for read-only clients), `SUPABASE_SERVICE_ROLE_KEY` (server-side only)

## Caveats

- Respect sites' Terms of Service and robots.txt. This project only uses public endpoints/pages and a polite User-Agent with minimal throttling.
- Network errors are handled gracefully and logged; the scraper will continue processing other sites.
- Never expose the Supabase Service Role key to the browser or public environments. It is used only by the API and scheduler processes to perform writes that bypass RLS.

## Development

- Format and lint: `make -C job-leads fmt && make -C job-leads lint`
- Tests: `make -C job-leads test`
