# Job Leads Web (React/Next.js)

React UI for the Job Leads tool. Reads from the FastAPI at `NEXT_PUBLIC_API_URL` and performs mutations via server actions.

Setup
- `cp .env.local.example .env.local` and adjust URL if needed
- `npm install`
- `npm run dev` (http://localhost:3000)

Notes
- Ensure the API is running: `make -C ../job-leads run-api`
- The UI calls: `/jobs`, `/leads/{id}`, `/run-scrape`, `/actions/*`

