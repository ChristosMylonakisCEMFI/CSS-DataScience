"""
check_setup.py - verify (and fix) everything needed for the scraping tutorial.

    python check_setup.py          # diagnose only
    python check_setup.py --fix    # diagnose, then install what is missing

Nothing here is destructive: --fix only runs `pip install` for the packages
listed in requirements.txt. Browsers are never installed silently; if one is
missing you get a direct download link for your operating system.
"""
import argparse
import importlib
import os
import platform
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REQS = os.path.join(HERE, "requirements.txt")

GREEN, RED, YELLOW, BOLD, OFF = "\033[92m", "\033[91m", "\033[93m", "\033[1m", "\033[0m"
if platform.system() == "Windows":
    os.system("")  # enable ANSI colours in cmd.exe

PKGS = [
    # import name, pip spec, minimum version (or None)
    ("requests", "requests>=2.32", (2, 32)),
    ("bs4", "beautifulsoup4>=4.12", None),
    ("pandas", "pandas>=1.4", None),
    ("selenium", "selenium>=4.25", (4, 25)),
    ("matplotlib", "matplotlib>=3.5", None),
]

CHROME_DOWNLOAD = "https://www.google.com/chrome/"
EDGE_DOWNLOAD = "https://www.microsoft.com/edge/download"

results = []


def report(ok, label, detail="", fix=""):
    results.append((ok, label, fix))
    mark = f"{GREEN}PASS{OFF}" if ok else f"{RED}FAIL{OFF}"
    print(f"  [{mark}] {label}" + (f"  {detail}" if detail else ""))
    if not ok and fix:
        print(f"         {YELLOW}fix:{OFF} {fix}")


def parse_version(v):
    out = []
    for part in v.split(".")[:3]:
        digits = "".join(ch for ch in part if ch.isdigit())
        out.append(int(digits) if digits else 0)
    return tuple(out)


def check_python():
    v = sys.version_info
    ok = v >= (3, 9)
    report(ok, f"Python {v.major}.{v.minor}.{v.micro}",
           detail="(need >= 3.9)" if not ok else "",
           fix="Install Python 3.9+ from https://www.python.org/downloads/")


def check_packages():
    missing = []
    for mod, spec, minver in PKGS:
        try:
            m = importlib.import_module(mod)
        except ImportError:
            report(False, f"package: {spec}", "not installed",
                   fix=f"pip install '{spec}'")
            missing.append(spec)
            continue
        ver = getattr(m, "__version__", "?")
        if minver and ver != "?" and parse_version(ver) < minver:
            need = ".".join(map(str, minver))
            report(False, f"package: {mod}", f"found {ver}, need >= {need}",
                   fix=f"pip install --upgrade '{spec}'")
            missing.append(spec)
        else:
            report(True, f"package: {mod}", ver)
    return missing


def find_browser():
    names = ["chrome", "google-chrome", "chromium", "msedge"]
    for n in names:
        p = shutil.which(n)
        if p:
            return p
    candidates = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/usr/bin/google-chrome", "/usr/bin/chromium-browser",
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return None


def check_browser():
    b = find_browser()
    link = CHROME_DOWNLOAD if platform.system() != "Windows" else CHROME_DOWNLOAD
    report(bool(b), "browser (Chrome/Edge)", os.path.basename(b) if b else "not found",
           fix=f"Download Chrome: {link}   (or Edge: {EDGE_DOWNLOAD})")
    return bool(b)


def check_selenium_cache():
    """Selenium caches its driver in ~/.cache/selenium. If ~/.cache is a FILE
    (some libraries create it), driver download fails with a confusing error."""
    cache = os.path.join(os.path.expanduser("~"), ".cache")
    if os.path.isfile(cache):
        alt = os.path.join(os.path.expanduser("~"), "selenium_cache")
        report(False, "selenium driver cache", f"'{cache}' is a file, not a folder",
               fix=(f"set an alternative cache location before running Selenium:\n"
                    f"           Windows : set SE_CACHE_PATH={alt}\n"
                    f"           mac/Linux: export SE_CACHE_PATH={alt}"))
        os.environ.setdefault("SE_CACHE_PATH", alt)
        return False
    report(True, "selenium driver cache", "ok")
    return True


def check_driver():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        o = Options()
        o.add_argument("--headless=new")
        o.add_argument("--log-level=3")
        d = webdriver.Chrome(options=o)
        d.quit()
        report(True, "chromedriver (auto-managed by Selenium 4)", "launched ok")
        return True
    except Exception as e:
        report(False, "chromedriver", str(e).splitlines()[0][:90],
               fix="Usually fixed by: pip install --upgrade 'selenium>=4.25'  "
                   "and installing Chrome (see above).")
        return False


def check_network():
    try:
        import requests
        url = ("https://boards-api.greenhouse.io/v1/boards/anthropic/jobs/"
               "4981828008?pay_transparency=true")
        r = requests.get(url, headers={"User-Agent": "CEMFI CSS-DataScience setup check"},
                         timeout=30)
        ok = r.status_code == 200 and "title" in r.json()
        report(ok, "network: reach the Greenhouse API", f"HTTP {r.status_code}",
               fix="Check your internet connection / proxy / firewall.")
        return ok
    except Exception as e:
        report(False, "network: reach the Greenhouse API", str(e)[:80],
               fix="Check your internet connection / proxy / firewall.")
        return False


def do_fix(missing):
    print(f"\n{BOLD}Installing missing packages...{OFF}")
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
    cmd += missing if missing else ["-r", REQS]
    print("  " + " ".join(cmd) + "\n")
    subprocess.call(cmd)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fix", action="store_true",
                    help="install missing/outdated packages, then re-check")
    args = ap.parse_args()

    print(f"\n{BOLD}Setup check - web scraping tutorial{OFF}")
    print(f"  {platform.system()} {platform.release()} | {sys.executable}\n")

    check_python()
    missing = check_packages()

    if missing and args.fix:
        do_fix(missing)
        print(f"\n{BOLD}Re-checking after install...{OFF}\n")
        results.clear()
        check_python()
        missing = check_packages()

    check_browser()
    check_selenium_cache()
    if not missing:
        check_driver()
        check_network()

    failed = [(lbl, fix) for ok, lbl, fix in results if not ok]
    print()
    if not failed:
        print(f"{GREEN}{BOLD}All checks passed. You are ready.{OFF}")
        print("  Next:  python code/01_json.py\n")
        return 0

    print(f"{RED}{BOLD}{len(failed)} check(s) failed.{OFF}")
    if missing and not args.fix:
        print(f"  Most of this is fixed automatically by:\n"
              f"      {BOLD}python check_setup.py --fix{OFF}")
    for lbl, fix in failed:
        if fix:
            print(f"  - {lbl}\n      {fix}")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
