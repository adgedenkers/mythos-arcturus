#!/usr/bin/env python3
"""
Voice Profile Handler — Switch Iris's voice between profiles.

Commands:
  /voice              — Show current voice profile and list available
  /voice claude       — Switch to Claude voice
  /voice gpt4o        — Switch to GPT-4o voice
  /voice iris         — Switch back to Iris default
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

try:
    from prompt_assembler import (
        get_voice_profile,
        set_voice_profile,
        get_available_voice_profiles,
    )
    _assembler_available = True
except ImportError:
    _assembler_available = False
    logger.error("Could not import prompt_assembler — voice commands unavailable")


async def voice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /voice command."""
    if not _assembler_available:
        await update.message.reply_text("⚠️ Prompt assembler not available.")
        return

    args = context.args if context.args else []

    if not args:
        # Show current profile and list available
        current = get_voice_profile()
        profiles = get_available_voice_profiles()

        lines = [f"🎙️ **Voice Profile: {current}**\n"]
        lines.append("Available profiles:")
        for p in profiles:
            marker = "→" if p.get('active') else " "
            lines.append(f"  {marker} `{p['name']}` — {p.get('description', '')}")
        lines.append(f"\nSwitch: `/voice claude` or `/voice gpt4o` or `/voice iris`")

        await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
        return

    profile_name = args[0].lower().strip()

    # Normalize common aliases
    aliases = {
        'default': 'iris',
        'home': 'iris',
        'gpt': 'gpt4o',
        'gpt4': 'gpt4o',
        'openai': 'gpt4o',
    }
    profile_name = aliases.get(profile_name, profile_name)

    success = set_voice_profile(profile_name)

    if success:
        profiles = get_available_voice_profiles()
        desc = ""
        for p in profiles:
            if p['name'] == profile_name:
                desc = p.get('description', '')
                break
        await update.message.reply_text(
            f"🎙️ Voice → **{profile_name}**\n{desc}",
            parse_mode='Markdown'
        )
    else:
        available = get_available_voice_profiles()
        names = ", ".join(f"`{p['name']}`" for p in available)
        await update.message.reply_text(
            f"⚠️ Voice profile `{profile_name}` not found.\nAvailable: {names}",
            parse_mode='Markdown'
        )
