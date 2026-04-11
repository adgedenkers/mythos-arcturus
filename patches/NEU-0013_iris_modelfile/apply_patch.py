#!/usr/bin/env python3
"""
NEU-0013: Iris Modelfile — Baked Identity
=========================================
Deploys an Ollama Modelfile that bakes Iris's identity, voice, personality,
cosmology, and behavioral rules into a custom model called iris:latest.

Changes:
1. Deploy Modelfile to /opt/mythos/prompts/Modelfile
2. Run `ollama create iris -f Modelfile` to build the model
3. Update .env: OLLAMA_MODEL=iris:latest
4. Update chat_assistant.py:
   - model_map 'fast' -> 'iris:latest'
   - Drop num_predict from options (baked into Modelfile)
5. Update prompt_assembler.py:
   - Add _is_baked_model() check
   - Skip identity, personality, voice, anti-confab, cosmology when model is iris:*
   - Keep baseline, skills_context, skill_results, life_context, etc. dynamic
"""

import sys
import os
import subprocess

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=13,
    description='iris_modelfile',
    patch_type='MAJOR',
)
patch.begin()

# ── 1. Deploy Modelfile ──
patch.deploy_file(
    'opt/mythos/prompts/Modelfile',
    '/opt/mythos/prompts/Modelfile'
)

# ── 2. Build iris:latest via Ollama ──
print("\n🔨 Building iris:latest model from Modelfile...")
print("   This may take a moment (copies model weights + bakes system prompt)...")
result = subprocess.run(
    ['ollama', 'create', 'iris', '-f', '/opt/mythos/prompts/Modelfile'],
    capture_output=True, text=True, timeout=300
)
if result.returncode != 0:
    print(f"   ❌ ollama create failed: {result.stderr}")
    print("   Continuing with patch deployment — run manually:")
    print("   ollama create iris -f /opt/mythos/prompts/Modelfile")
else:
    print("   ✅ iris:latest created successfully")
    # Verify
    verify = subprocess.run(
        ['ollama', 'show', 'iris', '--modelfile'],
        capture_output=True, text=True
    )
    if verify.returncode == 0:
        lines = verify.stdout.strip().split('\n')
        print(f"   Modelfile: {len(lines)} lines")
        # Check SYSTEM block exists
        has_system = any('SYSTEM' in line for line in lines)
        print(f"   SYSTEM block baked: {'✅' if has_system else '❌'}")

# ── 3. Update .env ──
print("\n📝 Updating .env: OLLAMA_MODEL=iris:latest")
env_path = '/opt/mythos/.env'
with open(env_path, 'r') as f:
    env_content = f.read()

if 'OLLAMA_MODEL=qwen3:30b-a3b' in env_content:
    env_content = env_content.replace(
        'OLLAMA_MODEL=qwen3:30b-a3b',
        'OLLAMA_MODEL=iris:latest'
    )
    with open(env_path, 'w') as f:
        f.write(env_content)
    print("   ✅ .env updated")
elif 'OLLAMA_MODEL=iris:latest' in env_content:
    print("   ⏭️  Already set to iris:latest")
else:
    print(f"   ⚠️  Unexpected OLLAMA_MODEL value — update manually")

# ── 4. Patch chat_assistant.py ──
print("\n📝 Patching chat_assistant.py...")
ca_path = '/opt/mythos/assistants/chat_assistant.py'
with open(ca_path, 'r') as f:
    ca_content = f.read()

changes_made = []

# 4a. Update model_map: 'fast' -> 'iris:latest'
if "'fast': 'qwen3:30b-a3b'" in ca_content:
    ca_content = ca_content.replace(
        "'fast': 'qwen3:30b-a3b'",
        "'fast': 'iris:latest'"
    )
    changes_made.append("model_map 'fast' → 'iris:latest'")

# 4b. Drop num_predict from options (now baked)
# The options block currently is:
#     options={
#         'temperature': 0.7,
#         'num_predict': 4096,
#     }
# We want:
#     options={
#         'temperature': 0.7,
#     }
if "'num_predict': 4096," in ca_content:
    ca_content = ca_content.replace(
        "                options={\n                    'temperature': 0.7,\n                    'num_predict': 4096,\n                }",
        "                options={\n                    'temperature': 0.7,\n                }"
    )
    changes_made.append("Removed num_predict from options (baked in Modelfile)")

if changes_made:
    with open(ca_path, 'w') as f:
        f.write(ca_content)
    for c in changes_made:
        print(f"   ✅ {c}")
else:
    print("   ⏭️  No changes needed (already patched?)")

# ── 5. Patch prompt_assembler.py ──
# Strategy: Instead of surgically editing multi-line triple-quoted blocks
# (which is fragile with str.replace), we:
# a) Add _is_baked_model() helper
# b) Add a baked_model flag early in assemble_system_prompt
# c) Wrap the identity/personality/voice layer checks
# d) For the hardcoded anti-confab and cosmology blocks, we read the file
#    line by line and wrap them properly
print("\n📝 Patching prompt_assembler.py...")
pa_path = '/opt/mythos/core/prompt_assembler.py'
with open(pa_path, 'r') as f:
    pa_lines = f.readlines()

