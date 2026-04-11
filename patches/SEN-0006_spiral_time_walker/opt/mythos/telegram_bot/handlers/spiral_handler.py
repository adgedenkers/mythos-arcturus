"""
SEN-0006: Spiral Time Walker — Telegram Handler

Commands:
  /spiral          — current position + transit pressure
  /spiral reset    — reset spiral to today = new Cycle 1, Day 1
  /spiral history  — show epoch history
  /spiral brief    — force-generate today's morning brief
"""

import logging
import sys
from datetime import date

log = logging.getLogger("iris.handlers.spiral")

# ── Handler Registration ──────────────────────────────────────────────────────

def register(application):
    """Register /spiral command handler with the Telegram application."""
    from telegram.ext import CommandHandler
    application.add_handler(CommandHandler("spiral", handle_spiral))
    log.info("Registered /spiral command handler")


# ── Main Handler ──────────────────────────────────────────────────────────────

async def handle_spiral(update, context):
    """Handle /spiral and subcommands."""
    args = context.args or []
    subcommand = args[0].lower() if args else "status"

    if subcommand == "reset":
        await _handle_reset(update, context, args[1:])
    elif subcommand == "history":
        await _handle_history(update, context)
    elif subcommand == "brief":
        await _handle_force_brief(update, context)
    else:
        await _handle_status(update, context)


async def _handle_status(update, context):
    """Show current spiral position and transit pressure."""
    try:
        sys.path.insert(0, "/opt/mythos")
        from astrology.spiral import get_spiral_status
        status = get_spiral_status()
        await update.message.reply_text(status, parse_mode="Markdown")
    except Exception as e:
        log.error(f"spiral handler status error: {e}")
        await update.message.reply_text(f"⚠️ Spiral engine error: {e}")


async def _handle_reset(update, context, extra_args):
    """Reset spiral — today becomes new Cycle 1, Day 1."""
    try:
        sys.path.insert(0, "/opt/mythos")
        from astrology.spiral import reset_spiral, get_position

        reason = " ".join(extra_args) if extra_args else "Manual reset via Telegram"
        pos = reset_spiral("adge", reason=reason)

        if pos:
            msg = (
                f"🔄 *Spiral Reset*\n\n"
                f"New epoch {pos.epoch_number} begins today.\n"
                f"You are now on: *{pos.full_label}*\n"
                f"_{pos.day_focus}_\n\n"
                f"Epoch started: {pos.epoch_start.strftime('%B %-d, %Y')}"
            )
        else:
            msg = "⚠️ Reset completed but could not retrieve new position."

        await update.message.reply_text(msg, parse_mode="Markdown")
    except Exception as e:
        log.error(f"spiral handler reset error: {e}")
        await update.message.reply_text(f"⚠️ Reset error: {e}")


async def _handle_history(update, context):
    """Show epoch history."""
    try:
        sys.path.insert(0, "/opt/mythos")
        from astrology.spiral import get_epoch_history

        history = get_epoch_history("adge")
        if not history:
            await update.message.reply_text("No epoch history found.")
            return

        lines = ["📜 *Spiral Epoch History*\n"]
        for ep in history:
            started = ep["started_at"]
            ended = ep["ended_at"]
            if hasattr(started, "strftime"):
                started = started.strftime("%b %-d, %Y")
            if ended and hasattr(ended, "strftime"):
                ended = ended.strftime("%b %-d, %Y")
            elif not ended:
                ended = "active"

            reason = ep.get("reason") or ""
            lines.append(
                f"*Epoch {ep['epoch_number']}* — {started} → {ended}\n"
                + (f"  _{reason}_" if reason else "")
            )

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        log.error(f"spiral handler history error: {e}")
        await update.message.reply_text(f"⚠️ History error: {e}")


async def _handle_force_brief(update, context):
    """Force-generate today's morning brief (bypasses delivery tracking)."""
    try:
        sys.path.insert(0, "/opt/mythos")
        from astrology.spiral import build_brief_context

        brief = build_brief_context(force=True)
        if brief:
            # Strip the INSTRUCTION FOR IRIS block for direct Telegram display
            display = brief.split("INSTRUCTION FOR IRIS:")[0].strip()
            await update.message.reply_text(
                f"```\n{display}\n```",
                parse_mode="Markdown"
            )
        else:
            await update.message.reply_text("⚠️ Could not generate brief.")
    except Exception as e:
        log.error(f"spiral handler force brief error: {e}")
        await update.message.reply_text(f"⚠️ Brief error: {e}")
