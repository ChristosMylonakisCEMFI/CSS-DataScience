# Getting ready for the course

Please do this **before the first session**, ideally a week ahead. It takes
about fifteen minutes.

You need two things, and you almost certainly have one of them already:

1. a free GitHub account;
2. a web browser.

That is the whole list. **You do not have to install Python, or an editor, or
anything else on your laptop.** We work on a computer that GitHub gives us in
the cloud, called a *Codespace*, and it arrives with everything already on it.
You use it through an ordinary browser tab.

You do not need to know anything about programming to follow these steps. Do
them in order. At the end you will run one command that checks everything and
tells you whether you are ready.

If you get stuck at any point, stop and email us. It is far easier to sort out
beforehand than in the room.

> Prefer to work on your own laptop instead? That is fine, and the appendix at
> the end explains how. It takes longer and there is more to go wrong, so we
> suggest doing the steps below first, and treating the laptop version as a
> bonus.

---

## Part 1. Create a GitHub account

1. Go to <https://github.com/signup> and create a free account.
2. GitHub emails you a code. **Open the email and confirm your address.** An
   unconfirmed account cannot open a Codespace, and this is the most common
   reason people get stuck at Part 2.

The free account is enough. You will never be asked to pay or to enter card
details for this course.

Write your username and password down somewhere you will find them again.

---

## Part 2. Open the course in a Codespace

1. Make sure you are **signed in to GitHub** in your browser.
2. Go to the course repository:
   <https://github.com/ChristosMylonakisCEMFI/CSS-DataScience>
3. Click the green **`< > Code`** button near the top right.
4. In the little panel that opens, click the **Codespaces** tab (next to
   "Local").
5. Click **Create codespace on main**.

A new tab opens and starts building your machine. **The first time takes
around three to five minutes.** You will see text scrolling past; you do not
need to read it. Leave the tab alone until it settles down.

When it is ready you are looking at an editor. Three parts matter:

- **the left column** — the list of files in the course;
- **the middle** — where files open when you click them;
- **the bottom panel** — the *terminal*, where you type commands.

If you cannot see the terminal, press `Ctrl` and the backtick key `` ` ``
together (the key just above `Tab`), or use the menu at the top left:
**Terminal → New Terminal**.

Everything from here on is typed into that bottom panel: type the line, press
Enter, wait until the cursor comes back before typing the next one.

---

## Part 3. Tell Git your name

Git records who made each change to a file, so it wants to know who you are.
Type these two lines into the terminal, replacing the name and email with your
own. Use the same email address as your GitHub account, and keep the quotation
marks:

```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Nothing visible happens. That is what success looks like.

---

## Part 4. Check that everything works

Type:

```
python check_setup.py
```

You get one line per item. If everything is in place, it ends like this:

```
  [PASS] Python 3.12.4
  [PASS] package: requests  2.32.5
  [PASS] package: bs4  4.12.3
  [PASS] package: selenium  4.36.0
  [PASS] package: pandas  2.2.1
  [PASS] package: numpy  1.26.4
  [PASS] package: matplotlib  3.8.3
  [PASS] package: sklearn  1.4.1
  [PASS] Git  git version 2.45.1
  [PASS] Git knows who you are  Your Name <you@example.com>
  [PASS] browser (Chrome/Edge)  google-chrome
  [PASS] VS Code (the editor)  you are working in a Codespace
  [PASS] selenium driver cache  ok
  [PASS] chromedriver (auto-managed by Selenium 4)  launched ok
  [PASS] network: reach the Greenhouse API  HTTP 200

All checks passed. You are ready for the course.
```

**If any line says `FAIL`**, the exact fix is printed just underneath it. Do
what it says, then run `python check_setup.py` again.

A line marked `NOTE` is a suggestion, not a problem. Ignore it.

**You are not expected to understand this output.** If it does not end with
"All checks passed", copy the whole panel into an email and send it to us.

---

## Part 5. Four things to know about Codespaces

**Your work is saved.** Closing the tab does not lose anything. The Codespace
keeps your files exactly as you left them.

**It stops itself after 30 minutes of inactivity.** This is normal and costs
you nothing. Reopening it puts everything back.

**To get back to it later**, go to <https://github.com/codespaces> and click
the one you created. Starting a stopped Codespace takes a few seconds, not the
few minutes the first build took. You do not create a new one each time.

