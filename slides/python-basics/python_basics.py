"""
Python for economists.

Select a few lines and press Shift+Enter. They run in the terminal below, and
whatever they produce appears there. A line that evaluates to something has
its value echoed, which is why you will see output you did not print.

The whole file also runs at once, with:  python python_basics.py
"""

# ---------------------------------------------------------------------------
# 1. Values and the names we give them
# ---------------------------------------------------------------------------
# "=" does not assert an equality. It stores the value on the right under the
# name on the left.

wage = 32.5                  # float: a number with decimals
hours = 38                   # int:   a whole number
occupation = "Economist"     # str:   text, in quotes
remote = True                # bool:  True or False

print(occupation, "earns", wage * hours, "per week")

# The type decides what an operator means. This is the commonest source of
# quiet errors in applied work:

print(38 * 2)        # arithmetic
print("38" * 2)      # on text the same operator repeats, it does not multiply

# "38" is not the number 38. When a column read from a file misbehaves in ways
# that make no sense, this is almost always why.
#
# When something is wrong, Python prints a traceback. Read the LAST line first:
# that is the error. The lines above it only say where it happened.


# ---------------------------------------------------------------------------
# 2. Records: dictionaries and lists
# ---------------------------------------------------------------------------
# A scraper hands you one job posting at a time, each a set of named fields.
# That is a dictionary: key-value pairs, looked up by name, not by position.

posting = {
    "company": "Affirm",
    "title": "AI Solutions Engineer",
    "is_remote": True,
    "lo": 150_000,
    "hi": 225_000,
}

print(posting["title"])

# Fields can be added and changed afterwards.

posting["currency"] = "USD"
posting["hi"] = 230_000
print(posting["lo"], "to", posting["hi"], posting["currency"])

# Many records is a list: ordered, and indexed from ZERO.

postings = [
    posting,
    {"company": "Stripe", "title": "Economist",      "is_remote": False,
     "lo": 180_000, "hi": 250_000, "currency": "USD"},
    {"company": "Ramp",   "title": "Data Scientist", "is_remote": True,
     "lo": 160_000, "hi": 210_000, "currency": "USD"},
]

print(len(postings), "postings")
print(postings[0]["company"])     # the first
print(postings[-1]["company"])    # the last

# A list of dictionaries is the shape data has before it becomes a table.


# ---------------------------------------------------------------------------
# 3. Functions and loops
# ---------------------------------------------------------------------------
# A function names a calculation so you write it once - you have already
# written one, percentage_change, in growth.py. A loop applies it to each
# record in turn.
#
# The colon and the indentation are not decoration: they are how Python knows
# which lines belong to the function or the loop.

def midpoint(p):
    return (p["lo"] + p["hi"]) / 2

for p in postings:
    print(p["company"], "-", p["title"], ":", midpoint(p))

# "if" chooses between branches on a condition.

for p in postings:
    if p["is_remote"]:
        print(p["title"], "is remote")
    else:
        print(p["title"], "is on site")

# That is the whole of the language you need today. Everything below is a
# library: code other people wrote, that you import and use.


# ---------------------------------------------------------------------------
# 4. Tables: pandas
# ---------------------------------------------------------------------------
# Looping by hand does not scale to ten thousand records. A DataFrame is a
# table with named columns, where an operation applies to a whole column.

import pandas as pd

print(pd.DataFrame(postings))

# read_csv usually takes a filename, but a web address works too - so this file
# needs no data of its own. About ten thousand job adverts, collected from
# sixty-three company career pages in the web scraping session:

URL = ("https://raw.githubusercontent.com/ChristosMylonakisCEMFI/"
       "CSS-DataScience/main/slides/web-scraping/data/postings.csv")

jobs = pd.read_csv(URL)

print(jobs.shape)          # (rows, columns)
print(jobs.head())

# Look at the shape and the first rows before anything else. Then look at what
# is missing - in real data that is the rule, not the exception.

print(jobs.isna().mean().round(3))

# Half the postings state no salary, and those that do use several currencies.
# So select the rows that can actually be used. Conditions are combined with &
# (and) and | (or), each in brackets. A new column is created by assigning to a
# name that does not exist yet, and the arithmetic applies to the whole column
# at once, with no loop.

CURRENCY = "USD"

pay = jobs[(jobs["currency"] == CURRENCY) & jobs["lo"].notna()].copy()
pay["mid"] = (pay["lo"] + pay["hi"]) / 2

print(len(pay), "postings with a salary range in", CURRENCY)
print(pay["mid"].describe().round(0))

# groupby is the operation you will use most: split into groups, compute the
# same statistic within each.

print(pay.groupby("is_remote")["mid"].agg(["count", "mean", "median"]).round(0))

# Remote and on-site pay almost the same. Conclude nothing from that: these are
# different jobs at different firms, and the comparison holds nothing fixed.
# Making it mean something is the subject of the web scraping session.


# ---------------------------------------------------------------------------
# 5. One figure
# ---------------------------------------------------------------------------
# The pattern below - make a figure and an axis, draw on the axis, label it -
# is worth copying verbatim. Everything else you plot is a variation on it.
#
# There is no screen attached to a Codespace, so the figure is written to a
# file. Click salaries.png in the Explorer to see it.

import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.5, 3.5))
_ = ax.hist(pay["mid"] / 1000, bins=40, color="0.35")
ax.set_xlabel(f"Midpoint of posted salary range (thousands of {CURRENCY})")
ax.set_ylabel("Number of postings")
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig("salaries.png", dpi=150)
print("wrote salaries.png")

# The distribution is right-skewed, which is why the median and the mean above
# differ. It is also lumpy: firms post round numbers.


# ---------------------------------------------------------------------------
# 6. Change one thing, and send it back
# ---------------------------------------------------------------------------
# You did not write this file. You fetched it, which is how most code reaches
# you: already written, by someone else, to be read and run before it is
# changed.
#
# Make one edit. In section 5, halve the number of bins, and run those lines
# again. The shape should survive; the detail should coarsen.
#
# Then, in the terminal:
#
#     git status
#     git diff
#
# git diff shows your one line and nothing else. That readability is why this
# course keeps its work in .py files.
#
# Then record and publish it:
#
#     git add python_basics.py
#     git commit -m "Use 20 histogram bars"
#     git push
#
# Refresh your repository page on GitHub and your change is there, with your
# name against it. That is the whole loop: read someone's code, run it, change
# one thing, explain the change, push it.
