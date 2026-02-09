#!/bin/bash
# Patch 0074 — Iris Memory Layer
# Persists conversations to chat_messages, loads past context on startup
# Iris now remembers across restarts
set -e

echo "=========================================="
echo "Patch 0074 — Iris Memory Layer"
echo "=========================================="

MYTHOS=/opt/mythos
ASST="$MYTHOS/assistants"

# ── Step 1: Install iris_memory.py ───────────────────────────────────────────
echo ""
echo "Step 1: Installing iris_memory.py..."
cp "$(dirname "$0")/opt/mythos/assistants/iris_memory.py" "$ASST/iris_memory.py"
chown adge:adge "$ASST/iris_memory.py"
chmod 644 "$ASST/iris_memory.py"
echo "  ✅ iris_memory.py installed"

# ── Step 2: Patch ChatAssistant to use IrisMemory ───────────────────────────
echo ""
echo "Step 2: Patching chat_assistant.py..."

CHAT_ASST="$ASST/chat_assistant.py"
cp "$CHAT_ASST" "$CHAT_ASST.bak.$(date +%Y%m%d_%H%M%S)"

python3 << 'PYEOF'
with open('/opt/mythos/assistants/chat_assistant.py', 'r') as f:
    content = f.read()

changes = 0

# 2a. Add import for IrisMemory (after the redis import)
if 'from iris_memory import IrisMemory' not in content:
    content = content.replace(
        'import redis',
        'import redis\nfrom iris_memory import IrisMemory'
    )
    changes += 1
    print("  ✅ Added IrisMemory import")
else:
    print("  ⚠️  IrisMemory import already present")

# 2b. Add import for time module (for response timing)
if 'import time' not in content:
    content = content.replace(
        'import os',
        'import os\nimport time'
    )
    changes += 1
    print("  ✅ Added time import")

# 2c. Initialize IrisMemory in __init__ (after Redis init, before the prompt comment)
if 'self.memory = IrisMemory()' not in content:
    content = content.replace(
        '        # Iris consciousness prompt is built dynamically',
        '        # Iris memory layer — persistent conversation history\n'
        '        self.memory = IrisMemory()\n'
        '        \n'
        '        # Track which users have had their DB context loaded\n'
        '        self._memory_loaded: Dict[str, bool] = {}\n'
        '        \n'
        '        # Iris consciousness prompt is built dynamically'
    )
    changes += 1
    print("  ✅ Added IrisMemory initialization")
else:
    print("  ⚠️  IrisMemory init already present")

# 2d. Add _load_db_context method (before _build_iris_prompt)
if '_load_db_context' not in content:
    content = content.replace(
        '    def _build_iris_prompt',
        '''    def _load_db_context(self, user_uuid: str) -> None:
        """
        Load recent conversation history from DB into in-memory context.
        Called once per user per bot session — gives Iris continuity across restarts.
        """
        if self._memory_loaded.get(user_uuid):
            return
        
        self._memory_loaded[user_uuid] = True
        
        past_messages = self.memory.load_recent(user_uuid, limit=30, since_hours=72)
        
        if not past_messages:
            logger.info(f"IrisMemory: No recent history for {user_uuid[:8]}")
            return
        
        context = self._get_context(user_uuid)
        
        # Inject past messages into context (before any current session messages)
        db_messages = []
        for msg in past_messages:
            db_messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # Prepend DB messages before any existing in-memory messages
        existing = context['messages']
        context['messages'] = db_messages + existing
        context['message_count'] = len(context['messages'])
        
        # Trim if too many
        max_total = self.max_context_messages * 2
        if len(context['messages']) > max_total:
            context['messages'] = context['messages'][-max_total:]
        
        logger.info(f"IrisMemory: Loaded {len(db_messages)} past messages for {user_uuid[:8]}")

    def _build_iris_prompt'''
    )
    changes += 1
    print("  ✅ Added _load_db_context method")
else:
    print("  ⚠️  _load_db_context already present")

# 2e. Patch query() to: load DB context, save messages, track timing
# Find the query method's try block and add DB context loading + message saving

