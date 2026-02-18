#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Installing Patch 0097: Iris Life Awareness ==="

# Copy life context builder
echo "Installing life_context.py..."
sudo cp "$SCRIPT_DIR/opt/mythos/core/life_context.py" /opt/mythos/core/life_context.py

# Backup chat_assistant.py
echo "Backing up chat_assistant.py..."
sudo cp /opt/mythos/assistants/chat_assistant.py /opt/mythos/assistants/chat_assistant.py.bak.$(date +%Y%m%d_%H%M%S)

# Apply the patch to chat_assistant.py
echo "Patching chat_assistant.py..."
sudo /opt/mythos/.venv/bin/python3 "$SCRIPT_DIR/opt/mythos/core/patch_chat_assistant.py"

# Test life context builder
echo "Testing life context builder..."
/opt/mythos/.venv/bin/python3 /opt/mythos/core/life_context.py
echo ""

echo "=== MANUAL STEPS ==="
echo ""
echo "1. Restart the bot:"
echo "   sudo systemctl restart mythos-bot.service"
echo ""
echo "2. Test by talking to Iris normally:"
echo "   - 'Hey Iris, what do I have going on today?'"
echo "   - 'What should I be doing right now?'"
echo "   - 'Have I done my routines?'"
echo ""
echo "She should now know your routines, tasks, bills, balances,"
echo "and calendar without you running /checkin first."
echo ""
echo "=== Patch 0097 installed ==="
