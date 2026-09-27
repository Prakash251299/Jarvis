#!/usr/bin/env bash
# =============================================================================
# Jarvis AI Assistant - Local Setup Script
# =============================================================================
set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

JARVIS_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════╗"
echo "║        JARVIS Local AI Voice Assistant Setup       ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ─── Step 1: Check prerequisites ───────────────────────────────────────────
echo -e "${BLUE}[1/8] Checking prerequisites...${NC}"

check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo -e "${RED}✗ $1 is not installed. Please install it first.${NC}"
        return 1
    fi
    echo -e "${GREEN}✓ $1 found${NC}"
}

check_command python3
check_command pip3
check_command flutter
check_command ffmpeg
check_command curl

# Check Python version
PY_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if python3 -c 'import sys; exit(0 if sys.version_info >= (3,12) else 1)'; then
    echo -e "${GREEN}✓ Python $PY_VERSION${NC}"
else
    echo -e "${RED}✗ Python 3.12+ required (found $PY_VERSION)${NC}"
    exit 1
fi

# ─── Step 2: Install Ollama ────────────────────────────────────────────────
echo ""
echo -e "${BLUE}[2/8] Checking Ollama...${NC}"
if ! command -v ollama &> /dev/null; then
    echo -e "${YELLOW}Ollama not found. Installing...${NC}"
    curl -fsSL https://ollama.ai/install.sh | sh
    echo -e "${GREEN}✓ Ollama installed${NC}"
else
    echo -e "${GREEN}✓ Ollama already installed${NC}"
fi

# Start Ollama service
echo -e "${YELLOW}Starting Ollama service...${NC}"
ollama serve &>/dev/null &
sleep 3

# ─── Step 3: Pull Qwen3 8B model ─────────────────────────────────────────
echo ""
echo -e "${BLUE}[3/8] Pulling Qwen3 8B model (this may take a while)...${NC}"
if ollama list | grep -q "qwen3:8b"; then
    echo -e "${GREEN}✓ qwen3:8b already downloaded${NC}"
else
    echo -e "${YELLOW}Downloading qwen3:8b (~5GB)...${NC}"
    ollama pull qwen3:8b
    echo -e "${GREEN}✓ qwen3:8b downloaded${NC}"
fi

# ─── Step 4: Install Piper TTS ────────────────────────────────────────────
echo ""
echo -e "${BLUE}[4/8] Installing Piper TTS...${NC}"
PIPER_DIR="$HOME/.local/share/piper"
PIPER_BIN="$HOME/.local/bin/piper"
mkdir -p "$PIPER_DIR" "$HOME/.local/bin"

if ! command -v piper &> /dev/null && [ ! -f "$PIPER_BIN" ]; then
    echo -e "${YELLOW}Downloading Piper TTS...${NC}"
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
    ARCH=$(uname -m)
    
    if [ "$OS" = "darwin" ]; then
        PIPER_URL="https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_macos_x86_64.tar.gz"
        if [ "$ARCH" = "arm64" ]; then
            PIPER_URL="https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_macos_aarch64.tar.gz"
        fi
    else
        PIPER_URL="https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_linux_x86_64.tar.gz"
    fi
    
    curl -fsSL "$PIPER_URL" -o /tmp/piper.tar.gz
    tar -xzf /tmp/piper.tar.gz -C "$HOME/.local/bin/" 2>/dev/null || \
        tar -xzf /tmp/piper.tar.gz -C /tmp/piper_extract/ && \
        cp /tmp/piper_extract/piper "$PIPER_BIN" 2>/dev/null || true
    rm -f /tmp/piper.tar.gz
    chmod +x "$PIPER_BIN" 2>/dev/null || true
    echo -e "${GREEN}✓ Piper installed${NC}"
    
    # Download default voice
    echo -e "${YELLOW}Downloading default Piper voice (en_US-lessac-medium)...${NC}"
    VOICE_BASE="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium"
    curl -fsSL "${VOICE_BASE}/en_US-lessac-medium.onnx" -o "${PIPER_DIR}/en_US-lessac-medium.onnx"
    curl -fsSL "${VOICE_BASE}/en_US-lessac-medium.onnx.json" -o "${PIPER_DIR}/en_US-lessac-medium.onnx.json"
    echo -e "${GREEN}✓ Default voice downloaded${NC}"
else
    echo -e "${GREEN}✓ Piper already installed${NC}"
fi

# ─── Step 5: Backend Python setup ─────────────────────────────────────────
echo ""
echo -e "${BLUE}[5/8] Setting up Python backend...${NC}"
cd "$JARVIS_DIR/backend"

if [ ! -d "venv" ]; then
    python3.12 -m venv venv 2>/dev/null || python3 -m venv venv
fi
source venv/bin/activate

pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}✓ Python dependencies installed${NC}"

# Copy .env if not exists
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✓ .env created from .env.example${NC}"
fi

deactivate

# ─── Step 6: Flutter setup ────────────────────────────────────────────────
echo ""
echo -e "${BLUE}[6/8] Setting up Flutter...${NC}"
cd "$JARVIS_DIR/flutter"
flutter pub get
echo -e "${GREEN}✓ Flutter dependencies installed${NC}"

# ─── Step 7: Run code generation ─────────────────────────────────────────
echo ""
echo -e "${BLUE}[7/8] Running Flutter code generation...${NC}"
flutter pub run build_runner build --delete-conflicting-outputs 2>/dev/null || \
    dart run build_runner build --delete-conflicting-outputs
echo -e "${GREEN}✓ Code generation complete${NC}"

# ─── Step 8: Final verification ──────────────────────────────────────────
echo ""
echo -e "${BLUE}[8/8] Verifying setup...${NC}"
if curl -s http://localhost:11434/api/tags &>/dev/null; then
    echo -e "${GREEN}✓ Ollama is running${NC}"
else
    echo -e "${YELLOW}⚠ Ollama may not be running. Start it with: ollama serve${NC}"
fi

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════════════╗"
echo "║              Setup Complete! 🎉                    ║"
echo "╚════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo -e "${CYAN}To start Jarvis:${NC}"
echo ""
echo -e "  ${YELLOW}Terminal 1 (Backend):${NC}"
echo -e "  cd $JARVIS_DIR/backend"
echo -e "  source venv/bin/activate"
echo -e "  uvicorn app.main:app --reload"
echo ""
echo -e "  ${YELLOW}Terminal 2 (Flutter):${NC}"
echo -e "  cd $JARVIS_DIR/flutter"
echo -e "  flutter run -d macos  # or: flutter run -d chrome"
echo ""
