"""
Shared settings for every script in this folder.

We scrape three job postings from one company (Anthropic). They are all
software engineering roles at increasing seniority, so the numbers we get
back should line up in a way that makes sense.
"""
import os

# ---------------------------------------------------------------------------
# The three jobs we will scrape.
# The number is Greenhouse's internal job id; you can see it in the page URL.
# ---------------------------------------------------------------------------
COMPANY = "anthropic"

JOBS = {
    4981828008: "Senior+ Software Engineer, Research Tools",
    5304425008: "Staff Software Engineer, Labs: Applied AI",
    5157847008: "Staff+ Software Engineer, Platform",
}

# The page a human opens in a browser
WEB = "https://job-boards.greenhouse.io/{company}/jobs/{job_id}"

# The hidden address that returns the SAME job as data instead of as a page
API = ("https://boards-api.greenhouse.io/v1/boards/{company}/jobs/{job_id}"
       "?pay_transparency=true")

# The whole board at once - every job the company has open, in one request
BOARD_API = ("https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
             "?content=true&pay_transparency=true")

# ---------------------------------------------------------------------------
# Always identify yourself. A User-Agent header tells the server who is
# calling. It is polite, and some servers reject requests without one.
# ---------------------------------------------------------------------------
HEADERS = {"User-Agent": "CEMFI CSS-DataScience teaching example (student)"}

# ---------------------------------------------------------------------------
# Use ONE Session for all your requests.
#
# Every fresh https:// connection costs a handshake with the server, which is
# slow. A Session keeps the connection open and reuses it, so the second and
# third requests are much faster than the first. It also remembers your
# headers and cookies for you.
#
#   requests.get(url)        -> new connection every single time
#   session.get(url)         -> reuses the open one
# ---------------------------------------------------------------------------
import requests

SESSION = requests.Session()
SESSION.headers.update(HEADERS)

# ---------------------------------------------------------------------------
# Selenium stores its browser driver in ~/.cache/selenium. On some machines
# ~/.cache already exists as a FILE, which makes Selenium fail with a
# confusing message. Pointing it somewhere else costs nothing and avoids it.
# ---------------------------------------------------------------------------
os.environ.setdefault(
    "SE_CACHE_PATH", os.path.join(os.path.expanduser("~"), "selenium_cache")
)


def url_web(job_id):
    return WEB.format(company=COMPANY, job_id=job_id)


def url_api(job_id):
    return API.format(company=COMPANY, job_id=job_id)


def url_board():
    return BOARD_API.format(company=COMPANY)


def show(rows, header="RESULT"):
    """Print a list of dicts as a small table, without needing pandas."""
    print("\n" + "=" * 78)
    print(header)
    print("=" * 78)
    for r in rows:
        lo, hi = r["lo"], r["hi"]
        width = 100 * (hi - lo) / ((hi + lo) / 2)
        print(f"  {r['title'][:44]:46s} ${lo:>9,.0f} - ${hi:>9,.0f}   "
              f"width {width:4.1f}%")
