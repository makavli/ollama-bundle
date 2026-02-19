README - ollama_vs_code.py (man-style)
=====================================

NAME
----
ollama_vs_code.py - Command-line helper for using local Ollama models (explain, fix, test, generate files)

SYNOPSIS
--------
python3 ollama_vs_code.py [OPTIONS] [prompt]

DESCRIPTION
-----------
`ollama_vs_code.py` is a small CLI client that talks to a local Ollama server
(`http://localhost:11434`) and performs common tasks using your local models
(for example `deepseek-coder-v2`, `llama3`, `deepseek-v2`). The script can:

- List models available to Ollama
- Explain source code read from stdin
- Attempt to fix code given an optional error message
- Write unit tests for provided code
- Chat with a model using a prompt
- Create files (scripts or any content) from model-generated output

This file documents each option and provides examples and troubleshooting
information in a man-page-like style.

REQUIREMENTS
------------
- Python 3
- `requests` library (pip install requests)
- Ollama service running and reachable at `http://localhost:11434`

OPTIONS (DETAILED)
------------------

positional argument:
  prompt
      Optional prompt or question to send directly to the model. If omitted
      and the operation expects stdin (for `--explain`, `--fix`, `--tests`),
      data is read from standard input.

--model MODEL
      Select the model to use. Default: `deepseek-coder-v2`.
      Example: `--model llama3`

--list
      List models available from the local Ollama server.
      Example:

      ```bash
      python3 ollama_vs_code.py --list
      ```

--explain
      Read source code from stdin and ask the selected model to explain it in
      detail. Use with input redirection or a pipe.
      Example:

      ```bash
      python3 ollama_vs_code.py --explain < my_module.py
      ```

--fix
      Read code from stdin and ask the model to fix it. Use `--error` to
      provide error output or context that the model should consider.
      Example:

      ```bash
      python3 ollama_vs_code.py --fix --error "TypeError: expected str" < bad.py
      ```

--error ERROR
      Attach an error message or traceback to provide context for `--fix`.

--tests
      Read code from stdin and ask the model to generate unit tests for it.
      Example:

      ```bash
      python3 ollama_vs_code.py --tests < module_to_test.py
      ```

--check
      Quick health check: verify Ollama is reachable at
      `http://localhost:11434` and show how many models are available.

--write-file FILE
      Create a file with model-generated content. FILE may be a path, `-`
      (stdout), or a value like `/tmp/script.sh`.

      Behavior:
      - If a positional `prompt` is provided, it is used as the prompt to the
        model and the generated content is written to FILE.
      - If `FILE` is `-` or there is piped stdin, the script reads the prompt
        from stdin.
      - If the generated content starts with a shebang (`#!`), the script
        will attempt to set the executable bit on the created file.

      Examples:

      Provide the prompt as a heredoc (recommended to avoid shell escapes):

      ```bash
      cat > /tmp/prompt.txt <<'PROMPT'
      Write a bash script that prints "Hello from model" and exits 0
      PROMPT

      python3 ollama_vs_code.py --write-file /tmp/test_script.sh < /tmp/prompt.txt
      ls -l /tmp/test_script.sh
      /tmp/test_script.sh
      ```

      Use direct positional prompt (quote carefully):

      ```bash
      python3 ollama_vs_code.py --write-file ~/hello.py "Write a Python script that prints('hello')"
      ```

      Write to stdout instead of file:

      ```bash
      python3 ollama_vs_code.py --write-file - "Generate a small README snippet"
      ```

USAGE NOTES
-----------

- Shell quoting: For prompts that contain special shell characters (for
  example `!`), prefer using stdin/heredoc with a single-quoted delimiter
  (`<<'EOF'`) to avoid history expansion and interpolation. Example:

  ```bash
  cat > /tmp/prompt <<'EOF'
  #!/bin/bash
  echo "Hello from generated script"
  EOF

  python3 ollama_vs_code.py --write-file /tmp/gen.sh < /tmp/prompt
  ```

- Review model output before executing it. The script writes model output
  to disk when requested, but it does not run or validate the generated
  code. Always inspect and test generated scripts before executing them.

- If you want the generated file to be executable, include a shebang on the
  first line (`#!/usr/bin/env bash` or `#!/usr/bin/env python3`). The CLI
  will set the executable bit for files that begin with `#!`.

SECURITY & PRIVACY
------------------

- The model runs locally against your Ollama server; no content is sent to
  external services by the CLI itself. If you use other extensions that use
  cloud APIs, review their settings.
- The model cannot directly modify your files by itself — only this CLI
  writes output to files when you call `--write-file`.
- Always inspect generated content before running it, especially scripts or
  code that will run with elevated permissions.

EXIT CODES
----------

0  Success
1  Generic error (e.g., Ollama not reachable, missing prompt on stdin when
   required, or filesystem permissions error)

EXAMPLES (COMPREHENSIVE)
------------------------

List models and choose one for a quick chat:

```bash
python3 ollama_vs_code.py --list
python3 ollama_vs_code.py --model llama3 "Explain the difference between lists and tuples in Python"
```

Explain a module:

```bash
python3 ollama_vs_code.py --explain < mymodule.py
```

Fix code using an error message:

```bash
python3 ollama_vs_code.py --fix --error "IndexError: list index out of range" < buggy.py
```

Generate a test file:

```bash
python3 ollama_vs_code.py --tests < functions.py > tests_for_functions.py
```

Create an executable script from a heredoc prompt:

```bash
python3 ollama_vs_code.py --write-file ~/bin/hello_from_model.sh <<'PROMPT'
Write a bash script that prints "Hello from model" and exits 0
PROMPT

chmod +x ~/bin/hello_from_model.sh
~/bin/hello_from_model.sh
```

DIAGNOSTICS
-----------

If the CLI reports that it cannot reach Ollama:

```bash
# Check Ollama service
sudo systemctl status ollama

# Check the API endpoint
curl -s http://localhost:11434/api/tags | jq .
```

If file writing fails, check permissions and output path. If you cannot
execute the generated script, ensure the shebang is present and that the
file has execute permission.

FILES
-----
`~/.continue/config.json` - (optional) if you use the Continue extension for
VS Code; not required for the CLI.

SEE ALSO
--------
`ollama` - Ollama CLI (model management), `docker` (when running OpenWebUI),
`Continue` extension for VS Code (optional)

AUTHORS
-------
This README was generated to document the `ollama_vs_code.py` tool in your
workspace. The script is provided as-is; review before use.
