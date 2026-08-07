"""
salary_summary.py - sections 5 and 6 of python_basics.py, as a finished
program: one entry point, paths resolved from the file, figure saved to disk.

    cd slides/python-basics
    python salary_summary.py

Same table, same figure, no cells and no hidden state. This is the form the
scraping and prediction sessions take.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# Paths are written relative to this file, not to wherever you happen to be
# standing when you run it. This one line is why the script works from any
# folder, while a bare relative path would not.
HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "web-scraping" / "data" / "postings.csv"
FIGURE = HERE / "salary_distribution.pdf"


def load_usd_postings(path):
    """Postings quoting a salary range in USD, with the midpoint added."""
    jobs = pd.read_csv(path)
    pay = jobs[(jobs["currency"] == "USD") & jobs["lo"].notna()].copy()
    pay["mid"] = (pay["lo"] + pay["hi"]) / 2
    return jobs, pay


def main():
    jobs, pay = load_usd_postings(DATA)

    print(f"{len(jobs):,} postings from {jobs['company'].nunique()} companies")
    print(f"{jobs['lo'].isna().mean():.0%} state no salary at all")
    print(f"{len(pay):,} state a range in USD\n")

    print("Midpoint of the posted range, by whether the post is remote:")
    print(pay.groupby("is_remote")["mid"].agg(["count", "mean", "median"]).round(0))

    fig, ax = plt.subplots(figsize=(6.5, 3.5))
    ax.hist(pay["mid"] / 1000, bins=40, color="0.35")
    ax.set_xlabel("Midpoint of posted salary range (thousands of USD)")
    ax.set_ylabel("Number of postings")
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    fig.savefig(FIGURE)
    print(f"\nFigure written to {FIGURE.name}")


if __name__ == "__main__":
    main()
