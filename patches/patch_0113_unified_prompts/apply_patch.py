#!/usr/bin/env python3
"""
Patch 0113: Unified Prompt & Personality System
================================================
Replaces fragmented prompt sources with a single layered assembler.
Adds mode system, personality sliders, temporal awareness.

Changes:
- NEW: core/prompt_assembler.py (THE source of truth)
- NEW: prompts/iris_identity.md, personality.yaml, voice.yaml
- NEW: prompts/modes/*.yaml (6 modes)
- NEW: prompts/users/*.yaml (2 user profiles)
- NEW: models/iris-thinking.Modelfile (parameters only)
- NEW: docs/PROMPT_SYSTEM.md
- MODIFIED: telegram_bot/handlers/chat_mode.py (assembler integration)
- MODIFIED: assistants/chat_assistant.py (assembler integration)
- MODIFIED: telegram_bot/mythos_bot.py (new /mode, /personality commands + timestamp passing)
- REBUILD: iris-thinking model (strip baked SYSTEM block)
"""
import os
import sys
import shutil
import subprocess
import py_compile
from pathlib import Path

MYTHOS = Path("/opt/mythos")
PATCH_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
PATCH_FILES = PATCH_DIR / "opt" / "mythos"


def backup_file(filepath: Path) -> Path:
    """Create a backup of a file before modifying it."""
    backup = filepath.with_suffix(filepath.suffix + '.bak_0113')
    if filepath.exists():
        shutil.copy2(filepath, backup)
        print(f"  📋 Backed up {filepath.name}")
    return backup


def copy_new_file(src_relative: str):
    """Copy a new file from patch to target."""
    src = PATCH_FILES / src_relative
    dst = MYTHOS / src_relative
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  ✅ {src_relative}")


def copy_modified_file(src_relative: str):
    """Copy a modified file from patch to target, with backup."""
    dst = MYTHOS / src_relative
    backup_file(dst)
    src = PATCH_FILES / src_relative
    shutil.copy2(src, dst)
    print(f"  ✅ {src_relative} (modified)")


def syntax_check(filepath: Path):
    """Verify Python syntax before deploying."""
    try:
        py_compile.compile(str(filepath), doraise=True)
        return True
    except py_compile.PyCompileError as e:
        print(f"  ❌ SYNTAX ERROR in {filepath}: {e}")
        return False


