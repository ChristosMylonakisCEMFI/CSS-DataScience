"""
THE TEXT IS DATA TOO
===========================================================================

So far we used one number from each posting. But the posting is mostly TEXT,
and the text says what the job requires and what it offers. Two questions:

  1. What is a technical skill associated with, in posted pay?
  2. Is a desirable job attribute (remote work) associated with lower pay,
     as compensating differential theory predicts?

The hard part is turning text into variables in a way you could defend in a
seminar. Three rules we follow here:

  (a) DO NOT invent the list of skills. If you pick the terms after seeing
      which ones correlate with pay, the exercise is circular. We take an
      external, published taxonomy: the O*NET "Hot Technologies" list
      (data/onet_hot_technologies.csv, 170 technologies).

  (b) READ THE RIGHT SECTION. A skill named under "Requirements" is a
      requirement; the same word in the company blurb is not. We split the
      posting into sections and look only at the relevant ones.

  (c) HANDLE NEGATION. "No ML experience is required" is not an ML
      requirement. We check the words just before each match.

    python 07_text_as_data.py

Source: O*NET 29.1 Technology Skills, National Center for O*NET Development,
used under CC BY 4.0. Refresh with --refresh-onet.
"""
import argparse
import csv
import html
import importlib.util
import os
import re

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
FIGS = os.path.join(HERE, "..", "figs")
ONET_CSV = os.path.join(DATA, "onet_hot_technologies.csv")
ONET_URL = ("https://www.onetcenter.org/dl_files/database/db_29_1_text/"
            "Technology%20Skills.txt")


