"""
iris_integrity_handler.py — Telegram handler for /iris_integrity (NEU-0005)

Commands:
  /iris_integrity          — Show health summary (fast, reads latest scan)
  /iris_integrity scan     — Run a fresh fast scan then show summary
  /iris_integrity full     — Run full scan (files + tables + services, ~60s)
  /iris_integrity context  — Show what Iris carries in her awareness
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger("mythos.iris.integrity")


async def iris_integrity_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /iris_integrity command."""
    import sys
    sys.path.insert(0, '/opt/mythos/iris/integrity')
    from iris_integrity import (
        run_integrity_scan,
        read_latest_integrity_report,
        build_health_summary,
        format_telegram_report,
        format_iris_context,
    )

    args = context.args or []
    subcommand = args[0].lower() if args else "status"

    msg = update.message

    if subcommand == "scan":
        await msg.reply_text("🔍 Running integrity scan (services + tables)...")
        run_integrity_scan(fast=True)
        health = build_health_summary()
        report = format_telegram_report(health)
        await msg.reply_text(report, parse_mode="Markdown")

    elif subcommand == "full":
        await msg.reply_text("🔍 Running full integrity scan (this takes ~60s)...")
        run_integrity_scan(fast=False)
        health = build_health_summary()
        report = format_telegram_report(health)
        await msg.reply_text(report, parse_mode="Markdown")

    elif subcommand == "context":
        health = build_health_summary()
        ctx_str = format_iris_context(health)
        await msg.reply_text(
            f"*What I carry in my awareness:*\n\n`{ctx_str}`",
            parse_mode="Markdown"
        )

    else:
        # Default: status from latest scan
        health = build_health_summary()
        if health.get("scan_age") == "never":
            await msg.reply_text(
                "No integrity scan has been run yet.\n"
                "Use /iris\\_integrity scan to run one.",
                parse_mode="Markdown"
            )
            return
        report = format_telegram_report(health)
        await msg.reply_text(report, parse_mode="Markdown")
