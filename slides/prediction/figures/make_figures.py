"""Generate the simulation figures for the prediction slides.

Each figure comes from a small simulation with a known data-generating process,
so the plots demonstrate the point rather than assert it.

    python make_figures.py                  # all figures
    python make_figures.py overfit_reg      # selected figures

Figures are written next to this script as PDF. All randomness is seeded, so
the committed figures are reproducible.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from numpy.polynomial import Polynomial
from sklearn.datasets import make_moons
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import Lasso, LinearRegression, LogisticRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, roc_auc_score, roc_curve
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

# ---------------------------------------------------------------------------
# Plain academic plotting style: white background, restrained colours,
# no bold titles, no decorative annotation boxes.
# ---------------------------------------------------------------------------
BLACK = "#000000"
BLUE = "#1F4E79"
RED = "#8B1A1A"
GRAY = "#595959"
LIGHTGRAY = "#BFBFBF"

HERE = Path(__file__).resolve().parent

# Figures are drawn on a deliberately small canvas. On the slide they are shown
# at roughly 0.5-0.8 of the text width, so a small canvas keeps the axis text
# large relative to the figure and therefore legible when projected.
SCALE = 0.68


def sz(w, h):
    """Canvas size in inches, scaled so text stays readable on a slide."""
    return (w * SCALE, h * SCALE)


plt.rcParams.update(
    {
        "figure.dpi": 130,
        "savefig.bbox": "tight",
        "savefig.pad_inches": 0.03,
        "font.size": 11,
        "axes.titlesize": 11,
        "axes.titleweight": "normal",
        "axes.labelsize": 11,
        "xtick.labelsize": 9.5,
        "ytick.labelsize": 9.5,
        "axes.edgecolor": BLACK,
        "axes.linewidth": 0.8,
        "axes.grid": True,
        "grid.color": LIGHTGRAY,
        "grid.linewidth": 0.5,
        "grid.linestyle": "-",
        "grid.alpha": 0.6,
        "legend.frameon": False,
        "legend.fontsize": 9.5,
        "xtick.color": BLACK,
        "ytick.color": BLACK,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "axes.labelcolor": BLACK,
        "text.color": BLACK,
        "axes.titlecolor": BLACK,
        "lines.linewidth": 1.6,
    }
)


def _finish(fig, name):
    out = HERE / f"fig_{name}.pdf"
    fig.savefig(out)
    plt.close(fig)
    print(f"  wrote {out.name}")


def _clean(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def _legend_below(ax, ncol, pad=0.05, **kw):
    """Place the legend under the axes rather than inside them.

    Whatever the curves do, they cannot cover the legend and the legend cannot
    cover them. The position is measured rather than guessed: get_tightbbox
    reports where the axes really end once the tick labels and the x label are
    drawn, and the legend goes `pad` below that, in figure coordinates.

    Call this AFTER fig.tight_layout(), which is what fixes the geometry.
    `savefig.bbox = "tight"` then grows the canvas to include the legend.
    """
    fig = ax.figure
    fig.canvas.draw()
    bb = ax.get_tightbbox(fig.canvas.get_renderer())
    bb = bb.transformed(fig.transFigure.inverted())
    pos = ax.get_position()
    ax.legend(loc="upper center",
              bbox_to_anchor=(pos.x0 + pos.width / 2, bb.y0 - pad),
              bbox_transform=fig.transFigure, ncol=ncol,
              frameon=False, borderaxespad=0.0, handlelength=1.9,
              columnspacing=1.5, **kw)


# ---------------------------------------------------------------------------
# Overfitting in a regression problem
# ---------------------------------------------------------------------------
def overfit_reg():
    """Polynomial fits of increasing degree.

    Polynomials are fitted with numpy's Polynomial.fit, which rescales the
    domain to [-1, 1] before solving the least-squares problem. This keeps the
    design matrix well conditioned, so training error is weakly decreasing in
    the degree, as nested models require.
    """
    rng = np.random.default_rng(7)

    def true_f(x):
        return np.sin(2.2 * x) + 0.35 * x

    n = 20
    x = np.sort(rng.uniform(0, 3, n))
    y = true_f(x) + rng.normal(0, 0.30, n)
    xte = np.sort(rng.uniform(0, 3, 200))
    yte = true_f(xte) + rng.normal(0, 0.30, 200)
    xg = np.linspace(0, 3, 600)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=sz(9.2, 3.5))

    # --- left: fits of three degrees on the same sample
    ax1.plot(xg, true_f(xg), color=GRAY, lw=1.3, ls="--", label="true $f(x)$")
    ax1.scatter(x, y, s=24, color=BLACK, zorder=5, label="sample")
    for deg, col, ls in [(1, BLUE, "-"), (3, GRAY, "-"), (n - 1, RED, "-")]:
        p = Polynomial.fit(x, y, deg)
        ax1.plot(xg, p(xg), color=col, ls=ls, lw=1.7, label=f"degree {deg}")
    ax1.set_ylim(-2.6, 3.0)
    ax1.set_xlabel("$x$")
    ax1.set_ylabel("$y$")
    ax1.set_title("Fits to 20 observations")
    _clean(ax1)

    # --- right: training and test error against degree
    degs = np.arange(1, n)
    tr_err, te_err = [], []
    for deg in degs:
        p = Polynomial.fit(x, y, deg)
        tr_err.append(np.sqrt(mean_squared_error(y, p(x))))
        te_err.append(np.sqrt(mean_squared_error(yte, p(xte))))
    ax2.semilogy(degs, tr_err, "-o", color=BLUE, ms=3.5, label="training sample")
    ax2.semilogy(degs, te_err, "-s", color=RED, ms=3.5, label="test sample")
    best = degs[int(np.argmin(te_err))]
    ax2.axvline(best, color=GRAY, lw=1.0, ls=":")
    ax2.annotate(f"minimum at degree {best}", (best, min(te_err)),
                 textcoords="offset points", xytext=(12, -28), fontsize=9,
                 color=BLACK, arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8))
    ax2.set_xlabel("polynomial degree")
    ax2.set_ylabel("RMSE")
    ax2.set_title("Training and test error")
    ax2.set_xticks([1, 5, 10, 15, 19])
    _clean(ax2)

    fig.tight_layout(w_pad=2.0)
    _legend_below(ax1, ncol=3, fontsize=8.5)
    _legend_below(ax2, ncol=2, fontsize=9)
    _finish(fig, "overfit_reg")


# ---------------------------------------------------------------------------
# Overfitting with a binary outcome
# ---------------------------------------------------------------------------
def overfit_clf():
    X, y = make_moons(n_samples=120, noise=0.32, random_state=3)
    xx, yy = np.meshgrid(np.linspace(X[:, 0].min() - .5, X[:, 0].max() + .5, 300),
                         np.linspace(X[:, 1].min() - .5, X[:, 1].max() + .5, 300))
    grid = np.c_[xx.ravel(), yy.ravel()]
    bg = ListedColormap(["#DCE6F1", "#F2DEDE"])
    pts = ListedColormap([BLUE, RED])

    fig, axes = plt.subplots(1, 2, figsize=sz(9.0, 3.5))
    specs = [
        (make_pipeline(StandardScaler(), LogisticRegression()),
         "Logistic regression"),
        (DecisionTreeClassifier(random_state=0),
         "Unrestricted tree"),
    ]
    for ax, (model, title) in zip(axes, specs):
        model.fit(X, y)
        zz = model.predict(grid).reshape(xx.shape)
        ax.contourf(xx, yy, zz, cmap=bg, alpha=1.0)
        ax.contour(xx, yy, zz, colors=BLACK, linewidths=0.7)
        ax.scatter(X[:, 0], X[:, 1], c=y, cmap=pts, s=18, edgecolor="white", lw=0.4)
        ax.set_title(title)
        ax.set_xticks([]); ax.set_yticks([])
        ax.grid(False)
    fig.tight_layout()
    _finish(fig, "overfit_clf")


# ---------------------------------------------------------------------------
# Bias and variance across repeated samples
# ---------------------------------------------------------------------------
def bias_variance():
    rng = np.random.default_rng(11)

    def true_f(x):
        return np.sin(2.0 * x)

    xg = np.linspace(0, 3, 300)
    fig, axes = plt.subplots(1, 2, figsize=sz(9.2, 3.4), sharey=True)
    specs = [(1, "Degree 1 (high bias)"),
             (12, "Degree 12 (high variance)")]
    for ax, (deg, title) in zip(axes, specs):
        preds = []
        for _ in range(60):
            x = np.sort(rng.uniform(0, 3, 25))
            y = true_f(x) + rng.normal(0, 0.35, 25)
            p = Polynomial.fit(x, y, deg)
            preds.append(p(xg))
            ax.plot(xg, p(xg), color=GRAY, lw=0.5, alpha=0.30)
        ax.plot(xg, np.mean(preds, axis=0), color=RED, lw=1.9, label="mean fit")
        ax.plot(xg, true_f(xg), color=BLACK, lw=1.5, ls="--", label="true $f(x)$")
        ax.set_ylim(-2.3, 2.3)
        ax.set_title(title)
        ax.set_xlabel("$x$")
        _clean(ax)
    axes[0].set_ylabel("fitted value")
    fig.tight_layout()
    for ax in axes:
        _legend_below(ax, ncol=2, fontsize=8.5)
    _finish(fig, "bias_variance")


# ---------------------------------------------------------------------------
# The bias-variance trade-off
# ---------------------------------------------------------------------------
def tradeoff():
    c = np.linspace(0.2, 5, 300)
    bias2 = 3.2 * np.exp(-1.1 * c)
    var = 0.09 * c ** 1.7
    noise = np.full_like(c, 0.35)
    total = bias2 + var + noise

    fig, ax = plt.subplots(figsize=sz(5.6, 3.5))
    ax.plot(c, bias2, color=BLUE, lw=1.6, label="squared bias")
    ax.plot(c, var, color=RED, lw=1.6, label="variance")
    ax.plot(c, noise, color=GRAY, lw=1.3, ls=":", label="irreducible variance")
    ax.plot(c, total, color=BLACK, lw=2.0, label="expected test error")
    best = c[int(np.argmin(total))]
    ax.axvline(best, color=GRAY, lw=1.0, ls="--")
    ax.annotate("minimum", (best, total.min()), textcoords="offset points",
                xytext=(12, 34), fontsize=9,
                arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8))
    ax.set_xlabel("model complexity")
    ax.set_ylabel("expected squared error")
    ax.set_yticks([])
    ax.set_ylim(0, 3.6)
    _clean(ax)
    fig.tight_layout()
    _legend_below(ax, ncol=2, fontsize=9)
    _finish(fig, "tradeoff")


# ---------------------------------------------------------------------------
# Data leakage
# ---------------------------------------------------------------------------
def leakage():
    """A regressor constructed from the outcome inflates the cross-validated
    score; on data where it is unavailable the model performs no better."""
    rng = np.random.default_rng(5)
    n = 400
    X = rng.normal(size=(n, 6))
    beta = np.array([1.0, -0.8, 0.5, 0.0, 0.0, 0.0])
    logit = X @ beta
    y = (rng.uniform(size=n) < 1 / (1 + np.exp(-logit))).astype(int)
    leak = y + rng.normal(0, 0.25, n)

    Xtr, Xte, ytr, yte, ltr, lte = train_test_split(
        X, y, leak, test_size=0.4, random_state=0)

    def cv_auc(Xd, yd):
        m = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500))
        return cross_val_score(m, Xd, yd, cv=5, scoring="roc_auc").mean()

    honest_cv = cv_auc(Xtr, ytr)
    leak_cv = cv_auc(np.column_stack([Xtr, ltr]), ytr)

    m_h = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)).fit(Xtr, ytr)
    honest_test = roc_auc_score(yte, m_h.predict_proba(Xte)[:, 1])
    m_l = make_pipeline(StandardScaler(), LogisticRegression(max_iter=500)).fit(
        np.column_stack([Xtr, ltr]), ytr)
    leak_test = roc_auc_score(
        yte, m_l.predict_proba(np.column_stack([Xte, np.zeros_like(lte)]))[:, 1])

    fig, ax = plt.subplots(figsize=sz(5.4, 3.5))
    xpos = np.arange(2)
    w = 0.34
    ax.bar(xpos - w / 2, [honest_cv, leak_cv], w, color=BLUE,
           label="cross-validated AUC")
    ax.bar(xpos + w / 2, [honest_test, leak_test], w, color=RED,
           label="AUC without the leaked regressor")
    for xp, v in zip(xpos - w / 2, [honest_cv, leak_cv]):
        ax.text(xp, v + .012, f"{v:.2f}", ha="center", fontsize=9.5)
    for xp, v in zip(xpos + w / 2, [honest_test, leak_test]):
        ax.text(xp, v + .012, f"{v:.2f}", ha="center", fontsize=9.5)
    ax.axhline(0.5, color=GRAY, ls=":", lw=1.0)
    ax.set_xticks(xpos)
    ax.set_xticklabels(["Without leakage", "With leakage"])
    ax.set_ylabel("AUC")
    # a little headroom above the 1.00 bar and its label
    ax.set_ylim(0.4, 1.12)
    ax.grid(axis="x")
    _clean(ax)
    fig.tight_layout()
    _legend_below(ax, ncol=1, fontsize=8.8)
    _finish(fig, "leakage")


# ---------------------------------------------------------------------------
# RMSE and MAE under an outlier
# ---------------------------------------------------------------------------
def rmse_mae():
    rng = np.random.default_rng(2)
    x = np.linspace(0, 10, 40)
    y = 1.5 + 0.8 * x + rng.normal(0, 0.6, x.size)

    fig, axes = plt.subplots(1, 2, figsize=sz(9.0, 3.4), sharey=True)
    for ax, title in zip(axes, ["No outlier", "One outlier"]):
        yc = y.copy()
        if title == "One outlier":
            yc[20] += 9.0
        m = LinearRegression().fit(x[:, None], yc)
        pred = m.predict(x[:, None])
        rmse = np.sqrt(mean_squared_error(yc, pred))
        mae = mean_absolute_error(yc, pred)
        ax.scatter(x, yc, s=22, color=BLACK, zorder=4)
        if title == "One outlier":
            ax.scatter(x[20], yc[20], s=70, facecolor="white",
                       edgecolor=RED, lw=1.6, zorder=5)
        ax.plot(x, pred, color=BLUE, lw=1.7)
        ax.set_title(title)
        ax.text(0.04, 0.95, f"RMSE {rmse:.2f}\nMAE  {mae:.2f}",
                transform=ax.transAxes, va="top", fontsize=9,
                family="monospace")
        ax.set_xlabel("$x$")
        _clean(ax)
    axes[0].set_ylabel("$y$")
    fig.tight_layout(w_pad=2.0)
    _finish(fig, "rmse_mae")


# ---------------------------------------------------------------------------
# Accuracy under an imbalanced outcome
# ---------------------------------------------------------------------------
def accuracy_trap():
    rng = np.random.default_rng(4)
    n = 1000
    y = (rng.uniform(size=n) < 0.05).astype(int)
    pred = np.zeros_like(y)
    tn = int(np.sum((y == 0) & (pred == 0)))
    fp = int(np.sum((y == 0) & (pred == 1)))
    fn = int(np.sum((y == 1) & (pred == 0)))
    tp = int(np.sum((y == 1) & (pred == 1)))
    acc = (tp + tn) / n
    cm = np.array([[tn, fp], [fn, tp]])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=sz(9.0, 3.4),
                                   gridspec_kw={"width_ratios": [1, 1.1]})
    ax1.bar(["$y=0$", "$y=1$"], [np.sum(y == 0), np.sum(y == 1)],
            color=[BLUE, RED], width=0.55)
    for i, v in enumerate([np.sum(y == 0), np.sum(y == 1)]):
        ax1.text(i, v + 10, str(int(v)), ha="center", fontsize=10)
    ax1.set_ylabel("observations")
    ax1.set_title("Outcome frequencies")
    ax1.grid(axis="x")
    _clean(ax1)

    ax2.imshow(cm, cmap="Greys", vmin=0, vmax=cm.max() * 1.4)
    for (i, j), v in np.ndenumerate(cm):
        ax2.text(j, i, str(v), ha="center", va="center", fontsize=13)
    ax2.set_xticks([0, 1]); ax2.set_xticklabels(["pred. 0", "pred. 1"])
    ax2.set_yticks([0, 1]); ax2.set_yticklabels(["actual 0", "actual 1"])
    ax2.set_title(f"Always predict 0: accuracy {acc:.0%}")
    ax2.grid(False)
    fig.tight_layout(w_pad=2.0)
    _finish(fig, "accuracy_trap")


# ---------------------------------------------------------------------------
# ROC curve
# ---------------------------------------------------------------------------
def roc():
    """Two predicted scores of differing quality.

    The outcome depends on a latent index. Two predictions of that index are
    formed, one precise and one noisy, so the curves separate clearly and the
    area has something to distinguish.
    """
    rng = np.random.default_rng(3)
    n = 800
    z = rng.normal(size=n)
    y = (z + rng.normal(0, 0.6, n) > 0).astype(int)
    scores = [
        (z + rng.normal(0, 0.35, n), RED, "precise prediction"),
        (z + rng.normal(0, 2.20, n), BLUE, "noisy prediction"),
    ]

    fig, ax = plt.subplots(figsize=sz(5.2, 3.9))
    for s, col, lab in scores:
        fpr, tpr, _ = roc_curve(y, s)
        ax.plot(fpr, tpr, color=col, lw=1.8,
                label=f"{lab} (AUC = {roc_auc_score(y, s):.2f})")
    ax.plot([0, 1], [0, 1], color=GRAY, ls="--", lw=1.1, label="no information")
    ax.set_xlabel("false positive rate")
    ax.set_ylabel("true positive rate")
    ax.set_xlim(-0.02, 1.02); ax.set_ylim(-0.02, 1.02)
    _clean(ax)
    fig.tight_layout()
    _legend_below(ax, ncol=1, fontsize=8.5)
    _finish(fig, "roc")


# ---------------------------------------------------------------------------
# The role of the regressor, not the estimator
# ---------------------------------------------------------------------------
def monotone():
    """A monotone transformation, given to each family in turn.

    Both cells of the right-hand pair are the same number: a tree splits on
    the ordering of x, which log leaves alone. The left-hand pair is the same
    transformation worth 0.15 of RMSE to a linear model.
    """
    from sklearn.ensemble import RandomForestRegressor

    rng = np.random.default_rng(9)
    n = 120
    x = rng.uniform(0.3, 6, n)
    y = 2.0 * np.log(x) + rng.normal(0, 0.25, n)
    xtr, xte, ytr, yte = train_test_split(x, y, test_size=0.4, random_state=0)

    def rmse(model, tr, te):
        m = model().fit(tr[:, None], ytr)
        return np.sqrt(mean_squared_error(yte, m.predict(te[:, None])))

    families = (("Least squares", LinearRegression),
                ("Random forest",
                 lambda: RandomForestRegressor(n_estimators=300, random_state=0)))
    raw = [rmse(M, xtr, xte) for _, M in families]
    log = [rmse(M, np.log(xtr), np.log(xte)) for _, M in families]

    fig, ax = plt.subplots(figsize=sz(6.4, 3.4))
    pos = np.arange(2)
    ax.bar(pos - 0.19, raw, width=0.36, color=GRAY, label="regressor $x$")
    ax.bar(pos + 0.19, log, width=0.36, color=BLUE, label="regressor $\\log x$")
    for i, (u, v) in enumerate(zip(raw, log)):
        ax.text(i - 0.19, u + .012, f"{u:.2f}", ha="center", fontsize=9)
        ax.text(i + 0.19, v + .012, f"{v:.2f}", ha="center", fontsize=9)
    ax.axhline(0.25, color=BLACK, ls=":", lw=0.9)
    ax.text(-0.44, 0.262, "noise floor", fontsize=8, ha="left")
    ax.set_xticks(pos)
    ax.set_xticklabels([f for f, _ in families])
    ax.set_ylim(0, max(raw) * 1.25)
    ax.set_ylabel("test RMSE")
    ax.set_title("Outcome generated by $y = 2\\log x + \\varepsilon$", fontsize=10)
    ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    ax.grid(axis="x")
    _clean(ax)
    fig.tight_layout()
    _finish(fig, "monotone")


# ---------------------------------------------------------------------------
# Combinations neither estimator can form for itself
# ---------------------------------------------------------------------------
def combine():
    """Supplying a combination of two regressors, to each family in turn.

    Both outcomes are built from something no estimator can construct: a ratio
    in the first panel, a rank within a group in the second. Both estimators
    see the ingredients and fifteen irrelevant regressors besides. The bars
    are the cross-validated error before and after the combination is handed
    over, so the comparison is within an estimator, not between the two.
    """
    from sklearn.ensemble import RandomForestRegressor

    def score(X, y, model):
        return -cross_val_score(model, X, y, cv=5,
                                scoring="neg_root_mean_squared_error").mean()

    def both(raw, built, y):
        out = []
        for m in (LinearRegression(),
                  RandomForestRegressor(n_estimators=300, random_state=0)):
            out.append((score(raw, y, m), score(built, y, m)))
        return out

    rng = np.random.default_rng(3)
    junk = 15

    # (a) the outcome depends on a ratio of two regressors
    n = 600
    a, b = rng.uniform(1, 10, n), rng.uniform(1, 10, n)
    Z = rng.normal(size=(n, junk))
    y1 = 4 * (a / b) + rng.normal(0, 0.5, n)
    panel_a = both(np.c_[a, b, Z], np.c_[a, b, Z, a / b], y1)

    # (b) the outcome depends on the rank of x within its group. The group
    # identifier is among the regressors, so nothing is being withheld.
    n, G = 1200, 150
    g = rng.integers(0, G, n)
    x = rng.uniform(1, 10, G)[g] * rng.uniform(0.5, 1.5, n)
    Z = rng.normal(size=(n, junk))
    pct = np.empty(n)
    for k in range(G):
        m = g == k
        if m.sum():
            pct[m] = (np.argsort(np.argsort(x[m])) + 0.5) / m.sum()
    y2 = 3 * pct + rng.normal(0, 0.3, n)
    panel_b = both(np.c_[x, g, Z], np.c_[x, g, Z, pct], y2)

    fig, axes = plt.subplots(1, 2, figsize=sz(9.6, 3.4))
    titles = ("Outcome depends on a ratio $a/b$",
              "Outcome depends on rank within a group")
    for ax, res, title in zip(axes, (panel_a, panel_b), titles):
        pos = np.arange(2)
        raw = [r[0] for r in res]
        built = [r[1] for r in res]
        ax.bar(pos - 0.19, raw, width=0.36, color=GRAY, label="as given")
        ax.bar(pos + 0.19, built, width=0.36, color=BLUE,
               label="with the combination")
        for i, (u, v) in enumerate(zip(raw, built)):
            ax.text(i - 0.19, u * 1.03, f"{u:.2f}", ha="center", fontsize=8.5)
            ax.text(i + 0.19, v * 1.03, f"{v:.2f}", ha="center", fontsize=8.5)
        ax.set_xticks(pos)
        ax.set_xticklabels(["Least squares", "Random forest"], fontsize=9)
        ax.set_ylim(0, max(raw) * 1.22)
        ax.set_title(title, fontsize=10)
        ax.grid(axis="x")
        _clean(ax)
    axes[0].set_ylabel("cross-validated RMSE")
    axes[0].legend(frameon=False, fontsize=8.5, loc="upper right")
    fig.tight_layout(w_pad=2.0)
    _finish(fig, "combine")


# ---------------------------------------------------------------------------
# LASSO coefficient path
# ---------------------------------------------------------------------------
def lasso_path():
    rng = np.random.default_rng(6)
    n, p = 70, 40
    X = rng.normal(size=(n, p))
    beta = np.zeros(p)
    beta[:3] = [2.5, -2.0, 1.2]
    y = X @ beta + rng.normal(0, 2.5, n)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.4, random_state=0)

    alphas = np.logspace(-2.0, 0.9, 60)
    coefs, te_err = [], []
    for a in alphas:
        m = make_pipeline(StandardScaler(), Lasso(alpha=a, max_iter=5000))
        m.fit(Xtr, ytr)
        coefs.append(m.named_steps["lasso"].coef_)
        te_err.append(np.sqrt(mean_squared_error(yte, m.predict(Xte))))
    coefs = np.array(coefs)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=sz(9.2, 3.4))
    noise_labelled = False
    for j in range(p):
        if beta[j] != 0:
            ax1.plot(alphas, coefs[:, j], color=BLUE, lw=1.8, zorder=4,
                     label="nonzero coefficient" if j == 0 else None)
        else:
            ax1.plot(alphas, coefs[:, j], color=GRAY, lw=0.7, alpha=0.5,
                     label="zero coefficient" if not noise_labelled else None)
            noise_labelled = True
    ax1.set_xscale("log")
    ax1.axhline(0, color=BLACK, lw=0.7)
    ax1.set_xlabel("penalty $\\lambda$")
    ax1.set_ylabel("estimated coefficient")
    ax1.set_title("Coefficient paths")
    _clean(ax1)

    ax2.plot(alphas, te_err, "-o", color=RED, lw=1.6, ms=3)
    best = alphas[int(np.argmin(te_err))]
    ax2.axvline(best, color=GRAY, ls="--", lw=1.0)
    ax2.annotate("minimum", (best, min(te_err)), textcoords="offset points",
                 xytext=(14, 30), fontsize=9,
                 arrowprops=dict(arrowstyle="-", color=GRAY, lw=0.8))
    ax2.set_xscale("log")
    ax2.set_xlabel("penalty $\\lambda$")
    ax2.set_ylabel("test RMSE")
    ax2.set_title("Test error")
    _clean(ax2)
    fig.tight_layout(w_pad=2.0)
    _legend_below(ax1, ncol=2, fontsize=8.5)
    _finish(fig, "lasso_path")


# ---------------------------------------------------------------------------
# A single tree and an average of trees
# ---------------------------------------------------------------------------
def tree_rf():
    X, y = make_moons(n_samples=220, noise=0.30, random_state=2)
    xx, yy = np.meshgrid(np.linspace(X[:, 0].min() - .5, X[:, 0].max() + .5, 300),
                         np.linspace(X[:, 1].min() - .5, X[:, 1].max() + .5, 300))
    grid = np.c_[xx.ravel(), yy.ravel()]
    bg = ListedColormap(["#DCE6F1", "#F2DEDE"])
    pts = ListedColormap([BLUE, RED])

    fig, axes = plt.subplots(1, 2, figsize=sz(9.0, 3.5))
    specs = [
        (DecisionTreeClassifier(random_state=0), "Single tree"),
        (RandomForestClassifier(n_estimators=300, random_state=0),
         "Average of 300 trees"),
    ]
    for ax, (model, title) in zip(axes, specs):
        model.fit(X, y)
        zz = model.predict_proba(grid)[:, 1].reshape(xx.shape)
        ax.contourf(xx, yy, zz, levels=[0, .5, 1], cmap=bg)
        ax.contour(xx, yy, zz, levels=[.5], colors=BLACK, linewidths=0.8)
        ax.scatter(X[:, 0], X[:, 1], c=y, cmap=pts, s=16, edgecolor="white", lw=0.4)
        ax.set_title(title)
        ax.set_xticks([]); ax.set_yticks([])
        ax.grid(False)
    fig.tight_layout()
    _finish(fig, "tree_rf")


# ---------------------------------------------------------------------------
# Comparison of estimators
# ---------------------------------------------------------------------------
def compare():
    from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
    from sklearn.tree import DecisionTreeRegressor

    rng = np.random.default_rng(21)
    n = 500
    Xr = rng.normal(size=(n, 8))
    yr = (2 * np.sin(Xr[:, 0]) + Xr[:, 1] ** 2 - 1.5 * Xr[:, 2]
          + Xr[:, 0] * Xr[:, 3] + rng.normal(0, 0.6, n))
    reg_models = {
        "OLS": make_pipeline(StandardScaler(), LinearRegression()),
        "LASSO": make_pipeline(StandardScaler(), Lasso(alpha=0.05, max_iter=5000)),
        "Tree": DecisionTreeRegressor(max_depth=5, random_state=0),
        "Forest": RandomForestRegressor(n_estimators=200, random_state=0),
        "Boosting": GradientBoostingRegressor(random_state=0),
    }
    # Keep the individual fold scores: the standard error across folds is what
    # tells the reader which of these differences are differences at all.
    reg_folds = {k: -cross_val_score(m, Xr, yr, cv=5,
                                     scoring="neg_root_mean_squared_error")
                 for k, m in reg_models.items()}
    reg_scores = {k: s.mean() for k, s in reg_folds.items()}
    reg_se = {k: s.std(ddof=1) / np.sqrt(len(s)) for k, s in reg_folds.items()}

    Xc, yc = make_moons(n_samples=600, noise=0.30, random_state=7)
    clf_models = {
        "Logit": make_pipeline(StandardScaler(), LogisticRegression()),
        "Penalized\nlogit": make_pipeline(StandardScaler(), LogisticRegression(C=0.3)),
        "Tree": DecisionTreeClassifier(max_depth=5, random_state=0),
        "Forest": RandomForestClassifier(n_estimators=200, random_state=0),
        "Boosting": GradientBoostingClassifier(random_state=0),
    }
    clf_folds = {k: cross_val_score(m, Xc, yc, cv=5, scoring="roc_auc")
                 for k, m in clf_models.items()}
    clf_scores = {k: s.mean() for k, s in clf_folds.items()}
    clf_se = {k: s.std(ddof=1) / np.sqrt(len(s)) for k, s in clf_folds.items()}

    # wider than the other two-panel figures: ten estimator names have to sit
    # side by side without running into one another
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=sz(10.8, 3.4))
    ax1.bar(list(reg_scores), list(reg_scores.values()), color=BLUE, width=0.6,
            yerr=list(reg_se.values()), capsize=4,
            error_kw={"ecolor": RED, "elinewidth": 1.6, "capthick": 1.6})
    for i, (v, e) in enumerate(zip(reg_scores.values(), reg_se.values())):
        ax1.text(i, v + e + .05, f"{v:.2f}", ha="center", fontsize=9)
    ax1.set_ylim(0, max(reg_scores.values()) * 1.25)
    ax1.set_ylabel("cross-validated RMSE")
    ax1.set_title("Continuous outcome (lower better)")
    ax1.grid(axis="x")
    ax1.tick_params(axis="x", labelsize=8.5)
    _clean(ax1)

    ax2.bar(list(clf_scores), list(clf_scores.values()), color=BLUE, width=0.6,
            yerr=list(clf_se.values()), capsize=4,
            error_kw={"ecolor": RED, "elinewidth": 1.6, "capthick": 1.6})
    ax2.set_ylim(0.5, 1.09)
    for i, (v, e) in enumerate(zip(clf_scores.values(), clf_se.values())):
        ax2.text(i, v + e + .012, f"{v:.2f}", ha="center", fontsize=9)
    ax2.set_ylabel("cross-validated AUC")
    ax2.set_title("Binary outcome (higher better)")
    ax2.grid(axis="x")
    ax2.tick_params(axis="x", labelsize=8.5)
    _clean(ax2)

    fig.tight_layout(w_pad=2.0)
    _finish(fig, "compare")


# ---------------------------------------------------------------------------
# Boosting
# ---------------------------------------------------------------------------
def boosting():
    from sklearn.ensemble import GradientBoostingRegressor
    rng = np.random.default_rng(14)
    x = np.sort(rng.uniform(0, 3, 80))
    y = np.sin(2.2 * x) + 0.3 * x + rng.normal(0, 0.2, x.size)
    xg = np.linspace(0, 3, 300)

    fig, axes = plt.subplots(1, 3, figsize=sz(9.4, 3.0), sharey=True)
    for ax, m_est in zip(axes, [1, 5, 60]):
        m = GradientBoostingRegressor(n_estimators=m_est, max_depth=2,
                                      learning_rate=0.3, random_state=0)
        m.fit(x[:, None], y)
        ax.scatter(x, y, s=14, color=BLACK, alpha=0.6)
        ax.plot(xg, m.predict(xg[:, None]), color=BLUE, lw=1.8)
        ax.set_title(f"{m_est} tree" + ("s" if m_est > 1 else ""))
        ax.set_xlabel("$x$")
        _clean(ax)
    axes[0].set_ylabel("$y$")
    fig.tight_layout()
    _finish(fig, "boosting")


# ---------------------------------------------------------------------------
# Sampling variability of a single split
# ---------------------------------------------------------------------------
def cv_stability():
    rng = np.random.default_rng(8)
    n = 200
    X = rng.normal(size=(n, 5))
    y = X @ np.array([1.0, -1.0, 0.5, 0, 0]) + rng.normal(0, 1.0, n)

    single, cv = [], []
    for seed in range(40):
        Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed)
        m = LinearRegression().fit(Xtr, ytr)
        single.append(np.sqrt(mean_squared_error(yte, m.predict(Xte))))
        cv.append(-cross_val_score(LinearRegression(), X, y, cv=5,
                                   scoring="neg_root_mean_squared_error").mean())

    fig, ax = plt.subplots(figsize=sz(5.2, 3.4))
    ax.scatter(np.zeros(40) + rng.normal(0, .03, 40), single,
               facecolor="white", edgecolor=RED, s=26, lw=1.1)
    ax.scatter(np.ones(40) + rng.normal(0, .03, 40), cv,
               facecolor="white", edgecolor=BLUE, s=26, lw=1.1)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["single split", "5-fold CV"])
    ax.set_ylabel("estimated test RMSE")
    ax.set_xlim(-0.4, 1.4)
    ax.grid(axis="x")
    _clean(ax)
    fig.tight_layout()
    _finish(fig, "cv_stability")


FIGURES = {
    "overfit_reg": overfit_reg,
    "overfit_clf": overfit_clf,
    "bias_variance": bias_variance,
    "tradeoff": tradeoff,
    "leakage": leakage,
    "rmse_mae": rmse_mae,
    "accuracy_trap": accuracy_trap,
    "roc": roc,
    "monotone": monotone,
    "combine": combine,
    "lasso_path": lasso_path,
    "tree_rf": tree_rf,
    "compare": compare,
    "boosting": boosting,
    "cv_stability": cv_stability,
}


def main(argv):
    wanted = argv[1:] if len(argv) > 1 else list(FIGURES)
    for name in wanted:
        if name not in FIGURES:
            print(f"  unknown figure: {name} (have: {', '.join(FIGURES)})")
            continue
        print(f"building {name} ...")
        FIGURES[name]()
    print("done.")


if __name__ == "__main__":
    main(sys.argv)
