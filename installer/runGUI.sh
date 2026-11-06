#!/usr/bin/env bash
# Install prerequisites (once), then set up Ollama models + the OpenWebUI container.
# Any arguments are passed on to setup_all.py, e.g.:
#   ./runGUI.sh --host-network
#   ./runGUI.sh llama3:latest deepseek-coder-v2:latest
set -euo pipefail
cd "$(dirname "$0")"

sudo ./prepare_install.sh
sudo python3 ./setup_all.py "$@"
