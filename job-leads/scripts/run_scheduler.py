from __future__ import annotations

import os
import time
from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

from job_agent.notify import notify_new_jobs
from job_agent.orchestrator import load_config, run_scrape


def job():
    cfg = load_config("config.yaml")
    all_c, filt_c, uniq_c, new_jobs = run_scrape(cfg)
    notify_new_jobs(new_jobs, cfg)
    print(
        f"[{datetime.now(timezone.utc).isoformat()}] scrape done: all={all_c} filtered={filt_c} unique={uniq_c} new={len(new_jobs)}"
    )


def main():
    load_dotenv()
    cfg = load_config("config.yaml")
    cron = cfg.get("schedule_cron", "0 */6 * * *")
    scheduler = BackgroundScheduler(timezone="UTC")
    # run once on start
    job()
    # schedule cron
    scheduler.add_job(job, "cron", **{k: v for k, v in zip(["minute", "hour", "day", "month", "day_of_week"], cron.split())})
    scheduler.start()
    print("Scheduler started. Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()


if __name__ == "__main__":
    main()

