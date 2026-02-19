# Offline OpenWebUI installer for Ollama (Docker)

This repository contains a small installer script to run OpenWebUI from a local Docker image or local source directory when you don't have network access.

Files added:
- /install_openwebui_offline.sh — Installer script

Quick start (from repository root):

1. Make the script executable:

```bash
chmod +x install_openwebui_offline.sh
```

2a. If you have a saved Docker image tarball (recommended for offline):

```bash
./install_openwebui_offline.sh -i /path/to/openwebui_image.tar -n openwebui:local -p 3000
```

2b. Or build from local source (requires Docker and local base images already present):

```bash
./install_openwebui_offline.sh -s /path/to/openwebui_source -n openwebui:local -p 3000
```

Notes:
- If OpenWebUI must connect to an Ollama server, pass the Ollama host with `-o`, e.g. `-o http://172.17.0.1:11434`.
- Building from local source offline will fail if Docker needs to pull base images; prefer using a pre-saved image tar.

If you want, I can also:
- add a `docker save` helper to export an image for offline transport
- create a `docker-compose.yml` wrapper for easier management
