#!/bin/bash
# Patch 0105: Add 'thinking' model class (qwen3:30b-a3b) and make it default
set -e

MYTHOS="/opt/mythos"
BOT="$MYTHOS/telegram_bot"
HANDLERS="$BOT/handlers"

echo "=== Patch 0105: Thinking Model Class ==="

# ── 1. Update chat_mode.py MODEL_MAP and default ──
echo "→ Updating chat_mode.py..."
cp "$HANDLERS/chat_mode.py" "$HANDLERS/chat_mode.py.bak.$(date +%Y%m%d_%H%M%S)"

# Add 'thinking' to MODEL_MAP
sed -i "s|'deep': 'qwen2.5:32b',|'deep': 'qwen2.5:32b',\n    'thinking': 'qwen3:30b-a3b',|" "$HANDLERS/chat_mode.py"

# Update the env default fallback
sed -i "s|OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:32b')|OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen3:30b-a3b')|" "$HANDLERS/chat_mode.py"

echo "  ✓ chat_mode.py updated"

# ── 2. Update mythos_bot.py /model command ──
echo "→ Updating mythos_bot.py..."
cp "$BOT/mythos_bot.py" "$BOT/mythos_bot.py.bak.$(date +%Y%m%d_%H%M%S)"

# Add 'thinking' to the valid model list
sed -i 's|if new_model in \["auto", "fast", "deep"\]:|if new_model in ["auto", "fast", "deep", "thinking"]:|' "$BOT/mythos_bot.py"

# Add thinking to descriptions dict
sed -i '/"deep": "qwen2.5:32b (~30s)"/a\                "thinking": "qwen3:30b-a3b (deep reasoning)"' "$BOT/mythos_bot.py"

# Change default session model from "auto" to "thinking"
sed -i 's|"current_model": "auto",|"current_model": "thinking",|' "$BOT/mythos_bot.py"

# Update the /model help text
sed -i 's|"`/model auto` - qwen2.5:32b\\n"|"`/model auto` - qwen2.5:32b\\n"\n            "`/model thinking` - qwen3:30b-a3b (DEFAULT)\\n"|' "$BOT/mythos_bot.py"

# Update "Use: auto, fast, deep" error message
sed -i 's|"Use: auto, fast, deep"|"Use: auto, fast, deep, thinking"|' "$BOT/mythos_bot.py"

echo "  ✓ mythos_bot.py updated"

# ── 3. Update .env default ──
echo "→ Updating .env..."
if grep -q "^OLLAMA_MODEL=" "$MYTHOS/.env"; then
    sed -i 's|^OLLAMA_MODEL=.*|OLLAMA_MODEL=qwen3:30b-a3b|' "$MYTHOS/.env"
else
    echo "OLLAMA_MODEL=qwen3:30b-a3b" >> "$MYTHOS/.env"
fi
echo "  ✓ .env updated"

# ── 4. Restart bot ──
echo "→ Restarting mythos-bot..."
sudo systemctl restart mythos-bot.service
sleep 2

if systemctl is-active --quiet mythos-bot.service; then
    echo "  ✓ Bot restarted successfully"
else
    echo "  ✗ Bot failed to start! Check: journalctl -u mythos-bot -n 30"
    exit 1
fi

echo ""
echo "=== Patch 0105 Complete ==="
echo "Default model is now: qwen3:30b-a3b (thinking)"
echo "Use /model in Telegram to verify"
echo "Use /model thinking | auto | fast | deep to switch"
