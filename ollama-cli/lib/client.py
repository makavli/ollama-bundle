"""Ollama API Client"""

import requests
import json
import sys
import os
from typing import Optional


class OllamaClient:
    """Client for interacting with Ollama local LLM server"""
    
    def __init__(self, base_url: str = None):
        # Priority: explicit parameter > environment variable > default
        if base_url is None:
            base_url = os.environ.get('OLLAMA_URL', 'http://localhost:11434')
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
    
    def check_connection(self) -> bool:
        """Check if Ollama is running"""
        try:
            response = requests.get(f"{self.api_url}/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def list_models(self) -> list:
        """List available models"""
        try:
            response = requests.get(f"{self.api_url}/tags")
            data = response.json()
            return [m['name'] for m in data.get('models', [])]
        except Exception as e:
            print(f"Error listing models: {e}")
            return []
    
    def generate(self, prompt: str, model: str = "deepseek-coder-v2", stream: bool = False) -> str:
        """Generate response from Ollama"""
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": stream
            }
            
            response = requests.post(
                f"{self.api_url}/generate",
                json=payload,
                stream=stream
            )
            
            if stream:
                result = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        result += chunk.get('response', '')
                        if not chunk.get('done', False):
                            sys.stdout.write(chunk.get('response', ''))
                            sys.stdout.flush()
                return result
            else:
                data = response.json()
                return data.get('response', '')
        except Exception as e:
            print(f"Error generating response: {e}")
            return ""
    
    def explain_code(self, code: str, model: str = "deepseek-coder-v2") -> str:
        """Ask model to explain code"""
        prompt = f"""Explain this code in detail:

```
{code}
```

Explain what it does, line by line:"""
        return self.generate(prompt, model, stream=True)
    
    def fix_code(self, code: str, error: Optional[str] = None, model: str = "deepseek-coder-v2") -> str:
        """Ask model to fix code"""
        error_context = f"\nError: {error}" if error else ""
        prompt = f"""Fix this code:{error_context}

```
{code}
```

Provide the corrected code:"""
        return self.generate(prompt, model=model, stream=True)
    
    def write_tests(self, code: str, model: str = "deepseek-coder-v2") -> str:
        """Ask model to write tests for code"""
        prompt = f"""Write unit tests for this code:

```
{code}
```

Write comprehensive tests:"""
        return self.generate(prompt, model=model, stream=True)
    
    def chat(self, message: str, model: str = "deepseek-coder-v2") -> str:
        """Chat with the model"""
        return self.generate(message, model, stream=True)
