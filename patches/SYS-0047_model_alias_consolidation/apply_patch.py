import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=47,
    description='Consolidate model aliases into core/model_aliases.py',
    patch_type='MINOR',
)
patch.begin()

# 1. Deploy the canonical alias file
patch.deploy_file('opt/mythos/core/model_aliases.py', '/opt/mythos/core/model_aliases.py')

# 2. Update ollama_models.py — replace hardcoded MODEL_ALIASES with import
target = '/opt/mythos/telegram_bot/handlers/ollama_models.py'
with open(target, 'r') as f:
    content = f.read()

# Replace the hardcoded alias dict
old_aliases = '''# ── Short aliases for quick model switching ─────────────────────────────────
MODEL_ALIASES = {
    "fast": "qwen3:30b-a3b",
    "a3b": "qwen3:30b-a3b",
    "deep": "qwen3:32b",
    "32b": "qwen3:32b",
    "think": "qwen3:32b",
}'''

new_aliases = '''# ── Short aliases — imported from single source of truth ────────────────────
from core.model_aliases import MODEL_ALIASES'''

if old_aliases in content:
    content = content.replace(old_aliases, new_aliases)
    with open(target, 'w') as f:
        f.write(content)
    print(f"✅ Updated {target} — removed hardcoded aliases")
else:
    print(f"⚠ {target} — alias block not found (may already be updated)")

# Also fix the fallback default in the same file
old_default = 'return os.getenv("OLLAMA_MODEL", "qwen3:30b-a3b")'
new_default = '''from core.model_aliases import DEFAULT_MODEL
    return os.getenv("OLLAMA_MODEL", DEFAULT_MODEL)'''
# Actually, let's just fix the hardcoded string
content_check = open(target, 'r').read()
if 'os.getenv("OLLAMA_MODEL", "qwen3:30b-a3b")' in content_check:
    content_check = content_check.replace(
        'os.getenv("OLLAMA_MODEL", "qwen3:30b-a3b")',
        'os.getenv("OLLAMA_MODEL", "iris-deep:latest")'
    )
    with open(target, 'w') as f:
        f.write(content_check)
    print(f"✅ Updated {target} — fixed default model fallback")

# Also remove the old alias resolution that re-imports from chat_mode
content_check = open(target, 'r').read()
old_resolve = """    # Check if it's one of the old aliases
    if model_name in ("auto", "fast", "deep"):
        from handlers.chat_mode import MODEL_MAP
        resolved = MODEL_MAP.get(model_name, os.getenv("OLLAMA_MODEL", "qwen3:30b-a3b"))"""
new_resolve = """    # Check if it's one of the old aliases
    if model_name in ("auto", "fast", "deep"):
        from core.model_aliases import resolve_alias
        resolved = resolve_alias(model_name)"""
if old_resolve in content_check:
    content_check = content_check.replace(old_resolve, new_resolve)
    with open(target, 'w') as f:
        f.write(content_check)
    print(f"✅ Updated {target} — fixed old alias resolution path")

# 3. Update chat_mode.py — replace hardcoded MODEL_MAP with import
target = '/opt/mythos/telegram_bot/handlers/chat_mode.py'
with open(target, 'r') as f:
    content = f.read()

old_map = """OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen3:30b-a3b')
# Model mapping for /model command
MODEL_MAP = {
    'auto': 'qwen3:30b-a3b',
    'fast': 'qwen3:30b-a3b',
    'deep': 'qwen3:32b',
    'thinking': 'qwen3:32b',
}"""

new_map = """from core.model_aliases import MODEL_ALIASES as MODEL_MAP, DEFAULT_MODEL
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', DEFAULT_MODEL)"""

if old_map in content:
    content = content.replace(old_map, new_map)
    with open(target, 'w') as f:
        f.write(content)
    print(f"✅ Updated {target} — now imports from core.model_aliases")
else:
    print(f"⚠ {target} — MODEL_MAP block not found (may already be updated)")

# 4. Update chat_assistant.py — model_map from import
target = '/opt/mythos/assistants/chat_assistant.py'
with open(target, 'r') as f:
    content = f.read()

old_model_map = """        self.model_map = {
            'auto': self.default_model,
            'fast': 'iris:latest',
            'deep': 'iris-deep:latest',
        }"""

new_model_map = """        from core.model_aliases import MODEL_ALIASES
        self.model_map = MODEL_ALIASES.copy()
        self.model_map['auto'] = self.default_model"""

if old_model_map in content:
    content = content.replace(old_model_map, new_model_map)
    with open(target, 'w') as f:
        f.write(content)
    print(f"✅ Updated {target} — model_map now imports from core.model_aliases")
else:
    print(f"⚠ {target} — model_map block not found (may already be updated)")

# 5. Update mythos_bot.py — model descriptions from import
target = '/opt/mythos/telegram_bot/mythos_bot.py'
with open(target, 'r') as f:
    content = f.read()

