#!/usr/bin/env python3
"""
Telegram Bot Handler: /registry
================================
Shows Neo4j application registry audit.

Commands:
  /registry              — Full audit: all apps, node counts, orphans
  /registry <app_id>     — Detail for one app
  /registry orphans      — Show only orphan labels
  /registry cleanup <id> — Show cleanup query for an app
"""

import os
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def _get_neo4j_driver():
    """Get Neo4j driver from environment."""
    from neo4j import GraphDatabase
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'password')
    return GraphDatabase.driver(uri, auth=(user, password))


async def handle_registry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /registry command."""
    try:
        from core.app_registry import AppRegistry, APP_DEFINITIONS

        args = context.args if context.args else []
        driver = _get_neo4j_driver()

        try:
            registry = AppRegistry(neo4j_driver=driver)

            if not args:
                # Full audit
                report = registry.format_audit_report(include_orphans=True)
                # Telegram has 4096 char limit
                if len(report) > 4000:
                    # Send in chunks
                    chunks = _split_message(report, 4000)
                    for chunk in chunks:
                        await update.message.reply_text(chunk)
                else:
                    await update.message.reply_text(report)

            elif args[0] == 'orphans':
                orphans = registry.find_orphan_labels()
                if orphans:
                    lines = ["⚠️ ORPHAN LABELS (not registered to any app):\n"]
                    for o in orphans:
                        lines.append(f"  • {o['label']}: {o['count']:,} nodes")
                    lines.append(f"\nTotal orphan nodes: {sum(o['count'] for o in orphans):,}")
                    await update.message.reply_text('\n'.join(lines))
                else:
                    await update.message.reply_text("✅ No orphan labels found. All nodes are registered.")

            elif args[0] == 'cleanup' and len(args) > 1:
                app_id = args[1]
                if app_id not in APP_DEFINITIONS:
                    await update.message.reply_text(
                        f"❌ Unknown app: {app_id}\n\n"
                        f"Available: {', '.join(sorted(APP_DEFINITIONS.keys()))}"
                    )
                    return

                # Show count query first
                count_q = registry.get_cleanup_query(app_id, dry_run=True)
                delete_q = registry.get_cleanup_query(app_id, dry_run=False)
                audit = registry.audit_app(app_id)

                lines = [f"🗑️ Cleanup queries for: {app_id}"]
                if audit:
                    lines.append(f"Total nodes: {audit['total_nodes']:,}")
                    if registry.is_protected(app_id):
                        lines.append("🔒 This app is PROTECTED")
                lines.append(f"\n--- COUNT (safe) ---\n{count_q}")
                lines.append(f"\n--- DELETE (destructive) ---\n{delete_q}")
                lines.append("\n⚠️ Run the COUNT query first. Only run DELETE if you're sure.")

                await update.message.reply_text('\n'.join(lines))

            elif args[0] == 'apps':
                # Just list app IDs
                lines = ["📦 Registered Applications:\n"]
                for app_id, defn in sorted(APP_DEFINITIONS.items()):
                    protected = " 🔒" if defn.get('protected') else ""
                    lines.append(f"  • {app_id}{protected} — {defn['display_name']}")
                lines.append(f"\nTotal: {len(APP_DEFINITIONS)} apps")
                lines.append("\nUse /registry <app_id> for details")
                await update.message.reply_text('\n'.join(lines))

            else:
                # Assume it's an app_id
                app_id = args[0]
                if app_id not in APP_DEFINITIONS:
                    await update.message.reply_text(
                        f"❌ Unknown app: {app_id}\n\n"
                        f"Available: {', '.join(sorted(APP_DEFINITIONS.keys()))}"
                    )
                    return

                audit = registry.audit_app(app_id)
                defn = APP_DEFINITIONS[app_id]

                lines = [f"📦 {defn['display_name']}"]
                if defn.get('protected'):
                    lines.append("🔒 PROTECTED — requires explicit confirmation to delete")
                lines.append(f"\n{defn['description']}\n")
                lines.append(f"Source files:")
                for f in defn['source_files']:
                    lines.append(f"  {f}")
                lines.append(f"\nOwned labels ({len(defn['owned_labels'])}):")
                if audit:
                    for label in defn['owned_labels']:
                        count = audit['labels'].get(label, 0)
                        lines.append(f"  • {label}: {count:,}")
                    lines.append(f"\nTotal nodes: {audit['total_nodes']:,}")
                else:
                    for label in defn['owned_labels']:
                        lines.append(f"  • {label}")

                lines.append(f"\nOwned relationships ({len(defn['owned_relationships'])}):")
                # Show first 10, then count remainder
                shown = defn['owned_relationships'][:10]
                remaining = len(defn['owned_relationships']) - 10
                for r in shown:
                    lines.append(f"  • {r}")
                if remaining > 0:
                    lines.append(f"  ... and {remaining} more")

                await update.message.reply_text('\n'.join(lines))

        finally:
            driver.close()

    except ImportError as e:
        await update.message.reply_text(f"❌ Import error: {e}")
    except Exception as e:
        logger.error(f"Registry command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


def _split_message(text: str, max_len: int) -> list:
    """Split a long message into chunks at newline boundaries."""
    chunks = []
    current = ""
    for line in text.split('\n'):
        if len(current) + len(line) + 1 > max_len:
            chunks.append(current)
            current = line
        else:
            current = current + '\n' + line if current else line
    if current:
        chunks.append(current)
    return chunks
