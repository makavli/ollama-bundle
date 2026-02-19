#!/usr/bin/env python3
"""
Ollama VS Code Integration CLI
Use local LLMs to generate code and work with files
"""

import sys
import os
import argparse
from pathlib import Path

# Add lib directory to path
lib_dir = Path(__file__).parent.parent / "lib"
sys.path.insert(0, str(lib_dir.parent))
sys.path.insert(0, str(lib_dir))

from client import OllamaClient


def main():
    parser = argparse.ArgumentParser(
        description="Ollama VS Code Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List available models
  python3 ollama_vs_code.py --list

  # Ask a question
  python3 ollama_vs_code.py "How do I read a file in Python?"

  # Explain code from file
  python3 ollama_vs_code.py --explain < myfile.py

  # Fix code with error message
  python3 ollama_vs_code.py --fix --error "TypeError: expected string" < code.py

  # Write tests for code
  python3 ollama_vs_code.py --tests < code.py

  # Select model
  python3 ollama_vs_code.py --model llama3 "Your question here"
        """
    )
    
    parser.add_argument("prompt", nargs='?', help="Question or prompt")
    parser.add_argument("--model", default="deepseek-coder-v2", 
                       help="Model to use (default: deepseek-coder-v2)")
    parser.add_argument("--host", default=None, help="Ollama host (default: localhost, or OLLAMA_HOST env var)")
    parser.add_argument("--port", type=int, default=None, help="Ollama port (default: 11434, or OLLAMA_PORT env var)")
    parser.add_argument("--list", action="store_true", help="List available models")
    parser.add_argument("--explain", action="store_true", help="Explain code from stdin")
    parser.add_argument("--fix", action="store_true", help="Fix code from stdin")
    parser.add_argument("--error", help="Error message (use with --fix)")
    parser.add_argument("--tests", action="store_true", help="Write tests for code")
    parser.add_argument("--check", action="store_true", help="Check Ollama connection")
    parser.add_argument("--write-file", metavar='FILE', help="Create a file with model output (use '-' to read prompt from stdin)")
    parser.add_argument("-f", "--prompt-file", metavar='PROMPT_FILE', help="Read prompt from a file instead of positional arg or stdin")
    
    args = parser.parse_args()
    
    # Build Ollama URL from host/port or environment variable
    ollama_url = None
    if args.host or args.port:
        host = args.host or os.environ.get('OLLAMA_HOST', 'localhost')
        port = args.port or int(os.environ.get('OLLAMA_PORT', '11434'))
        ollama_url = f"http://{host}:{port}"
    else:
        ollama_url = os.environ.get('OLLAMA_URL', None)
    
    client = OllamaClient(base_url=ollama_url)
    
    # Check connection
    if not client.check_connection():
        display_url = ollama_url or "http://localhost:11434"
        print(f"❌ Cannot connect to Ollama at {display_url}")
        print("Start Ollama service: sudo systemctl start ollama")
        print(f"Or set OLLAMA_URL env var or use --host/--port options")
        sys.exit(1)
    
    # List models
    if args.list:
        print("Available models:")
        for model in client.list_models():
            print(f"  • {model}")
        return
    
    # Check connection
    if args.check:
        print(f"✓ Ollama is running at {client.base_url}")
        models = client.list_models()
        print(f"✓ Available models: {len(models)}")
        return
    
    # Helper: read prompt file if provided, or check for default 'prompt' file
    prompt_file_content = None
    prompt_file_path = args.prompt_file
    
    # If no -f flag, check for default 'prompt' file in priority order
    if not prompt_file_path:
        from pathlib import Path
        script_dir = Path(__file__).parent  # src/
        repo_root = script_dir.parent.parent  # ../..
        
        # Check locations in priority order
        candidates = [
            Path("prompt"),                              # Current directory
            script_dir / "prompt",                       # src/prompt
            repo_root / "examples" / "prompt",           # examples/prompt
            script_dir.parent / "examples" / "prompt",   # ../examples/prompt
        ]
        
        for candidate in candidates:
            if candidate.exists():
                prompt_file_path = str(candidate)
                break
    
    if prompt_file_path:
        try:
            with open(prompt_file_path, 'r', encoding='utf-8') as pf:
                prompt_file_content = pf.read()
        except Exception as e:
            print(f"Error reading prompt file {prompt_file_path}: {e}")
            sys.exit(1)

    # Read from stdin or prompt file if needed
    if args.explain or args.fix or args.tests:
        if prompt_file_content is not None:
            code = prompt_file_content
        else:
            # prefer stdin when piped
            if not sys.stdin.isatty():
                code = sys.stdin.read()
            else:
                print("No input provided: use --prompt-file or pipe code into stdin")
                sys.exit(1)

        if args.explain:
            print("Explaining code...\n")
            client.explain_code(code, args.model)
        elif args.fix:
            print("Fixing code...\n")
            client.fix_code(code, args.error)
        elif args.tests:
            print("Writing tests...\n")
            client.write_tests(code)
    
    # Regular prompt
    elif args.prompt:
        print(f"Thinking (using {args.model})...\n")
        client.chat(args.prompt, args.model)
    # Create a file with model output
    elif args.write_file:
        # Determine prompt source: priority: --prompt-file, positional prompt, piped stdin, interactive
        if prompt_file_content is not None:
            prompt = prompt_file_content
        elif args.prompt:
            prompt = args.prompt
        else:
            if args.write_file == '-' or not sys.stdin.isatty():
                prompt = sys.stdin.read()
                if not prompt.strip():
                    print("No input on stdin to generate file content from.")
                    sys.exit(1)
            else:
                prompt = input("Enter prompt for file content: ")

        print(f"Generating content using model {args.model}...\n")
        content = client.generate(prompt, model=args.model, stream=False)

        # Try to extract separate answer and script from model output.
        # Supported formats (best-effort):
        # 1) JSON: {"answer": "...", "script": "..."}
        # 2) Delimiter marker: '===SCRIPT===' or '---SCRIPT---'
        # 3) First fenced code block (``` ... ```)
        import re
        import json as _json

        answer = None
        script = None

        # Pre-processing: strip markdown code fence if present (e.g., ```json\n{...}\n```)
        content_to_parse = content
        fence_match = re.match(r'^```(?:json|javascript)?\s*\n([\s\S]*)\n```\s*$', content.strip())
        if fence_match:
            content_to_parse = fence_match.group(1)

        # 1) JSON parse
        try:
            j = _json.loads(content_to_parse)
            if isinstance(j, dict) and ('script' in j or 'answer' in j):
                script = j.get('script') or j.get('code') or j.get('file')
                answer = j.get('answer') or j.get('explanation') or None
        except (_json.JSONDecodeError, ValueError) as json_err:
            # Fallback: try to extract JSON-like content with regex
            if content_to_parse.strip().startswith('{'):
                try:
                    # Extract script value
                    script_match = re.search(r'"script"\s*:\s*"((?:\\.|[^"\\])*)"', content_to_parse, re.DOTALL)
                    if script_match:
                        script_raw = script_match.group(1)
                        # Decode common escape sequences
                        script = script_raw.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r').replace('\\"', '"').replace("\\'", "'")
                    # Extract answer value
                    answer_match = re.search(r'"answer"\s*:\s*"((?:\\.|[^"\\])*)"', content_to_parse, re.DOTALL)
                    if answer_match:
                        answer_raw = answer_match.group(1)
                        answer = answer_raw.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r').replace('\\"', '"').replace("\\'", "'")
                except Exception:
                    pass

        # 2) Marker split
        if script is None:
            for marker in ['\n===SCRIPT===\n', '\n---SCRIPT---\n', '\n###SCRIPT###\n']:
                if marker in content:
                    parts = content.split(marker, 1)
                    answer = parts[0].strip()
                    script = parts[1].strip()
                    break

        # 3) Fenced code block
        if script is None:
            m = re.search(r"```(?:[a-zA-Z0-9_-]+)?\n([\s\S]*?)\n```", content)
            if m:
                script = m.group(1).strip()
                # Answer is content with the fence removed
                answer = (content[:m.start()] + content[m.end():]).strip()

        # If nothing matched, fallback: full content is script
        if script is None:
            script = content

        # Determine output path
        out_path = args.write_file
        if out_path == '-':
            # When writing to stdout, print answer first (if present), then script
            if answer:
                print(answer)
                print('\n---SCRIPT---\n')
            print(script)
        else:
            from os import path, chmod, makedirs
            from stat import S_IRUSR, S_IWUSR, S_IXUSR
            out_path = path.expanduser(out_path)
            d = path.dirname(out_path)
            if d and not path.exists(d):
                makedirs(d, exist_ok=True)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(script)
            # Make executable if starts with shebang
            if script.lstrip().startswith('#!'):
                try:
                    st = S_IRUSR | S_IWUSR | S_IXUSR
                    chmod(out_path, st)
                except Exception:
                    pass
            # Print answer to terminal if present, then confirm file written
            if answer:
                print(answer)
                print()
            print(f"Wrote generated script to: {out_path}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
