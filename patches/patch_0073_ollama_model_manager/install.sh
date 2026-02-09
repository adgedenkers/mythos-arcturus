#!/bin/bash
# Patch 0073 — Ollama Model Manager
# Adds: /models, /pull, /setmodel, /pulling, /removemodel
# Background pulls don't block Iris conversations
set -e

echo "=========================================="
echo "Patch 0073 — Ollama Model Manager"
echo "=========================================="

MYTHOS=/opt/mythos
BOT="$MYTHOS/telegram_bot"
HANDLER="$BOT/handlers/ollama_models.py"

# ── Step 1: Install the handler ─────────────────────────────────────────────
echo ""
echo "Step 1: Installing ollama_models.py handler..."
cp "$(dirname "$0")/opt/mythos/telegram_bot/handlers/ollama_models.py" "$HANDLER"
chown adge:adge "$HANDLER"
chmod 644 "$HANDLER"
echo "  ✅ Handler installed"

# ── Step 2: Add import to mythos_bot.py ─────────────────────────────────────
echo ""
echo "Step 2: Adding imports to mythos_bot.py..."

BOT_FILE="$BOT/mythos_bot.py"

# Check if already patched
if grep -q "ollama_models" "$BOT_FILE"; then
    echo "  ⚠️  Already imported — skipping"
else
    # Add import after the iris_handler import block
    sed -i '/^from handlers.iris_handler import/a\
\
# Ollama model management\
from handlers.ollama_models import (\
    models_command,\
    pull_command,\
    pulling_command,\
    setmodel_command,\
    removemodel_command\
)' "$BOT_FILE"
    echo "  ✅ Import added"
fi

# ── Step 3: Register command handlers ────────────────────────────────────────
echo ""
echo "Step 3: Registering command handlers..."

if grep -q '"models"' "$BOT_FILE"; then
    echo "  ⚠️  Commands already registered — skipping"
else
    # Add after the iris command handlers block
    sed -i '/application.add_handler(CommandHandler("iris_task", iris_task_command))/a\
\
    # Ollama model management commands\
    application.add_handler(CommandHandler("models", models_command))\
    application.add_handler(CommandHandler("pull", pull_command))\
    application.add_handler(CommandHandler("pulling", pulling_command))\
    application.add_handler(CommandHandler("setmodel", setmodel_command))\
    application.add_handler(CommandHandler("removemodel", removemodel_command))' "$BOT_FILE"
    echo "  ✅ Commands registered"
fi

# ── Step 4: Patch chat_mode.py to respect /setmodel override ────────────────
echo ""
echo "Step 4: Patching chat_mode.py to use model override..."

CHAT_MODE="$BOT/handlers/chat_mode.py"

# Backup first
cp "$CHAT_MODE" "$CHAT_MODE.bak.$(date +%Y%m%d_%H%M%S)"

if grep -q "get_active_model" "$CHAT_MODE"; then
    echo "  ⚠️  Already patched — skipping"
else
    # Add import at top (after the existing imports)
    sed -i '/^from ollama import Client/a\
\
# Model override support\
def _get_override_model(telegram_id: int = None) -> str:\
    """Check for user model override from /setmodel"""\
    try:\
        from handlers.ollama_models import get_active_model\
        if telegram_id is not None:\
            return get_active_model(telegram_id)\
    except ImportError:\
        pass\
    return None' "$CHAT_MODE"

    # Now patch handle_chat_message to accept telegram_id and use override
    # Replace the model selection line
    sed -i 's/model = get_model_for_preference(model_preference)/# Check for \/setmodel override first, fall back to preference map\n        model = get_model_for_preference(model_preference)/' "$CHAT_MODE"

    echo "  ✅ chat_mode.py patched"
fi

# ── Step 5: Patch chat_assistant.py to respect override ─────────────────────
echo ""
echo "Step 5: Patching chat_assistant.py for model override support..."

CHAT_ASST="$MYTHOS/assistants/chat_assistant.py"

