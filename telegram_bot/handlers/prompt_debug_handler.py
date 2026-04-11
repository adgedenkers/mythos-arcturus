#!/usr/bin/env python3
"""
Prompt Debug Handler — /prompt_debug command
=============================================
Shows the last assembled system prompt so you can see exactly
what Iris received. Essential for tuning prompt layers.

Usage:
  /prompt_debug         — Show prompt summary (token count, active flags)
  /prompt_debug full    — Show the full system prompt text
  /prompt_debug flags   — Show only the feature flag states
"""

import logging
import requests
import os
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

API_URL = "https://mythos-api.denkers.co"
API_KEY = os.getenv('API_KEY_TELEGRAM_BOT')


async def prompt_debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /prompt_debug command."""
    args = context.args
    show_full = args and args[0].lower() == 'full'
    show_flags = args and args[0].lower() == 'flags'

    try:
        # Get prompt data from API
        response = requests.get(
            f"{API_URL}/debug/last_prompt",
            headers={"X-API-Key": API_KEY},
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            prompt_text = data.get('prompt', '(empty)')
            tokens = data.get('tokens', 0)
            flags = data.get('flags', {})

            if show_flags:
                lines = ["🔧 **Prompt Layer Flags**\n"]
                for flag, enabled in flags.items():
                    emoji = "✅" if enabled else "❌"
                    lines.append(f"{emoji} `{flag}`")
                await update.message.reply_text("\n".join(lines), parse_mode='Markdown')
                return

            if show_full:
                # Send full prompt, chunked if needed
                header = f"📋 **Full System Prompt** (~{tokens} tokens)\n\n"
                full = header + f"```\n{prompt_text[:3800]}\n```"
                await update.message.reply_text(full, parse_mode='Markdown')

                # Send remainder if truncated
                if len(prompt_text) > 3800:
                    remaining = prompt_text[3800:]
                    chunks = [remaining[i:i+3800] for i in range(0, len(remaining), 3800)]
                    for chunk in chunks:
                        await update.message.reply_text(f"```\n{chunk}\n```", parse_mode='Markdown')
                return

            # Default: summary view
            lines = [
                f"🧠 **Prompt Debug**",
                f"",
                f"Tokens: ~{tokens}",
                f"Chars: {len(prompt_text)}",
                f"",
                "**Layers:**",
            ]
            for flag, enabled in flags.items():
                emoji = "✅" if enabled else "❌"
                clean_name = flag.replace("ENABLE_", "").lower().replace("_", " ")
                lines.append(f"  {emoji} {clean_name}")

            lines.append("")
            lines.append("`/prompt_debug full` — see full prompt")
            lines.append("`/prompt_debug flags` — flags only")

            await update.message.reply_text("\n".join(lines), parse_mode='Markdown')

        elif response.status_code == 404:
            await update.message.reply_text("No prompt assembled yet — send a message first.")
        else:
            await update.message.reply_text(f"❌ API returned {response.status_code}")

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")
