# %% [markdown]
# # Python for economists
#
# So far this repository has been about Git: you created it, wrote `growth.py`,
# and pushed your commits to GitHub. The commands were the subject and the
# Python was incidental. Here they swap over.
#
# This file covers the five ideas you cannot read anyone else's code without:
# values, records, loops and functions, tables, and figures. It is not a course
# in the language, which takes months.
#
# From section 5 it uses a real file: about ten thousand job adverts collected
# from sixty-three company career pages. That file is the one collected in the
# web scraping session.

# %% [markdown]
# ---
# ## 1. How this file works
#
# `growth.py` was a script. You ran it with `python growth.py` and it went from
# top to bottom, all at once.
#
# This is a script too, and you can still run it that way. But the `# %%` lines
# cut it into **blocks**, and VS Code will run a single block on its own. Put
# your cursor in the block below and press `Shift` + `Enter`.

# %%
2 + 2

# %% [markdown]
# A panel opens beside the code and shows the answer. The first time you do
# this, VS Code asks which Python to use — choose the recommended 3.12. It only
# asks once.
#
# Three things to notice, because all three cause confusion later.
#
# **The value of the last line is displayed for you.** You did not have to ask
# for it. That happens only when you run a block this way; running the whole
# file with `python python_basics.py` shows nothing but what you explicitly
# `print()`, exactly as `growth.py` did.
#
# **The blocks share one memory.** A name created in one is available in the
# next.
#
# **They run in the order you run them**, not the order they appear on the
# screen. A name from a block you have not run yet does not exist. If things
# stop making sense, run the blocks again from the top.

# %% [markdown]
# ---
# ## 2. Values and the names we give them
#
# `=` does not assert an equality. It stores the value on the right under the
# name on the left, so that you can refer to it again.

# %%
wage = 32.5                  # float: a number with decimals
hours = 38                   # int:   a whole number
occupation = "Economist"     # str:   text, in quotes
remote = True                # bool:  True or False

weekly = wage * hours
print(occupation, "earns", weekly, "per week")

# %% [markdown]
# Python decides the type from what you wrote, and the type decides what the
# operators mean. This is the commonest source of quiet errors in applied work,
# so it is worth seeing once, deliberately:

# %%
print(38 * 2)        # arithmetic
print("38" * 2)      # the same operator on text: repetition, not multiplication

# %% [markdown]
# `"38"` is not the number 38. When a column read from a file misbehaves in ways
# that make no sense, this is almost always why.
#
# When something is genuinely wrong, Python stops and prints a *traceback*. It
# is long, and beginners read it from the top. Read the **last line first**:
# that is the error. The lines above it only say where it happened.

# %% [markdown]
# ---
# ## 3. Records: dictionaries and lists
#
# A scraper does not hand you a table. It hands you one job posting at a time,
# each a set of fields with names. In Python that is a **dictionary**: a
# collection of `key: value` pairs, looked up by name rather than by position.

# %%
posting = {
    "company": "Affirm",
    "title": "AI Solutions Engineer",
    "is_remote": True,
    "lo": 150_000,
    "hi": 225_000,
}

posting["title"]

# %% [markdown]
# Fields can be read, changed, and added after the fact.

# %%
posting["currency"] = "USD"              # add a field
posting["hi"] = 230_000                  # change one

print(posting["lo"], "to", posting["hi"], posting["currency"])
print(list(posting.keys()))

# %% [markdown]
# Many records is a **list**: ordered, and indexed from **zero**.

# %%
postings = [
    posting,
    {"company": "Stripe", "title": "Economist",      "is_remote": False,
     "lo": 180_000, "hi": 250_000, "currency": "USD"},
    {"company": "Ramp",   "title": "Data Scientist", "is_remote": True,
     "lo": 160_000, "hi": 210_000, "currency": "USD"},
]

print(len(postings), "postings")
print(postings[0]["company"])     # the first one
print(postings[-1]["company"])    # the last one

# %% [markdown]
# A list of dictionaries is the natural shape of data before it becomes a table,
# and it is exactly what the scraping session produces.

# %% [markdown]
# ---
# ## 4. Doing the same thing to every record
#
# A **function** names a calculation so that you write it once — you have
# already written one, `percentage_change`, in `growth.py`. A **loop** applies
# it to each record in turn.
#
# Note the colon and the indentation: in Python, indentation is not decoration.
# It is how the language knows which lines belong to the function or the loop.

# %%
def midpoint(p):
    # the middle of a posted salary range
    return (p["lo"] + p["hi"]) / 2


for p in postings:
    print(p["company"], "-", p["title"], ":", midpoint(p))

# %% [markdown]
# `if` chooses between branches on a condition, and combines with the loop:

# %%
for p in postings:
    if p["is_remote"]:
        print(p["title"], "is remote")
    else:
        print(p["title"], "is on site")