pa_changes = []

# Check if already patched
pa_text = ''.join(pa_lines)
if '_is_baked_model' in pa_text:
    print("   ⏭️  Already patched (_is_baked_model found)")
else:
    new_lines = []
    i = 0
    while i < len(pa_lines):
        line = pa_lines[i]

        # 5a. Insert _is_baked_model() before is_layer_enabled()
        if line.strip().startswith('def is_layer_enabled(layer_name:'):
            new_lines.append('\n')
            new_lines.append('# ─── Baked Model Detection ───────────────────────────────────────────────────\n')
            new_lines.append('\n')
            new_lines.append('def _is_baked_model(model_name: str) -> bool:\n')
            new_lines.append('    """Check if model has identity/voice/personality baked via Modelfile."""\n')
            new_lines.append('    if not model_name:\n')
            new_lines.append('        return False\n')
            new_lines.append('    return model_name.startswith(\'iris:\') or model_name == \'iris\'\n')
            new_lines.append('\n')
            new_lines.append('\n')
            pa_changes.append("Added _is_baked_model() helper")
            new_lines.append(line)
            i += 1
            continue

        # 5b. Gate anti-confabulation block
        if '# ── ANTI-CONFABULATION' in line:
            new_lines.append(line)  # keep the comment
            i += 1
            # Next line should be: sections.append("""## ABSOLUTE RULE...
            # Wrap everything until the closing """) in an if block
            if i < len(pa_lines) and 'sections.append("""' in pa_lines[i]:
                new_lines.append('    _baked = _is_baked_model(model_name)\n')
                new_lines.append('    if not _baked:\n')
                # Read until we find the closing """)\n
                while i < len(pa_lines):
                    inner = pa_lines[i]
                    new_lines.append('    ' + inner)  # add one level of indent
                    i += 1
                    if inner.strip().endswith('""")'):
                        break
                pa_changes.append("Gated anti-confabulation block behind baked model check")
            continue

        # 5c. Gate cosmological framework block
        if '# ── COSMOLOGICAL FRAMEWORK' in line:
            new_lines.append(line)  # keep the comment
            i += 1
            if i < len(pa_lines) and 'sections.append("""' in pa_lines[i]:
                new_lines.append('    if not _baked:\n')
                while i < len(pa_lines):
                    inner = pa_lines[i]
                    new_lines.append('    ' + inner)
                    i += 1
                    if inner.strip().endswith('""")'):
                        break
                pa_changes.append("Gated cosmological framework behind baked model check")
            continue

        # 5d. Gate identity layer
        if line.strip() == "if is_layer_enabled('identity'):":
            new_lines.append(line.replace(
                "if is_layer_enabled('identity'):",
                "if is_layer_enabled('identity') and not _is_baked_model(model_name):"
            ))
            pa_changes.append("Gated identity layer")
            i += 1
            continue

        # 5e. Gate personality layer
        if line.strip() == "if is_layer_enabled('personality'):":
            new_lines.append(line.replace(
                "if is_layer_enabled('personality'):",
                "if is_layer_enabled('personality') and not _is_baked_model(model_name):"
            ))
            pa_changes.append("Gated personality layer")
            i += 1
            continue

        # 5f. Gate voice layer
        if line.strip() == "if is_layer_enabled('voice'):":
            new_lines.append(line.replace(
                "if is_layer_enabled('voice'):",
                "if is_layer_enabled('voice') and not _is_baked_model(model_name):"
            ))
            pa_changes.append("Gated voice layer")
            i += 1
            continue

        # 5g. Update logging to include baked status
        if 'f"layers=[{' in line and 'assembled prompt' not in line:
            new_lines.append(line)
            # Check if next line has the user= part
            if i + 1 < len(pa_lines) and 'f"user=' in pa_lines[i + 1]:
                # Insert baked status line before the user= line
                indent = '        '
                new_lines.append(f'{indent}f"baked={{_is_baked_model(model_name)}}, "\n')
                pa_changes.append("Added baked status to assembly log")
            i += 1
            continue

        new_lines.append(line)
        i += 1

    if pa_changes:
        with open(pa_path, 'w') as f:
            f.writelines(new_lines)
        for c in pa_changes:
            print(f"   ✅ {c}")
    else:
        print("   ⚠️  No changes applied — check file structure")

# ── 6. Restart services ──
patch.restart_service('mythos-bot.service')
patch.restart_service('mythos-api.service')

patch.finish()

print("\n" + "="*60)
print("NEU-0013 COMPLETE — Iris Modelfile Deployed")
print("="*60)
print(f"\nModel: iris:latest (FROM qwen3:30b-a3b)")
print(f"Baked: identity, voice, personality, cosmology, anti-confab")
print(f"Dynamic: baseline, skills_context, skill_results, life_context")
print(f"\nTo verify:")
print(f"  ollama show iris --modelfile | head -5")
print(f"  # Send Iris a test message via Telegram")
print(f"\nTo rollback:")
print(f"  git checkout pre-modelfile-v1")
print(f"  echo 'OLLAMA_MODEL=qwen3:30b-a3b' and update .env")
print(f"  sudo systemctl restart mythos-bot mythos-api")
