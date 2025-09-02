# Job Leads — Scraper, API, and Dashboard

Job Leads is a local-first toolkit to scrape job boards, normalize and score results, track leads, and browse/edit them via a small API and Streamlit dashboard.

This project targets Python 3.11 on macOS/Linux. No Docker required.

## Quick Start

1) Create and activate a virtualenv, then install deps:

```
make -C job-leads setup
```

2) Run a scrape once (creates `out/jobs.sqlite` and `out/jobs.csv`):

```
make -C job-leads run-scrape
```

3) Start the API (http://localhost:8000):

```
make -C job-leads run-api
```

4) Start the Streamlit dashboard:

```
make -C job-leads run-dashboard
```

5) (Optional) Run the scheduler that scrapes on an interval and sends notifications for new jobs:

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

Set secrets in `.env` (copy `.env.example`):

- `SLACK_WEBHOOK_URL`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `SMTP_FROM`, `NOTIFY_EMAIL`

## Caveats

- Respect sites' Terms of Service and robots.txt. This project only uses public endpoints/pages and a polite User-Agent with minimal throttling.
- Network errors are handled gracefully and logged; the scraper will continue processing other sites.

## Development

- Format and lint: `make -C job-leads fmt && make -C job-leads lint`
- Tests: `make -C job-leads test`

