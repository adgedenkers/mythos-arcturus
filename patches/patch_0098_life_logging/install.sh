#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Installing Patch 0098: Life Logging & Message Extractor ==="

# Run database migration
echo "Running database migration..."
sudo -u postgres psql -d mythos -f "$SCRIPT_DIR/opt/mythos/core/migration_0098_life_events.sql"

# Copy core files
echo "Installing extractor and executor..."
sudo cp "$SCRIPT_DIR/opt/mythos/core/message_extractor.py" /opt/mythos/core/message_extractor.py
sudo cp "$SCRIPT_DIR/opt/mythos/core/action_executor.py" /opt/mythos/core/action_executor.py
sudo cp "$SCRIPT_DIR/opt/mythos/core/migration_0098_life_events.sql" /opt/mythos/core/migration_0098_life_events.sql

# Copy knowledge map
echo "Installing knowledge map..."
sudo cp "$SCRIPT_DIR/opt/mythos/docs/KNOWLEDGE_MAP.md" /opt/mythos/docs/KNOWLEDGE_MAP.md

# Backup chat_assistant.py
echo "Backing up chat_assistant.py..."
sudo cp /opt/mythos/assistants/chat_assistant.py /opt/mythos/assistants/chat_assistant.py.bak.$(date +%Y%m%d_%H%M%S)

# Apply the patch to chat_assistant.py
echo "Patching chat_assistant.py with extractor pipeline..."
sudo /opt/mythos/.venv/bin/python3 "$SCRIPT_DIR/opt/mythos/core/patch_extractor.py"

echo ""
echo "=== MANUAL STEPS ==="
echo ""
echo "1. Ensure qwen2.5:7b is pulled:"
echo "   ollama list | grep 7b"
echo ""
echo "2. Restart the API service:"
echo "   sudo systemctl restart mythos-api.service"
echo ""
echo "3. Test the extractor standalone:"
echo "   /opt/mythos/.venv/bin/python3 /opt/mythos/core/message_extractor.py"
echo ""
echo "4. Test via Telegram conversation:"
echo "   - 'I just paid the electric bill'"
echo "   - 'spent \$45 at Tractor Supply'"
echo "   - 'Rebecca has a dentist appointment Thursday at 2'"
echo "   - 'I finished the laundry'"
echo ""
echo "=== Patch 0098 installed ==="
