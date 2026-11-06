#!/usr/bin/env python3
"""
Ollama VS Code Integration CLI
Use local LLMs to generate code and work with files
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

# Make lib/ importable when run as a script
LIB_DIR = Path(__file__).resolve().parent.parent / "lib"
sys.path.insert(0, str(LIB_DIR))

from client import DEFAULT_MODEL, OllamaClient, OllamaError  # noqa: E402

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent


def build_parser():
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

  # Generate a script into a file
  python3 ollama_vs_code.py --write-file backup.sh "bash script that backs up ~/docs"

  # Select model
  python3 ollama_vs_code.py --model llama3 "Your question here"
        """,
    )
    parser.add_argument("prompt", nargs="?", help="Question or prompt")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("--host", default=None, help="Ollama host (default: localhost, or OLLAMA_HOST env var)")
    parser.add_argument("--port", type=int, default=None, help="Ollama port (default: 11434, or OLLAMA_PORT env var)")
    parser.add_argument("--list", action="store_true", help="List available models")
    parser.add_argument("--explain", action="store_true", help="Explain code from stdin")
    parser.add_argument("--fix", action="store_true", help="Fix code from stdin")
    parser.add_argument("--error", help="Error message (use with --fix)")
    parser.add_argument("--tests", action="store_true", help="Write tests for code")
    parser.add_argument("--check", action="store_true", help="Check Ollama connection")
    parser.add_argument("--write-file", metavar="FILE",
                        help="Create a file with model output ('-' prints to stdout)")
    parser.add_argument("-f", "--prompt-file", metavar="PROMPT_FILE",
                        help="Read prompt/code from a file instead of the argument or stdin")
    return parser


def resolve_url(args):
    """--host/--port > OLLAMA_URL > OLLAMA_HOST/OLLAMA_PORT > default."""
    if args.host or args.port:
        host = args.host or os.environ.get("OLLAMA_HOST", "localhost")
        port = args.port or int(os.environ.get("OLLAMA_PORT", "11434"))
        if "://" not in host and ":" not in host:
            return f"http://{host}:{port}"
        return host
    return os.environ.get("OLLAMA_URL") or os.environ.get("OLLAMA_HOST")


def default_prompt_file():
    """The bundled example prompt, used only when --write-file gets no other input."""
    for candidate in (Path("prompt"), SCRIPT_DIR / "prompt", REPO_ROOT / "examples" / "prompt"):
        if candidate.is_file():
            return candidate
    return None


def read_input(args, stdin=None):
    """Where the text to work on comes from, in priority order:
    --prompt-file, the positional prompt, piped stdin. Returns None if there is none.
    (Previously a bundled example file silently won over piped input.)"""
    stdin = stdin if stdin is not None else sys.stdin
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8")
    if args.prompt:
        return args.prompt
    if not stdin.isatty():
        data = stdin.read()
        return data if data.strip() else None
    return None


def _unescape(raw):
    try:
        return json.loads(f'"{raw}"')
    except ValueError:
        return raw.replace("\\n", "\n").replace("\\t", "\t").replace('\\"', '"')


def split_answer_and_script(content):
    """Best-effort split of model output into (answer, script). Supports:
    1) JSON {"answer": ..., "script": ...} (optionally inside a ```json fence)
    2) a ===SCRIPT=== / ---SCRIPT--- / ###SCRIPT### marker line
    3) the first fenced code block
    Otherwise the whole output is the script."""
    stripped = content.strip()
    fence = re.match(r"^```(?:json|javascript)?\s*\n([\s\S]*)\n```\s*$", stripped)
    to_parse = fence.group(1) if fence else stripped

    try:
        data = json.loads(to_parse)
        if isinstance(data, dict) and ("script" in data or "answer" in data):
            script = data.get("script") or data.get("code") or data.get("file")
            answer = data.get("answer") or data.get("explanation")
            if script is not None:
                return answer, script
    except ValueError:
        if to_parse.startswith("{"):
            script_match = re.search(r'"script"\s*:\s*"((?:\\.|[^"\\])*)"', to_parse, re.DOTALL)
            answer_match = re.search(r'"answer"\s*:\s*"((?:\\.|[^"\\])*)"', to_parse, re.DOTALL)
            if script_match:
                return (_unescape(answer_match.group(1)) if answer_match else None,
                        _unescape(script_match.group(1)))

    for marker in ("\n===SCRIPT===\n", "\n---SCRIPT---\n", "\n###SCRIPT###\n"):
        if marker in content:
            answer, script = content.split(marker, 1)
            return answer.strip() or None, script.strip()

    block = re.search(r"```(?:[a-zA-Z0-9_-]+)?\n([\s\S]*?)\n```", content)
    if block:
        answer = (content[:block.start()] + content[block.end():]).strip()
        return answer or None, block.group(1).strip()

    return None, content


def write_output(out_path, answer, script):
    if out_path == "-":
        if answer:
            print(answer)
            print("\n---SCRIPT---\n")
        print(script)
        return
    path = Path(out_path).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(script, encoding="utf-8")
    if script.lstrip().startswith("#!"):
        path.chmod(0o755)          # make generated scripts with a shebang executable
    if answer:
        print(answer)
        print()
    print(f"Wrote generated script to: {path}")


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    client = OllamaClient(base_url=resolve_url(args))

    if not client.check_connection():
        print(f"❌ Cannot connect to Ollama at {client.base_url}")
        print("Start Ollama service: sudo systemctl start ollama")
        print("Or set OLLAMA_URL env var or use --host/--port options")
        return 1

    try:
        if args.list:
            print("Available models:")
            for model in client.list_models():
                print(f"  • {model}")
            return 0

        if args.check:
            print(f"✓ Ollama is running at {client.base_url}")
            print(f"✓ Available models: {len(client.list_models())}")
            return 0

        if args.explain or args.fix or args.tests:
            code = read_input(args)
            if code is None:
                print("No input provided: pipe code into stdin or use --prompt-file")
                return 1
            if args.explain:
                print("Explaining code...\n")
                client.explain_code(code, model=args.model)
            elif args.fix:
                print("Fixing code...\n")
                client.fix_code(code, args.error, model=args.model)
            else:
                print("Writing tests...\n")
                client.write_tests(code, model=args.model)
            return 0

        if args.write_file:
            prompt = read_input(args)
            if prompt is None:
                example = default_prompt_file()
                if example is not None:
                    print(f"(no prompt given - using example prompt {example})")
                    prompt = example.read_text(encoding="utf-8")
                elif sys.stdin.isatty():
                    prompt = input("Enter prompt for file content: ")
            if not prompt or not prompt.strip():
                print("No prompt to generate file content from.")
                return 1
            print(f"Generating content using model {args.model}...\n")
            content = client.generate(prompt, model=args.model, stream=False)
            answer, script = split_answer_and_script(content)
            write_output(args.write_file, answer, script)
            return 0

        if args.prompt:
            print(f"Thinking (using {args.model})...\n")
            client.chat(args.prompt, args.model)
            return 0
    except OllamaError as e:
        print(f"❌ {e}")
        return 1

    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
