# Python basics — instructor notes

Thirty minutes, taught immediately after the Git and GitHub tutorial, in the
same Codespace and the same repository the participants have just created.

## How the two halves fit together

Participants start the session by copying a **template repository** — see
[`template-repo/`](../../template-repo/) at the top of this repo, which holds
its contents. Their new repository arrives with a README, `python_basics.py`,
and a `.devcontainer` recipe that installs pandas, matplotlib and ipykernel.

For the first ninety minutes that file sits unopened in the Explorer while they
write `growth.py` and learn `status`, `add`, `commit`, `push`. Then they open it
and the emphasis reverses: the language becomes the subject and Git the
background.

One repository, one Codespace, one browser tab, nothing to install and no data
file to find. Section 5 reads `postings.csv` over https from this repository, so
the template carries no data of its own.

## Why a script with `# %%` blocks, and not a notebook

`python_basics.py` is an ordinary Python file. The `# %%` comments cut it into
blocks that VS Code will run one at a time, with output and figures appearing in
a panel beside the code — the interactive feel of a notebook, in a file that
behaves like source code.

That matters because of how the session ends. Participants change one line and
push it, so `git diff` is part of the exercise, and on a `.py` it shows their one
line and nothing else. The same edit in a `.ipynb` would sit inside a JSON blob
next to the saved output, and would need a "clear all outputs" ritual before
every commit to stay readable. It also makes the whole course one format:
sessions 2 and 3 are scripts too.

The cost is that the prose is comments rather than rendered markdown. Blocks
marked `# %% [markdown]` do render if you run them, but in the editor they read
as comment text.

## Publishing the template (do this once)

1. Create a new, empty repository on your account named
   `growth-calculator-template`.
2. Copy in everything from [`template-repo/`](../../template-repo/) — the
   README, `python_basics.py`, and the `.devcontainer` folder — and push.
3. In that repository: **Settings → General → tick "Template repository"**.
4. Check that **Use this template** now appears as a green button on its page.

Do **not** add a `.gitignore`. Creating one is a lesson in the Git tutorial, and
supplying it in advance spoils that section.

If you name the repository something else, change `\templaterepo` near the top
of
[`github_codespaces_tutorial.tex`](../git-github-codespaces/github_codespaces_tutorial.tex)
and rebuild; the slide picks it up from there.

The template is the only home of `python_basics.py`. Edit it there rather than
keeping a second copy here, so there is nothing to keep in sync.

## What it covers, and roughly when

| | Section | Minutes |
| --- | --- | --- |
| 1 | Running a file in blocks: `# %%`, `Shift`+`Enter`, execution order | 2 |
| 2 | Values and names; `int`, `float`, `str`, `bool`; reading a traceback | 4 |
| 3 | Records: dictionaries and lists | 6 |
| 4 | Functions, `for`, `if`, and why indentation is syntax | 5 |
| 5 | Tables: `DataFrame`, `read_csv`, missing values, filtering, `groupby` | 10 |
| 6 | One figure in matplotlib | 3 |
| 7 | Change one line, read the diff, commit and push | 2 |

Thirty with no slack. If you are running late, section 6 is the one to cut: the
figure is the nicest thing in the session but the least load-bearing for what
follows. Do not cut section 7 — it is the point of the exercise.

Deliberately absent: classes, comprehensions, recursion, NumPy as a topic in its
own right, and seaborn. Each is defensible in a longer course and none is needed
to read the code in sessions 2 and 3.

## The framing to say out loud

Participants do not write this file, and that is deliberate. They have already
built something from nothing that morning, in `growth.py`. What they have not
done is the other half of working with other people: take code somebody else
wrote, run it, understand a piece of it well enough to change it, and send the
change back. Section 7 is that loop, and `git diff` on a `.py` is what makes it
legible.

## Also here

[`salary_summary.py`](salary_summary.py) is sections 5 and 6 written as a
self-contained program, reading the local copy of `postings.csv`. It is not used
in the session, but it is a compact worked example if somebody asks what the
analysis looks like as a finished script.

```bash
cd slides/python-basics
python salary_summary.py
```

## Two things to watch in the room

**Clicking the wrong button.** Someone will use "New repository" instead of "Use
this template" and end up with an empty repo and no `python_basics.py`. The fix
is to delete it and start again from the template page; it takes a minute.

**The interpreter prompt.** The first time anyone presses `Shift`+`Enter`, VS
Code asks which Python to use. Say out loud that this will happen and that the
recommended 3.12 is the right answer, before thirty people ask individually.
