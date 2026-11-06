# Installation & Setup

System installation and configuration scripts.

## Available Scripts

- `setup_all.py` - Complete system setup
- `prepare_install.sh` - System preparation
- `install_nvidia_driver.sh` - GPU driver setup
- `setup_vs_code_ai.sh` - VS Code integration
- `runGUI.sh` - Run prepare_install + setup_all in one go (arguments are passed to setup_all.py)

## Quick Start

```bash
bash prepare_install.sh
python3 setup_all.py
bash runGUI.sh
```

## Configuration

### Environment Variables for setup_all.py

Control service ports and endpoints:

```bash
# Ollama URL as seen from the OpenWebUI container
export OPENWEBUI_OLLAMA_URL=http://host.docker.internal:11434   # default (bridged)
# ...or skip networking issues entirely:  sudo python3 setup_all.py --host-network

# OpenWebUI web server port
export OPENWEBUI_PORT=3000           # Default: 3000

# Run setup with custom configuration
python3 setup_all.py
```

### Resource Configuration

Ollama's performance settings live in its systemd service. Exporting them in
your shell does nothing, because `setup_all.py` restarts Ollama through systemd:

```bash
sudo systemctl edit ollama
# [Service]
# Environment="OLLAMA_MAX_LOADED_MODELS=2"   # concurrent models
# Environment="OLLAMA_NUM_PARALLEL=2"        # parallel requests per model
sudo systemctl restart ollama
```

`setup_all.py` keeps this override file unless you pass `--reset-ollama-override`.

### Service Endpoints After Setup

- **Ollama API**: `http://localhost:11434`
- **OpenWebUI Web UI**: `http://localhost:3000`
- **Container → Ollama**: `http://host.docker.internal:11434`

### Custom Port Example

```bash
# Run OpenWebUI on port 8080 instead of 3000
export OPENWEBUI_PORT=8080
python3 setup_all.py

# Access at: http://localhost:8080
```
