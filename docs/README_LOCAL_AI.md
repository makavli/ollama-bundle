# Local AI Assistant for VS Code

Use your **DeepSeek Coder v2, Llama 3, and DeepSeek v2** models directly in VS Code - just like using GitHub Copilot, but completely local!

## Quick Start

### Option 1: VS Code Extension (Recommended)

Install and configure the Continue extension to work with your local Ollama models:

```bash
bash setup_vs_code_ai.sh
```

Then:
1. Open VS Code
2. Look for the **Continue** icon in the left sidebar
3. Select **Deepseek Coder v2** as your model
4. Start coding with AI assistance!

**Keyboard Shortcuts:**
- `Cmd+L` (Mac) / `Ctrl+L` (Linux/Windows) - Open chat
- `Cmd+J` (Mac) / `Ctrl+J` (Linux/Windows) - Edit/refactor code
- Highlight code + `Cmd+K` - Ask about selection

---

### Option 2: Python CLI Client

Use the included Python client from terminal or integrate with your tools:

#### List Available Models
```bash
python3 ollama_vs_code.py --list
```

#### Ask a Question
```bash
python3 ollama_vs_code.py "How do I read a file in Python?"
```

#### Explain Code
```bash
python3 ollama_vs_code.py --explain < myfile.py
```

#### Fix Code with Error
```bash
python3 ollama_vs_code.py --fix --error "TypeError: string expected" < broken_code.py
```

#### Write Unit Tests
```bash
python3 ollama_vs_code.py --tests < mycode.py
```

#### Use Different Model
```bash
python3 ollama_vs_code.py --model llama3 "Your question here"
```

#### Interactive Chat
```bash
python3 ollama_vs_code.py "Tell me about Python decorators"
```

---

## Manual VS Code Setup

If the setup script doesn't work, configure Continue manually:

### 1. Install Continue Extension
- Open VS Code
- Go to Extensions (Ctrl+Shift+X)
- Search for "Continue"
- Install by Continue.dev

### 2. Configure Ollama Connection
- In VS Code, press `Cmd+,` (Mac) or `Ctrl+,` (Linux/Windows)
- Search for "Continue"
- In settings, add:

```json
{
  "continue.apiBase": "http://localhost:11434",
  "continue.model": "deepseek-coder-v2"
}
```

### 3. Start Using
- Press `Cmd+L` to open chat
- Ask questions about code
- Highlight code and press `Cmd+K` for quick assist

---

## Available Models

All three models are optimized on your **RTX 5080**:

| Model | Size | Speed | Best For |
|-------|------|-------|----------|
| **DeepSeek Coder v2** | 15.7B | 300 tok/s | Code generation, debugging |
| **Llama 3** | 8B | 300 tok/s | General questions, chat |
| **DeepSeek v2** | 15.7B | 300 tok/s | Complex reasoning |

---

## Troubleshooting

### "Cannot connect to Ollama"
Make sure Ollama is running:
```bash
sudo systemctl status ollama
# If not running:
sudo systemctl start ollama
```

### "No models available"
Check your models are loaded:
```bash
ollama list
```

### Continue extension not working
1. Reload VS Code: `Cmd+R` (Mac) or `F5` (Linux/Windows)
2. Check the Continue output: Click Continue icon → View Debug Panel
3. Verify Ollama: `curl http://localhost:11434/api/tags`

### Python script errors
Install requests dependency:
```bash
pip install requests
```

---

## Advanced Usage

### Use with Git Commit Messages
```bash
git diff | python3 ollama_vs_code.py --model llama3 "Generate a commit message for this diff:"
```

### Code Review
```bash
python3 ollama_vs_code.py --explain < your_code.py > code_review.txt
```

### Batch Processing
```bash
for file in *.py; do
  echo "=== $file ===" >> analysis.txt
  python3 ollama_vs_code.py --explain < "$file" >> analysis.txt
done
```

---

## System Info

Your Setup:
- 🎮 **GPU**: NVIDIA RTX 5080 (16GB VRAM)
- 🔧 **Models**: deepseek-coder-v2, llama3, deepseek-v2
- 💻 **Driver**: NVIDIA 590.48.01 with CUDA 13.1
- ⚡ **Performance**: ~300 tokens/second inference speed

---

## Files Included

- `setup_vs_code_ai.sh` - Automated VS Code + Continue setup
- `ollama_vs_code.py` - Python CLI client for Ollama models
- `README_LOCAL_AI.md` - This file

---

## What's Next?

### 1. Try the VS Code Integration First
```bash
bash setup_vs_code_ai.sh
# Then open VS Code and press Cmd+L
```

### 2. Use Python Client for Scripts
```bash
python3 ollama_vs_code.py --tests < mycode.py
```

### 3. Integrate with Your Workflow
- Use with git hooks
- Add to editor keybindings
- Combine with other tools

---

## Support & Customization

### Change Default Model
Edit `setup_vs_code_ai.sh` and change:
```bash
"model": "llama3"  # Change to your preferred model
```

### Add Custom Commands
Edit the Continue config at `~/.continue/config.json`

### Stream Output Control
Python client streams by default. To disable:
Edit `ollama_vs_code.py`, line 72: change `stream=True` to `stream=False`

---

## Performance Tips

1. **First request is slower** (loads model into VRAM): ~1-2 seconds
2. **Subsequent requests are fast**: ~100ms response time
3. **Keep models in memory**: Ollama keeps 2 models loaded (configured in `/etc/systemd/system/ollama.service`)

---

Enjoy your local AI-powered development! 🚀