# %% [markdown]
# That is the whole of the language you need today: values, dictionaries, lists,
# functions, loops, and `if`. Everything below is a *library* — code other
# people wrote, that you import and use.

# %% [markdown]
# ---
# ## 5. Tables: pandas
#
# Looping over records by hand does not scale to ten thousand of them. **pandas**
# gives you the object you actually want, a `DataFrame`: a table with named
# columns, where an operation applies to a whole column at once.
#
# Our three records become a table directly.

# %%
import pandas as pd

df = pd.DataFrame(postings)
df

# %% [markdown]
# Now the real file. `read_csv` usually takes a filename, but it will take a web
# address just as happily — which is convenient here, because it means this
# repository needs no data file of its own. The address below is the copy of
# `postings.csv` that lives in the course repository on GitHub.

# %%
URL = ("https://raw.githubusercontent.com/ChristosMylonakisCEMFI/"
       "CSS-DataScience/main/slides/web-scraping/data/postings.csv")

jobs = pd.read_csv(URL)

print(jobs.shape)          # (rows, columns)
jobs.head()

# %% [markdown]
# Always look at the shape and the first rows before anything else. The second
# thing to look at is what is **missing** — in real data this is the rule, not
# the exception.

# %%
jobs.isna().mean().round(3)      # share of missing values, by column

# %% [markdown]
# Roughly half the postings state no salary at all, and those that do use
# several currencies. Any statement about pay has to be conditioned on both, so
# we select the rows we can actually use.
#
# Three things to read carefully. The currency is written once, as a name, so
# that changing it changes the selection and everything reported afterwards.
# Conditions are combined with `&` (and) and `|` (or), and each must be wrapped
# in brackets. And a new column is created simply by assigning to a name that
# does not exist yet — the arithmetic applies to the whole column at once, with
# no loop.

# %%
CURRENCY = "USD"

pay = jobs[(jobs["currency"] == CURRENCY) & jobs["lo"].notna()].copy()
pay["mid"] = (pay["lo"] + pay["hi"]) / 2

print(len(pay), "postings with a salary range in", CURRENCY)
pay["mid"].describe().round(0)

# %% [markdown]
# `groupby` is the operation you will use most: split the rows into groups, and
# compute the same statistic within each.

# %%
pay.groupby("is_remote")["mid"].agg(["count", "mean", "median"]).round(0)

# %% [markdown]
# Remote and on-site postings pay almost the same. Resist the temptation to
# conclude anything from that: these are different jobs at different firms, and
# the comparison holds nothing fixed. Making it mean something is the subject of
# the scraping session, which returns to exactly this table.

# %% [markdown]
# ---
# ## 6. One figure
#
# **matplotlib** is the standard plotting library. The pattern below — create a
# figure and an axis, draw on the axis, label it — is worth copying verbatim,
# because everything else you will ever plot is a variation on it.

# %%
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(6.5, 3.5))
ax.hist(pay["mid"] / 1000, bins=40, color="0.35")
ax.set_xlabel(f"Midpoint of posted salary range (thousands of {CURRENCY})")
ax.set_ylabel("Number of postings")
ax.spines[["top", "right"]].set_visible(False)
plt.show()

# %% [markdown]
# The distribution is right-skewed, which is why the median and the mean above
# differ. It is also visibly lumpy: firms post round numbers.

# %% [markdown]
# ---
# ## 7. Change one thing, and send it back
#
# You did not write this file. Somebody else did, and you have just run it,
# which is the ordinary condition of working on a project with other people.
# The next step is the one that matters: understand a piece of it well enough to
# change it, and then return your change.
#
# **Make one small edit.** Pick whichever you prefer:
#
# - in section 6, halve the number of bins in the histogram, and run that
#   block again;
# - in section 5, set `CURRENCY` to euros instead, and see how many postings
#   survive.
#
# **Then look at what you changed**, in the terminal:
#
# ```bash
# git status
# git diff
# ```
#
# `git diff` shows your one line, and only your one line. That readability is
# not an accident: it is why the course keeps its work in `.py` files. The same
# edit inside a Jupyter notebook would be buried in the notebook's saved output,
# and the diff would be unreadable.
#
# **Then record and send it:**
#
# ```bash
# git add python_basics.py
# git commit -m "Use twenty bins in the salary histogram"
# git push
# ```
#
# Refresh your repository page on GitHub and your change is there, with your
# name on it. That is the whole collaboration loop: read someone's code, run it,
# change one thing, explain the change, push it.
#
# ### Where to go from here
#
# - Section 5 is what the prediction session assumes.
# - Sections 3 to 5 are what the web scraping session assumes.
# - Both of those sessions are written as scripts like this one.
# - When you are stuck, the last line of the error and the library's
#   documentation will settle it faster than a search engine.
