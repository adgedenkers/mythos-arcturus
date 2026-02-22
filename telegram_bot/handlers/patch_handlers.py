#!/usr/bin/env python3
"""
Telegram Bot Handlers for Patch Management

Commands:
  /patch                  - Show patch system status and help
  /patch_status           - Show current version and recent patches
  /patch_list             - List available patches to apply
  /patch_apply <name>     - Apply a specific patch
  /patch_rollback [tag]   - Rollback to a previous state
"""

import os
import subprocess
import json
import logging
import re
from pathlib import Path
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Configuration
MYTHOS_ROOT = Path("/opt/mythos")
PATCH_DIR = MYTHOS_ROOT / "patches"
PATCH_SCRIPTS = PATCH_DIR / "scripts"
PATCH_LOGS = PATCH_DIR / "logs"

# Authorized users (from .env: TELEGRAM_ID_KA, TELEGRAM_ID_SERAPHE)
AUTHORIZED_IDS = set()


def _load_authorized_ids():
    """Load authorized Telegram IDs from environment"""
    global AUTHORIZED_IDS
    for key in ['TELEGRAM_ID_KA', 'TELEGRAM_ID_SERAPHE']:
        val = os.getenv(key)
        if val:
            try:
                AUTHORIZED_IDS.add(int(val))
            except ValueError:
                pass
    logger.info(f"Authorized patch users: {AUTHORIZED_IDS}")


_load_authorized_ids()


def _is_authorized(user_id: int) -> bool:
    """Check if user is authorized for patch operations"""
    return user_id in AUTHORIZED_IDS


def _run_git(*args) -> tuple[bool, str]:
    """Run a git command and return (success, output)"""
    try:
        result = subprocess.run(
            ["git"] + list(args),
            cwd=MYTHOS_ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)


def _get_current_version() -> str:
    """Get current git version tag"""
    success, output = _run_git("tag", "-l", "v*", "--sort=-v:refname")
    if success and output.strip():
        return output.strip().split('\n')[0]
    return "v0.0.0"


def _get_recent_tags(limit: int = 5) -> list[dict]:
    """Get recent tags with dates"""
    tags = []
    success, output = _run_git("tag", "-l", "--sort=-v:refname")
    if success:
        for tag in output.strip().split('\n')[:limit]:
            if tag:
                _, date_out = _run_git("log", "-1", "--format=%ci", tag)
                tags.append({
                    "tag": tag,
                    "date": date_out.strip()[:19] if date_out else "unknown"
                })
    return tags


def _get_pending_patches() -> list[str]:
    """Get list of patch directories that haven't been applied"""
    patches = []
    if PATCH_DIR.exists():
        for d in sorted(PATCH_DIR.iterdir()):
            if d.is_dir() and d.name.startswith("patch_"):
                # Check if it has an install.sh
                has_install = (d / "install.sh").exists()
                patches.append(f"{d.name}" + (" ✓" if has_install else ""))
    return patches


def _get_recent_logs(limit: int = 5) -> list[dict]:
    """Get recent patch application logs"""
    logs = []
    if PATCH_LOGS.exists():
        log_files = sorted(PATCH_LOGS.glob("*.json"), reverse=True)[:limit]
        for f in log_files:
            try:
                with open(f) as fp:
                    logs.append(json.load(fp))
            except Exception:
                pass
    return logs


def _get_highest_patch_number(logs: list[dict]) -> str:
    """
    Find the highest real patch number across all logs.
    Ignores test patches (9999) and returns the actual latest patch number.
    """
    highest = 0
    for log in logs:
        patch_name = log.get("patch", log.get("target_tag", ""))
        m = re.search(r"patch_(\d{4})", str(patch_name))
        if m:
            num = int(m.group(1))
            # Skip test patches (9999, 0000)
            if num < 9000 and num > highest:
                highest = num
    return f"{highest:04d}" if highest > 0 else "?"


# ============================================================
# Command Handlers
# ============================================================

async def patch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /patch - Show patch system overview and help
    """
    user_id = update.effective_user.id
    
    if not _is_authorized(user_id):
        await update.message.reply_text("❌ Not authorized for patch operations.")
        return
    
    version = _get_current_version()
    
    help_text = f"""🔧 <b>Mythos Patch System</b>

<b>Current Version:</b> <code>{version}</code>

<b>Commands:</b>
• /patch_status - Version info &amp; recent activity
• /patch_list - Available patches to apply
• /patch_apply &lt;name&gt; - Apply a specific patch
• /patch_rollback - Show rollback options
• /patch_rollback &lt;tag&gt; - Rollback to specific tag

