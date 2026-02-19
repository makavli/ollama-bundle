# Installation & Setup

System installation and configuration scripts.

## Available Scripts

- `setup_all.py` - Complete system setup
- `prepare_install.sh` - System preparation
- `install_nvidia_driver.sh` - GPU driver setup
- `setup_vs_code_ai.sh` - VS Code integration
- `runGUI.sh` - Start OpenWebUI

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
# Ollama service endpoint (used inside container)
export OLLAMA_HOST=0.0.0.0          # Default: host.docker.internal
export OLLAMA_PORT=11434             # Default: 11434

# OpenWebUI web server port
export OPENWEBUI_PORT=3000           # Default: 3000

# Run setup with custom configuration
python3 setup_all.py
```

### Resource Configuration

Control Ollama performance:

```bash
export OLLAMA_NUM_THREAD=8              # CPU threads (default: varies)
export OLLAMA_GPU_MEMORY=14000          # GPU VRAM (MB, default: auto)
export OLLAMA_MAX_LOADED_MODELS=2       # Concurrent models (default: 1)

python3 setup_all.py
```

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
