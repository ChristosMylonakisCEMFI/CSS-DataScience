"""
METHOD 1 - the hidden data address (a "JSON endpoint")
===========================================================================

When you open a job page in your browser, the browser quietly asks the
server a SECOND question: "give me the data for this job". The server
answers with JSON - plain structured data, no colours, no layout.

If we ask that same question ourselves, we skip the web page entirely.
No HTML to dig through. The salary arrives as a number.

    python 01_json.py
"""
import json

from config import JOBS, SESSION, url_api, show


def scrape_one(job_id):
    # 1. Ask the server for this job, as data.
    response = SESSION.get(url_api(job_id), timeout=60)

    # 2. Always check you got what you expected. 200 means "OK".
    response.raise_for_status()

    # 3. .json() turns the reply into an ordinary Python dictionary.
    job = response.json()

    # 4. Now just read the fields we want out of the dictionary.
    #    pay_input_ranges is a LIST because a job can have several pay
    #    zones (one per city). Here we take the first.
    pay = job["pay_input_ranges"][0]

    return {
        "title": job["title"],
        "location": job["location"]["name"],
        # amounts arrive in cents, so divide by 100
        "lo": pay["min_cents"] / 100,
        "hi": pay["max_cents"] / 100,
        "currency": pay["currency_type"],
    }


if __name__ == "__main__":
    # Look at one raw reply first, so you can see what we are working with.
    raw = SESSION.get(url_api(list(JOBS)[0]), timeout=60).json()
    print("The fields the server gives us for one job:")
    print("  " + ", ".join(sorted(raw.keys())))
    print("\nThe part we care about:")
    print(json.dumps(raw["pay_input_ranges"][0], indent=2)[:400])

    rows = [scrape_one(job_id) for job_id in JOBS]
    show(rows, "METHOD 1: JSON endpoint")

    print("\n  Three requests, three answers, nothing parsed.")
