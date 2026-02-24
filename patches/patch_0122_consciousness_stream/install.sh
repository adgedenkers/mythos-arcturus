#!/bin/bash
set -e

# ═══════════════════════════════════════════════════════════════════════════════
# Patch 0122: Consciousness Stream — Conversation Awareness Layer
# ═══════════════════════════════════════════════════════════════════════════════

MYTHOS="/opt/mythos"
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="/tmp/patch_0122_install.log"

echo "═══════════════════════════════════════════════════════" | tee "$LOG"
echo "Patch 0122: Consciousness Stream"                        | tee -a "$LOG"
echo "═══════════════════════════════════════════════════════" | tee -a "$LOG"

# ── 1. Run SQL Migration ────────────────────────────────────────────────────
echo "[1/7] Running SQL migration..." | tee -a "$LOG"
sudo -u postgres psql -d mythos -f "$PATCH_DIR/opt/mythos/migrations/migration_0122_consciousness_stream.sql" 2>&1 | tee -a "$LOG"
echo "  ✓ Tables created" | tee -a "$LOG"

# ── 2. Deploy new files ────────────────────────────────────────────────────
echo "[2/7] Deploying new files..." | tee -a "$LOG"

# Core modules
cp "$PATCH_DIR/opt/mythos/core/subject_tracker.py" "$MYTHOS/core/subject_tracker.py"
cp "$PATCH_DIR/opt/mythos/core/segment_manager.py" "$MYTHOS/core/segment_manager.py"
cp "$PATCH_DIR/opt/mythos/core/chat_mode_patch_0122.py" "$MYTHOS/core/chat_mode_patch_0122.py"
chmod +x "$MYTHOS/core/segment_manager.py"

# Worker
cp "$PATCH_DIR/opt/mythos/workers/subject_worker.py" "$MYTHOS/workers/subject_worker.py"

# Migration file (for reference)
mkdir -p "$MYTHOS/migrations"
cp "$PATCH_DIR/opt/mythos/migrations/migration_0122_consciousness_stream.sql" "$MYTHOS/migrations/"

echo "  ✓ Files deployed" | tee -a "$LOG"

# ── 3. Backup existing files ──────────────────────────────────────────────
echo "[3/7] Backing up files to patch..." | tee -a "$LOG"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

cp "$MYTHOS/telegram_bot/handlers/chat_mode.py" \
   "$MYTHOS/telegram_bot/handlers/chat_mode.py.bak.${TIMESTAMP}"

cp "$MYTHOS/core/prompt_assembler.py" \
   "$MYTHOS/core/prompt_assembler.py.bak.${TIMESTAMP}"

echo "  ✓ Backups created" | tee -a "$LOG"

# ── 4. Patch chat_mode.py ─────────────────────────────────────────────────
echo "[4/7] Patching chat_mode.py..." | tee -a "$LOG"
CHAT_MODE="$MYTHOS/telegram_bot/handlers/chat_mode.py"

# 4a. Add imports after existing imports (after the skills_context import block)
if ! grep -q "subject_tracker" "$CHAT_MODE"; then
    # Insert after the life_context import block
    sed -i '/^try:$/,/def build_life_context/{ 
        /def build_life_context/a\
\
# Consciousness Stream — subject tracking (Patch 0122)\
try:\
    from subject_tracker import process_message as track_subject, build_conversation_awareness\
    _subject_tracking_available = True\
except ImportError as e:\
    logger.warning(f"Subject tracking not available: {e}")\
    _subject_tracking_available = False\
    def track_subject(*args, **kwargs): return {}\
    def build_conversation_awareness(*args, **kwargs): return ""\
\
# Redis for async enrichment queue (Patch 0122)\
try:\
    import redis as _redis_mod\
    _redis_client = _redis_mod.Redis.from_url("redis://localhost:6379")\
except Exception:\
    _redis_client = None
    }' "$CHAT_MODE"
    echo "  ✓ Imports added" | tee -a "$LOG"
else
    echo "  ⊘ Imports already present" | tee -a "$LOG"
fi