**It is free, within a generous allowance.** GitHub gives free accounts 120
core-hours a month, which is about 60 hours of actual use on the size of
machine we get — far more than this course needs. Two small courtesies keep
you well inside it: click **Stop** rather than leaving it open overnight
(from <https://github.com/codespaces>, the "..." menu next to your Codespace),
and do not create several Codespaces when one will do.

---

## If something goes wrong

**There is no "Codespaces" tab on the green Code button**
You are not signed in to GitHub, or your email address is not yet confirmed.
Sign in, check your inbox for the confirmation email from GitHub, then reload
the page.

**"You have exceeded your usage quota" or a request for a payment method**
Your free allowance for this month is spent — usually because of another
course or project. It resets at the start of your next billing month. Tell us
and we will sort something out; do not enter card details on our account.

**The Codespace has been building for more than ten minutes**
Close the tab, go to <https://github.com/codespaces>, delete the one that is
stuck, and create it again from Part 2. A second attempt almost always works.

**`python: command not found`, or a `FAIL` on many packages at once**
The machine was handed to you before it finished setting itself up. In the
terminal, run `bash .devcontainer/setup.sh`, wait for it to finish, then run
the check again.

**Anything else**
Send us a screenshot of the whole browser window. Please do not spend an hour
on it alone.

---

## Before the first session

- Open your Codespace once and confirm `python check_setup.py` still passes.
- Do this on the connection you will actually use in class, if you can.
- Make sure you can sign in to GitHub without having to reset your password.
- Bring your charger.

That is everything. See you there.

---
---

# Appendix: working on your own laptop instead

**This is optional.** Everything in the course runs in the Codespace, and you
can safely ignore this appendix. It is here for two kinds of people: those who
would rather not depend on the internet in the room, and those who want to
keep using Python after the summer school is over.

Allow about half an hour, most of it waiting for downloads.

### A1. Install Python

Go to <https://www.python.org/downloads/> and click the large download button.
Version 3.9 or newer is fine.

**On Windows** — open the file you downloaded. On the installer's first
screen, at the bottom, there is a checkbox:

> **Add python.exe to PATH**

**Tick that box before clicking Install.** This is the single most common
reason a laptop setup fails later. If you have already installed Python
without it, run the installer again and choose "Modify".

**On a Mac** — open the file you downloaded and click through the installer.
There is nothing to tick.

### A2. Install Visual Studio Code

This is the editor. In the Codespace you get it for free in the browser; on
your laptop you install it yourself.

1. Download it from <https://code.visualstudio.com/> and install it.
2. Open it. In the left-hand strip of icons, click the one made of squares
   (**Extensions**), usually the fifth one down.
3. Search for `Python` and install the one published by **Microsoft**.
4. Search for `Jupyter` and install that one too, also by Microsoft.

### A3. Install Git

**On Windows** — download it from <https://git-scm.com/downloads> and run the
installer. It asks a lot of questions; **click Next on every screen** and
accept the defaults. None of them matter for us.

**On a Mac** — Git may already be there. If it is not, your Mac will offer to
install it during step A5; accept.

### A4. Install Google Chrome

The scraping session makes a browser visit pages by itself, and the code
expects Chrome: <https://www.google.com/chrome/>. You need not make it your
default browser. (Microsoft Edge also works, and is already on every Windows
machine.)

### A5. Open a terminal and download the course

The terminal is a window where you type commands instead of clicking. It looks
unfriendly and is harmless.

**On Windows** — press Start, type `powershell`, open **Windows PowerShell**.
**On a Mac** — press `Cmd` and the space bar, type `terminal`, press Enter.

Then type these three lines, one at a time, pressing Enter after each:

```
cd Documents
git clone https://github.com/ChristosMylonakisCEMFI/CSS-DataScience.git
cd CSS-DataScience
```

The first moves to your Documents folder, the second copies the course onto
your computer, the third moves into the new folder.

> **On a Mac**, if the second line offers to install "command line developer
> tools", accept, wait, then run the line again. That was Git installing
> itself.

> If your Documents folder is synced with OneDrive or Dropbox and the first
> line fails, leave out `cd Documents` and run the other two.

### A6. Install the packages, and check

**On Windows:**

```
python -m pip install -r requirements.txt
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
python check_setup.py
```

**On a Mac**, the same, but write `python3` in place of `python`.

The first line prints several screens of text and takes a few minutes. The
last line is the one that matters; read Part 4 above for how to interpret it.
If packages are missing, `python check_setup.py --fix` installs them for you.

### A7. Coming back later

The terminal forgets where it was each time you close it. To return to the
course folder, open a new terminal and type `cd Documents` then
`cd CSS-DataScience`. To open the course in the editor from there, type
`code .` (the dot is part of the command), or use **File → Open Folder** in VS
Code.

### A8. If something goes wrong

**`python is not recognized` (Windows)** — Python was installed without
ticking "Add python.exe to PATH". Run the installer again, choose "Modify",
tick it. Then close the terminal, open a new one, and try again.

**`pip is not recognized`** — use the longer form, `python -m pip ...`, which
is why the commands above are written that way.

**`git is not recognized`** — Git is not installed, or the terminal was
already open when you installed it. Close it and open a new one.

**`ModuleNotFoundError: No module named ...`** — the install did not finish.
Run `python check_setup.py --fix`.

**The network check fails** — usually a university or office firewall. Try
your home wifi or a phone hotspot, and tell us either way.

### A9. Optional: keeping the packages separate

Skip this if you are unsure. If you already use Python for other work and
would rather not add these packages to your main installation, create a
virtual environment before the install in A6:

```
python -m venv .venv
.venv\Scripts\activate            # Windows
source .venv/bin/activate         # Mac
python -m pip install -r requirements.txt
```

You must then run the `activate` line again in every new terminal window
before the course code will work. That is the price of the tidiness.
