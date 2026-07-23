"""
WHAT THE DATA SAYS
===========================================================================

With thousands of postings we can look at two descriptive questions:

  How much does the advertised range for the SAME posting vary by location,
  and is a desirable job feature (working remotely) associated with lower pay?

The second relates to compensating differential theory: undesirable job
attributes should be associated with higher pay, desirable ones with lower
pay. Estimating this from wage data is difficult, partly because more
productive workers tend to obtain both higher pay and better conditions, and
productivity is not fully observed.

A posted range is attached to a vacancy rather than to a hired worker, so
worker selection does not enter the observation in the same way. This is a
useful complement to wage data, not a complete solution.

    python 06_analysis.py
"""
import os
import re

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data", "postings.csv")


def load():
    d = pd.read_csv(DATA)
    d = d[(d.currency == "USD") & d.lo.notna() & (d.lo > 0)].copy()

    # A few postings quote an hourly wage. Convert to a yearly figure
    # (40 hours x 52 weeks = 2080) so everything is comparable.
    hourly = d.lo < 2000
    d.loc[hourly, ["lo", "hi"]] *= 2080

    d = d[(d.lo >= 25_000) & (d.hi <= 2_000_000) & (d.hi >= d.lo)]
    d["mid"] = (d.lo + d.hi) / 2
    d["log_pay"] = np.log(d["mid"])
    d["width"] = (d.hi - d.lo) / d["mid"]
    return d


def add_job_groups(d):
    """Sort titles into broad families and seniority levels."""
    families = [
        ("engineering", r"engineer|developer|architect|devops|sre"),
        ("data",        r"data scien|machine learning|research scien|analytics"),
        ("sales",       r"sales|account exec|account manager|business development"),
        ("marketing",   r"marketing|brand|growth|content"),
        ("product",     r"product manager|product owner"),
        ("design",      r"design|ux|creative"),
        ("support",     r"customer success|support|solutions"),
        ("g_and_a",     r"finance|account|legal|counsel|people|recruit|talent"),
    ]
    levels = [(5, r"\bvp\b|vice president|head of|director|chief"),
              (4, r"principal|staff|distinguished|fellow"),
              (3, r"\bmanager\b|\blead\b"),
              (2, r"senior|\bsr\.?\b"),
              (1, r"intern|new grad|junior|\bjr\.?\b|associate")]

    def family(t):
        t = t.lower()
        return next((f for f, p in families if re.search(p, t)), "other")

    def level(t):
        t = t.lower()
        return next((l for l, p in levels if re.search(p, t)), 2)

    d["family"] = d.title.map(family)
    d["level"] = d.title.map(level)
    # A "clean" title: lowercase, punctuation stripped, so the same role at
    # the same company matches across postings.
    d["clean_title"] = (d.title.str.lower()
                        .str.replace(r"[^a-z ]", " ", regex=True)
                        .str.replace(r"\s+", " ", regex=True).str.strip())
    return d


def within_group_regression(d, y, x, group_cols):
    """Regress y on x, comparing only WITHIN groups (a fixed-effects estimate).

    We subtract each group's mean from both variables. Whatever is constant
    inside a group - the employer's pay level, the occupation, the seniority -
    is removed, so the slope uses only variation inside the group.
    """
    d = d.dropna(subset=[y, x] + group_cols).copy()
    key = d[group_cols].astype(str).agg("|".join, axis=1)
    d, key = d[key.groupby(key).transform("size") >= 2], key[key.groupby(key).transform("size") >= 2]
    if d.empty:
        return None
    yd = d[y] - d[y].groupby(key).transform("mean")
    xd = d[x].astype(float) - d[x].astype(float).groupby(key).transform("mean")
    if xd.std() < 1e-12:
        return None
    beta = (xd * yd).sum() / (xd ** 2).sum()
    resid = yd - beta * xd
    # standard error clustered by company (postings at one firm are related)
    xu = xd.groupby(d.company).transform("sum") * 0 + xd
    meat = ((xd * resid).groupby(d.company).sum() ** 2).sum()
    se = np.sqrt(meat) / (xd ** 2).sum()
    return beta, se, len(d), key.nunique()


if __name__ == "__main__":
    d = add_job_groups(load())
    jobs = d.drop_duplicates("job_id")

    print("=" * 78)
    print("THE SAMPLE")
    print("=" * 78)
    print(f"  postings with a US salary range : {len(jobs):,}")
    print(f"  companies                       : {d.company.nunique()}")
    print(f"  median posted midpoint          : ${jobs['mid'].median():,.0f}")
    print(f"  median range width              : {jobs.width.median():.1%} of midpoint")

    # -----------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("1. THE SAME JOB, PRICED IN DIFFERENT CITIES")
    print("=" * 78)
    print("   Some postings carry several pay zones - one advert, one job id,")
    print("   different salary bands by location. Nothing differs but geography.\n")
    mz = d[d.n_zones > 1]
    spread = mz.groupby("job_id")["log_pay"].agg(["max", "min"])
    gap = np.exp(spread["max"] - spread["min"]) - 1
    print(f"   jobs advertising >1 pay zone : {mz.job_id.nunique():,}")
    print(f"   top-to-bottom gap            : mean {gap.mean():.1%}, "
          f"median {gap.median():.1%}, p90 {gap.quantile(.9):.1%}")

    within_job = mz["log_pay"] - mz.groupby("job_id")["log_pay"].transform("mean")
    within_cell = d["log_pay"] - d.groupby(["company", "family", "level"])["log_pay"].transform("mean")
    print(f"\n   variance of log pay within one job (pure geography) : {within_job.var():.4f}")
    print(f"   variance within company x family x level            : {within_cell.var():.4f}")
    print(f"   => geography alone is {within_job.var()/within_cell.var():.0%} of it")

    # -----------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("2. DOES REMOTE WORK PAY LESS?")
    print("=" * 78)
    d["remote"] = d.is_remote.astype(float)

    coarse = within_group_regression(d, "log_pay", "remote",
                                     ["company", "family", "level"])
    if coarse:
        b, se, n, g = coarse
        print(f"   comparing within company x family x seniority:")
        print(f"     remote effect = {np.exp(b)-1:+.1%}   (se {se:.3f}, N={n:,}, {g} cells)")

    both = d.groupby(["company", "clean_title"]).is_remote.transform("nunique")
    exact = d[both == 2]
    tight = within_group_regression(exact, "log_pay", "remote",
                                    ["company", "clean_title"])
    if tight:
        b, se, n, g = tight
        print(f"\n   comparing the SAME job title at the SAME company:")
        print(f"     remote effect = {np.exp(b)-1:+.1%}   (se {se:.3f}, N={n:,}, {g} cells)")

    print("\n   The estimate moves a lot when we tighten the comparison.")
    print("   Roles that happen to be remote are not the same roles - so most")
    print("   of the first number was the mix of jobs, not the price of remote.")

    # -----------------------------------------------------------------------
    print("\n" + "=" * 78)
    print("3. HOW WIDE ARE THE POSTED RANGES?")
    print("=" * 78)
    print("   A range is what the employer keeps open to negotiate.\n")
    by_level = jobs.groupby("level")["width"].agg(n="size", median="median")
    print(by_level.round(3).to_string())
    print("\n   by job family:")
    print(jobs.groupby("family")["width"].agg(n="size", median="median")
          .sort_values("median").round(3).to_string())
