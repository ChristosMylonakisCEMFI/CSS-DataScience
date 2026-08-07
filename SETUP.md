# Getting ready for the course

Do this **before the first session**.

You need a free **GitHub account** and a **browser**. Nothing is installed on
your laptop: we work on a computer GitHub provides in the cloud, called a
*Codespace*, which arrives with Python and everything else already on it.

**Step 1 is all that session 1 needs.** Steps 2 to 4 prepare the machine used
in sessions 2 and 3, and confirm that your account can open one at all. Do them
all now: the sessions run in the same week, and there is no time in between.

---

## 1. Create a GitHub account

Sign up at <https://github.com/signup>, then **open the email GitHub sends you
and confirm your address**. An unconfirmed account cannot open a Codespace,
and this is where most people get stuck.

## 2. Open the course in a Codespace

On the course repository page,
<https://github.com/ChristosMylonakisCEMFI/CSS-DataScience>:

**green `< > Code` button → Codespaces tab → Create codespace on main**.

The first launch takes a few minutes while it installs Python, the course
packages, and Chrome. Then you are looking at VS Code in your browser, with
the course files on the left and a terminal at the bottom. If you cannot see
the terminal, press `Ctrl` + `` ` ``.

## 3. Tell Git who you are

In the terminal, with your own name and the email you used for GitHub:

```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Despite the name, `--global` means "this machine", not "this account". A new
Codespace will ask again; session 1 covers it.

## 4. Check that it worked

```
python check_setup.py
```

Every line should say `PASS`, ending with "All checks passed". If a line says
`FAIL`, the exact fix is printed underneath it — do that, then run the command
again. `NOTE` is a suggestion, not a problem.

**If it does not pass, email the whole screen to <christos.mylonakis@cemfi.edu.es>.**
Do not spend an hour on it, and do not leave it until the first session.

---

## Reopening your Codespace later

Go to <https://github.com/codespaces> and click the one you made. It resumes
in seconds, with your files exactly as you left them.

**Do not click "Create codespace on main" a second time.** That builds another
machine and spends your free hours twice.

## Worth knowing

- It stops itself after 30 minutes of inactivity. Nothing is lost.
- GitHub gives free accounts 120 core-hours a month — about 60 hours on the
  machine we use, far more than this course needs. Stop it rather than leaving
  it running overnight.
- Delete your Codespaces from the same page when the course is over.
- Want to keep your own changes on GitHub? Click **Fork** on the course
  repository, <https://github.com/ChristosMylonakisCEMFI/CSS-DataScience>,
  and create the Codespace on your copy. Otherwise your edits live only inside
  the Codespace, which is fine for following along.

## In the sessions

Come with the four steps above already done. There is no time in the room to
sort out an account that cannot open a Codespace.

- **Session 1 (Git, GitHub, and Python)** needs only your GitHub account. You
  will create a new, empty repository of your own and a second Codespace on it,
  in the room, so that you see every step yourself.
- **Sessions 2 and 3 (prediction, web scraping)** use the Codespace you made
  today. Reopen it and the code is there.
- **Do not run `05_scale_up.py` in class.** It contacts about 109 websites,
  and a whole room doing that at once gets everyone blocked. Its output is
  already saved in the course repository, <https://github.com/ChristosMylonakisCEMFI/CSS-DataScience>,
  so session 3 works without it. Run it at home if you are curious.

## If something goes wrong

**No "Codespaces" tab on the Code button** — you are not signed in, or your
email is not confirmed yet.

**"You have exceeded your usage quota"** — your free allowance for this month
is spent, usually on another project. Email <christos.mylonakis@cemfi.edu.es>;
do not enter card details.

**Still building after ten minutes** — delete it at
<https://github.com/codespaces> and create it again. A second attempt almost
always works.

**Many packages `FAIL` at once** — the machine was handed over before it
finished setting up. Delete it at <https://github.com/codespaces> and create
it again.

---

## Alternative: working on your own laptop

Only if you would rather not use Codespaces. You need Python 3.9+ from
<https://www.python.org/downloads/> (on Windows, tick **"Add python.exe to
PATH"** in the installer), VS Code from <https://code.visualstudio.com/> with
its Python extension, Git from <https://git-scm.com/downloads>,
and Chrome from <https://www.google.com/chrome/>.

Then, in PowerShell (Windows) or Terminal (Mac):

```
git clone https://github.com/ChristosMylonakisCEMFI/CSS-DataScience.git
cd CSS-DataScience
python -m venv .venv
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # Mac
python -m pip install -r requirements.txt
python check_setup.py
```

On a Mac, write `python3` in place of `python`. Use the same `.venv` for every
session. If packages are missing, `python check_setup.py --fix` installs them.