<b>Auto-Processing:</b>
Patch zips dropped in ~/Downloads are automatically:
1. Extracted to /opt/mythos/patches/
2. Git-tagged before &amp; after
3. Pushed to GitHub

<b>Naming Convention:</b>
<code>patch_NNNN_description.zip</code>"""
    
    await update.message.reply_text(help_text, parse_mode='HTML')


async def patch_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /patch_status - Show current version and recent patches
    """
    user_id = update.effective_user.id
    
    if not _is_authorized(user_id):
        await update.message.reply_text("❌ Not authorized for patch operations.")
        return
    
    version = _get_current_version()
    tags = _get_recent_tags(5)
    logs = _get_recent_logs(20)  # Read more logs to find highest real patch
    
    has_remote, remote_url = _run_git("remote", "get-url", "origin")
    
    # Find the highest real patch number (not test patches)
    latest_patch = _get_highest_patch_number(logs)
    
    msg = "📊 <b>Patch Status</b>\n\n"
    msg += f"<b>Latest Patch:</b> <code>#{latest_patch}</code>\n"
    msg += f"<b>Git Tag:</b> <code>{version}</code>\n"
    github = "✓ Connected" if has_remote else "✗ Not configured"
    msg += f"<b>GitHub:</b> {github}\n\n"
    
    # Show recent patches, filtering out test patches from display
    msg += "<b>Recent Patches:</b>\n"
    display_count = 0
    for log in (logs or []):
        if display_count >= 5:
            break
        pname = log.get("patch", log.get("target_tag", "unknown"))
        m = re.search(r"patch_(\d{4})_(.+?)\.zip", str(pname))
        if m:
            num = int(m.group(1))
            # Skip test patches from the display list
            if num >= 9000:
                continue
            status = "✓" if log.get("status") == "success" else "✗"
            name = m.group(2).replace("_", " ")
            msg += f"  {status} <code>#{m.group(1)}</code> {name}\n"
            display_count += 1
        else:
            # Non-standard patch name — show but don't count toward limit aggressively
            status = "✓" if log.get("status") == "success" else "✗"
            msg += f"  {status} {pname}\n"
            display_count += 1
    
    if tags:
        msg += "\n<b>Git Tags:</b>\n"
        for t in tags[:5]:
            tag_name = t["tag"]
            tag_date = t["date"][:10]
            msg += f"  <code>{tag_name}</code> ({tag_date})\n"
    
    await update.message.reply_text(msg, parse_mode="HTML")


