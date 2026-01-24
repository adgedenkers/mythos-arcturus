#!/bin/bash
# ============================================================
# PATCH 0012: Telegram Commands + Auto-Execute Install
# ============================================================
# This patch:
# 1. Wires up /patch commands in the Telegram bot
# 2. Adds auto-execute of install.sh after patch extraction
# ============================================================

set -e

MYTHOS_ROOT="/opt/mythos"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[PATCH]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

log "Installing patch 0012: Telegram Commands + Auto-Execute"

# ============================================================
# 1. Update mythos_bot.py - add patch handler imports
# ============================================================

BOT_FILE="$MYTHOS_ROOT/telegram_bot/mythos_bot.py"

# Check if patch handlers already imported
if grep -q "patch_command" "$BOT_FILE"; then
    log "Patch handlers already imported in bot"
else
    log "Adding patch handler imports..."
    
    # Find the line with "from handlers import" and add patch imports after the closing paren
    # We'll add a new import block after the existing one
    
    # First, backup
    cp "$BOT_FILE" "$BOT_FILE.bak.$TIMESTAMP"
    
    # Add import after the existing handlers import block
    sed -i '/^from handlers import/,/)/ {
        /)/ a\
\
# Patch management handlers\
from handlers.patch_handlers import (\
    patch_command,\
    patch_status_command,\
    patch_list_command,\
    patch_apply_command,\
    patch_rollback_command,\
    patch_rollback_confirm_command\
)
    }' "$BOT_FILE"
    
    log "✓ Added patch handler imports"
fi

# ============================================================
# 2. Update mythos_bot.py - register command handlers
# ============================================================

if grep -q 'CommandHandler("patch"' "$BOT_FILE"; then
    log "Patch command handlers already registered"
else
    log "Registering patch command handlers..."
    
    # Find the last add_handler line and add our handlers after it
    # Looking for the pattern of existing handlers
    
    # Add after the "sold" handler (last command handler before message handlers)
    sed -i '/application.add_handler(CommandHandler("sold"/a\
    \
    # Patch management commands\
    application.add_handler(CommandHandler("patch", patch_command))\
    application.add_handler(CommandHandler("patch_status", patch_status_command))\
    application.add_handler(CommandHandler("patch_list", patch_list_command))\
    application.add_handler(CommandHandler("patch_apply", patch_apply_command))\
    application.add_handler(CommandHandler("patch_rollback", patch_rollback_command))\
    application.add_handler(CommandHandler("patch_rollback_confirm", patch_rollback_confirm_command))' "$BOT_FILE"
    
    log "✓ Registered patch command handlers"
fi

# ============================================================
# 3. Update mythos_patch_monitor.py - add auto-execute
# ============================================================

MONITOR_FILE="$MYTHOS_ROOT/mythos_patch_monitor.py"

if grep -q "AUTO_EXECUTE_INSTALL" "$MONITOR_FILE"; then
    log "Auto-execute already configured in monitor"
else
    log "Adding auto-execute capability to monitor..."
    
    cp "$MONITOR_FILE" "$MONITOR_FILE.bak.$TIMESTAMP"
    
    # Add config flag after GITHUB_PUSH_ENABLED
    sed -i '/^GITHUB_PUSH_ENABLED = True/a\
\
# Auto-execute install.sh after extraction\
AUTO_EXECUTE_INSTALL = True' "$MONITOR_FILE"
    
    log "✓ Added AUTO_EXECUTE_INSTALL flag"
fi

# Now add the auto-execute logic in the process_patch method
# We need to add it after the extraction and before the git commit

if grep -q "Running install.sh" "$MONITOR_FILE"; then
    log "Auto-execute logic already present"
else
    log "Adding auto-execute logic..."
    
    # Find the line with "✓ Patch extracted" and add auto-execute after it
    sed -i '/logger.info(f"✓ Patch processed: {name}")$/i\
\
            # ---- AUTO-EXECUTE install.sh if present ----\
            if AUTO_EXECUTE_INSTALL and extract_dir:\
                install_script = extract_dir / "install.sh"\
                if install_script.exists():\
                    logger.info(f"Running install.sh from {extract_dir}")\
                    try:\
                        # Make executable\
                        install_script.chmod(0o755)\
                        # Run it\
                        result = subprocess.run(\
                            [str(install_script)],\
                            cwd=str(extract_dir),\
                            capture_output=True,\
                            text=True,\
                            timeout=300\
                        )\
                        if result.returncode == 0:\
                            logger.info(f"✓ install.sh completed successfully")\
                        else:\
                            logger.error(f"install.sh failed: {result.stderr}")\
                    except subprocess.TimeoutExpired:\
                        logger.error("install.sh timed out (5 min limit)")\
                    except Exception as e:\
                        logger.error(f"install.sh error: {e}")\
' "$MONITOR_FILE"
    
    log "✓ Added auto-execute logic"
fi

# ============================================================
# 4. Restart services
# ============================================================

log "Restarting services..."

sudo systemctl restart mythos-patch-monitor
log "✓ Restarted mythos-patch-monitor"

# Check if telegram bot is a service
if systemctl list-units --type=service | grep -q "mythos.*bot"; then
    sudo systemctl restart mythos-telegram-bot 2>/dev/null || true
    log "✓ Restarted telegram bot service"
else
    warn "Telegram bot not running as service - restart manually if needed"
    echo "  Kill existing: pkill -f mythos_bot.py"
    echo "  Start fresh:   cd /opt/mythos/telegram_bot && python mythos_bot.py &"
fi

# ============================================================
# Done
# ============================================================

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  Patch 0012 Installed${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "New Telegram commands:"
echo "  /patch                - Overview and help"
echo "  /patch_status         - Current version and activity"
echo "  /patch_list           - Available patches"
echo "  /patch_apply <name>   - Apply a patch"
echo "  /patch_rollback       - Show rollback options"
echo ""
echo "Auto-execute: Enabled"
echo "  - install.sh will now run automatically after extraction"
echo "  - To disable: set AUTO_EXECUTE_INSTALL = False in monitor"
echo ""
echo "Restart your Telegram bot to activate commands:"
echo "  pkill -f mythos_bot.py"
echo "  cd /opt/mythos/telegram_bot && nohup python mythos_bot.py > /dev/null 2>&1 &"
echo ""
