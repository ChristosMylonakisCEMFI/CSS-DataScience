"""
FROM 3 JOBS TO ~10,000 - what changes when you scale up
===========================================================================

Three jobs is a demonstration. A dataset needs thousands. Going from one to
the other introduces four problems that did not exist before:

  1. Some boards do not exist  -> handle errors, never crash the whole run
  2. Waiting is the bottleneck -> do several requests at once (threads)
  3. Re-running wastes time    -> cache raw replies to disk
  4. You are a guest           -> identify yourself, do not hammer the server

    python 05_scale_up.py             # uses the cache if present
    python 05_scale_up.py --fresh     # ignore the cache and re-download

Output: data/postings.csv
"""
import argparse
import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from config import SESSION, BOARD_API

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
CACHE = os.path.join(DATA, "cache")

# A hand-written list of companies known to use Greenhouse. In a real project
# you would discover these automatically; typing a few hundred is fine here.
COMPANIES = """
stripe airbnb coinbase doordash instacart robinhood databricks figma notion asana
dropbox lyft pinterest reddit twitch cloudflare datadog snowflake gitlab hashicorp
elastic mongodb confluent twilio okta plaid brex ramp affirm chime marqeta
betterment wealthfront sofi carta benchling duolingo coursera squarespace webflow
vercel mixpanel amplitude sentry launchdarkly pagerduty retool airtable smartsheet
monday clickup linear front intercom zendesk discord roblox unity peloton whoop
strava calm noom hims faire flexport samsara verkada anduril zipline joby archer
opendoor compass redfin gusto rippling deel remote justworks checkr lattice
bamboohr attentive klaviyo braze iterable yelp nextdoor warbyparker glossier
sweetgreen wework grammarly canva miro loom anthropic scaleai huggingface
upstart lendingclub hopper turo lime ironclad clio sourcegraph replit
""".split()


def cache_path(company):
    return os.path.join(CACHE, f"{company}.json")


def fetch_board(company, use_cache=True):
    """Download one company's whole board. Returns a list of jobs (maybe empty).

    Note the bare `except`: with hundreds of companies, something WILL fail -
    a typo in a name, a company that closed, a momentary network blip. One
    failure must not stop the other 199.
    """
    path = cache_path(company)
    if use_cache and os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)

    try:
        r = SESSION.get(BOARD_API.format(company=company), timeout=45)
        if r.status_code != 200:
            return []                      # e.g. 404: no such board
        jobs = r.json().get("jobs", [])
    except Exception:
        return []                          # timeout, bad JSON, connection reset

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(jobs, fh)
    return jobs


REMOTE = re.compile(r"\bremote\b|\banywhere\b", re.I)


def flatten(company, jobs):
    """Turn the nested JSON into flat rows, one per (job, pay zone)."""
    rows = []
    for j in jobs:
        location = (j.get("location") or {}).get("name", "") or ""
        ranges = j.get("pay_input_ranges") or []
        base = {
            "company": j.get("company_name") or company,
            "job_id": j.get("id"),
            "title": (j.get("title") or "").strip(),
            "location": location.strip(),
            "department": (j.get("departments") or [{}])[0].get("name", ""),
            "first_published": j.get("first_published"),
            "n_zones": len(ranges),
            "is_remote": bool(REMOTE.search(location)),
        }
        if not ranges:
            rows.append({**base, "lo": None, "hi": None,
                         "currency": None, "zone": None})
        for p in ranges:
            rows.append({**base,
                         "lo": (p.get("min_cents") or 0) / 100,
                         "hi": (p.get("max_cents") or 0) / 100,
                         "currency": p.get("currency_type"),
                         "zone": (p.get("title") or "").strip()})
    return rows


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fresh", action="store_true", help="ignore the cache")
    ap.add_argument("--workers", type=int, default=8,
                    help="how many downloads to run at once (keep this modest)")
    args = ap.parse_args()

    os.makedirs(CACHE, exist_ok=True)
    companies = sorted(set(COMPANIES))
    print(f"Fetching {len(companies)} company boards "
          f"with {args.workers} workers...\n")

    start = time.time()
    all_rows, live = [], 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs_per_company = pool.map(
            lambda c: (c, fetch_board(c, use_cache=not args.fresh)), companies)
        for i, (company, jobs) in enumerate(jobs_per_company, start=1):
            if jobs:
                live += 1
                all_rows.extend(flatten(company, jobs))
            if i % 25 == 0:
                print(f"  {i:3d}/{len(companies)} boards | "
                      f"{len(all_rows):,} rows so far")

    df = pd.DataFrame(all_rows)
    os.makedirs(DATA, exist_ok=True)
    out = os.path.join(DATA, "postings.csv")
    df.to_csv(out, index=False)

    unique_jobs = df.drop_duplicates("job_id")
    print(f"\nDone in {time.time()-start:.0f}s")
    print(f"  boards that answered : {live}/{len(companies)}")
    print(f"  postings             : {len(unique_jobs):,}")
    print(f"  with a salary range  : {(unique_jobs.n_zones>0).sum():,} "
          f"({100*(unique_jobs.n_zones>0).mean():.0f}%)")
    print(f"  posting >1 pay zone  : {(unique_jobs.n_zones>1).sum():,}")
    print(f"\n  saved -> {os.path.relpath(out, HERE)}")
    print("  (raw replies cached in data/cache/ - re-running is instant)")
