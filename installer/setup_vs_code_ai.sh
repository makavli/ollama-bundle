#!/bin/bash
# VS Code Local AI Assistant Setup
# Installs Continue extension and configures it to use local Ollama models

set -e

echo "=========================================="
echo "VS Code Local AI Setup"
echo "=========================================="
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "⚠️  Don't run this as root. Run as your regular user:"
   echo "   bash setup_vs_code_ai.sh"
   exit 1
fi

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if code is installed
echo "STEP 1: Checking for VS Code..."
if ! command -v code &> /dev/null; then
    echo -e "${RED}❌ VS Code not found${NC}"
    echo "Install VS Code from: https://code.visualstudio.com/download"
    exit 1
fi
echo -e "${GREEN}✓ VS Code found$(code --version | head -1)${NC}"
echo ""

# Check if Ollama is running
echo "STEP 2: Checking Ollama connection..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${RED}❌ Ollama not accessible at localhost:11434${NC}"
    echo "Start Ollama service: sudo systemctl start ollama"
    exit 1
fi
echo -e "${GREEN}✓ Ollama is running${NC}"

# List available models
echo "Available models:"
curl -s http://localhost:11434/api/tags | python3 -c "import sys,json; tags=json.load(sys.stdin)['models']; [print(f\"  - {m['name']}\") for m in tags]"
echo ""

# Install Continue extension
echo "STEP 3: Installing Continue extension..."
code --install-extension Continue.continue > /dev/null 2>&1 || true

if code --list-extensions | grep -q "Continue.continue"; then
    echo -e "${GREEN}✓ Continue extension installed${NC}"
else
    echo -e "${YELLOW}⚠️  Continue extension may need to be installed manually${NC}"
    echo "Open VS Code and search for 'Continue' in Extensions, then install"
fi
echo ""

# Create Continue config file
echo "STEP 4: Creating Continue configuration..."
CONFIG_DIR="$HOME/.continue"
mkdir -p "$CONFIG_DIR"

CONFIG_FILE="$CONFIG_DIR/config.json"

cat > "$CONFIG_FILE" << 'CONTINUE_CONFIG'
{
  "models": [
    {
      "title": "Deepseek Coder v2",
      "provider": "ollama",
      "model": "deepseek-coder-v2",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "Llama 3",
      "provider": "ollama",
      "model": "llama3",
      "apiBase": "http://localhost:11434"
    },
    {
      "title": "Deepseek v2",
      "provider": "ollama",
      "model": "deepseek-v2",
      "apiBase": "http://localhost:11434"
    }
  ],
  "tabAutocompleteModel": {
    "title": "Deepseek Coder v2",
    "provider": "ollama",
    "model": "deepseek-coder-v2",
    "apiBase": "http://localhost:11434"
  },
  "slashCommands": [
    {
      "name": "edit",
      "description": "Edit highlighted code"
    },
    {
      "name": "comment",
      "description": "Write comments"
    }
  ],
  "customCommands": [
    {
      "name": "explain",
      "prompt": "Explain the selected code in detail",
      "description": "Explain highlighted code"
    }
  ]
}
CONTINUE_CONFIG

echo -e "${GREEN}✓ Configuration file created at: $CONFIG_FILE${NC}"
echo ""

# Alternative: Give user option to use manual config location
echo "STEP 5: Continue extension locations:"
echo ""
echo "If using VS Code settings.json (alternative):"
echo "1. Open VS Code settings: Ctrl+Shift+P → Preferences: Open Settings (JSON)"
echo "2. Add this to your settings.json:"
echo ""
echo '{
  "continue.apiBase": "http://localhost:11434"
}'
echo ""

echo "=========================================="
echo -e "${GREEN}✓ Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Open VS Code"
echo "2. Look for the 'Continue' icon in the left sidebar (or Cmd+Shift+L)"
echo "3. Select 'Deepseek Coder v2' as your model"
echo "4. Start asking questions or use Ctrl+L for inline suggestions"
echo ""
echo "Usage:"
echo "  Cmd+L (Mac) / Ctrl+L (Linux/Windows) - Quick chat"
echo "  Cmd+J (Mac) / Ctrl+J (Linux/Windows) - Edit code"
echo "  Highlight code + Cmd+K - Ask about selection"
echo ""
