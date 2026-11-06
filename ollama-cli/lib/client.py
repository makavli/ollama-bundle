"""Ollama API Client"""

import json
import os
import sys
from typing import Optional

import requests

DEFAULT_MODEL = "deepseek-coder-v2"
CONNECT_TIMEOUT = 5          # seconds to establish a connection
READ_TIMEOUT = 600           # generation on a CPU can be slow; don't hang forever


class OllamaError(Exception):
    """Raised when Ollama can't be reached or returns an error (e.g. unknown model)."""


def normalize_url(value: Optional[str]) -> str:
    """Accept the forms people actually use: 'localhost', 'host:11434',
    '0.0.0.0:11434' (Ollama's own OLLAMA_HOST format) or a full URL."""
    if not value:
        return "http://localhost:11434"
    value = value.strip().rstrip("/")
    if "://" not in value:
        value = f"http://{value}"
    scheme, rest = value.split("://", 1)
    host = rest.split("/", 1)[0]
    if host.startswith("0.0.0.0"):            # a bind address, not something you can connect to
        rest = "localhost" + rest[len("0.0.0.0"):]
        host = rest.split("/", 1)[0]
    if ":" not in host.rsplit("]", 1)[-1]:    # no port given (IPv6-safe check)
        rest = rest.replace(host, f"{host}:11434", 1)
    return f"{scheme}://{rest}"


class OllamaClient:
    """Client for interacting with Ollama local LLM server"""

    def __init__(self, base_url: Optional[str] = None):
        # Priority: explicit parameter > OLLAMA_URL > default
        self.base_url = normalize_url(base_url or os.environ.get("OLLAMA_URL"))
        self.api_url = f"{self.base_url}/api"

    def check_connection(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=CONNECT_TIMEOUT)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def list_models(self) -> list:
        """List available models"""
        response = self._request("get", "tags", timeout=CONNECT_TIMEOUT)
        return [m["name"] for m in response.json().get("models", [])]

    def _request(self, method, endpoint, **kwargs):
        try:
            response = requests.request(method, f"{self.api_url}/{endpoint}", **kwargs)
        except requests.RequestException as e:
            raise OllamaError(f"Cannot reach Ollama at {self.base_url}: {e}") from e
        if response.status_code >= 400:
            try:
                detail = response.json().get("error", response.text)
            except ValueError:
                detail = response.text
            raise OllamaError(f"Ollama returned {response.status_code}: {detail}")
        return response

    def generate(self, prompt: str, model: str = DEFAULT_MODEL, stream: bool = False) -> str:
        """Generate a response. With stream=True the text is also printed as it arrives."""
        payload = {"model": model, "prompt": prompt, "stream": stream}
        response = self._request("post", "generate", json=payload, stream=stream,
                                 timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
        if not stream:
            return response.json().get("response", "")

        result = []
        for line in response.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            if "error" in chunk:
                raise OllamaError(chunk["error"])
            piece = chunk.get("response", "")
            result.append(piece)
            sys.stdout.write(piece)
            sys.stdout.flush()
            if chunk.get("done"):
                break
        sys.stdout.write("\n")
        return "".join(result)

    def explain_code(self, code: str, model: str = DEFAULT_MODEL) -> str:
        """Ask model to explain code"""
        prompt = f"""Explain this code in detail:

```
{code}
```

Explain what it does, line by line:"""
        return self.generate(prompt, model, stream=True)

    def fix_code(self, code: str, error: Optional[str] = None, model: str = DEFAULT_MODEL) -> str:
        """Ask model to fix code"""
        error_context = f"\nError: {error}" if error else ""
        prompt = f"""Fix this code:{error_context}

```
{code}
```

Provide the corrected code:"""
        return self.generate(prompt, model=model, stream=True)

    def write_tests(self, code: str, model: str = DEFAULT_MODEL) -> str:
        """Ask model to write tests for code"""
        prompt = f"""Write unit tests for this code:

```
{code}
```

Write comprehensive tests:"""
        return self.generate(prompt, model=model, stream=True)

    def chat(self, message: str, model: str = DEFAULT_MODEL) -> str:
        """Chat with the model"""
        return self.generate(message, model, stream=True)
