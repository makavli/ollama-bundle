#!/usr/bin/env bash
set -euo pipefail

# Minimal installer: ensures Python and jq are available (Debian/Ubuntu)
if [[ $(id -u) -ne 0 ]]; then
  echo "Run this script with sudo if you want packages installed system-wide."
fi

if command -v apt-get >/dev/null 2>&1; then
  echo "Using apt to install prerequisites (python3-venv, python3-pip, jq, curl)"
  sudo apt-get update
  sudo apt-get install -y python3-venv python3-pip jq curl
else
  echo "apt-get not found. Please install python3, pip3 and jq manually for your distro."
fi

echo "Installing a small Python virtualenv helper in .venv (optional)"
python3 -m venv .venv || true
echo "To activate: source .venv/bin/activate"
echo "Prepared environment; next, run 'python3 setup_all.py' to orchestrate pull/restart."

exit 0
