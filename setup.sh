#!/usr/bin/env bash
#
# Pentest Toolbox GUI – universal installer (Linux)
# Tested on Ubuntu/Debian (APT) and Arch/Manjaro (Pacman).
#
# 1. Installs required OS packages (Python 3, virtualenv, Nmap, Nikto, SearchSploit).
# 2. Creates a local Python virtual environment (.venv) without sudo.
# 3. Ensures python-nmap is >=0.7.1 in requirements, then installs all Python deps.
#
# Usage:
#   bash setup.sh
#
set -euo pipefail

# --- Helper functions ----------------------------------------------------
cyan()  { printf '[1;36m%s[0m
' "$1"; }
green() { printf '[1;32m%s[0m
' "$1"; }
err()   { printf '[1;31m%s[0m
' "$1"; exit 1; }

# --- Initial info --------------------------------------------------------
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cyan "== Pentest Toolbox GUI installer =="
echo "Project directory: $PROJECT_DIR"

cd "$PROJECT_DIR"

# --- Detect package manager ---------------------------------------------
if command -v apt-get &>/dev/null; then
  PKG_MANAGER="apt"
elif command -v pacman &>/dev/null; then
  PKG_MANAGER="pacman"
else
  err "Unsupported distribution – install dependencies manually."
fi

# --- 1. Install OS packages ---------------------------------------------
cyan "[1/5] Installing system packages (sudo)…"
if [[ $PKG_MANAGER == "apt" ]]; then
  sudo apt-get update -y
  sudo apt-get install -y python3 python3-venv python3-pip nmap nikto git curl
else
  sudo pacman -Sy --noconfirm python python-virtualenv python-pip nmap nikto git curl
fi

# --- 2. Install / update SearchSploit -----------------------------------
cyan "[2/5] Ensuring SearchSploit (Exploit-DB) is present…"
if ! command -v searchsploit &>/dev/null; then
  sudo git clone --depth=1 https://gitlab.com/exploit-database/exploitdb.git /opt/exploitdb
  sudo ln -sf /opt/exploitdb/searchsploit /usr/local/bin/searchsploit
  sudo cp /opt/exploitdb/.searchsploit_rc /etc/searchsploit_rc || true
  green "SearchSploit installed to /opt/exploitdb"
else
  green "SearchSploit already present."
fi

# --- 3. Clean up any existing venv & create new one without sudo ------------
# Default venv directory
VENV_DIR=".venv"

cyan "[3/5] Replacing existing virtualenv (if any) and creating new one…"
# Remove old venv directory if it exists (use without sudo to avoid permission issues)
if [[ -d "$VENV_DIR" ]]; then
  echo "Removing old virtual environment: $VENV_DIR"
  rm -rf "$VENV_DIR"
fi

# Create new venv as current user
python3 -m venv "$VENV_DIR"

# Activate the new venv
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# Upgrade pip & tools
pip install --quiet --upgrade pip setuptools wheel
cyan "[3/5] Replacing existing virtualenv (if any) and creating new one…"
# Remove old venv directory if it exists (use without sudo to avoid permission issues)
if [[ -d "$VENV_DIR" ]]; then
  echo "Removing old virtual environment: $VENV_DIR"
  rm -rf "$VENV_DIR"
fi

# Create new venv as original user
python3 -m venv "$VENV_DIR"

# Activate the new venv
# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# Upgrade pip & tools
pip install --quiet --upgrade pip setuptools wheel

# Upgrade pip & tools
pip install --quiet --upgrade pip setuptools wheel

# --- 4. Patch requirements & install ------------------------------------. Patch requirements & install ------------------------------------. Patch requirements & install ------------------------------------
cyan "[4/5] Installing Python dependencies…"
if [[ -f requirements.txt ]]; then
  sed -i 's/^python-nmap.*/python-nmap>=0.7.1/' requirements.txt
  pip install --requirement requirements.txt
else
  err "requirements.txt not found!"
fi

# --- 5. Finished ---------------------------------------------------------
green "[5/5] Setup complete!"

# Automatically activate the venv and launch the app
# Note: the following will keep the process attached to your terminal
# Activate the virtual environment
source "$VENV_DIR/bin/activate"
# Launch Streamlit
streamlit run streamlit_app.py
