#!/usr/bin/env python3
"""
Patch chat_assistant.py to integrate the message extractor.

Adds:
1. Import of message_extractor and action_executor
2. Pre-pass extraction before main model call
3. Injection of extraction context into message
4. Post-pass execution of extracted actions
"""

ASSISTANT_PATH = '/opt/mythos/assistants/chat_assistant.py'


def apply():
    with open(ASSISTANT_PATH, 'r') as f:
        content = f.read()

    # Check if already patched
    if 'message_extractor' in content:
        print("Already patched — message_extractor reference found.")
        return

    # 1. Add imports (after life_context import)
    content = content.replace(
        'from life_context import build_life_context',
        'from life_context import build_life_context\n'
        'from message_extractor import extract as extract_message, format_extraction_for_context\n'
        'from action_executor import execute_actions'
    )

    # 2. Add extraction pre-pass and context injection in the query method
    # Find the spot right before "Build messages with context"
    content = content.replace(
        '            # Build messages with context\n'
        '            messages = self._build_messages(user_uuid, message, soul_name, model=model)',
        '            # === EXTRACTOR PRE-PASS ===\n'
        '            extraction = {"no_action": True}\n'
        '            extraction_context = ""\n'
        '            try:\n'
        '                extraction = extract_message(message)\n'
        '                extraction_context = format_extraction_for_context(extraction)\n'
        '                if extraction_context:\n'
        '                    logger.info(f"Extractor enriched message with: {extraction_context[:100]}")\n'
        '            except Exception as e:\n'
        '                logger.warning(f"Extractor pre-pass failed (non-fatal): {e}")\n'
        '            \n'
        '            # Build messages with context\n'
        '            enriched_message = message\n'
        '            if extraction_context:\n'
        '                enriched_message = message + "\\n\\n" + extraction_context\n'
        '            messages = self._build_messages(user_uuid, enriched_message, soul_name, model=model)'
    )

    # 3. Add post-pass action execution after response is generated
    # Find the spot right after grid analysis dispatch
    content = content.replace(
        '            # Dispatch to grid analysis (async, fire-and-forget)\n'
        '            self._dispatch_grid_analysis(',
        '            # === EXTRACTOR POST-PASS: Execute actions ===\n'
        '            try:\n'
        '                if not extraction.get("no_action"):\n'
        '                    action_results = execute_actions(extraction)\n'
        '                    if action_results:\n'
        '                        logger.info(f"Executor completed: {action_results}")\n'
        '            except Exception as e:\n'
        '                logger.warning(f"Action execution failed (non-fatal): {e}")\n'
        '            \n'
        '            # Dispatch to grid analysis (async, fire-and-forget)\n'
        '            self._dispatch_grid_analysis('
    )

    with open(ASSISTANT_PATH, 'w') as f:
        f.write(content)

    print("✅ chat_assistant.py patched with extractor pipeline.")


if __name__ == '__main__':
    apply()
