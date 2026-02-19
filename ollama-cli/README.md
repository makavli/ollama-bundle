# Ollama CLI

Professional command-line interface for local LLM operations with Ollama.

## Features

- **Code Generation**: Generate scripts and code from natural language prompts
- **Code Analysis**: Explain, fix, and write tests for code
- **File Output**: Save generated content directly to files with automatic parsing
- **Model Management**: List available models and check connection status
- **Streaming**: Real-time response streaming for interactive use

## Usage

### Basic Commands

```bash
# List available models
python3 src/ollama_vs_code.py --list

# Ask a question
python3 src/ollama_vs_code.py "Write a Python function to sort a list"

# Generate and save to file
python3 src/ollama_vs_code.py --write-file output.sh

# Explain code
python3 src/ollama_vs_code.py --explain < mycode.py
```

## Architecture

- `lib/` - Core client library (OllamaClient class)
- `src/` - CLI application entry point

## Configuration

### Command-line Options

```bash
# Specify custom Ollama host and port
python3 src/ollama_vs_code.py --host 192.168.1.100 --port 11434 "Your prompt"

# Override default model
python3 src/ollama_vs_code.py --model llama3 "Your question"

# Check connection and list models
python3 src/ollama_vs_code.py --check

# Use prompt from file
python3 src/ollama_vs_code.py -f /path/to/prompt.txt --write-file output.sh
```

### Environment Variables

```bash
# Set default Ollama URL (overrides --host and --port if both specified)
export OLLAMA_URL=http://192.168.1.100:11434
python3 src/ollama_vs_code.py "Your prompt"

# Or set host and port separately
export OLLAMA_HOST=myserver.local
export OLLAMA_PORT=8000
python3 src/ollama_vs_code.py "Your prompt"
```

### Default Configuration

- **Ollama URL**: `http://localhost:11434` (or `OLLAMA_URL` env var)
- **Host**: `localhost` (or `OLLAMA_HOST` env var)
- **Port**: `11434` (or `OLLAMA_PORT` env var)
- **Model**: `deepseek-coder-v2`

### Priority Order

1. `--host`/`--port` CLI arguments (if both provided)
2. `OLLAMA_URL` environment variable
3. `OLLAMA_HOST`/`OLLAMA_PORT` environment variables
4. Default: `http://localhost:11434`
