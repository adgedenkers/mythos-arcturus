#!/usr/bin/env python3
"""
Patch applicator for chat_assistant.py
Adds life context injection into Iris's system prompt.

This modifies _build_messages to include the life state context
alongside the existing memory context.
"""

import re

ASSISTANT_PATH = '/opt/mythos/assistants/chat_assistant.py'

def apply():
    with open(ASSISTANT_PATH, 'r') as f:
        content = f.read()

    # Check if already patched
    if 'life_context' in content:
        print("Already patched — life_context reference found.")
        return

    # 1. Add import at top of file (after the iris_memory import)
    content = content.replace(
        'from iris_memory import IrisMemory',
        'from iris_memory import IrisMemory\n'
        'import sys\n'
        'sys.path.insert(0, "/opt/mythos/core")\n'
        'from life_context import build_life_context'
    )

    # 2. Inject life context in _build_messages, after memory context
    content = content.replace(
        '''        # Append memory context to system prompt if available
        if memory_context:
            system_prompt += memory_context''',
        '''        # Append memory context to system prompt if available
        if memory_context:
            system_prompt += memory_context
        
        # Append life state context (routines, tasks, bills, calendar)
        try:
            life_ctx = build_life_context()
            if life_ctx:
                system_prompt += life_ctx
        except Exception as e:
            logger.warning(f"Life context build failed (non-fatal): {e}")'''
    )

    with open(ASSISTANT_PATH, 'w') as f:
        f.write(content)

    print("✅ chat_assistant.py patched with life context injection.")


if __name__ == '__main__':
    apply()
