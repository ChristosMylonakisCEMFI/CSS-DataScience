# Python basics — instructor notes

Taught in the second part of session 1, in the repository participants create
during the Git tutorial. The file itself is worked through live in the
Codespace; the Git deck carries only the framing and the instructions for the
closing exercise — *Now: somebody else's code*, *Set it up*, *Run it*, *Change
one thing*, *Record and publish your change*.

## Where the material lives

[`python_basics.py`](python_basics.py), in this folder. Participants fetch it
into their own repository during the session:

```bash
curl -O https://raw.githubusercontent.com/ChristosMylonakisCEMFI/CSS-DataScience/main/slides/python-basics/python_basics.py
pip install pandas matplotlib
```

Their repository is created empty in the Git tutorial, so nothing is installed
for them. They also need the **Python** extension, from the Extensions panel:
without it a `.py` file is plain text and `Shift`+`Enter` inserts a newline.

There is no Jupyter extension and no interactive window. Selected lines run in
a Python terminal and the output appears there, which is why section 5 writes
the figure to `salaries.png` rather than showing it.

Section 4 reads `postings.csv` over https, so no data file is fetched.

## Contents of `python_basics.py`

| Section | Topic |
| --- | --- |
| 1 | Values and names; `int`, `float`, `str`, `bool`; tracebacks |
| 2 | Records: dictionaries and lists |
| 3 | Functions, `for`, `if`, indentation |
| 4 | pandas: `DataFrame`, `read_csv`, missing values, filtering, `groupby` |
| 5 | One figure, written to `salaries.png` |
| 6 | Change one line, read the diff, commit and push |

Section 5 is the one to drop if time is short; section 6 is not, since the
exercise ends there.

Excluded: classes, comprehensions, recursion, NumPy as a separate topic, and
seaborn.

[`salary_summary.py`](salary_summary.py) is the same analysis as a finished
script. Not used in the session.

## Framing

Participants do not write this file. They have already built something from
nothing in `growth.py`; what remains is the other half of working with other
people — take code somebody else wrote, run it, understand a part of it well
enough to change it, and send the change back. Section 6 is that loop, and
`git diff` on a `.py` is what makes it legible.

## Before the session

Create an empty repository yourself, open a Codespace on it, and run the two
commands above, then select a few lines of the file and press `Shift`+`Enter`.

Two predictable problems in the room: the `curl` line is long and will be
mistyped, so have it ready to paste; and `Shift`+`Enter` does nothing until the
Python extension is installed, which looks like a broken file rather than a
missing extension.

## Also here

[`salary_summary.py`](salary_summary.py) — sections 5 and 6 as a self-contained
script reading the local `postings.csv`. Not used in the session.