# 4b. Add user subject tracking into handle_chat_message
# Insert after the perception_id logging block, before build_messages_for_ollama
if ! grep -q "Consciousness Stream: Track user" "$CHAT_MODE"; then
    sed -i '/# Build messages with Iris.*personality via unified assembler/i\
        # ── Consciousness Stream: Track user message subject (Patch 0122) ──\
        user_subject_result = {}\
        if _subject_tracking_available:\
            try:\
                _time_gap = None\
                _last_ts = _get_last_message_timestamp(get_chat_context(session))\
                if _last_ts and message_timestamp:\
                    _time_gap = (message_timestamp - _last_ts).total_seconds()\
                user_subject_result = track_subject(\
                    chat_id=session.get("chat_id", 0),\
                    telegram_id=user_info.get("telegram_id", 0),\
                    message=user_message,\
                    role="user",\
                    perception_id=perception_id,\
                    time_gap_seconds=_time_gap,\
                )\
                logger.debug(f"Subject tracked: {user_subject_result.get('"'"'segment_action'"'"', '"'"'?'"'"')} "\
                           f"segment={str(user_subject_result.get('"'"'segment_id'"'"', '"'"''"'"'))[:8]}")\
            except Exception as _e:\
                logger.warning(f"Subject tracking failed (non-fatal): {_e}")\
' "$CHAT_MODE"
    echo "  ✓ User subject tracking added" | tee -a "$LOG"
else
    echo "  ⊘ User tracking already present" | tee -a "$LOG"
fi

# 4c. Add assistant subject tracking after iris_response is obtained
if ! grep -q "Consciousness Stream: Track assistant" "$CHAT_MODE"; then
    sed -i '/# Log Iris.*response to perception_log/i\
        # ── Consciousness Stream: Track assistant response (Patch 0122) ──\
        if _subject_tracking_available:\
            try:\
                track_subject(\
                    chat_id=session.get("chat_id", 0),\
                    telegram_id=0,\
                    message=iris_response,\
                    role="assistant",\
                    perception_id=None,\
                )\
            except Exception as _e:\
                logger.warning(f"Assistant subject tracking failed (non-fatal): {_e}")\
' "$CHAT_MODE"
    echo "  ✓ Assistant subject tracking added" | tee -a "$LOG"
else
    echo "  ⊘ Assistant tracking already present" | tee -a "$LOG"
fi

# 4d. Ensure chat_id is stored in session (needed by subject tracker)
# Add to the message handler in mythos_bot.py if not present
BOT_MAIN="$MYTHOS/telegram_bot/mythos_bot.py"
if ! grep -q "chat_id.*effective_chat" "$BOT_MAIN"; then
    echo "  ℹ Note: chat_id may need to be added to session in mythos_bot.py message handler" | tee -a "$LOG"
    echo "    Add: context.user_data['chat_id'] = update.effective_chat.id" | tee -a "$LOG"
fi

echo "  ✓ chat_mode.py patched" | tee -a "$LOG"

# ── 5. Patch prompt_assembler.py ──────────────────────────────────────────
echo "[5/7] Patching prompt_assembler.py..." | tee -a "$LOG"
ASSEMBLER="$MYTHOS/core/prompt_assembler.py"

# 5a. Add import for conversation awareness
if ! grep -q "subject_tracker" "$ASSEMBLER"; then
    sed -i '/^logger = logging.getLogger/a\
\
# Consciousness Stream (Patch 0122)\
try:\
    from subject_tracker import build_conversation_awareness as _build_convo_awareness\
    _convo_awareness_available = True\
except ImportError:\
    _convo_awareness_available = False\
    def _build_convo_awareness(*args, **kwargs): return ""' "$ASSEMBLER"
    echo "  ✓ Import added to prompt_assembler" | tee -a "$LOG"
fi

# 5b. Add chat_id parameter to assemble_system_prompt
if ! grep -q "chat_id:" "$ASSEMBLER"; then
    sed -i 's/def assemble_system_prompt(/def assemble_system_prompt(\n    chat_id: int = 0,/' "$ASSEMBLER"
    echo "  ✓ chat_id parameter added" | tee -a "$LOG"
fi

# 5c. Add conversation awareness to the assembly
if ! grep -q "conversation_awareness" "$ASSEMBLER"; then
    # Add it to the parts dict
    sed -i "s/'web_results': web_ctx,/'web_results': web_ctx,\n        'conversation_awareness': _build_convo_awareness(chat_id) if _convo_awareness_available and chat_id else '',/" "$ASSEMBLER"
    
    # Add it to the final assembly (before life context)
    sed -i '/# Life context/i\
    # Conversation awareness (Patch 0122)\
    if parts.get("conversation_awareness"):\
        sections.append(parts["conversation_awareness"])' "$ASSEMBLER"
    
    echo "  ✓ Conversation awareness integrated into prompt assembly" | tee -a "$LOG"
