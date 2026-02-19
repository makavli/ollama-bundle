# Ollama Bundle - Local AI Development Suite

A comprehensive, bundle for deploying and working with local LLMs using Ollama.

![Structure](https://img.shields.io/badge/structure-organized-brightgreen) ![Status](https://img.shields.io/badge/status-production--ready-blue) ![Python](https://img.shields.io/badge/python-3.7+-blue)

## 📦 What's Included

### 🎯 Ollama CLI (`ollama-cli/`)
Professional-grade command-line interface for code generation and LLM interactions.

- Generate scripts from natural language
- Analyze, fix, and test code
- Save output directly to files
- Streaming and interactive modes

**Quick Start:**
```bash
cd ollama-cli
python3 src/ollama_vs_code.py --write-file output.sh
```

### 🔧 Installation & Setup (`installer/`)
Complete system setup and configuration tools.

- Automated Ollama installation
- GPU driver setup
- OpenWebUI container deployment
- VS Code integration

**Quick Start:**
```bash
cd installer
bash prepare_install.sh
python3 setup_all.py
bash runGUI.sh
```

### 📊 Benchmarks (`benchmarks/`)
Performance testing and comparison tools for models.

- Model loading benchmarks
- Response time measurements
- Memory usage tracking
- Throughput analysis

**Quick Start:**
```bash
cd benchmarks
python3 bench.py --model deepseek-coder-v2 --iterations 10
```

### 📝 Examples (`examples/`)
Sample prompts and configuration templates.

- JSON-formatted prompt examples
- Custom prompt creation guide
- Best practices for prompt engineering

**Quick Start:**
```bash
# Uses examples/prompt automatically
python3 ollama-cli/src/ollama_vs_code.py --write-file my_script.sh
```

### 📖 Documentation (`docs/`)
Comprehensive guides and technical references.

- Full CLI command reference
- Installation troubleshooting
- Architecture and best practices

## 🚀 Quick Start

### Prerequisites
- Ubuntu/Debian-based system
- Docker (for OpenWebUI)
- Python 3.7+
- 8GB+ RAM (16GB+ recommended for GPU models)

### 1. System Setup
```bash
cd installer
bash prepare_install.sh
```

### 2. Install Ollama & Models
```bash
python3 setup_all.py
```

### 3. Start Web UI
```bash
bash runGUI.sh
# Access at http://localhost:3000
```

### 4. Use CLI for Code Generation
```bash
cd ../ollama-cli
python3 src/ollama_vs_code.py --write-file my_script.sh
```

## 📂 Project Structure

```
ollama-bundle/
├── ollama-cli/          # CLI tool for code generation
│   ├── lib/             # OllamaClient library
│   ├── src/             # Main application
│   └── README.md
├── installer/           # Setup & installation scripts
│   ├── setup_all.py
│   ├── prepare_install.sh
│   └── README.md
├── benchmarks/          # Performance testing
│   ├── bench.py
│   ├── bench_deepseek.py
│   └── README.md
├── examples/            # Sample prompts & configs
│   ├── prompt
│   └── README.md
├── docs/                # Technical documentation
│   ├── README_OLLAMA_VS_CODE_MAN.md
│   ├── README_LOCAL_AI.md
│   ├── README_install_openwebui.md
│   └── README.md
└── README.md           # This file
```

## 🎓 Getting Started Guides

### For CLI Users
1. Start with `docs/README_LOCAL_AI.md`
2. Read `ollama-cli/README.md` for usage
3. See `docs/README_OLLAMA_VS_CODE_MAN.md` for complete reference

### For Developers
1. Check `ollama-cli/lib/client.py` for API
2. Explore `examples/` for prompt patterns
3. Review `benchmarks/` for performance testing

### For System Admins
1. Run `installer/prepare_install.sh`
2. Configure with `docs/README_install_openwebui.md`
3. Monitor with `benchmarks/bench.py`

## ⚙️ Configuration

### CLI Tool Configuration (`ollama-cli/`)

The CLI tool can be configured in three ways (in priority order):

#### 1. Command-line Arguments
```bash
# Specify custom Ollama endpoint
python3 src/ollama_vs_code.py --host 192.168.1.100 --port 11434 "Your prompt"

# Or use specific model
python3 src/ollama_vs_code.py --model llama3 "Your prompt"
```

#### 2. Environment Variables
```bash
# Set Ollama URL (overrides host/port)
export OLLAMA_URL=http://192.168.1.100:11434
python3 src/ollama_vs_code.py "Your prompt"

# Or set host and port separately
export OLLAMA_HOST=192.168.1.100
export OLLAMA_PORT=11434
python3 src/ollama_vs_code.py "Your prompt"
```

#### 3. Default Values
- `OLLAMA_URL`: `http://localhost:11434`
- `OLLAMA_HOST`: `localhost`
- `OLLAMA_PORT`: `11434`
- Default model: `deepseek-coder-v2`

### Setup & Installation Configuration (`installer/`)

The setup scripts read these environment variables:

```bash
# Ollama service binding (for container communication)
export OLLAMA_HOST=0.0.0.0              # Listen on all interfaces (default: host.docker.internal)
export OLLAMA_PORT=11434                # Ollama API port (default: 11434)

# OpenWebUI configuration
export OPENWEBUI_PORT=3000              # Web UI port (default: 3000)

# Ollama resource limits (systemd)
export OLLAMA_NUM_THREAD=8              # CPU threads for inference
export OLLAMA_GPU_MEMORY=14000          # GPU memory allocation (MB)
export OLLAMA_MAX_LOADED_MODELS=2       # Max concurrent loaded models
```

### Accessing Services Locally

- **Ollama API**: `http://localhost:11434`
- **OpenWebUI Web Interface**: `http://localhost:3000`
- **Default model**: Available at both endpoints

### Network Configuration

For remote access (e.g., from another machine):

```bash
# Make Ollama accessible on your network IP
export OLLAMA_HOST=0.0.0.0:11434

# Then access from remote machine:
# http://YOUR_MACHINE_IP:11434   (Ollama API)
# http://YOUR_MACHINE_IP:3000    (OpenWebUI)
```

### Default Models
- `deepseek-coder-v2` - Code-focused model
- `llama3` - General-purpose model
- `deepseek-v2` - Advanced reasoning

## 🔌 Integration Points

### Web UI - OpenWebUI
**Access at `http://localhost:3000`** (after running `bash installer/runGUI.sh`)

- Chat interface for all LLMs
- Model management
- Conversation history
- Multi-user support (when configured)

### CLI Tool
```bash
# Default (localhost)
python3 ollama-cli/src/ollama_vs_code.py "Your question"

# Remote Ollama instance
export OLLAMA_URL=http://remote-server:11434
python3 ollama-cli/src/ollama_vs_code.py "Your question"
```

### VS Code
- Install **Continue.dev** extension
- Run `installer/setup_vs_code_ai.sh`
- Use `Ctrl+K` to ask AI questions

### Docker/Kubernetes
- OpenWebUI container ready
- Ollama runs as systemd service
- Easy to containerize entire suite

### Direct HTTP API
- **Endpoint**: `http://localhost:11434` (or configured host/port)
- **Documentation**: See `ollama-cli/lib/client.py` for usage examples
- Example:
  ```bash
  curl -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d '{"model": "deepseek-coder-v2", "prompt": "Hello", "stream": false}'
  ```

## 📊 System Requirements

| Component | Minimum | Recommended | GPU |
|-----------|---------|-------------|-----|
| RAM | 8GB | 16GB | 24GB+ |
| Disk | 20GB | 50GB | 100GB+ |
| CPU | 4 cores | 8+ cores | 6+ cores |
| GPU VRAM | - | - | 10GB+ |

## 🛠️ Troubleshooting

### Ollama won't start
```bash
sudo systemctl restart ollama
# Check status
sudo systemctl status ollama
```

### Models won't load
```bash
# Check available memory
free -h
# Pull model manually
ollama pull deepseek-coder-v2
```

### Container issues
```bash
# Reset containers
docker ps -a | grep open-webui | awk '{print $1}' | xargs docker rm
bash installer/runGUI.sh
```

### GPU not detected
```bash
# Check GPU
nvidia-smi
# Verify drivers
ubuntu-drivers list
```

## 📞 Support

For issues and questions:
- Check relevant README in `docs/`
- Review `examples/` for sample usage
- Check Ollama docs: https://github.com/jmorganca/ollama

## 📜 License

[Add your license here]

## 🎉 Features at a Glance

✅ Local LLM deployment (no cloud required)  
✅ Code generation from natural language  
✅ Web UI for interactive use  
✅ CLI for automation and scripting  
✅ GPU acceleration support  
✅ Multiple model support  
✅ Performance benchmarking  
✅ VS Code integration  
✅ Production-ready architecture  
✅ Comprehensive documentation  

---

**Built for developers who want to run AI locally, responsibly, and efficiently.**
