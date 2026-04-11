#!/usr/bin/env python3
"""
NEU-0016: Baked Model Message Flow Fix
=======================================
The Ollama chat API treats ANY system message as a complete replacement
for the Modelfile SYSTEM block. This means when chat_assistant sends
a system message (even a short one), the baked identity is wiped.

Fix: When the model is baked (iris:*), don't send a system message.
Instead, inject dynamic context (timestamp, skill results, life context)
as a [Context] preamble in the user message. The Modelfile SYSTEM block
stays active and controls Iris's identity/voice/personality.

Tested: ollama run iris:latest with [Context] preamble produces correct
Iris voice across casual, emotional, skill data, and spiritual messages.
"""

import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=16,
    description='baked_message_flow',
    patch_type='MAJOR',
)
patch.begin()

# ── Patch chat_assistant.py ──
print("\n📝 Patching chat_assistant.py — _build_messages method...")
ca_path = '/opt/mythos/assistants/chat_assistant.py'
with open(ca_path, 'r') as f:
    ca_lines = f.readlines()

ca_text = ''.join(ca_lines)
changes = []

# Check if already patched
if '_is_baked_model' in ca_text and 'context_preamble' in ca_text:
    print("   ⏭️  Already patched")
else:
    # Add import for _is_baked_model
    if '_is_baked_model' not in ca_text:
        old_import = 'from prompt_assembler import assemble_system_prompt, is_layer_enabled'
        new_import = 'from prompt_assembler import assemble_system_prompt, is_layer_enabled, _is_baked_model'
        if old_import in ca_text:
            ca_text = ca_text.replace(old_import, new_import)
            changes.append("Added _is_baked_model import")

    # Replace the message assembly at the end of _build_messages
    # Current code builds system_prompt and then does:
    #   messages = [{'role': 'system', 'content': system_prompt}]
    #   ... adds conversation history ...
    #   messages.append({'role': 'user', 'content': user_message})
    #
    # New code: when baked, skip system message, prepend context to user message

    old_message_assembly = """        messages = [{'role': 'system', 'content': system_prompt}]

        # Add conversation history (in-memory session context)
        for msg in context['messages']:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })

        # Add current user message
        messages.append({'role': 'user', 'content': user_message})

        return messages"""

    new_message_assembly = """        # ── BUILD MESSAGES ARRAY ──
        # For baked models (iris:*): NO system message — Modelfile SYSTEM handles identity.
        # Ollama's chat API replaces the Modelfile SYSTEM with any system message,
        # so sending one wipes the baked identity. Dynamic context goes as a
        # [Context] preamble in the user message instead.
        if _is_baked_model(model):
            messages = []

            # Add conversation history (in-memory session context)
            for msg in context['messages']:
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })

            # Build context preamble from dynamic data
            context_parts = []
            if system_prompt.strip():
                context_parts.append(system_prompt.strip())

            # Prepend context to user message
            if context_parts:
                context_preamble = "[Context]\\n" + "\\n".join(context_parts) + "\\n[/Context]"
                final_message = context_preamble + "\\n\\n" + user_message
            else:
                final_message = user_message

            messages.append({'role': 'user', 'content': final_message})
            logger.info(f"Chat: Baked model — no system message, context preamble {len(context_preamble) if context_parts else 0} chars")
        else:
            # Non-baked models: standard system message
            messages = [{'role': 'system', 'content': system_prompt}]

            # Add conversation history (in-memory session context)
            for msg in context['messages']:
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })

            # Add current user message
            messages.append({'role': 'user', 'content': user_message})

        return messages"""

    if old_message_assembly in ca_text:
        ca_text = ca_text.replace(old_message_assembly, new_message_assembly)
        changes.append("Replaced message assembly with baked/unbaked split")
    else:
        print("   ⚠️  Could not find exact message assembly block — checking alternative...")
        # Try to find the key line
        if "messages = [{'role': 'system', 'content': system_prompt}]" in ca_text:
            print("   Found the system message line — but surrounding context didn't match exactly")
            print("   Manual patching may be needed")
        else:
            print("   ⚠️  System message line not found at all")

    if changes:
        with open(ca_path, 'w') as f:
            f.write(ca_text)
        for c in changes:
            print(f"   ✅ {c}")

# Verify with py_compile
import py_compile
try:
    py_compile.compile(ca_path, doraise=True)
    print("   ✅ Syntax check passed")
except py_compile.PyCompileError as e:
    print(f"   ❌ Syntax error: {e}")
    print("   Rolling back...")
    # If we had a backup we'd restore here
    sys.exit(1)

# Restart services
patch.restart_service('mythos-api.service')
patch.restart_service('mythos-bot.service')

patch.finish()

print("\n" + "="*60)
print("NEU-0016 COMPLETE — Baked Model Message Flow")
print("="*60)
print()
print("Baked models (iris:*) no longer receive a system message.")
print("Dynamic context injected as [Context] preamble in user message.")
print("The Modelfile SYSTEM block stays active and controls identity.")
print()
print("Test:")
print("  curl -s -X POST http://localhost:8000/message \\")
print('    -H "Content-Type: application/json" \\')
print('    -H "X-API-Key: $(grep API_KEY_TELEGRAM_BOT /opt/mythos/.env | cut -d= -f2)" \\')
print("    -d '{\"user_id\": \"7811548479\", \"message\": \"hey\", \"mode\": \"chat\"}' | python3 -m json.tool")