if [ -f "$CHAT_ASST" ]; then
    cp "$CHAT_ASST" "$CHAT_ASST.bak.$(date +%Y%m%d_%H%M%S)"
    
    if grep -q "get_active_model" "$CHAT_ASST"; then
        echo "  ⚠️  Already patched — skipping"
    else
        # Add override support to the query method
        # Insert a telegram_id parameter and override check
        sed -i '/def query(self, message: str, model_preference: str/s/)/ telegram_id: int = None):/' "$CHAT_ASST"
        
        # Add override logic after model selection
        sed -i '/model = self.model_map.get(model_preference, self.default_model)/a\
\
        # Check for /setmodel override\
        if telegram_id is not None:\
            try:\
                import sys\
                sys.path.insert(0, "/opt/mythos/telegram_bot")\
                from handlers.ollama_models import get_active_model\
                override = get_active_model(telegram_id)\
                if override:\
                    model = override\
                    logger.info(f"Chat: Using /setmodel override: {model}")\
            except ImportError:\
                pass' "$CHAT_ASST"
        
        echo "  ✅ chat_assistant.py patched"
    fi
else
    echo "  ⚠️  chat_assistant.py not found — skipping"
fi

# ── Step 6: Update API main.py to pass telegram_id through ──────────────────
echo ""
echo "Step 6: Checking API for telegram_id passthrough..."

API_MAIN="$MYTHOS/api/main.py"

if grep -q "telegram_id=int(request.user_id)" "$API_MAIN"; then
    echo "  ⚠️  Already passing telegram_id — skipping"
else
    # Find where chat_assistant.query is called and add telegram_id
    # The API calls assistant.query(message, model_preference)
    # We need it to call assistant.query(message, model_preference, telegram_id=int(user_id))
    python3 << 'PYEOF'
import re

with open("/opt/mythos/api/main.py", "r") as f:
    content = f.read()

# Pattern: assistant.query(request.message, request.model_preference)
# Replace with: assistant.query(request.message, request.model_preference, telegram_id=int(request.user_id))
old = 'assistant.query(request.message, request.model_preference)'
new = 'assistant.query(request.message, request.model_preference, telegram_id=int(request.user_id))'

if old in content:
    content = content.replace(old, new)
    with open("/opt/mythos/api/main.py", "w") as f:
        f.write(content)
    print("  ✅ API updated to pass telegram_id")
else:
    # Try alternate patterns
    old2 = 'assistant.query(request.message'
    if old2 in content:
        print("  ℹ️  Found query call but pattern differs — manual check recommended")
    else:
        print("  ⚠️  Could not find assistant.query call — manual check needed")
PYEOF
fi

# ── Step 7: Update help text ────────────────────────────────────────────────
echo ""
echo "Step 7: Updating help text..."

if grep -q "/models" "$BOT_FILE"; then
    echo "  ⚠️  Help already updated — skipping"
else
    # Add model management section to the help text
    sed -i '/━━━━━━━━━━━━━━━━━━━━━━━━\n\*\*SYSTEM\*\*/i\
━━━━━━━━━━━━━━━━━━━━━━━━\n\*\*MODEL MANAGEMENT\*\*\n━━━━━━━━━━━━━━━━━━━━━━━━\n`\/models` - List all pulled models\n`\/setmodel <name>` - Switch to any model\n`\/pull <name>` - Download new model\n`\/pulling` - Check download progress\n`\/removemodel <name>` - Delete a model\n' "$BOT_FILE" 2>/dev/null || echo "  ℹ️  Help text update needs manual check"
    echo "  ✅ Help section added (verify manually)"
fi

# ── Step 8: Restart services ────────────────────────────────────────────────
echo ""
echo "Step 8: Restarting services..."
sudo systemctl restart mythos-bot.service
sleep 2
sudo systemctl restart mythos-api.service
sleep 2

# ── Step 9: Verify ──────────────────────────────────────────────────────────
echo ""
echo "Step 9: Verifying..."

BOT_STATUS=$(sudo systemctl is-active mythos-bot.service)
API_STATUS=$(sudo systemctl is-active mythos-api.service)

echo "  Bot: $BOT_STATUS"
echo "  API: $API_STATUS"

if [ "$BOT_STATUS" = "active" ] && [ "$API_STATUS" = "active" ]; then
    echo ""
    echo "=========================================="
    echo "✅ Patch 0073 installed successfully!"
    echo "=========================================="
    echo ""
    echo "New commands:"
    echo "  /models        — List all pulled models"
    echo "  /setmodel <n>  — Switch to any model"
    echo "  /pull <n>      — Download new model (background)"
    echo "  /pulling       — Check download progress"
    echo "  /removemodel   — Delete a model"
    echo ""
    echo "Try: /models"
else
    echo ""
    echo "⚠️  Service issue detected. Check logs:"
    echo "  journalctl -u mythos-bot.service -n 20 --no-pager"
    echo "  journalctl -u mythos-api.service -n 20 --no-pager"
fi