fi

# 5d. Pass chat_id from chat_mode to prompt assembler
if ! grep -q "chat_id=.*session" "$CHAT_MODE" | grep -q "assemble_system_prompt"; then
    # Update the assemble_system_prompt call in chat_mode.py to pass chat_id
    sed -i 's/system_prompt = assemble_system_prompt(/system_prompt = assemble_system_prompt(\n        chat_id=session.get("chat_id", 0),/' "$CHAT_MODE"
    echo "  ✓ chat_id passed to prompt assembler" | tee -a "$LOG"
fi

echo "  ✓ prompt_assembler.py patched" | tee -a "$LOG"

# ── 6. Register subject worker ───────────────────────────────────────────
echo "[6/7] Registering subject worker..." | tee -a "$LOG"

# Add to workers/__init__.py
WORKERS_INIT="$MYTHOS/workers/__init__.py"
if ! grep -q "subject_worker" "$WORKERS_INIT"; then
    sed -i '/from .summary_worker import process_summary/a\
from .subject_worker import process_subject' "$WORKERS_INIT"
    
    sed -i 's/"process_summary"/"process_summary",\n    "process_subject"/' "$WORKERS_INIT"
    echo "  ✓ Worker registered in __init__.py" | tee -a "$LOG"
fi

# Add to worker.py's module mapping (if the pattern exists)
WORKER_PY="$MYTHOS/workers/worker.py"
if grep -q "WORKER_MODULES" "$WORKER_PY" || grep -q "worker_map" "$WORKER_PY"; then
    if ! grep -q "'subject'" "$WORKER_PY"; then
        # Try to add to whatever mapping dict exists
        sed -i "/'summary'/a\\    'subject': 'subject_worker'," "$WORKER_PY" 2>/dev/null || true
        echo "  ✓ Subject worker added to worker.py mapping" | tee -a "$LOG"
    fi
fi

# Install systemd services
sudo cp "$PATCH_DIR/etc/systemd/system/mythos-segment-manager.service" /etc/systemd/system/
sudo cp "$PATCH_DIR/etc/systemd/system/mythos-worker-subject.service" /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable mythos-segment-manager.service
sudo systemctl enable mythos-worker-subject.service

echo "  ✓ Systemd services installed" | tee -a "$LOG"

# ── 7. Restart services ──────────────────────────────────────────────────
echo "[7/7] Restarting services..." | tee -a "$LOG"

sudo systemctl restart mythos-bot.service
sudo systemctl start mythos-segment-manager.service
sudo systemctl start mythos-worker-subject.service

# Quick health check
sleep 3
echo "" | tee -a "$LOG"
echo "Service status:" | tee -a "$LOG"
systemctl is-active mythos-bot.service | tee -a "$LOG"
systemctl is-active mythos-segment-manager.service | tee -a "$LOG"
systemctl is-active mythos-worker-subject.service | tee -a "$LOG"

# Verify tables exist
echo "" | tee -a "$LOG"
echo "Table verification:" | tee -a "$LOG"
sudo -u postgres psql -d mythos -c "SELECT 'conversation_segments' as tbl, count(*) FROM conversation_segments UNION ALL SELECT 'conversation_subject_points', count(*) FROM conversation_subject_points;" 2>&1 | tee -a "$LOG"

echo "" | tee -a "$LOG"
echo "═══════════════════════════════════════════════════════" | tee -a "$LOG"
echo "✓ Patch 0122 installed successfully"                     | tee -a "$LOG"
echo "═══════════════════════════════════════════════════════" | tee -a "$LOG"
echo ""
echo "Next steps:"
echo "  1. Send a test message to Iris via Telegram"
echo "  2. Check: sudo -u postgres psql -d mythos -c 'SELECT * FROM conversation_subject_points ORDER BY created_at DESC LIMIT 5;'"
echo "  3. Check: sudo -u postgres psql -d mythos -c 'SELECT * FROM conversation_segments;'"
echo "  4. Monitor: journalctl -u mythos-bot -f"
echo ""
echo "NOTE: chat_id must be in session. If subject tracking shows chat_id=0,"
echo "add this line to your message handler in mythos_bot.py:"
echo "  context.user_data['chat_id'] = update.effective_chat.id"
