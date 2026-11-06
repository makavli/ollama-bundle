#!/usr/bin/env python3
"""
Orchestrator script:
- pulls the requested Ollama models (defaults provided)
- restarts the Ollama service
- recreates the OpenWebUI container, pointed at your Ollama server
- optionally removes an Ollama systemd drop-in override (--reset-ollama-override)

Run: sudo python3 setup_all.py [options] [model ...]    (sudo needed for docker/systemd)

How OpenWebUI reaches Ollama
----------------------------
Ollama listens on 127.0.0.1 by default, which a normal (bridged) container can't reach.
Pick one:
  * --host-network : run OpenWebUI on the host network and talk to 127.0.0.1 (works with
                     Ollama's defaults; the UI is then served directly on --port)
  * default        : bridged container using host.docker.internal; requires Ollama to
                     listen on all interfaces (OLLAMA_HOST=0.0.0.0 in its systemd service)
"""
import argparse
import os
import subprocess
import sys
from shutil import which

DEFAULT_MODELS = [
    "deepseek-coder-v2:latest",
    "deepseek-v2:latest",
    "llama3:latest",
    "nomic-embed-text:latest",   # embeddings for OpenWebUI documents/RAG
]
DROPIN = "/etc/systemd/system/ollama.service.d/override.conf"
IMAGE = "ghcr.io/open-webui/open-webui:main"


def run(cmd, check=True, capture=False):
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, text=True, capture_output=capture)


def ensure_cli(name):
    if which(name) is None:
        print(f"{name} not found in PATH; install it before running this script.")
        sys.exit(2)


def remove_ollama_dropin():
    if os.path.exists(DROPIN):
        print(f"Removing Ollama drop-in: {DROPIN}")
        run(["sudo", "rm", "-f", DROPIN])
        run(["sudo", "systemctl", "daemon-reload"])
    else:
        print("No Ollama drop-in found; nothing to remove")


def restart_ollama():
    print("Restarting Ollama service")
    run(["sudo", "systemctl", "restart", "ollama"])
    run(["sudo", "systemctl", "status", "--no-pager", "-n", "5", "ollama"], check=False)


def pull_models(models):
    pulled, failed = [], []
    for model in models:
        print(f"Pulling model: {model}")
        try:
            run(["ollama", "pull", model])
            pulled.append(model)
        except subprocess.CalledProcessError:
            print(f"Failed to pull {model}; continuing")
            failed.append(model)
    return pulled, failed


def openwebui_command(container, ui_port, ollama_url, host_network):
    """The docker run command. OpenWebUI reads OLLAMA_BASE_URL (not OLLAMA_BACKEND)."""
    cmd = ["sudo", "docker", "run", "-d", "--name", container,
           "-v", "open-webui:/app/backend/data",          # keep users/chats across re-creates
           "--restart", "unless-stopped"]
    if host_network:
        cmd += ["--network", "host", "-e", f"PORT={ui_port}"]
    else:
        cmd += ["--add-host=host.docker.internal:host-gateway", "-p", f"{ui_port}:8080"]
    cmd += ["-e", f"OLLAMA_BASE_URL={ollama_url}", IMAGE]
    return cmd


def recreate_openwebui(container, ui_port, ollama_url, host_network):
    print(f"Recreating container {container} ({IMAGE})")
    print(f"  Ollama URL (as seen from the container): {ollama_url}")
    print(f"  OpenWebUI port: {ui_port}")
    run(["sudo", "docker", "rm", "-f", container], check=False)
    run(openwebui_command(container, ui_port, ollama_url, host_network))
    run(["sudo", "docker", "ps", "--filter", "name=" + container,
         "--format", "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"], check=False)


def check_ui(ui_port):
    url = f"http://localhost:{ui_port}"
    print(f"Checking OpenWebUI at {url} (it can take a minute to start) ...")
    try:
        run(["curl", "-fsS", "--retry", "12", "--retry-delay", "5", "--retry-connrefused",
             "-o", "/dev/null", url])
        print(f"OpenWebUI reachable at {url}")
    except subprocess.CalledProcessError:
        print(f"OpenWebUI not reachable at {url} - check: sudo docker logs open-webui --tail 200")


def parse_args(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("models", nargs="*", help=f"models to pull (default: {' '.join(DEFAULT_MODELS)})")
    p.add_argument("--port", default=os.environ.get("OPENWEBUI_PORT", "3000"), help="OpenWebUI port (default 3000)")
    p.add_argument("--ollama-url", default=os.environ.get("OPENWEBUI_OLLAMA_URL"),
                   help="Ollama URL as seen from the container (default depends on --host-network)")
    p.add_argument("--host-network", action="store_true",
                   help="run OpenWebUI with --network host (works when Ollama only listens on 127.0.0.1)")
    p.add_argument("--reset-ollama-override", action="store_true",
                   help=f"delete {DROPIN} before restarting Ollama (this removes your custom Ollama settings)")
    p.add_argument("--skip-pull", action="store_true", help="don't pull any models")
    p.add_argument("--container", default="open-webui")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    for tool in ("ollama", "docker", "curl"):
        ensure_cli(tool)

    models = args.models or DEFAULT_MODELS
    ollama_url = args.ollama_url or (
        "http://127.0.0.1:11434" if args.host_network else "http://host.docker.internal:11434")

    print("Configuration:")
    print(f"  OpenWebUI -> Ollama: {ollama_url}  ({'host network' if args.host_network else 'bridged'})")
    print(f"  OpenWebUI port:      {args.port}")
    print()

    if args.reset_ollama_override:
        print("STEP 1: remove the Ollama drop-in override")
        remove_ollama_dropin()
    else:
        print(f"STEP 1: keeping any existing Ollama override ({DROPIN}); use --reset-ollama-override to remove it")

    print("STEP 2: restart Ollama")
    restart_ollama()

    pulled, failed = [], []
    if args.skip_pull:
        print("STEP 3: skipping model pulls")
    else:
        print("STEP 3: pull requested models via 'ollama pull'")
        pulled, failed = pull_models(models)

    print("STEP 4: recreate the OpenWebUI container")
    recreate_openwebui(args.container, args.port, ollama_url, args.host_network)

    print("STEP 5: quick checks")
    check_ui(args.port)

    print("Done. Summary:")
    print(f"  Models pulled: {pulled}")
    print(f"  Models failed: {failed}")
    if not args.host_network:
        print("If OpenWebUI shows no models, Ollama is probably only listening on 127.0.0.1.")
        print("Either re-run with --host-network, or make Ollama listen on all interfaces:")
        print("  sudo systemctl edit ollama   ->  [Service]  Environment=\"OLLAMA_HOST=0.0.0.0\"")
    return 1 if failed and not pulled else 0


if __name__ == "__main__":
    sys.exit(main())
