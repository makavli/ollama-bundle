#!/usr/bin/env python3
"""
Orchestrator script:
- cleans Ollama drop-in override if present
- pulls requested Ollama models (defaults provided)
- restarts Ollama service
- recreates OpenWebUI container with OLLAMA_BACKEND pointing to host

Run: sudo python3 setup_all.py    (sudo required for docker/systemd ops)
"""
import os
import subprocess
import sys
from shutil import which

DEFAULT_MODELS = [
    "deepseek-coder-v2:latest",
    "deepseek-v2:latest",
    "llama3:latest",
    "bge-mini:latest"
]

def run(cmd, check=True, capture=False, env=None):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, text=True, capture_output=capture, env=env)

def ensure_cli(name):
    if which(name) is None:
        print(f"{name} not found in PATH; install it before running this script.")
        sys.exit(2)

def remove_ollama_dropin():
    dropin = "/etc/systemd/system/ollama.service.d/override.conf"
    if os.path.exists(dropin):
        print(f"Removing existing Ollama drop-in: {dropin}")
        run(["sudo","rm","-f",dropin])
        run(["sudo","systemctl","daemon-reload"]) 
        print("Reloaded systemd after removing drop-in")
    else:
        print("No Ollama drop-in found; skipping removal")

def restart_ollama():
    print("Restarting Ollama service")
    run(["sudo","systemctl","restart","ollama"])
    run(["sudo","systemctl","status","--no-pager","-n","5","ollama"], check=False)

def pull_models(models):
    pulled = []
    failed = []
    for m in models:
        print(f"Pulling model: {m}")
        try:
            run(["ollama","pull",m])
            pulled.append(m)
        except subprocess.CalledProcessError:
            print(f"Failed to pull {m}; continuing")
            failed.append(m)
    return pulled, failed

def recreate_openwebui(image="ghcr.io/open-webui/open-webui:main", container="open-webui", 
                       ollama_backend="http://host.docker.internal:11434", 
                       ui_port="3000"):
    print(f"Recreating container {container} with image {image}")
    print(f"  Ollama backend: {ollama_backend}")
    print(f"  OpenWebUI port: {ui_port}")
    # Remove existing
    run(["sudo","docker","rm","-f",container], check=False)
    # Run with host-gateway mapping so container can reach host at host.docker.internal
    cmd = ["sudo","docker","run","-d","--name",container,
           "--add-host=host.docker.internal:host-gateway",
           "-p",f"{ui_port}:8080",
           "-e",f"OLLAMA_BACKEND={ollama_backend}",
           "--restart","unless-stopped",image]
    run(cmd)
    run(["sudo","docker","ps","--filter","name="+container,"--format","table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"], check=False)

def check_ui(ui_host="localhost", ui_port="3000"):
    url = f"http://{ui_host}:{ui_port}"
    print(f"Checking OpenWebUI at {url} ...")
    try:
        run(["curl","-fsS",url], check=True)
        print(f"OpenWebUI reachable at {url}")
    except subprocess.CalledProcessError:
        print(f"OpenWebUI not reachable at {url} — check container logs or port mapping")

def main():
    ensure_cli("ollama")
    ensure_cli("docker")
    ensure_cli("curl")

    models = DEFAULT_MODELS
    if len(sys.argv) > 1:
        models = sys.argv[1:]

    # Read configuration from environment variables
    ollama_host = os.environ.get('OLLAMA_HOST', 'host.docker.internal')
    ollama_port = os.environ.get('OLLAMA_PORT', '11434')
    ollama_backend = f"http://{ollama_host}:{ollama_port}"
    ui_port = os.environ.get('OPENWEBUI_PORT', '3000')
    
    print("Configuration:")
    print(f"  OLLAMA_BACKEND (for container): {ollama_backend}")
    print(f"  OPENWEBUI_PORT: {ui_port}")
    print()

    print("STEP 1: remove any existing Ollama drop-in override (if present)")
    remove_ollama_dropin()

    print("STEP 2: restart Ollama (ensure server uses default listening)")
    restart_ollama()

    print("STEP 3: pull requested models via 'ollama pull'")
    pulled, failed = pull_models(models)
    print(f"Pulled: {pulled}")
    if failed:
        print(f"Failed: {failed} (these may be unavailable)")

    print("STEP 4: recreate OpenWebUI container and point it to Ollama API")
    recreate_openwebui(ollama_backend=ollama_backend, ui_port=ui_port)

    print("STEP 5: quick checks")
    check_ui(ui_port=ui_port)

    print("Done. Summary:")
    print(f"  Models pulled: {pulled}")
    print(f"  Models failed: {failed}")
    print("If you still don't see models in web UI, try refreshing the UI and check container logs: sudo docker logs open-webui --tail 200")

if __name__ == '__main__':
    main()
