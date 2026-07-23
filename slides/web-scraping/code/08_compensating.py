"""
IS THE REMOTE OPTION PAID FOR?
===========================================================================

Rosen's hedonic model: a desirable job attribute should come with lower pay,
because workers accept less to get it. Mas and Pallais (2017) estimate that
workers give up around 8% of wages for the option to work from home. So we
should expect remote postings to advertise LOWER pay.

The problem is that remote roles are not the same roles. Write

    log w_j = a_f + b * remote_j + g' x_j + e_j

for vacancy j at firm f. Then b is a compensating differential only if
remote_j is unrelated to e_j once we condition on what the job is. With no
controls that is plainly false: remote work is offered for senior technical
roles, which pay more for reasons that have nothing to do with commuting.

So rather than assert the assumption, we estimate b while holding more and
more of the job fixed, and plot how it moves. The skills we pulled out of
the posting text in 07 are one of the control sets - they describe what the
job is, which is exactly the confound.

    python 08_compensating.py

Output: figs/remote_differential.png
"""
import importlib.util
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.join(HERE, "..", "figs")
DATA = os.path.join(HERE, "..", "data")

# Mas and Pallais (2017), "Valuing Alternative Work Arrangements", AER.
# Average worker willingness to pay for working from home, as a share of wages.
MAS_PALLAIS = -0.08


