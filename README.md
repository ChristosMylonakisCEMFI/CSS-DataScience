# Data Science for Economics: Mastering Unstructured Data

Slides, exercises, and code for the course "Data Science for Economics".

## Before the course starts

Read [`SETUP.md`](SETUP.md) and follow it step by step. It assumes no prior
experience.

All you need is a free GitHub account and a browser. Click **Code →
Codespaces → Create codespace on main** above, and wait a few minutes while it
builds. Everything is installed for you; nothing goes on your own laptop.

Once it opens, this command should report that every check passed:

```bash
python check_setup.py
```

Working on your own machine instead is covered at the end of
[`SETUP.md`](SETUP.md).

## Materials

### Session 1 — Git, GitHub, and Python

- [`slides/git-github-codespaces/`](slides/git-github-codespaces/): tutorial on
  Git, GitHub, and Codespaces. Participants create a repository, write and test
  a small program, and record and publish their changes.
- [`slides/python-basics/`](slides/python-basics/): `python_basics.py` — values,
  records, functions and loops, pandas, and one figure, applied to the job
  postings dataset. Participants fetch it into their own repository during the
  session:

  ```bash
  curl -O https://raw.githubusercontent.com/ChristosMylonakisCEMFI/CSS-DataScience/main/slides/python-basics/python_basics.py
  pip install pandas matplotlib
  ```

### Session 2 — Prediction

- [`slides/prediction/`](slides/prediction/): overfitting, the bias-variance
  trade-off, cross-validation, data leakage, measures of predictive accuracy,
  the construction of regressors, and a menu of estimators. Figures are produced
  by a seeded simulation in
  [`figures/make_figures.py`](slides/prediction/figures/make_figures.py).

### Session 3 — Web scraping

- [`slides/web-scraping/`](slides/web-scraping/): salary ranges collected from
  online job postings three ways — a JSON endpoint, BeautifulSoup, and Selenium
  — compared, then scaled to about 9,000 postings and used to examine
  compensating differentials. See its
  [README](slides/web-scraping/README.md).

