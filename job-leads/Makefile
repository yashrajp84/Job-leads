.PHONY: setup fmt lint test run-api run-dashboard run-scrape run-scheduler

setup:
	python -m venv .venv && . .venv/bin/activate && pip install -U pip && pip install -r requirements.txt

fmt:
	. .venv/bin/activate && black . && isort .

lint:
	. .venv/bin/activate && flake8 .

test:
	. .venv/bin/activate && pytest -q

run-api:
	. .venv/bin/activate && uvicorn api.main:app --reload --port 8000

run-dashboard:
	. .venv/bin/activate && streamlit run dashboard/app.py

run-scrape:
	. .venv/bin/activate && python -m job_agent.orchestrator --config config.yaml

run-scheduler:
	. .venv/bin/activate && python scripts/run_scheduler.py

