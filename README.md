# Data Science for Economics: Mastering Unstructured Data

Slides, exercises, and code for the course "Data Science for Economics".

## Before the course starts

Read [`SETUP.md`](SETUP.md) and follow it step by step. It assumes no prior
experience and takes about fifteen minutes.

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

- [`slides/git-github-codespaces/`](slides/git-github-codespaces/): a hands-on tutorial on Git, GitHub, and Codespaces.
- [`slides/web-scraping/`](slides/web-scraping/): a hands-on session on web scraping. Collect salary ranges from online job postings three ways (a JSON endpoint, BeautifulSoup, Selenium), compare the approaches, scale up to about 9,000 postings, and use them to look at compensating differentials. Runnable code, a one-command setup check, and slides. See its [README](slides/web-scraping/README.md) to get started.
- [`slides/prediction-competition/`](slides/prediction-competition/): a session on prediction — overfitting, the bias-variance trade-off, cross-validation, data leakage, measures of predictive accuracy, the construction of regressors, and a menu of estimators. Every figure is produced by a seeded simulation in [`figures/make_figures.py`](slides/prediction-competition/figures/make_figures.py); regenerate with `python make_figures.py`.