def _load(fn):
    spec = importlib.util.spec_from_file_location(fn.replace(".py", ""),
                                                  os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------------------------------------------------------------------
# (a) The attribute list comes from outside, not from us
# ---------------------------------------------------------------------------
def refresh_onet():
    """Re-download the O*NET list. Only needed to update the taxonomy."""
    import io
    from config import SESSION
    r = SESSION.get(ONET_URL, timeout=90)
    r.beta = r.raise_for_status()
    rows = csv.DictReader(io.StringIO(r.text), delimiter="\t")
    hot = {x["Example"].strip(): x["Commodity Title"].strip()
           for x in rows if x["Hot Technology"] == "Y"}
    with open(ONET_CSV, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["technology", "category"])
        for k in sorted(hot):
            w.writerow([k, hot[k]])
    print(f"refreshed {ONET_CSV}: {len(hot)} technologies")


def load_onet():
    with open(ONET_CSV, encoding="utf-8") as fh:
        return {r["technology"]: r["category"] for r in csv.DictReader(fh)}


# Words that only describe the vendor or the kind of product, not the product.
GENERIC = {"amazon", "apache", "adobe", "atlassian", "autodesk", "microsoft",
           "google", "apple", "oracle", "ibm", "bentley", "web", "services",
           "service", "software", "systems", "system", "tools", "tool",
           "platform", "development", "programming", "language", "database",
           "server", "the", "and", "for", "of"}

# Short names that are also ordinary English words. Matching "access" or
# "cloud" or "team" would tag most postings in the sample. For these we
# require the full product name ("Microsoft Access") instead.
AMBIGUOUS = {"access", "cloud", "teams", "team", "word", "sheets", "excel",
             "basic", "go", "processing", "pages", "notion", "ring", "unity",
             "snowflake", "elastic", "spark", "hive", "struts", "maven",
             "ant", "swift", "r", "c"}


def aliases(name):
    """The strings a technology might actually be written as in a posting."""
    out = set()
    for acronym in re.findall(r"\b([A-Z]{2,}[0-9]*)\b", name):
        out.add(acronym)                       # AWS, SQL, JIRA, EC2
    for inside in re.findall(r"\(([^)]+)\)", name):
        if 2 <= len(inside) <= 6:
            out.add(inside)
    words = [w for w in re.split(r"[\s/]+", name) if w.lower() not in GENERIC]
    core = " ".join(words).strip()             # "Apache Spark" -> "Spark"
    if core and not re.fullmatch(r"[A-Z]{2,}[0-9]*", core):
        out.add(core)
    return {a for a in out if len(a) >= 2 and re.search(r"[A-Za-z]", a)}


def build_patterns(technologies):
    pats = {}
    for name in technologies:
        forms = {name if a.lower() in AMBIGUOUS else a for a in aliases(name)}
        if not forms:
            continue
        alt = "|".join(sorted((re.escape(f) for f in forms), key=len, reverse=True))
        # no letter/digit either side, so "Go" does not match "Google"
        pats[name] = re.compile(r"(?<![A-Za-z0-9])(?:" + alt + r")(?![A-Za-z0-9+#])",
                                re.I)
    return pats


# ---------------------------------------------------------------------------
# (b) Sections, and (c) negation
# ---------------------------------------------------------------------------
HEAD_RE = re.compile(r"<(?:h[1-4]|strong)[^>]*>(.*?)</(?:h[1-4]|strong)>",
                     re.I | re.S)
WANTED_HEAD = re.compile(
    r"requirement|qualification|you have|you.ll bring|skills|what you|"
    r"about you|good fit|experience|responsibilit|what we.re looking", re.I)
NEGATION = re.compile(r"\b(no|not|without|isn't|aren't|non)\b[^.]{0,30}$", re.I)


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def requirement_text(content_html):
    """Text of the sections that state what the job needs.

    Falls back to the whole posting when no headers are recognised, so we
    never silently drop a posting.
    """
    heads = list(HEAD_RE.finditer(content_html))
    if not heads:
        return strip_tags(content_html)
    chunks = []
    for i, m in enumerate(heads):
        title = strip_tags(m.group(1))
        if not WANTED_HEAD.search(title):
            continue
        end = heads[i + 1].start() if i + 1 < len(heads) else len(content_html)
        chunks.append(strip_tags(content_html[m.end():end]))
    return " ".join(chunks) if chunks else strip_tags(content_html)


def mentions(text, pattern):
    """True if the pattern appears and is not negated just before."""
    for m in pattern.finditer(text):
        if NEGATION.search(text[max(0, m.start() - 40):m.start()]):
            continue
        return True
    return False


# ---------------------------------------------------------------------------
# Job classification (same helpers as 06)
# ---------------------------------------------------------------------------
def level(title):
    t = title.lower()
    for lv, pat in [(5, r"\bvp\b|vice president|head of|director|chief"),
                    (4, r"principal|staff|distinguished|fellow"),
                    (3, r"\bmanager\b|\blead\b"),
                    (2, r"senior|\bsr\.?\b"),
                    (1, r"intern|new grad|junior|\bjr\.?\b|associate")]:
        if re.search(pat, t):
            return lv
    return 2


def family(title):
    t = title.lower()
    for fam, pat in [("engineering", r"engineer|developer|architect|devops|sre"),
                     ("data", r"data scien|machine learning|analytics|research scien"),
                     ("sales", r"sales|account exec|account manager"),
                     ("marketing", r"marketing|brand|growth"),
                     ("product", r"product manager"),
                     ("design", r"design|\bux\b"),
                     ("support", r"customer success|support|solutions"),
                     ("g_and_a", r"finance|account|legal|counsel|people|recruit")]:
        if re.search(pat, t):
            return fam
    return "other"


# ---------------------------------------------------------------------------
# Estimation: within-group (fixed effects) slope, clustered by company
# ---------------------------------------------------------------------------
def within(df, y, x, groups):
    d = df.dropna(subset=[y, x]).copy()
    key = d[groups].astype(str).agg("|".join, axis=1)
    keep = key.groupby(key).transform("size") >= 2
    d, key = d[keep], key[keep]
    if len(d) < 20:
        return np.nan, np.nan, 0
    yd = d[y] - d[y].groupby(key).transform("mean")
    xd = d[x] - d[x].groupby(key).transform("mean")
    if xd.std() < 1e-12:
        return np.nan, np.nan, 0
    b = (xd * yd).sum() / (xd ** 2).sum()
    resid = yd - b * xd
    se = np.sqrt(((xd * resid).groupby(d.company).sum() ** 2).sum()) / (xd ** 2).sum()
    return b, se, len(d)


def build_frame():
    """Collect postings WITH their text, reusing the cache from 05.

    One row per (posting, pay zone). A posting that quotes a different band
    per city contributes several rows sharing a job_id - that is what lets us
    compare the same posting across locations.
    """
    scale = _load("05_scale_up.py")
    rows = []
    for company in sorted(set(scale.COMPANIES)):
        for j in scale.fetch_board(company):
            pays = [p for p in (j.get("pay_input_ranges") or [])
                    if p.get("currency_type") == "USD"]
            if not pays:
                continue
            content = html.unescape(j.get("content") or "")
            base = dict(
                company=str(j.get("company_name") or company),
                job_id=j.get("id"),
                title=str(j.get("title") or ""),
                location=str((j.get("location") or {}).get("name", "") or ""),
                n_zones=len(pays),
                req_text=requirement_text(content),
                full_text=strip_tags(content),
            )
            for p in pays:
                lo, hi = p["min_cents"] / 100, p["max_cents"] / 100
                if not (25_000 <= lo < hi <= 2_000_000):
                    continue
                rows.append({**base, "lo": lo, "hi": hi,
                             "zone": (p.get("title") or "").strip()})
    d = pd.DataFrame(rows).reset_index(drop=True)
    d["mid"] = (d.lo + d.hi) / 2
    d["lmid"] = np.log(d["mid"])
    d["width"] = (d.hi - d.lo) / d["mid"]      # reserved room, as a share
    d["ratio"] = d.hi / d.lo                    # top of band / bottom of band
    d["level"] = d.title.map(level)
    d["family"] = d.title.map(family)
    d["ctitle"] = (d.title.str.lower()
                   .str.replace(r"[^a-z ]", " ", regex=True)
                   .str.replace(r"\s+", " ", regex=True).str.strip())
    both = (d.location + " | " + d.full_text)
    d["remote"] = both.str.contains(r"\bremote\b|work from home|distributed",
                                    case=False, regex=True).astype(float)
    return d


def main(min_count=25, make_figure=True):
    onet = load_onet()
    pats = build_patterns(onet)
    rows = build_frame()
    # one row per posting, for everything except the location comparison
    d = rows.drop_duplicates("job_id").reset_index(drop=True)
    print(f"pay quotes (posting x zone)      : {len(rows):,}")
    print(f"postings                         : {len(d):,}")
    print(f"companies                        : {d.company.nunique()}")
    print(f"O*NET hot technologies searched  : {len(pats)}")

    # =======================================================================
    # RESULT 1 - the same posting, priced in different cities
    # =======================================================================
    multi = rows[rows.n_zones > 1]
    spread = multi.groupby("job_id")["lmid"].agg(["max", "min"])
    gap = np.exp(spread["max"] - spread["min"]) - 1
    within_posting = multi.lmid - multi.groupby("job_id").lmid.transform("mean")
    cell = d.groupby(["company", "family", "level"]).lmid.transform("mean")
    within_cell = d.lmid - cell
    print("\n" + "=" * 78)
    print("RESULT 1  Same posting, different city")
    print("=" * 78)
    print(f"  postings quoting >1 city band : {multi.job_id.nunique():,}")
    print(f"  top-to-bottom gap, mean       : {gap.mean():.1%}")
    print(f"                       median   : {gap.median():.1%}")
    print(f"                       p90      : {gap.quantile(.9):.1%}")
    print(f"  var(log pay) within a posting : {within_posting.var():.4f}")
    print(f"  var within firm x family x lvl: {within_cell.var():.4f}")
    print(f"  -> location share             : "
          f"{within_posting.var()/within_cell.var():.0%}")

    # =======================================================================
    # RESULT 2 - what the text is associated with
    # =======================================================================
    hits = {}
    for name, pat in pats.items():
        col = d.req_text.map(lambda t, p=pat: float(mentions(t, p)))
        if col.sum() >= min_count:
            hits[name] = col
    S = pd.DataFrame(hits)
    print(f"\ntechnologies mentioned in >= {min_count} postings: {S.shape[1]}")

    est = []
    for name in S.columns:
        d["_x"] = S[name]
        b, se, n = within(d, "lmid", "_x", ["company", "level"])
        if b == b:
            est.append((name, onet[name], 100 * (np.exp(b) - 1), 100 * se,
                        int(S[name].sum())))
    est.sort(key=lambda r: -r[2])

    print("\n" + "=" * 78)
    print("RESULT 2  Skills and posted pay (within company x seniority)")
    print("=" * 78)
    print(f"  {'technology':28s} {'premium':>9s} {'(se)':>7s} {'postings':>9s}")
    for name, _, b, se, n in est[:10]:
        print(f"  {name[:28]:28s} {b:+8.1f}% {se:6.1f} {n:9d}")
    print("  " + "." * 60)
    for name, _, b, se, n in est[-10:]:
        print(f"  {name[:28]:28s} {b:+8.1f}% {se:6.1f} {n:9d}")

    pd.DataFrame(est, columns=["technology", "category", "premium_pct",
                               "se_pct", "n_postings"]).to_csv(
        os.path.join(DATA, "skill_premia.csv"), index=False)

    # =======================================================================
    # RESULT 3 - how wide are the bands, and do the widths look chosen?
    # =======================================================================
    print("\n" + "=" * 78)
    print("RESULT 3  The width of the band")
    print("=" * 78)
    r = d.ratio.round(3)
    top = r.value_counts().head(6)
    print(f"  median width  : {d.width.median():.1%} of the midpoint")
    print(f"  IQR           : [{d.width.quantile(.25):.1%}, "
          f"{d.width.quantile(.75):.1%}]")
    print(f"\n  most common top/bottom ratios:")
    for val, cnt in top.items():
        print(f"     {val:.3f}   {cnt:5d} postings ({cnt/len(d):5.1%})")
    print(f"  the six most common ratios cover {top.sum()/len(d):.0%} "
          f"of all postings")
    print("\n  median width by seniority:")
    for lv, g in d.groupby("level"):
        if len(g) >= 20:
            print(f"     level {lv}  n={len(g):5d}   {g.width.median():.1%}")

    # ---- compensating differential: remote ---------------------------------
    print("\n" + "=" * 78)
    print("APPENDIX  Remote work and posted pay (tightening the comparison)")
    print("=" * 78)
    rows = []
    b1, s1, n1 = within(d, "lmid", "remote", ["company"])
    rows.append(("company", b1, s1, n1))
    b2, s2, n2 = within(d, "lmid", "remote", ["company", "family", "level"])
    rows.append(("company x family x level", b2, s2, n2))
    pair = d.groupby(["company", "ctitle"]).remote.transform("nunique")
    b3, s3, n3 = within(d[pair == 2], "lmid", "remote", ["company", "ctitle"])
    rows.append(("company x exact title", b3, s3, n3))
    print(f"  {'comparison held fixed':28s} {'remote':>9s} {'(se)':>7s} {'N':>8s}")
    for label, b, se, n in rows:
        if b == b:
            print(f"  {label:28s} {100*(np.exp(b)-1):+8.1f}% "
                  f"{100*se:6.1f} {n:8d}")
    if b1 == b1 and b3 == b3:
        print(f"\n  Of the {100*(np.exp(b1)-1):.0f}% raw gap, "
              f"{100*(np.exp(b1)-np.exp(b3)):.0f}pp is composition "
              f"(which roles are offered remotely)")
        print(f"  and about {100*(np.exp(b3)-1):.0f}% remains once the exact "
              f"job is held fixed.")

    if make_figure:
        save_figure(est)
        save_width_figure(d)


def save_figure(est, k=10):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("\n(matplotlib not installed - skipping figure)")
        return
    sel = est[:k] + est[-k:]
    names = [e[0][:26] for e in sel][::-1]
    vals = [e[2] for e in sel][::-1]
    errs = [e[3] for e in sel][::-1]
    colors = ["#1A7F37" if v > 0 else "#CF222E" for v in vals]
    fig, ax = plt.subplots(figsize=(11.2, 5.9))   # wide, to fill a 16:9 slide
    ax.barh(range(len(vals)), vals, color=colors, height=0.72,
            xerr=errs, error_kw=dict(ecolor="#57606A", elinewidth=1.1, capsize=2.5))
    ax.set_yticks(range(len(vals)))
    ax.set_yticklabels(names, fontsize=9)
    ax.axvline(0, color="#24292F", lw=0.9)
    ax.set_xlabel("Difference in posted pay (%), within company $\\times$ seniority",
                  fontsize=10)
    ax.set_title("Posted pay and O*NET hot technologies", fontsize=12,
                 fontweight="bold", loc="left", pad=26)
    ax.text(0.0, 1.012, "Associations, not causal returns. "
            "Whiskers are $\\pm$1 s.e. (clustered by company).",
            transform=ax.transAxes, fontsize=8, color="#57606A")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#D0D7DE", lw=0.6, alpha=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    os.makedirs(FIGS, exist_ok=True)
    out = os.path.join(FIGS, "skill_premia.png")
    fig.savefig(out, dpi=200)
    print(f"\nfigure -> {os.path.relpath(out, HERE)}")


def save_width_figure(d, lo=1.0, hi=2.2):
    """Histogram of the top/bottom ratio of each posted band.

    If widths were tailored to each vacancy the distribution would be smooth.
    Spikes at round values say the width is largely conventional.
    """
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return
    r = d.ratio[(d.ratio >= lo) & (d.ratio <= hi)]
    edges = np.arange(lo, hi + 0.005, 0.005)
    counts, _ = np.histogram(r, bins=edges)
    fig, ax = plt.subplots(figsize=(11.2, 5.2))
    ax.hist(r, bins=edges, color="#0969DA")
    ax.set_xlabel("Top of the posted band / bottom of the posted band",
                  fontsize=10)
    ax.set_ylabel("Postings", fontsize=10)
    ax.set_ylim(0, counts.max() * 1.16)          # headroom for the labels
    ax.set_title("Posted pay bands cluster on a few round widths",
                 fontsize=12, fontweight="bold", loc="left", pad=26)
    ax.text(0.0, 1.012,
            f"{len(r):,} postings. Each bar is a 0.5-percentage-point bin.",
            transform=ax.transAxes, fontsize=8, color="#57606A")
    # label the tallest bars, at the height they actually reach,
    # skipping any that would sit on top of a label already placed
    placed = []
    for i in np.argsort(counts)[::-1]:
        if len(placed) == 5:
            break
        centre = (edges[i] + edges[i + 1]) / 2
        if any(abs(centre - p) < 0.03 for p in placed):
            continue
        placed.append(centre)
        ax.annotate(f"{centre:.3g}", xy=(centre, counts[i]), xytext=(0, 6),
                    textcoords="offset points", ha="center",
                    fontsize=8.5, color="#24292F", fontweight="bold")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#D0D7DE", lw=0.6, alpha=0.8)
    ax.set_axisbelow(True)
    fig.tight_layout()
    os.makedirs(FIGS, exist_ok=True)
    out = os.path.join(FIGS, "range_width.png")
    fig.savefig(out, dpi=200)
    print(f"figure -> {os.path.relpath(out, HERE)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh-onet", action="store_true")
    ap.add_argument("--min-count", type=int, default=25)
    a = ap.parse_args()
    if a.refresh_onet:
        refresh_onet()
    main(min_count=a.min_count)
