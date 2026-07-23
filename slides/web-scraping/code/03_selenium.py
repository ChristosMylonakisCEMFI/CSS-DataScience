"""
METHOD 3 - drive a real browser
===========================================================================

Sometimes the page you download is nearly empty, because the content is
built by JavaScript AFTER the page loads. requests cannot run JavaScript,
so it sees nothing. Selenium solves this by opening an actual browser,
letting it do its work, and then reading the finished result.

It always works. It is also slow, heavy, and easy to break.

    python 03_selenium.py

The first run downloads a "driver" (the program that controls Chrome).
Selenium 4 does this automatically - you do not need to install anything.
"""
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException

from config import JOBS, url_web, show


def start_browser(headless=True):
    options = Options()
    if headless:
        # "headless" = run the browser invisibly, with no window.
        # Comment this out once, and watch it actually work. It is fun.
        options.add_argument("--headless=new")
    options.add_argument("--log-level=3")      # keep Chrome quiet
    return webdriver.Chrome(options=options)


def scrape_one(driver, job_id, attempts=3):
    driver.get(url_web(job_id))

    # WAIT. This is the part beginners skip, and it is the cause of most
    # Selenium bugs. The page is not ready the instant get() returns, so we
    # wait until the element we need actually exists (up to 20 seconds).
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "bdi"))
    )

    # Even after waiting, this page rebuilds itself once more. An element we
    # grabbed a moment ago can be thrown away and replaced - and using it
    # then raises StaleElementReferenceException. The cure is to look the
    # elements up again and retry.
    for attempt in range(attempts):
        try:
            title = driver.find_element(By.TAG_NAME, "h1").text
            bdi_texts = [e.text for e in driver.find_elements(By.TAG_NAME, "bdi")]
            amounts = [
                float(t.replace("$", "").replace(",", ""))
                for t in bdi_texts if t.startswith("$")
            ]
            if not title or not amounts:
                raise StaleElementReferenceException("page not settled yet")

            return {
                "title": title,
                "location": None,
                "lo": min(amounts),
                "hi": max(amounts),
                "currency": next((t for t in bdi_texts if t.isalpha()), None),
            }
        except StaleElementReferenceException:
            if attempt == attempts - 1:
                raise
            time.sleep(1.0)      # let it settle, then look again


if __name__ == "__main__":
    print("Starting Chrome...")
    driver = start_browser(headless=True)
    try:
        rows = [scrape_one(driver, job_id) for job_id in JOBS]
    finally:
        # ALWAYS close the browser, even if something failed above.
        # Otherwise you leave invisible Chrome processes running.
        driver.quit()

    show(rows, "METHOD 3: Selenium (a real browser)")

    print("\n  Same numbers again - but we launched a whole browser to get them.")
    print("  Use Selenium when the other two methods genuinely cannot work.")
