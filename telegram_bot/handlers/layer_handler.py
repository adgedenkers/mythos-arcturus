#!/usr/bin/env python3
"""
Layer Handler — Telegram commands for toggling prompt layers.

Commands:
  /layer           — Show all layers and their status
  /layer list      — Same as /layer
  /layer on <name> — Enable a layer
  /layer off <name> — Disable a layer
  /layer info <name> — Show details about a layer
  /layer reset     — Disable all non-locked layers (back to baseline)

This is the control panel for Phase A prompt tuning.
"""
import logging
import sys

sys.path.insert(0, "/opt/mythos/core")

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def _get_assembler():
    """Import prompt_assembler at call time (not import time) to get fresh module."""
    from prompt_assembler import get_layer_status, toggle_layer, is_layer_enabled
    return get_layer_status, toggle_layer, is_layer_enabled


async def layer_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /layer commands."""
    args = context.args or []

    if not args or args[0] == 'list':
        await _show_layers(update)
    elif args[0] == 'on' and len(args) >= 2:
        await _toggle(update, args[1], True)
    elif args[0] == 'off' and len(args) >= 2:
        await _toggle(update, args[1], False)
    elif args[0] == 'info' and len(args) >= 2:
        await _show_info(update, args[1])
    elif args[0] == 'reset':
        await _reset_all(update)
    else:
        await update.message.reply_text(
            "**Prompt Layer Control**\n\n"
            "`/layer` — show all layers\n"
            "`/layer on <name>` — enable layer\n"
            "`/layer off <name>` — disable layer\n"
            "`/layer info <name>` — layer details\n"
            "`/layer reset` — disable all (baseline only)",
            parse_mode='Markdown'
        )


async def _show_layers(update: Update):
    """Show all layers and their status."""
    get_layer_status, _, _ = _get_assembler()
    status = get_layer_status()

    lines = ["**Prompt Layers**\n"]
    for name, info in status.items():
        if info.get('locked'):
            icon = "🔒"
        elif info.get('enabled'):
            icon = "✅"
        else:
            icon = "⬜"

        desc = info.get('description', '')
        # Truncate description for display
        if len(desc) > 60:
            desc = desc[:57] + "..."

        lines.append(f"{icon} `{name}` — {desc}")

    enabled_count = sum(1 for v in status.values() if v.get('enabled'))
    total = len(status)
    lines.append(f"\n{enabled_count}/{total} layers active.")
    lines.append("\n`/layer on <name>` or `/layer off <name>` to toggle.")

    await update.message.reply_text("\n".join(lines), parse_mode='Markdown')


async def _toggle(update: Update, layer_name: str, enabled: bool):
    """Toggle a layer on or off."""
    _, toggle_layer, _ = _get_assembler()
    success, message = toggle_layer(layer_name, enabled)

    if success:
        state = "✅ ON" if enabled else "⬜ OFF"
        await update.message.reply_text(
            f"{state} — `{layer_name}`\n\n{message}\n\n"
            f"Takes effect on the next message.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(f"❌ {message}", parse_mode='Markdown')


async def _show_info(update: Update, layer_name: str):
    """Show detailed info about a specific layer."""
    get_layer_status, _, _ = _get_assembler()
    status = get_layer_status()

    if layer_name not in status:
        await update.message.reply_text(
            f"❌ Unknown layer: `{layer_name}`\n\n"
            f"Available: {', '.join(f'`{k}`' for k in status.keys())}",
            parse_mode='Markdown'
        )
        return

    info = status[layer_name]
    state = "✅ ENABLED" if info.get('enabled') else "⬜ DISABLED"
    locked = " (🔒 locked)" if info.get('locked') else ""

    msg = (
        f"**Layer: `{layer_name}`** {state}{locked}\n\n"
        f"**What it does:**\n{info.get('description', 'No description.')}\n\n"
        f"**Notes:**\n{info.get('notes', 'None.')}"
    )

    await update.message.reply_text(msg, parse_mode='Markdown')


async def _reset_all(update: Update):
    """Disable all non-locked layers."""
    get_layer_status, toggle_layer, _ = _get_assembler()
    status = get_layer_status()

    disabled = []
    for name, info in status.items():
        if info.get('enabled') and not info.get('locked'):
            success, _ = toggle_layer(name, False)
            if success:
                disabled.append(name)

    if disabled:
        names = ", ".join(f"`{n}`" for n in disabled)
        await update.message.reply_text(
            f"🔄 **Reset to baseline.**\n\n"
            f"Disabled: {names}\n\n"
            f"Only baseline context is active now. "
            f"Enable layers one at a time with `/layer on <name>`.",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "Already at baseline — no layers were enabled.",
            parse_mode='Markdown'
        )