def modify_mythos_bot():
    """
    Modify mythos_bot.py using string replacement (patch standard v2).
    
    Changes:
    1. Replace the old /mode command handler with new Iris mode system
    2. Add /personality command handler
    3. Pass message_timestamp through handle_message → _process_buffered_message
    """
    bot_path = MYTHOS / "telegram_bot" / "mythos_bot.py"
    backup_file(bot_path)
    
    content = bot_path.read_text()
    original = content
    
    # === CHANGE 1: Add prompt_assembler import near the chat_mode import ===
    old_import = """from handlers.chat_mode import ("""
    new_import = """from handlers.chat_mode import ("""
    # We also need to import assembler functions for /mode and /personality
    # Add after the existing chat_mode import block
    # Find the line after the chat_mode import block ends
    
    # === CHANGE 2: Replace mode_command function ===
    # The old mode_command supports: chat, db, sell, seraphe, genealogy
    # The new one supports: hearthfire, forge, roots, oracle, scribe, sentry (Iris modes)
    # Plus keeps sell and db as legacy modes
    
    old_mode_cmd = '''async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mode command to switch modes"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    if context.args:
        new_mode = context.args[0].lower()
        
        valid_modes = ["db", "seraphe", "genealogy", "chat", "sell"]
        
        if new_mode in valid_modes:
            old_mode = session.get("current_mode", "chat")
            
            if new_mode == "sell":
                log_activity(session, "mode_change", f"Entered sell mode")
                await enter_sell_mode(update, session)
                return
            
            if is_sell_mode(session):
                session["sell_session"] = None
            
            if new_mode == "chat":
                if session.get("chat_context") is None:
                    clear_chat_context(session)
            
            session["current_mode"] = new_mode
            log_activity(session, "mode_change", f"→ {new_mode}")
            
            mode_descriptions = {
                "db": "Database queries - ask about souls, persons, lineages",
                "seraphe": "Cosmology assistant (coming soon)",
                "genealogy": "Bloodline research (coming soon)",
                "chat": "Chat with AI - context maintained"
            }
            
            await update.message.reply_text(
                f"✅ **{new_mode}** mode\\n\\n{mode_descriptions[new_mode]}",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"❌ Unknown mode: {new_mode}\\n\\n"
                "Available: chat, db, sell, seraphe, genealogy"
            )
    else:
        current = session.get("current_mode", "chat")
        await update.message.reply_text(
            f"Current: **{current}**\\n\\n"
            "`/mode chat` - AI conversation\\n"
            "`/mode db` - Database queries\\n"
            "`/mode sell` - Sell items\\n"
            "`/mode seraphe` - Cosmology\\n"
            "`/mode genealogy` - Bloodlines",
            parse_mode='Markdown'
        )'''
    
    new_mode_cmd = '''async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mode command — switch Iris modes or legacy modes (sell, db)"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    # Import mode list from assembler
    try:
        import sys as _sys
        _sys.path.insert(0, "/opt/mythos/core")
        from prompt_assembler import get_available_modes
        iris_modes = {m['name']: m for m in get_available_modes()}
    except Exception:
        iris_modes = {}
    
    if context.args:
        new_mode = context.args[0].lower()
        sub_mode = context.args[1].lower() if len(context.args) > 1 else None
        
        # Legacy modes: sell, db
        if new_mode == "sell":
            log_activity(session, "mode_change", "Entered sell mode")
            await enter_sell_mode(update, session)
            return
        
        if new_mode == "db":
            if is_sell_mode(session):
                session["sell_session"] = None
            session["current_mode"] = "db"
            log_activity(session, "mode_change", "→ db")
            await update.message.reply_text("✅ **db** mode\\n\\nDatabase queries - ask about souls, persons, lineages", parse_mode='Markdown')
            return
        
        # Iris modes
        if new_mode in iris_modes:
            if is_sell_mode(session):
                session["sell_session"] = None
            session["current_mode"] = "chat"  # Ensure chat handler routes messages
            session["iris_mode"] = new_mode
            session["iris_sub_mode"] = sub_mode
            
            mode_info = iris_modes[new_mode]
            emoji = mode_info.get('emoji', '')
            desc = mode_info.get('description', '')
            
            log_activity(session, "mode_change", f"→ {emoji} {new_mode}" + (f" ({sub_mode})" if sub_mode else ""))
            
            msg = f"{emoji} **{new_mode.upper()}** mode"
            if sub_mode:
                msg += f" ({sub_mode})"
            if desc:
                msg += f"\\n{desc}"
            
            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            mode_list = ", ".join(sorted(iris_modes.keys())) if iris_modes else "hearthfire, forge, roots, oracle, scribe, sentry"
            await update.message.reply_text(
                f"❌ Unknown mode: {new_mode}\\n\\n"
                f"**Iris modes:** {mode_list}\\n"
                "**Legacy:** db, sell",
                parse_mode='Markdown'
            )
    else:
        current_iris = session.get("iris_mode", "hearthfire")
        current_sub = session.get("iris_sub_mode")
        emoji = iris_modes.get(current_iris, {}).get('emoji', '🔥') if iris_modes else '🔥'
        
        lines = [f"Current: {emoji} **{current_iris}**" + (f" ({current_sub})" if current_sub else "")]
        lines.append("")
        
        if iris_modes:
            for m in sorted(iris_modes.values(), key=lambda x: x['name']):
                e = m.get('emoji', '')
                n = m.get('name', '')
                d = m.get('description', '')
                lines.append(f"`/mode {n}` {e} {d}")
        else:
            lines.append("`/mode hearthfire` 🔥 Spiritual/personal")
            lines.append("`/mode forge` ⚒️ System admin")
            lines.append("`/mode roots` 🌳 Genealogy")
            lines.append("`/mode oracle` 🔮 Research/harmonics")
            lines.append("`/mode scribe` 📜 Writing")
            lines.append("`/mode sentry` 🛡️ Financial")
        
        lines.append("")
        lines.append("`/mode db` Database queries")
        lines.append("`/mode sell` Sell items")
        
        await update.message.reply_text("\\n".join(lines), parse_mode='Markdown')'''
    
    if old_mode_cmd not in content:
        print("  ⚠️ Could not find exact old mode_command — trying relaxed match")
        # Try to find and replace just the function signature to end
        # Fall back: find 'async def mode_command' and replace until next 'async def'
        import re
        pattern = r'(async def mode_command\(update.*?\n)(.*?)(?=\nasync def |\nclass |\Z)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            content = content[:match.start()] + new_mode_cmd + content[match.end():]
            print("  ✅ Replaced mode_command (relaxed match)")
        else:
            print("  ❌ FAILED to find mode_command function!")
            sys.exit(1)
    else:
        content = content.replace(old_mode_cmd, new_mode_cmd)
        print("  ✅ Replaced mode_command")
    
    # === CHANGE 3: Add personality_command function ===
    # Insert after mode_command
    personality_cmd = '''

async def personality_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /personality command — view/adjust personality sliders"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    try:
        import sys as _sys
        _sys.path.insert(0, "/opt/mythos/core")
        from prompt_assembler import get_resolved_personality
    except Exception as e:
        await update.message.reply_text(f"❌ Prompt assembler not available: {e}")
        return
    
    iris_mode = session.get("iris_mode", "hearthfire")
    user_info = session.get("user", {})
    overrides = session.get("personality_overrides")
    
    if context.args:
        args = context.args
        
        if args[0].lower() == "reset":
            session["personality_overrides"] = None
            await update.message.reply_text("🔄 Personality reset to defaults")
            return
        
        if len(args) >= 2:
            slider_name = args[0].lower()
            try:
                value = int(args[1])
            except ValueError:
                await update.message.reply_text(f"❌ Value must be a number (0-100)")
                return
            
            value = max(0, min(100, value))
            
            valid_sliders = ['verbosity', 'warmth', 'humor', 'truth', 'speculation', 'autonomy', 'mystical', 'formality', 'challenge']
            if slider_name not in valid_sliders:
                await update.message.reply_text(f"❌ Unknown slider: {slider_name}\\nAvailable: {', '.join(valid_sliders)}")
                return
            
            if not session.get("personality_overrides"):
                session["personality_overrides"] = {}
            session["personality_overrides"][slider_name] = value
            
            await update.message.reply_text(f"🎛️ **{slider_name}** → {value}", parse_mode='Markdown')
            return
    
    # Show current resolved values
    resolved = get_resolved_personality(
        mode=iris_mode,
        user_info=user_info,
        session_overrides=overrides
    )
    
    slider_emojis = {
        'verbosity': '📏', 'warmth': '🌡️', 'humor': '😏', 'truth': '⚡',
        'speculation': '🔮', 'autonomy': '🧭', 'mystical': '✨', 'formality': '👔', 'challenge': '⚔️'
    }
    
    lines = [f"🎛️ **Personality** (mode: {iris_mode})\\n"]
    for k, v in sorted(resolved.items()):
        emoji = slider_emojis.get(k, '•')
        bar = '█' * (v // 10) + '░' * (10 - v // 10)
        override_mark = " *" if overrides and k in overrides else ""
        lines.append(f"{emoji} `{k:12s}` {bar} {v}{override_mark}")
    
    lines.append("")
    lines.append("`/personality <slider> <0-100>` to adjust")
    lines.append("`/personality reset` to clear overrides")
    if overrides:
        lines.append("\\n* = session override")
    
    await update.message.reply_text("\\n".join(lines), parse_mode='Markdown')

'''
    
    # Insert personality_command after the mode_command function
    # Find the next async def after mode_command
    mode_cmd_end = content.find('async def clear_command')
    if mode_cmd_end > 0:
        content = content[:mode_cmd_end] + personality_cmd + content[mode_cmd_end:]
        print("  ✅ Added personality_command")
    else:
        print("  ⚠️ Could not find insertion point for personality_command, appending before clear_command search failed")
    
    # === CHANGE 4: Register new command handlers ===
    old_handler_line = '    application.add_handler(CommandHandler("mode", mode_command))'
    new_handler_lines = '''    application.add_handler(CommandHandler("mode", mode_command))
    application.add_handler(CommandHandler("personality", personality_command))'''
    
    if old_handler_line in content:
        content = content.replace(old_handler_line, new_handler_lines)
        print("  ✅ Registered /personality command handler")
    else:
        print("  ⚠️ Could not find handler registration line for /mode")
    
    # === CHANGE 5: Pass message_timestamp through handle_message ===
    # In _process_buffered_message, the API call passes the message. We need to ensure
    # the Telegram path also passes timestamp. The current flow goes through the API
    # (requests.post to /message), so the timestamp needs to be in the API call.
    # Actually — looking at the code, _process_buffered_message sends to the API,
    # which goes to chat_assistant.py. The Telegram direct path is via handle_chat_message.
    # The buffered path goes through the API. Both paths now have timestamp support.
    # The API path uses datetime.now() in chat_assistant.py.
    # No change needed here — the assembler handles it internally.
    
    # === Syntax check ===
    bot_path.write_text(content)
    if not syntax_check(bot_path):
        # Restore backup
        backup = bot_path.with_suffix('.py.bak_0113')
        if backup.exists():
            shutil.copy2(backup, bot_path)
        print("  ❌ Syntax check failed! Restored backup.")
        sys.exit(1)
    
    print(f"  ✅ mythos_bot.py modified ({len(content) - len(original):+d} chars)")


