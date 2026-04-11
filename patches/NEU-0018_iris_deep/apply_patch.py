#!/usr/bin/env python3
"""
NEU-0018: iris-deep:latest — Full 32B Modelfile
=================================================
Same calibration-proven prompt as iris:latest (v3), but FROM qwen3:32b.
Full 32B params instead of 3B active. Slower (~30-50s) but significantly
deeper reasoning, better instruction following, and richer responses.

Changes:
1. Deploy Modelfile.deep to /opt/mythos/prompts/
2. Build iris-deep:latest via ollama create
3. Update chat_assistant.py model_map: 'deep' -> 'iris-deep:latest'
4. Update /setmodel handler aliases
"""

import sys
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=18,
    description='iris_deep_modelfile',
    patch_type='MINOR',
)
patch.begin()

# 1. Deploy Modelfile.deep
patch.deploy_file(
    'opt/mythos/prompts/Modelfile.deep',
    '/opt/mythos/prompts/Modelfile.deep'
)

# 2. Build iris-deep:latest
print("\n🔨 Building iris-deep:latest from Modelfile.deep...")
print("   (This copies qwen3:32b weights — may take a moment)")
result = subprocess.run(
    ['ollama', 'create', 'iris-deep', '-f', '/opt/mythos/prompts/Modelfile.deep'],
    capture_output=True, text=True, timeout=300
)
if result.returncode != 0:
    print(f"   ❌ ollama create failed: {result.stderr}")
    print("   Run manually: ollama create iris-deep -f /opt/mythos/prompts/Modelfile.deep")
else:
    print("   ✅ iris-deep:latest created")

# 3. Update chat_assistant.py model_map: 'deep' -> 'iris-deep:latest'
print("\n📝 Patching chat_assistant.py...")
ca_path = '/opt/mythos/assistants/chat_assistant.py'
with open(ca_path, 'r') as f:
    ca_text = f.read()

ca_changes = []

# The model_map currently has 'deep': self.default_model
# We want 'deep': 'iris-deep:latest'
if "'deep': self.default_model" in ca_text:
    ca_text = ca_text.replace(
        "'deep': self.default_model",
        "'deep': 'iris-deep:latest'"
    )
    ca_changes.append("model_map 'deep' → 'iris-deep:latest'")

if ca_changes:
    with open(ca_path, 'w') as f:
        f.write(ca_text)
    for c in ca_changes:
        print(f"   ✅ {c}")

# 4. Update /setmodel handler aliases
print("\n📝 Patching ollama_models.py...")
handler_path = '/opt/mythos/telegram_bot/handlers/ollama_models.py'
try:
    with open(handler_path, 'r') as f:
        handler_text = f.read()

    handler_changes = []

    # Update deep/32b alias to point to iris-deep:latest
    if "'deep': 'qwen3:32b'" in handler_text:
        handler_text = handler_text.replace(
            "'deep': 'qwen3:32b'",
            "'deep': 'iris-deep:latest'"
        )
        handler_changes.append("/setmodel deep → iris-deep:latest")

    if "'32b': 'qwen3:32b'" in handler_text:
        handler_text = handler_text.replace(
            "'32b': 'qwen3:32b'",
            "'32b': 'iris-deep:latest'"
        )
        handler_changes.append("/setmodel 32b → iris-deep:latest")

    if handler_changes:
        with open(handler_path, 'w') as f:
            f.write(handler_text)
        for c in handler_changes:
            print(f"   ✅ {c}")
    else:
        print("   ⏭️  Aliases already set or format differs")

except FileNotFoundError:
    print("   ⚠️  ollama_models.py not found — skip alias update")

# Restart services
patch.restart_service('mythos-api.service')
patch.restart_service('mythos-bot.service')

patch.finish()

print("\n" + "="*60)
print("NEU-0018 COMPLETE — iris-deep:latest Deployed")
print("="*60)
print()
print("Models:")
print("  iris:latest      — fast (qwen3:30b-a3b, ~8-12s)")
print("  iris-deep:latest — deep (qwen3:32b, ~30-50s)")
print()
print("Switch via Telegram: /setmodel deep")
print("Switch back:         /setmodel fast")
print()
print("Test deep directly:")
print("  ollama run iris-deep 'hey, how are things going?'")