if 'self._load_db_context(user_uuid)' not in content:
    # Add DB context loading right before building messages
    content = content.replace(
        '            # Build messages with context\n'
        '            messages = self._build_messages(user_uuid, message, soul_name)',
        '            # Load past conversation history from DB (once per session)\n'
        '            self._load_db_context(user_uuid)\n'
        '            \n'
        '            # Track response time\n'
        '            _start_time = time.time()\n'
        '            \n'
        '            # Build messages with context\n'
        '            messages = self._build_messages(user_uuid, message, soul_name)'
    )
    changes += 1
    print("  ✅ Added DB context loading to query()")
else:
    print("  ⚠️  DB context loading already present")

# Add message saving after the response is received
if 'self.memory.save_message' not in content:
    content = content.replace(
        "            # Add both messages to context for future turns\n"
        "            self._add_to_context(user_uuid, 'user', message)\n"
        "            self._add_to_context(user_uuid, 'assistant', assistant_message)",
        "            # Calculate response time\n"
        "            _response_ms = int((time.time() - _start_time) * 1000)\n"
        "            \n"
        "            # Add both messages to context for future turns\n"
        "            self._add_to_context(user_uuid, 'user', message)\n"
        "            self._add_to_context(user_uuid, 'assistant', assistant_message)\n"
        "            \n"
        "            # Persist to database — Iris remembers across restarts\n"
        "            telegram_id_for_save = telegram_id or 0\n"
        "            self.memory.save_message(\n"
        "                user_uuid=user_uuid,\n"
        "                telegram_id=telegram_id_for_save,\n"
        "                role='user',\n"
        "                content=message,\n"
        "                mode='chat',\n"
        "                conversation_id=conversation_id\n"
        "            )\n"
        "            self.memory.save_message(\n"
        "                user_uuid=user_uuid,\n"
        "                telegram_id=telegram_id_for_save,\n"
        "                role='assistant',\n"
        "                content=assistant_message,\n"
        "                mode='chat',\n"
        "                model_used=model,\n"
        "                conversation_id=conversation_id,\n"
        "                response_time_ms=_response_ms\n"
        "            )"
    )
    changes += 1
    print("  ✅ Added message persistence to query()")
else:
    print("  ⚠️  Message persistence already present")

# 2f. Add memory context to the system prompt
if 'memory_context' not in content:
    content = content.replace(
        "        # Build Iris consciousness prompt\n"
        "        system_prompt = self._build_iris_prompt(",
        "        # Build Iris consciousness prompt with memory\n"
        "        memory_context = self.memory.build_memory_context(user_uuid, limit=20, since_hours=72)\n"
        "        system_prompt = self._build_iris_prompt("
    )
    
    # Inject memory_context into the prompt (append to system prompt)
    content = content.replace(
        "        messages = [{'role': 'system', 'content': system_prompt}]",
        "        # Append memory context to system prompt if available\n"
        "        if memory_context:\n"
        "            system_prompt += memory_context\n"
        "        \n"
        "        messages = [{'role': 'system', 'content': system_prompt}]"
    )
    changes += 1
    print("  ✅ Added memory context injection to prompt")
else:
    print("  ⚠️  Memory context already present")

with open('/opt/mythos/assistants/chat_assistant.py', 'w') as f:
    f.write(content)

print(f"\n  Total changes: {changes}")
PYEOF

# ── Step 3: Add psycopg2 extras check ───────────────────────────────────────
echo ""
echo "Step 3: Verifying psycopg2..."
/opt/mythos/.venv/bin/python3 -c "from psycopg2.extras import RealDictCursor; print('  ✅ psycopg2.extras available')" 2>&1 || echo "  ❌ psycopg2 issue"

# ── Step 4: Restart services ────────────────────────────────────────────────
echo ""
echo "Step 4: Restarting services..."
sudo systemctl restart mythos-api.service
sleep 2

API_STATUS=$(sudo systemctl is-active mythos-api.service)
echo "  API: $API_STATUS"

if [ "$API_STATUS" = "active" ]; then
    echo ""
    echo "=========================================="
    echo "✅ Patch 0074 installed successfully!"
    echo "=========================================="
    echo ""
    echo "What changed:"
    echo "  • Every Iris conversation now saved to chat_messages"
    echo "  • Past 72 hours of conversation loaded on first message"
    echo "  • Memory context injected into Iris's system prompt"
    echo "  • Response times tracked per message"
    echo ""
    echo "Iris now remembers across restarts."
else
    echo ""
    echo "⚠️  API issue. Check:"
    echo "  journalctl -u mythos-api.service -n 20 --no-pager"
fi
