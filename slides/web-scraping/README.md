# Web scraping for applied research

A hands-on session. We collect salary ranges from online job postings three
different ways, compare the approaches, and then use about 9,000 postings to
look at a standard question in labour economics (compensating differentials).

Nothing to install: your Codespace already has everything. If you have not set
one up yet, do [`SETUP.md`](../../SETUP.md) first.

> **Note on the data.** The example targets live job postings, which companies
> add and remove continually. By the time you run this, the specific postings
> and numbers will differ from those in the slides. The code is written to
> handle that; the method is what matters, not the exact figures.

---

## 1. Before writing any code, look at the page

Open these three links in your browser, in order. This is the habit worth
taking away from the whole session: **never write a scraper for a page you
have not read.**

1. The board — every open job at one company
   <https://job-boards.greenhouse.io/anthropic>

2. One job advert. Scroll down to **Annual Salary**. Those are the numbers we
   want.
   <https://job-boards.greenhouse.io/anthropic/jobs/4981828008>

3. The same job, as *data* instead of as a page
   <https://boards-api.greenhouse.io/v1/boards/anthropic/jobs/4981828008?pay_transparency=true>

The third link is the one that matters. Your browser was already fetching it
behind the scenes; we are just asking for it directly.

**Try it yourself:** open link 2, press `F12` to open developer tools, click
the **Network** tab, filter to **Fetch/XHR**, and reload the page. You will
see the request to `boards-api.greenhouse.io` appear in the list.

---

## 2. Run the scripts, in order

```bash
cd code

python 01_json.py            # method 1: ask for the data directly
python 02_beautifulsoup.py   # method 2: download the page, dig out the numbers
python 03_selenium.py        # method 3: drive a real browser
python 04_compare.py         # all three side by side: do they agree, what do they cost?

python 05_scale_up.py        # NOT IN CLASS - see below
python 06_analysis.py        # what the data says
python 07_text_as_data.py    # turn the posting TEXT into variables
python 08_compensating.py    # is the remote option paid for?
```

The first three each print the same three salaries. That is the point: three
very different techniques, one answer.

**Do not run `05_scale_up.py` during the session.** It downloads the boards of
about 109 companies. A room full of people doing that at the same moment sends
thousands of requests from the same place within a couple of minutes, which is
discourteous at best and gets everyone rate-limited at worst. Its output,
`data/postings.csv`, is already in the repository, so `06`, `07` and `08` run
without it.

Run it at home afterwards, where it is exactly what it claims to be: an
illustration of threads, caching, and error handling at scale. It caches every
reply in `data/cache/`, so a second run makes no requests at all. Use
`--fresh` to force a re-download, and `--workers` to be gentler.

---

## 3. What each file is

| File | What it does |
| --- | --- |
| `code/config.py` | Shared settings: which jobs, which URLs, one shared session |
| `code/01_json.py` | Method 1 — the hidden data address |
| `code/02_beautifulsoup.py` | Method 2 — parse the HTML page |
| `code/03_selenium.py` | Method 3 — drive a real browser |
| `code/04_compare.py` | Timing and agreement across the three |
| `code/05_scale_up.py` | Threads, caching, error handling, ~100 boards |
| `code/06_analysis.py` | The economics |
| `code/07_text_as_data.py` | Skills from the posting text, using the O\*NET taxonomy |
| `code/08_compensating.py` | The remote pay gap as more of the job is held fixed |
| `data/postings.csv` | The collected dataset |
| `data/onet_hot_technologies.csv` | The external skill taxonomy (see below) |

### Turning text into variables

`07_text_as_data.py` extracts technical skills from the posting text and asks
which ones are associated with higher posted pay. Three rules keep it
defensible:

1. **The skill list comes from outside.** We use the O\*NET *Hot Technologies*
   list (170 technologies), not terms we chose. Picking terms after seeing
   which correlate with pay would make the exercise circular.
2. **Only the relevant sections are read.** A tool named under *Requirements*
   is a requirement; the same word in the company blurb is not.
3. **Negation is handled.** "No ML experience is required" is not an ML
   requirement.

The results are **associations, not causal returns**: Excel and SAP appear in
lower-paid administrative roles, which is selection, not an effect of the
tool.

> **Data source.** `data/onet_hot_technologies.csv` is derived from O\*NET 29.1
> Technology Skills by the National Center for O\*NET Development, used under
> [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Refresh it with
> `python 07_text_as_data.py --refresh-onet`.

---

## 4. Troubleshooting

Anything that looks like a missing package or a broken browser is a setup
problem, not a scraping one: run `python check_setup.py` from the top folder
of the repository and follow what it prints.

**`StaleElementReferenceException`**
Not a bug in your code — the page rebuilt itself while you were reading it.
Wait for the element and look it up again; see `03_selenium.py`.

**A company board returns nothing**
Normal. Companies close boards and change names. `05_scale_up.py` is written
so one failure never stops the run.

---

## 5. A note on scraping responsibly

- Prefer a bulk download or an official API when one exists.
- Identify yourself with a `User-Agent` header, as the code here does.
- Ask for many records in one request rather than many requests.
- Do not collect personal data you do not need, and check the site's terms.
- Cache raw responses. It is faster, kinder to the server, and it is what
  makes your results reproducible later.
