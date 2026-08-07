# Growth calculator

This repository is yours. You made it from a template at the start of the first
session of *Data Science for Economics*, and everything in it from here on is
your own work.

## The two halves of the session

**Git and GitHub.** You will write a small program, `growth.py`, and its tests,
and put them under version control: `git status` to see what changed, `git add`
to choose what to record, `git commit` to record it, `git push` to send it to
GitHub. The program itself is deliberately simple, because the commands are the
point.

**Python basics.** Then open [`python_basics.py`](python_basics.py) and the
emphasis reverses: half an hour on the language itself, ending with a real
dataset of about ten thousand job adverts.

That file is an ordinary Python script — `python python_basics.py` runs it from
top to bottom — but the `# %%` lines cut it into blocks, and VS Code will run
one block at a time. Put the cursor in a block and press `Shift` + `Enter`; the
output, figures included, appears in a panel beside the code. The first time,
VS Code asks which Python to use: choose the recommended 3.12.

You did not write that file, which is the normal situation when you join a
project. It ends by asking you to change one line of it and push the change
back, which is the normal thing to do next.

## Working here later

This Codespace stops itself after 30 minutes of inactivity, and nothing is lost.
Reopen it from <https://github.com/codespaces> rather than creating a second one.

Everything the code needs is already installed. If you ever want to work on your
own laptop instead, you would need Python 3.9 or later and:

```bash
pip install pandas matplotlib ipykernel
```