old_desc = """            descriptions = {
                "auto": "qwen3:30b-a3b",
                "fast": "qwen3:30b-a3b (~10s)",
                "deep": "qwen3:32b",
                "thinking": "qwen3:30b-a3b (deep reasoning)",
            }"""

new_desc = """            from core.model_aliases import get_model_description
            descriptions = {k: get_model_description(k) for k in ["auto", "fast", "deep", "thinking"]}"""

if old_desc in content:
    content = content.replace(old_desc, new_desc)
    with open(target, 'w') as f:
        f.write(content)
    print(f"✅ Updated {target} — descriptions now from core.model_aliases")
else:
    print(f"⚠ {target} — descriptions block not found (may already be updated)")

# Also fix the valid model check and help display in mythos_bot.py
old_valid = '        if new_model in ["auto", "fast", "deep", "thinking"]:'
new_valid = '        from core.model_aliases import is_known_alias\n        if is_known_alias(new_model):'
if old_valid in content:
    content = open(target, 'r').read()  # re-read after prior edit
    content = content.replace(old_valid, new_valid)
    with open(target, 'w') as f:
        f.write(content)
    print(f"✅ Updated {target} — model validation via is_known_alias()")

# Fix the help display at bottom of /model command
old_help_display = '''        current = session.get("current_model", "auto")
        await update.message.reply_text(
            f"Current: **{current}**\\n\\n"
            "`/model thinking` - qwen3:30b-a3b (DEFAULT)\\n"
            "`/model auto` - qwen2.5:32b\\n"
            "`/model fast` - qwen3:30b-a3b\\n"
            "`/model deep` - qwen2.5:32b",
            parse_mode='Markdown'
        )'''
new_help_display = '''        from core.model_aliases import get_help_text
        current = session.get("current_model", "auto")
        await update.message.reply_text(
            f"Current: **{current}**\\n\\n" + get_help_text(),
            parse_mode='Markdown'
        )'''
content = open(target, 'r').read()
if old_help_display in content:
    content = content.replace(old_help_display, new_help_display)
    with open(target, 'w') as f:
        f.write(content)
    print(f"✅ Updated {target} — /model help text from core")
else:
    print(f"⚠ {target} — help display block not found for replacement")

# 6. Update help_handler.py — both help text blocks
target = '/opt/mythos/telegram_bot/handlers/help_handler.py'
with open(target, 'r') as f:
    content = f.read()

# First block (extended help, lines ~88-102)
old_help1 = """━━━━━━━━━━━━━━━━━━━━━━━━
**MODEL SELECTION**
━━━━━━━━━━━━━━━━━━━━━━━━
`/model thinking` — qwen3:30b-a3b (default, deep reasoning)
`/model deep` — qwen3:32b
`/model fast` — qwen3:30b-a3b (quick, conversational)
`/model auto` — qwen3:30b-a3b
**Advanced:**
`/setmodel <exact_name>` — Use any installed model
`/models` — List all installed Ollama models"""

new_help1 = """━━━━━━━━━━━━━━━━━━━━━━━━
**MODEL SELECTION**
━━━━━━━━━━━━━━━━━━━━━━━━
`/model deep` — iris-deep:latest (qwen3:32b, deeper reasoning)
`/model fast` — iris:latest (qwen3:30b-a3b, quick conversational)
`/model auto` — default model
**Advanced:**
`/setmodel <exact_name>` — Use any installed model
`/models` — List all installed Ollama models"""

if old_help1 in content:
    content = content.replace(old_help1, new_help1)
    print(f"✅ Updated {target} — first help block")
else:
    print(f"⚠ {target} — first help block not found")

# Second block (compact help, lines ~632-648)
old_help2 = """━━━━━━━━━━━━━━━━━━━━━━━━
**MODELS**
━━━━━━━━━━━━━━━━━━━━━━━━
`/model thinking` — qwen3:30b-a3b (default)
`/model deep` — qwen3:32b
`/model fast` — qwen3:30b-a3b"""

new_help2 = """━━━━━━━━━━━━━━━━━━━━━━━━
**MODELS**
━━━━━━━━━━━━━━━━━━━━━━━━
`/model deep` — iris-deep:latest (qwen3:32b)
`/model fast` — iris:latest (qwen3:30b-a3b)"""

if old_help2 in content:
    content = content.replace(old_help2, new_help2)
    print(f"✅ Updated {target} — second help block")
else:
    print(f"⚠ {target} — second help block not found")

with open(target, 'w') as f:
    f.write(content)

# Restart bot
patch.restart_service('mythos-bot.service')

patch.finish()
print("\n✅ SYS-0047 complete — all model aliases consolidated into core/model_aliases.py")
print("   One file to update when models change: /opt/mythos/core/model_aliases.py")
print("   Updated: ollama_models.py, chat_mode.py, chat_assistant.py, mythos_bot.py, help_handler.py")
