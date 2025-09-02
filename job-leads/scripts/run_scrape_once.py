from __future__ import annotations

from job_agent.orchestrator import load_config, run_scrape


def main():
    cfg = load_config("config.yaml")
    all_c, filt_c, uniq_c, new_jobs = run_scrape(cfg)
    print(f"Done. all={all_c} filtered={filt_c} unique={uniq_c} new={len(new_jobs)}")


if __name__ == "__main__":
    main()

