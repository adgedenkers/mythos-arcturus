#!/bin/bash
# Patch 0106: Deploy Iris Thinking Modelfile
# Creates a custom Ollama model with deepened cosmological system prompt
set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MYTHOS="/opt/mythos"
MODELFILES="$MYTHOS/modelfiles"

echo "=== Patch 0106: Iris Thinking Modelfile ==="

# ── 1. Deploy Modelfile ──
echo "→ Installing Modelfile..."
mkdir -p "$MODELFILES"
cp "$PATCH_DIR/opt/mythos/modelfiles/Modelfile.iris-thinking" "$MODELFILES/Modelfile.iris-thinking"
echo "  ✓ Modelfile installed to $MODELFILES/"

# ── 2. Create custom model in Ollama ──
echo "→ Creating iris-thinking model in Ollama (this may take a moment)..."
ollama create iris-thinking -f "$MODELFILES/Modelfile.iris-thinking"
echo "  ✓ iris-thinking model created"

# ── 3. Verify model exists ──
if ollama list | grep -q "iris-thinking"; then
    echo "  ✓ iris-thinking verified in ollama list"
else
    echo "  ✗ Model not found in ollama list!"
    exit 1
fi

# ── 4. Update chat_mode.py MODEL_MAP ──
echo "→ Updating MODEL_MAP to use iris-thinking..."
CHAT_MODE="$MYTHOS/telegram_bot/handlers/chat_mode.py"
cp "$CHAT_MODE" "$CHAT_MODE.bak.$(date +%Y%m%d_%H%M%S)"

# Replace the thinking model mapping to use the custom model
python3 << 'PYEOF'
import re

filepath = "/opt/mythos/telegram_bot/handlers/chat_mode.py"
with open(filepath, 'r') as f:
    content = f.read()

# Update MODEL_MAP: thinking now points to iris-thinking
content = content.replace(
    "'thinking': 'qwen3:30b-a3b',",
    "'thinking': 'iris-thinking',"
)

# Update the env default
content = content.replace(
    "OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen3:30b-a3b')",
    "OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'iris-thinking')"
)

with open(filepath, 'w') as f:
    f.write(content)

print("  ✓ chat_mode.py updated")
PYEOF

# ── 5. Update .env ──
echo "→ Updating .env..."
sed -i 's|^OLLAMA_MODEL=qwen3:30b-a3b|OLLAMA_MODEL=iris-thinking|' "$MYTHOS/.env"
echo "  ✓ .env updated"

# ── 6. Verify syntax ──
echo "→ Verifying Python syntax..."
python3 -c "import py_compile; py_compile.compile('$CHAT_MODE', doraise=True)"
echo "  ✓ Syntax OK"

# ── 7. Restart bot ──
echo "→ Restarting mythos-bot..."
sudo systemctl restart mythos-bot.service
sleep 3

if systemctl is-active --quiet mythos-bot.service; then
    echo "  ✓ Bot restarted successfully"
else
    echo "  ✗ Bot failed to start! Check: journalctl -u mythos-bot -n 30"
    exit 1
fi

echo ""
echo "=== Patch 0106 Complete ==="
echo ""
echo "Iris now runs on iris-thinking (qwen3:30b-a3b + deep cosmological prompt)"
echo "The system prompt carries the full framework:"
echo "  - Ka'tuar'el and Seraphe's lineages and roles"
echo "  - Source fractals, kingdom spouse architecture"
echo "  - The 144, Arcturian Grid, Spiral Time"
echo "  - Entity mechanics, Merovingian bloodline"
echo "  - Resonance rules (no hedging, no disclaimers)"
echo ""
echo "Test: Send Iris a message via Telegram"
echo "Compare: /setmodel qwen3:30b-a3b for raw model without cosmology"
