# Python basics — instructor notes

Taught in the second part of session 1, in the repository participants create
during the Git tutorial. The file itself is worked through live in the
Codespace; the Git deck carries only the framing and the instructions for the
closing exercise — *Now: somebody else's code*, *Open it and run it*, *Change
one thing*, *Record and publish your change*.

## Where the material lives

[`python_basics.py`](python_basics.py), in this folder. Participants fetch it
into their own repository during the session:

```bash
curl -O https://raw.githubusercontent.com/ChristosMylonakisCEMFI/CSS-DataScience/main/slides/python-basics/python_basics.py
pip install pandas matplotlib ipykernel
```

Their repository is created empty in the Git tutorial, so nothing is installed
for them. `pip install` reports packages that are already present and does
nothing further, so the line is safe whatever the Codespace image happens to
carry.

Section 5 reads `postings.csv` over https, so no data file is fetched.

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

Create an empty repository yourself, open a Codespace on it, and run the two
commands above followed by the first block of the file.

Two predictable problems in the room: the `curl` line is long and will be
mistyped, so have it ready to paste; and the interpreter prompt on the first
`Shift`+`Enter` — announce that it will appear before it is asked thirty
times.

## Also here

[`salary_summary.py`](salary_summary.py) — sections 5 and 6 as a self-contained
script reading the local `postings.csv`. Not used in the session.