async def patch_list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /patch_list - List available patches
    """
    user_id = update.effective_user.id
    
    if not _is_authorized(user_id):
        await update.message.reply_text("❌ Not authorized for patch operations.")
        return
    
    patches = _get_pending_patches()
    
    if not patches:
        await update.message.reply_text("📦 No patches in <code>/opt/mythos/patches/</code>", parse_mode='HTML')
        return
    
    msg = "📦 <b>Available Patches:</b>\n\n"
    for p in patches:
        msg += f"• <code>{p}</code>\n"
    
    msg += "\nUse /patch_apply &lt;name&gt; to apply."
    
    await update.message.reply_text(msg, parse_mode='HTML')


async def patch_apply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /patch_apply <patch_name> - Apply a specific patch
    """
    user_id = update.effective_user.id
    
    if not _is_authorized(user_id):
        await update.message.reply_text("❌ Not authorized for patch operations.")
        return
    
    if not context.args:
        await update.message.reply_text(
            "Usage: /patch_apply &lt;patch_name&gt;\n\n"
            "Use /patch_list to see available patches.",
            parse_mode='HTML'
        )
        return
    
    patch_name = context.args[0]
    patch_path = PATCH_DIR / patch_name
    
    if not patch_path.exists():
        await update.message.reply_text(f"❌ Patch not found: <code>{patch_name}</code>", parse_mode='HTML')
        return
    
    await update.message.reply_text(f"⏳ Applying patch: <code>{patch_name}</code>...", parse_mode='HTML')
    
    try:
        script = PATCH_SCRIPTS / "patch_apply.sh"
        if not script.exists():
            await update.message.reply_text("❌ patch_apply.sh not found!")
            return
        
        result = subprocess.run(
            [str(script), str(patch_path)],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            new_version = _get_current_version()
            await update.message.reply_text(
                f"✅ Patch applied successfully!\n\n"
                f"<b>New version:</b> <code>{new_version}</code>",
                parse_mode='HTML'
            )
        else:
            error_msg = result.stderr[-500:] if result.stderr else "Unknown error"
            await update.message.reply_text(
                f"❌ Patch failed!\n\n<pre>{error_msg}</pre>",
                parse_mode='HTML'
            )
    
    except subprocess.TimeoutExpired:
        await update.message.reply_text("❌ Patch timed out (5 min limit)")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def patch_rollback_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /patch_rollback [tag] - Show rollback options or rollback to specific tag
    """
    user_id = update.effective_user.id
    
    if not _is_authorized(user_id):
        await update.message.reply_text("❌ Not authorized for patch operations.")
        return
    
    # No arguments - show available rollback points
    if not context.args:
        tags = _get_recent_tags(10)
        
        pre_tags = [t for t in tags if t['tag'].startswith('pre-')]
        version_tags = [t for t in tags if t['tag'].startswith('v')]
        
        msg = "🔄 <b>Rollback Options</b>\n\n"
        
        if pre_tags:
            msg += "<b>Pre-patch snapshots:</b>\n"
            for t in pre_tags[:5]:
                msg += f"• <code>{t['tag']}</code>\n"
        
        if version_tags:
            msg += "\n<b>Version tags:</b>\n"
            for t in version_tags[:5]:
                msg += f"• <code>{t['tag']}</code> ({t['date'][:10]})\n"
        
        msg += "\nUse /patch_rollback &lt;tag&gt; to rollback."
        
        await update.message.reply_text(msg, parse_mode='HTML')
        return
    
    # Rollback to specific tag
    target_tag = context.args[0]
    
    # Verify tag exists
    success, _ = _run_git("rev-parse", target_tag)
    if not success:
        await update.message.reply_text(f"❌ Tag not found: <code>{target_tag}</code>", parse_mode='HTML')
        return
    
    await update.message.reply_text(
        f"⚠️ <b>Confirm Rollback</b>\n\n"
        f"Rolling back to: <code>{target_tag}</code>\n\n"
        f"Reply with /patch_rollback_confirm {target_tag} to proceed.",
        parse_mode='HTML'
    )


async def patch_rollback_confirm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /patch_rollback_confirm <tag> - Actually perform the rollback
    """
    user_id = update.effective_user.id
    
    if not _is_authorized(user_id):
        await update.message.reply_text("❌ Not authorized for patch operations.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /patch_rollback_confirm &lt;tag&gt;", parse_mode='HTML')
        return
    
    target_tag = context.args[0]
    
    await update.message.reply_text(f"⏳ Rolling back to <code>{target_tag}</code>...", parse_mode='HTML')
    
    try:
        # Use the rollback script with auto-confirm via stdin
        script = PATCH_SCRIPTS / "patch_rollback.sh"
        if not script.exists():
            await update.message.reply_text("❌ patch_rollback.sh not found!")
            return
        
        # We need to bypass the confirmation prompt
        # Instead, run git commands directly
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pre_rollback_tag = f"pre-rollback-{timestamp}"
        
        # Save current state
        _run_git("add", "-A")
        _run_git("commit", "-m", f"Auto-commit before rollback to {target_tag}")
        _run_git("tag", "-a", pre_rollback_tag, "-m", f"State before rollback to {target_tag}")
        
        # Checkout target state
        success, output = _run_git("checkout", target_tag, "--", ".")
        if not success:
            await update.message.reply_text(f"❌ Rollback failed:\n<pre>{output}</pre>", parse_mode='HTML')
            return
        
        # Commit rollback
        _run_git("add", "-A")
        _run_git("commit", "-m", f"Rollback to {target_tag}")
        
        # Push
        _run_git("push", "origin", "main", "--tags")
        
        # Restart service
        subprocess.run(["sudo", "systemctl", "restart", "mythos-patch-monitor"], capture_output=True)
        
        await update.message.reply_text(
            f"✅ Rollback complete!\n\n"
            f"<b>Rolled back to:</b> <code>{target_tag}</code>\n"
            f"<b>Previous state saved as:</b> <code>{pre_rollback_tag}</code>",
            parse_mode='HTML'
        )
    
    except Exception as e:
        await update.message.reply_text(f"❌ Rollback error: {e}")


# Export all handlers
__all__ = [
    'patch_command',
    'patch_status_command', 
    'patch_list_command',
    'patch_apply_command',
    'patch_rollback_command',
    'patch_rollback_confirm_command'
]
