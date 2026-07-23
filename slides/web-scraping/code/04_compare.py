"""
ALL THREE, SIDE BY SIDE - do they agree, and what does each one cost?
===========================================================================

    python 04_compare.py

The interesting result is not that JSON is a bit faster per job. It is the
last block: the JSON endpoint can hand us the ENTIRE board in one request,
which the other two methods can never do.
"""
import importlib.util
import os
import time

from config import JOBS, COMPANY, SESSION, url_board, show

HERE = os.path.dirname(os.path.abspath(__file__))


def load(filename):
    """Import a module whose filename starts with a digit.

    Python's normal `import 01_json` is a syntax error, so we load the file
    by path instead. Nothing deep here - just a naming inconvenience.
    """
    name = filename.replace(".py", "")
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, filename))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


m_json = load("01_json.py")
m_soup = load("02_beautifulsoup.py")
m_selenium = load("03_selenium.py")


REPEATS = 3      # one timing is mostly network noise; take the median of a few


def timed(fn, repeats=REPEATS):
    """Run fn several times, return its output and the MEDIAN elapsed time.

    Timing a single run of anything that touches the network tells you very
    little: the same code can be twice as slow simply because a packet took
    a detour. Repeating and taking the median removes most of that.
    """
    durations, out = [], None
    for _ in range(repeats):
        start = time.time()
        out = fn()
        durations.append(time.time() - start)
    durations.sort()
    return out, durations[len(durations) // 2]


if __name__ == "__main__":
    results, timings = {}, {}
    print(f"Timing each method (median of {REPEATS} runs)...")

    results["json"], timings["1. JSON endpoint"] = timed(
        lambda: [m_json.scrape_one(i) for i in JOBS])

    results["soup"], timings["2. requests + BeautifulSoup"] = timed(
        lambda: [m_soup.scrape_one(i) for i in JOBS])

    driver = m_selenium.start_browser(headless=True)
    try:
        results["selenium"], timings["3. Selenium (browser)"] = timed(
            lambda: [m_selenium.scrape_one(driver, i) for i in JOBS])
    finally:
        driver.quit()

    show(results["json"], "THE DATA (identical from all three methods)")

    print("\n" + "=" * 78)
    print("DO THEY AGREE?")
    print("=" * 78)
    for name in ("soup", "selenium"):
        agree = all(
            abs(a["lo"] - b["lo"]) < 1 and abs(a["hi"] - b["hi"]) < 1
            for a, b in zip(results["json"], results[name])
        )
        print(f"  json vs {name:9s}: {'IDENTICAL' if agree else 'MISMATCH'}")

    print("\n" + "=" * 78)
    print("WHAT EACH ONE COST (3 jobs)")
    print("=" * 78)
    base = timings["1. JSON endpoint"]
    for label, seconds in timings.items():
        print(f"  {label:30s} {seconds:6.2f}s   "
              f"{seconds/3:5.2f}s per job   {seconds/base:4.1f}x")

    # -----------------------------------------------------------------------
    # The real point.
    # -----------------------------------------------------------------------
    start = time.time()
    board = SESSION.get(url_board(), timeout=90).json()
    elapsed = time.time() - start
    n = len(board["jobs"])
    with_pay = sum(1 for j in board["jobs"] if j.get("pay_input_ranges"))

    print("\n" + "=" * 78)
    print("THE POINT: ask once for everything")
    print("=" * 78)
    print(f"  One request returned {n} jobs ({with_pay} with salary) "
          f"in {elapsed:.1f}s")
    print(f"  That is {elapsed/n*1000:.1f} ms per job.\n")
    for label, seconds in timings.items():
        per_job = seconds / 3
        print(f"  {label:30s} would need {per_job*n/60:5.1f} min "
              f"for the same {n} jobs  ({per_job/(elapsed/n):.0f}x slower)")
    print("\n  Speed in scraping is about HOW MANY REQUESTS you make,")
    print("  not about how fast your parser is.")