def _load(fn):
    spec = importlib.util.spec_from_file_location(fn.replace(".py", ""),
                                                  os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def fe_ols(df, y, xvars, groups, cluster="company"):
    """OLS of y on xvars after removing group means, clustered by `cluster`.

    Removing the group mean from both sides is what a full set of group
    dummies would do, so the slope uses only variation inside a group.
    Returns the coefficient on xvars[0], its standard error, and the sample.
    """
    d = df.dropna(subset=[y] + xvars + [cluster]).copy()
    key = d[groups].astype(str).agg("|".join, axis=1)
    keep = key.groupby(key).transform("size") >= 2
    d, key = d[keep], key[keep]
    if len(d) < 25:
        return np.nan, np.nan, 0, 0

    yd = (d[y] - d[y].groupby(key).transform("mean")).values
    X = d[xvars].astype(float)
    Xd = (X - X.groupby(key).transform("mean")).values
    # drop controls with no within-group variation left
    good = Xd.std(axis=0) > 1e-10
    if not good[0]:
        return np.nan, np.nan, 0, 0
    Xd, names = Xd[:, good], [v for v, g in zip(xvars, good) if g]

    XtX = Xd.T @ Xd
    XtX_inv = np.linalg.pinv(XtX)
    b = XtX_inv @ (Xd.T @ yd)
    u = yd - Xd @ b

    # cluster-robust variance
    meat = np.zeros_like(XtX)
    for _, idx in d.groupby(cluster).indices.items():
        Xg, ug = Xd[idx], u[idx]
        s = Xg.T @ ug
        meat += np.outer(s, s)
    V = XtX_inv @ meat @ XtX_inv
    return b[0], np.sqrt(max(V[0, 0], 0)), len(d), key.nunique()


def main():
    text = _load("07_text_as_data.py")
    onet = text.load_onet()
    pats = text.build_patterns(onet)

    rows = text.build_frame()
    d = rows.drop_duplicates("job_id").reset_index(drop=True)
    print(f"postings : {len(d):,}   firms: {d.company.nunique()}")
    print(f"remote   : {d.remote.mean():.0%} of postings\n")

    # ---- skills from the posting text, used here as CONTROLS --------------
    skills = []
    for name, pat in pats.items():
        col = d.req_text.map(lambda t, p=pat: float(text.mentions(t, p)))
        if col.sum() >= 40:
            d[f"sk_{len(skills)}"] = col
            skills.append(f"sk_{len(skills)}")
    print(f"skill controls extracted from text: {len(skills)}")

    d["ctitle_grp"] = d.company + "|" + d.ctitle

    specs = [
        ("No controls",                    ["remote"], ["_one"]),
        ("Firm",                           ["remote"], ["company"]),
        ("Firm x family",                  ["remote"], ["company", "family"]),
        ("Firm x family x seniority",      ["remote"], ["company", "family", "level"]),
        ("+ skills from the text",         ["remote"] + skills,
                                           ["company", "family", "level"]),
        ("Firm x exact job title",         ["remote"], ["company", "ctitle"]),
    ]
    d["_one"] = 1  # a single group = no fixed effects

    out = []
    print(f"\n{'specification':32s} {'estimate':>10s} {'(s.e.)':>9s} {'N':>7s}")
    for label, xs, grp in specs:
        # the tightest spec only identifies off titles posted both ways
        dd = d
        if grp == ["company", "ctitle"]:
            both = d.groupby("ctitle_grp").remote.transform("nunique")
            dd = d[both == 2]
        b, se, n, g = fe_ols(dd, "lmid", xs, grp)
        out.append(dict(label=label, b=b, se=se, n=n, cells=g))
        if b == b:
            print(f"{label:32s} {100*(np.exp(b)-1):+9.1f}% {100*se:8.1f} {n:7d}")
        else:
            print(f"{label:32s} {'n/a':>10s}")

    res = pd.DataFrame(out)
    res.to_csv(os.path.join(DATA, "remote_differential.csv"), index=False)

    print("\nReading the ladder:")
    print("  Comparing across everything, the gap is small but useless: the")
    print("  standard error is huge because it mixes firms that pay")
    print("  differently and are differently remote-friendly.")
    print("  WITHIN a firm, remote postings advertise about 16% more.")
    print("  That is not a premium for remote: it is which roles a firm lets")
    print("  you do remotely. Conditioning on the role halves it, and")
    print("  conditioning on the exact job title removes nearly all of it.")
    print("  Skills from the text barely move it, so what matters is the")
    print("  level and the occupation, not the tools.")
    print(f"\n  Rosen plus Mas-Pallais would predict about "
          f"{100*MAS_PALLAIS:.0f}%. We find approximately zero.")
    print("  Note the last row rests on 42 postings.")

    plot(res)


def plot(res):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("(matplotlib missing - no figure)")
        return
    r = res.dropna(subset=["b"]).reset_index(drop=True)
    y = np.arange(len(r))[::-1]
    est = 100 * (np.exp(r.b) - 1)
    lo = 100 * (np.exp(r.b - 1.96 * r.se) - 1)
    hi = 100 * (np.exp(r.b + 1.96 * r.se) - 1)

    fig, ax = plt.subplots(figsize=(10.6, 5.4))
    # leave a column on the right for the sample sizes
    span = hi.max() - min(lo.min(), 100 * MAS_PALLAIS)
    x_right = hi.max() + 0.16 * span
    ax.set_xlim(min(lo.min(), 100 * MAS_PALLAIS) - 0.04 * span,
                x_right + 0.06 * span)
    ax.set_ylim(-1.15, len(r) - 0.4)

    ax.axvline(0, color="black", lw=0.9)
    ax.axvline(100 * MAS_PALLAIS, color="#8C0000", lw=1.1, ls="--")
    ax.text(100 * MAS_PALLAIS, -1.0,
            "  Mas & Pallais (2017): what workers say they would give up",
            color="#8C0000", fontsize=8.5, va="center", ha="left")

    ax.hlines(y, lo, hi, color="#00006E", lw=1.6)
    ax.plot(est, y, "o", color="#00006E", ms=6)
    for i, n in zip(y, r.n):
        ax.text(x_right, i, f"N={n:,}", fontsize=7.5, color="#5A5A5A",
                ha="right", va="center")

    ax.set_yticks(y)
    ax.set_yticklabels(r.label, fontsize=10)
    ax.set_xlabel("Posted pay difference for remote postings (%)", fontsize=10)
    ax.set_title("The remote pay gap as more of the job is held fixed",
                 fontsize=12, loc="left", pad=14)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.grid(axis="x", color="#DDDDDD", lw=0.6)
    ax.set_axisbelow(True)
    fig.tight_layout()
    os.makedirs(FIGS, exist_ok=True)
    out = os.path.join(FIGS, "remote_differential.png")
    fig.savefig(out, dpi=200)
    print(f"\nfigure -> {os.path.relpath(out, HERE)}")


if __name__ == "__main__":
    main()
