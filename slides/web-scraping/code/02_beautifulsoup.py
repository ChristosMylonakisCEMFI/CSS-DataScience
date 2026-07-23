"""
METHOD 2 - download the human page and dig the numbers out of the HTML
===========================================================================

This is what most people mean by "web scraping".

We ask for the same page a person would see. The server sends HTML: text
wrapped in tags that describe how to display it. BeautifulSoup turns that
text into a tree we can search.

On this site the salary numbers sit inside <bdi> tags, which we found by
right-clicking the number in the browser and choosing "Inspect".

    python 02_beautifulsoup.py
"""
from bs4 import BeautifulSoup

from config import JOBS, SESSION, url_web, show


def scrape_one(job_id):
    # 1. Download the page. This is HTML text, not data.
    response = SESSION.get(url_web(job_id), timeout=60)
    response.raise_for_status()

    # 2. Parse that text into a searchable tree.
    soup = BeautifulSoup(response.text, "html.parser")

    # 3. The job title is the page's main heading, <h1>.
    title = soup.find("h1").get_text(strip=True)

    # 4. Every <bdi> tag on the page. On this site they hold the salary
    #    numbers and the currency: ['$300,000', '$405,000', 'USD']
    bdi_texts = [tag.get_text(strip=True) for tag in soup.find_all("bdi")]

    # 5. Turn the ones that look like money into numbers.
    #    '$300,000'  ->  300000.0
    amounts = [
        float(t.replace("$", "").replace(",", ""))
        for t in bdi_texts if t.startswith("$")
    ]
    currency = next((t for t in bdi_texts if t.isalpha()), None)

    return {
        "title": title,
        "location": None,          # harder to get reliably from the HTML
        "lo": min(amounts),
        "hi": max(amounts),
        "currency": currency,
    }


if __name__ == "__main__":
    # Show what the raw page looks like before we parse it.
    html = SESSION.get(url_web(list(JOBS)[0]), timeout=60).text
    print(f"The page is {len(html):,} characters of HTML.")
    print("The first 200 characters:\n")
    print("  " + html[:200].replace("\n", " "))

    soup = BeautifulSoup(html, "html.parser")
    print("\nThe <bdi> tags on that page:")
    print("  ", [t.get_text(strip=True) for t in soup.find_all("bdi")])

    rows = [scrape_one(job_id) for job_id in JOBS]
    show(rows, "METHOD 2: requests + BeautifulSoup")

    print("\n  Same numbers - but we had to know the salary lives in <bdi>.")
    print("  If the site changes that tag tomorrow, this script breaks silently.")
