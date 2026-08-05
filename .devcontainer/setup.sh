#!/usr/bin/env bash
# Runs once, when a Codespace is created. Participants never run this by hand.
#
# Deliberately not "set -e": if Chrome fails to install we still want a usable
# Codespace, and check_setup.py will report the problem clearly.
set -u

# Never let apt stop to ask a question: the Codespace would appear to hang.
export DEBIAN_FRONTEND=noninteractive

echo
echo "==> Installing the Python packages for the course"
python -m pip install --user --no-cache-dir --upgrade pip
python -m pip install --user --no-cache-dir -r requirements.txt

echo
echo "==> Installing a browser (the scraping session drives one with Selenium)"
arch="$(uname -m)"
if [ "$arch" = "x86_64" ]; then
    deb=/tmp/google-chrome.deb
    if curl -fsSL -o "$deb" \
        https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb; then
        sudo apt-get update -qq
        sudo apt-get install -y -qq "$deb" \
            || echo "WARNING: Chrome failed to install. Everything except the Selenium script still works."
        rm -f "$deb"
    else
        echo "WARNING: could not download Chrome. Everything except the Selenium script still works."
    fi
else
    # Apple Silicon and other non-Intel machines: Google publishes no .deb,
    # so use Chromium, which Selenium drives in exactly the same way.
    sudo apt-get update -qq
    sudo apt-get install -y -qq chromium \
        || echo "WARNING: no browser installed. Everything except the Selenium script still works."
fi

echo
echo "==> Done. Confirm with:  python check_setup.py"
echo
