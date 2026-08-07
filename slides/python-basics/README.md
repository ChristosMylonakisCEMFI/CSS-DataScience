# Python basics — instructor notes

Taught in the second part of session 1, in the repository participants create
during the Git tutorial. The file itself is worked through live in the
Codespace; the Git deck carries only the framing and the instructions for the
closing exercise — *Now: somebody else's code*, *Open it and run it*, *Change
one thing*, *Record and publish your change*.

## Where the material lives

<https://github.com/ChristosMylonakisCEMFI/growth-calculator-template>

Participants copy it with **Use this template** in step 1 of the Git tutorial.
Their repository then contains `python_basics.py` and a devcontainer that
installs pandas, matplotlib and ipykernel, so the file runs with nothing to
install.

The template is public, since a private one cannot be copied by non-collaborators;
participants make their own copy private. It carries no `.gitignore`, because
creating one is a lesson in the Git tutorial. Edit the template directly to
change what participants receive; [`template-repo/`](../../template-repo/) is a
mirror kept for review, and the two must be updated together.

Renaming the template requires changing `\templaterepo` in
[`github_codespaces_tutorial.tex`](../git-github-codespaces/github_codespaces_tutorial.tex).

## Contents of `python_basics.py`

| Section | Topic |
| --- | --- |
| 1 | Running a file in blocks: `# %%`, `Shift`+`Enter`, execution order |
| 2 | Values and names; `int`, `float`, `str`, `bool`; tracebacks |
| 3 | Records: dictionaries and lists |
| 4 | Functions, `for`, `if`, indentation |
| 5 | pandas: `DataFrame`, `read_csv`, missing values, filtering, `groupby` |
| 6 | One figure in matplotlib |
| 7 | Change one line, read the diff, commit and push |

Section 5 reads `postings.csv` over https, so the template holds no data.
Section 6 is the section to drop if time is short; section 7 is not, since the
exercise ends there.

Excluded: classes, comprehensions, recursion, NumPy as a separate topic, and
seaborn.

## Framing

Participants do not write this file. They have already built something from
nothing in `growth.py`; what remains is the other half of working with other
people — take code somebody else wrote, run it, understand a part of it well
enough to change it, and send the change back. Section 7 is that loop, and
`git diff` on a `.py` is what makes it legible.

## Before the session

Copy the template yourself, open a Codespace on the result, and confirm that the
interpreter prompt behaves and that `Shift`+`Enter` runs a block.

Two predictable problems in the room: participants who click "New repository"
instead of "Use this template" and end up without the file, and the interpreter
prompt on the first `Shift`+`Enter` — announce the answer, Python 3.12, before
it is asked thirty times.

## Also here

[`salary_summary.py`](salary_summary.py) — sections 5 and 6 as a self-contained
script reading the local `postings.csv`. Not used in the session.
