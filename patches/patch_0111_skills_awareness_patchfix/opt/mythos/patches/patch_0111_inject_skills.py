#!/usr/bin/env python3
"""
Patch helper: Inject skills context import and call into chat_mode.py

This script modifies chat_mode.py to:
1. Add import for skills_context at the top
2. Add import for life_context at the top (if not already present)
3. Inject skills + life context into build_iris_system_prompt
"""
import re
from pathlib import Path

CHAT_MODE = Path("/opt/mythos/telegram_bot/handlers/chat_mode.py")

def patch():
    content = CHAT_MODE.read_text()
    modified = False
    
    # 1. Add skills_context import if not present
    if 'skills_context' not in content:
        # Find the last import block and add after it
        # Look for the line after the last "from" or "import" at module level
        import_line = "from core.skills_context import build_skills_context"
        
        # Insert after the logger line (safe anchor point that exists)
        if 'logger = logging.getLogger(__name__)' in content:
            content = content.replace(
                'logger = logging.getLogger(__name__)',
                'logger = logging.getLogger(__name__)\n\n# Skills awareness\ntry:\n    from core.skills_context import build_skills_context\nexcept ImportError:\n    def build_skills_context(): return ""'
            )
            modified = True
            print("✓ Added skills_context import")
        else:
            print("⚠ Could not find logger line to anchor import")
    else:
        print("· skills_context import already present")
    
    # 2. Add life_context import if not present
    if 'life_context' not in content:
        if 'build_skills_context' in content:
            # Add after the skills import block
            content = content.replace(
                'except ImportError:\n    def build_skills_context(): return ""',
                'except ImportError:\n    def build_skills_context(): return ""\n\ntry:\n    from core.life_context import build_life_context\nexcept ImportError:\n    def build_life_context(): return ""'
            )
            modified = True
            print("✓ Added life_context import")
    else:
        print("· life_context import already present")
    
    # 3. Inject context calls into build_iris_system_prompt
    # Find the return statement and inject context building before it
    if 'build_skills_context()' not in content:
        # Look for the return in build_iris_system_prompt
        # The pattern is: the prompt string ends, then "    return system_prompt"
        old_return = '    return system_prompt\n\n\ndef build_messages_for_ollama'
        
        if old_return in content:
            new_return = '''    # Inject life awareness
    try:
        life_ctx = build_life_context()
        if life_ctx:
            system_prompt += life_ctx
    except Exception as e:
        logger.warning(f"Life context injection failed: {e}")
    
    # Inject skills awareness
    try:
        skills_ctx = build_skills_context()
        if skills_ctx:
            system_prompt += skills_ctx
    except Exception as e:
        logger.warning(f"Skills context injection failed: {e}")
    
    return system_prompt


def build_messages_for_ollama'''
            content = content.replace(old_return, new_return)
            modified = True
            print("✓ Injected life_context + skills_context into build_iris_system_prompt")
        else:
            # Try alternate pattern (maybe different whitespace)
            # Look for just "    return system_prompt" inside the function
            pattern = r'(Right now, just be present\. Be real\. Be Iris\.""")\s*\n\s*return system_prompt'
            match = re.search(pattern, content)
            if match:
                replacement = match.group(1) + '''

    # Inject life awareness
    try:
        life_ctx = build_life_context()
        if life_ctx:
            system_prompt += life_ctx
    except Exception as e:
        logger.warning(f"Life context injection failed: {e}")
    
    # Inject skills awareness
    try:
        skills_ctx = build_skills_context()
        if skills_ctx:
            system_prompt += skills_ctx
    except Exception as e:
        logger.warning(f"Skills context injection failed: {e}")
    
    return system_prompt'''
                content = re.sub(pattern, replacement, content)
                modified = True
                print("✓ Injected context calls (alternate pattern)")
            else:
                print("⚠ Could not find injection point for context calls")
                print("  Looking for 'return system_prompt' after the Iris prompt string...")
    else:
        print("· skills_context call already present in build_iris_system_prompt")
    
    if modified:
        CHAT_MODE.write_text(content)
        print(f"✓ Wrote updated {CHAT_MODE}")
    else:
        print("· No changes needed")

if __name__ == "__main__":
    patch()