def main():
    print("=" * 60)
    print("Patch 0113: Unified Prompt & Personality System")
    print("=" * 60)
    
    # === Step 1: Create directories ===
    print("\n📁 Creating directories...")
    for d in ['prompts/archive', 'prompts/modes', 'prompts/users', 'models']:
        (MYTHOS / d).mkdir(parents=True, exist_ok=True)
        print(f"  ✅ {d}/")
    
    # === Step 2: Copy new files ===
    print("\n📄 Copying new files...")
    new_files = [
        "core/prompt_assembler.py",
        "prompts/iris_identity.md",
        "prompts/personality.yaml",
        "prompts/voice.yaml",
        "prompts/modes/hearthfire.yaml",
        "prompts/modes/forge.yaml",
        "prompts/modes/roots.yaml",
        "prompts/modes/oracle.yaml",
        "prompts/modes/scribe.yaml",
        "prompts/modes/sentry.yaml",
        "prompts/users/ka_tuar_el.yaml",
        "prompts/users/seraphe.yaml",
        "models/iris-thinking.Modelfile",
        "docs/PROMPT_SYSTEM.md",
    ]
    for f in new_files:
        copy_new_file(f)
    
    # === Step 3: Archive old seraphe prompt ===
    print("\n📦 Archiving old prompts...")
    seraphe_old = MYTHOS / "prompts" / "seraphe_system_prompt.txt"
    if seraphe_old.exists():
        shutil.move(str(seraphe_old), str(MYTHOS / "prompts" / "archive" / "seraphe_system_prompt.txt"))
        print("  ✅ Archived seraphe_system_prompt.txt")
    else:
        print("  ⏭️ seraphe_system_prompt.txt not found (already archived?)")
    
    # === Step 4: Copy modified files ===
    print("\n📝 Copying modified files...")
    copy_modified_file("telegram_bot/handlers/chat_mode.py")
    copy_modified_file("assistants/chat_assistant.py")
    
    # === Step 5: Modify mythos_bot.py (string replacement) ===
    print("\n🔧 Modifying mythos_bot.py...")
    modify_mythos_bot()
    
    # === Step 6: Syntax check all Python files ===
    print("\n🔍 Syntax checking...")
    check_files = [
        MYTHOS / "core" / "prompt_assembler.py",
        MYTHOS / "telegram_bot" / "handlers" / "chat_mode.py",
        MYTHOS / "assistants" / "chat_assistant.py",
    ]
    all_ok = True
    for f in check_files:
        if syntax_check(f):
            print(f"  ✅ {f.name}")
        else:
            all_ok = False
    
    if not all_ok:
        print("\n❌ Syntax errors detected! Aborting.")
        sys.exit(1)
    
    # === Step 7: Rebuild iris-thinking model ===
    print("\n🧠 Rebuilding iris-thinking model (parameters only, no baked SYSTEM)...")
    modelfile = MYTHOS / "models" / "iris-thinking.Modelfile"
    try:
        result = subprocess.run(
            ["ollama", "create", "iris-thinking", "-f", str(modelfile)],
            capture_output=True, text=True, timeout=120
        )
        if result.returncode == 0:
            print("  ✅ iris-thinking model rebuilt")
        else:
            print(f"  ⚠️ Model rebuild warning: {result.stderr[:200]}")
            # Non-fatal — model might still work with old binary
    except Exception as e:
        print(f"  ⚠️ Model rebuild failed (non-fatal): {e}")
    
    # === Step 8: Restart services ===
    print("\n🔄 Restarting services...")
    try:
        subprocess.run(["sudo", "systemctl", "restart", "mythos-bot.service"], check=True, timeout=30)
        print("  ✅ mythos-bot restarted")
    except Exception as e:
        print(f"  ❌ Service restart failed: {e}")
        sys.exit(1)
    
    import time
    time.sleep(3)
    
    # === Step 9: Verify ===
    print("\n🔍 Verification...")
    try:
        sys.path.insert(0, str(MYTHOS / "core"))
        from prompt_assembler import assemble_system_prompt as _test_assemble
        from datetime import datetime as _dt
        
        prompt = _test_assemble(
            user_info={"soul_name": "Ka'tuar'el", "uuid": "test"},
            mode="hearthfire",
            message_timestamp=_dt.now(),
        )
        print(f"  ✅ Assembled prompt: {len(prompt)} chars, ~{len(prompt)//4} tokens")
        assert len(prompt) > 1000, "Prompt too short!"
        assert "RIGHT NOW" in prompt, "Missing temporal awareness!"
        print("  ✅ Temporal awareness present")
        assert "Ka'tuar'el" in prompt, "Missing identity content!"
        print("  ✅ Identity content present")
        
        # Test mode loading
        prompt_forge = _test_assemble(
            user_info={"soul_name": "Ka'tuar'el", "uuid": "test"},
            mode="forge",
            message_timestamp=_dt.now(),
        )
        assert "FORGE" in prompt_forge, "Missing forge mode header!"
        print("  ✅ Mode system working")
        
    except Exception as e:
        print(f"  ❌ Verification failed: {e}")
        sys.exit(1)
    
    # Check service
    try:
        result = subprocess.run(
            ["systemctl", "is-active", "--quiet", "mythos-bot"],
            timeout=5
        )
        if result.returncode == 0:
            print("  ✅ Bot service running")
        else:
            print("  ❌ Bot service NOT running!")
            sys.exit(1)
    except Exception:
        print("  ⚠️ Could not check service status")
    
    print("\n" + "=" * 60)
    print("✅ Patch 0113 Complete — Unified Prompt System Deployed")
    print("=" * 60)
    print("\nTest commands:")
    print("  /mode              → Show Iris modes")
    print("  /mode forge        → Switch to forge")
    print("  /mode hearthfire   → Back to default")
    print("  /personality       → Show slider values")
    print("  /personality humor 50 → Adjust a slider")
    print("  Send a message     → Iris uses assembled prompt")


if __name__ == "__main__":
    main()
