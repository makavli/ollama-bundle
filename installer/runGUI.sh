# (optional) install prerequisites
sudo ./prepare_install.sh

# run the orchestrator (sudo required for docker/systemd ops)
sudo ./setup_all.py
# or to pull specific models:
sudo ./setup_all.py deepseek-coder-v2:latest llama3:latest deepseek-v2:latest other:model