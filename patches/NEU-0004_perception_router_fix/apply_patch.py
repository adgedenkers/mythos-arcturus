import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=4,
    description='perception_router_fix',
    patch_type='MINOR',
)
patch.begin()

# --- Patch chat_assistant.py ---
target = '/opt/mythos/assistants/chat_assistant.py'

with open(target, 'r') as f:
    content = f.read()

original = content

# =============================================================
# FIX 1: Remove the misplaced import from line 1
#         (it was inserted BEFORE the shebang)
# =============================================================
content = content.replace(
    'from mythos.neuro.perception_router import PerceptionRouter\n#!/usr/bin/env python3',
    '#!/usr/bin/env python3',
    1
)
print("  ✓ Fix 1: Removed misplaced import from before shebang")

# Now add the import in the correct place — after the ollama import
content = content.replace(
    'from ollama import Client',
    'from ollama import Client\nfrom mythos.neuro.perception_router import PerceptionRouter',
    1
)
print("  ✓ Fix 1: Added PerceptionRouter import after ollama import")

# =============================================================
# FIX 2: Restore indentation on def query line
#         (it's at column 0, needs 4-space indent for class method)
# =============================================================
content = content.replace(
    '    \n    \ndef query(self, message: str,',
    '    \n    \n    def query(self, message: str,',
    1
)
print("  ✓ Fix 2: Restored 4-space indent on def query()")

# =============================================================
# FIX 3: Add self.perception_router init in __init__
# =============================================================
init_block = (
    "        self.default_model = os.getenv('OLLAMA_MODEL', 'qwen2.5:32b')\n"
    "\n"
    "        # Perception router (NEU stream)\n"
    "        try:\n"
    "            self.perception_router = PerceptionRouter(\n"
    "                pg_conn_string=\"dbname=mythos user=postgres\"\n"
    "            )\n"
    "            logger.info(\"ChatAssistant: perception router initialized\")\n"
    "        except Exception as e:\n"
    "            logger.warning(f\"ChatAssistant: perception router unavailable: {e}\")\n"
    "            self.perception_router = None"
)

content = content.replace(
    "        self.default_model = os.getenv('OLLAMA_MODEL', 'qwen2.5:32b')",
    init_block,
    1
)
print("  ✓ Fix 3: Added self.perception_router init in __init__")

# =============================================================
# FIX 4: Replace the inline PerceptionRouter() instantiation
#         with self.perception_router usage
# =============================================================
old_logging = (
    "        # NEU-0004 perception logging\n"
    "        try:\n"
    "            router = PerceptionRouter(\"dbname=mythos user=postgres\")\n"
    "            router.log_event(\n"
    "                source=\"telegram\",\n"
    "                source_platform=\"telegram\",\n"
    "                content=message\n"
    "            )\n"
    "        except Exception as e:\n"
    "            logger.debug(f\"Perception logging skipped: {e}\")"
)

new_logging = (
    "        # NEU-0004 perception logging\n"
    "        if getattr(self, 'perception_router', None):\n"
    "            try:\n"
    "                self.perception_router.log_event(\n"
    "                    content=message,\n"
    "                    source=\"telegram\",\n"
    "                    source_platform=\"telegram\",\n"
    "                    raw_data={\"telegram_id\": telegram_id}\n"
    "                )\n"
    "            except Exception as e:\n"
    "                logger.warning(f\"Perception logging failed: {e}\")"
)

content = content.replace(old_logging, new_logging, 1)
print("  ✓ Fix 4: Replaced inline router instantiation with self.perception_router")

# Verify changes were made
if content == original:
    print("  ❌ No changes made — anchors may not match")
    sys.exit(1)

# Write patched file
with open(target, 'w') as f:
    f.write(content)
print(f"  ✓ Wrote patched {target}")

# py_compile check
import py_compile
try:
    py_compile.compile(target, doraise=True)
    print(f"  ✓ py_compile passed")
except py_compile.PyCompileError as e:
    print(f"  ❌ py_compile FAILED: {e}")
    with open(target, 'w') as f:
        f.write(original)
    print(f"  ↩ Rolled back {target}")
    sys.exit(1)

# Restart API
patch.restart_service('mythos-api.service')

patch.finish()
