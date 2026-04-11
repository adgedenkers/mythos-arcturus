#!/usr/bin/env python3
"""
Grid Manifest Handler — /grid command for Telegram
===================================================
Inspect the processing manifest for any exchange.

Commands:
    /grid                   → Show last exchange manifest
    /grid <exchange_id>     → Show manifest for specific exchange
    /grid stats             → Processing stats for last 24h
    /grid versions          → Show node-layer version registry
    /grid stale <node>      → Show exchanges needing reprocessing

Stream: NEU
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger('handler.grid_manifest')


async def handle_grid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /grid command."""
    import sys
    sys.path.insert(0, '/opt/mythos/neuro')

    args = context.args if context.args else []
    subcommand = args[0].lower() if args else 'last'

    try:
        if subcommand == 'stats':
            await _show_stats(update)
        elif subcommand == 'versions':
            await _show_versions(update)
        elif subcommand == 'stale':
            node = args[1] if len(args) > 1 else None
            await _show_stale(update, node)
        elif subcommand == 'last':
            await _show_last(update)
        else:
            # Assume it's an exchange_id
            await _show_manifest(update, subcommand)
    except Exception as e:
        logger.error(f"/grid error: {e}", exc_info=True)
        await update.message.reply_text(f"Error: {e}")


async def _show_last(update):
    """Show manifest for the most recent exchange."""
    import psycopg2
    from psycopg2.extras import RealDictCursor
    import os

    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        cursor_factory=RealDictCursor,
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT exchange_id, processed_at
        FROM grid_processing_manifest
        ORDER BY processed_at DESC
        LIMIT 1
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        await update.message.reply_text("No grid processing manifest entries yet.")
        return

    await _show_manifest(update, row['exchange_id'])


async def _show_manifest(update, exchange_id: str):
    """Show full manifest for an exchange."""
    from grid_manifest import ManifestWriter

    writer = ManifestWriter()
    entries = writer.get_exchange_manifest(exchange_id)

    if not entries:
        await update.message.reply_text(f"No manifest found for exchange: {exchange_id[:24]}...")
        return

    lines = [f"🔍 Grid Manifest: {exchange_id[:24]}...\n"]

    # Group by node
    nodes = {}
    for e in entries:
        node = e['node']
        if node not in nodes:
            nodes[node] = []
        nodes[node].append(e)

    node_emoji = {
        'anchor': '⛰️', 'echo': '🌊', 'beacon': '🔥', 'synth': '💨',
        'nexus': '⏳', 'mirror': '🪞', 'glyph': '🔣', 'harmonia': '💗',
        'gateway': '🚪',
    }

    for node, layers in sorted(nodes.items()):
        emoji = node_emoji.get(node, '•')
        lines.append(f"\n{emoji} {node.upper()}")
        for l in sorted(layers, key=lambda x: x['layer']):
            layer = l['layer']
            version = l['version']
            if l['activated']:
                ext = l.get('extracted_count', 0)
                ms = l.get('processing_ms', '?')
                summary = l.get('output_summary', '')[:60]
                lines.append(f"  L{layer} v{version} ✅ {ext} extracted ({ms}ms)")
                if summary:
                    lines.append(f"    → {summary}")
            else:
                reason = l.get('skipped_reason', 'unknown')
                lines.append(f"  L{layer} v{version} ⬜ skipped: {reason}")

    await update.message.reply_text("\n".join(lines))


async def _show_stats(update):
    """Show processing stats."""
    from grid_manifest import ManifestWriter

    writer = ManifestWriter()
    stats = writer.get_processing_stats(hours=24)

    if not stats or not stats.get('total_activations'):
        await update.message.reply_text("No grid processing in the last 24 hours.")
        return

    lines = [
        "📊 Grid Processing Stats (24h)\n",
        f"Exchanges processed: {stats.get('unique_exchanges', 0)}",
        f"Total activations: {stats.get('fired', 0)}",
        f"Skipped: {stats.get('skipped', 0)}",
        f"Knowledge extracted: {stats.get('total_extractions', 0)}",
        f"Avg processing time: {int(stats.get('avg_ms', 0))}ms",
        f"Last processed: {stats.get('last_processed', 'never')}",
    ]
    await update.message.reply_text("\n".join(lines))


async def _show_versions(update):
    """Show version registry."""
    from grid_manifest import VersionRegistry

    registry = VersionRegistry()
    summary = registry.get_status_summary()

    lines = [
        f"📋 Grid Version Registry ({summary['active']}/{summary['total_registered']} active)\n",
    ]

    node_emoji = {
        'anchor': '⛰️', 'echo': '🌊', 'beacon': '🔥', 'synth': '💨',
        'nexus': '⏳', 'mirror': '🪞', 'glyph': '🔣', 'harmonia': '💗',
        'gateway': '🚪',
    }

    for node, layers in sorted(summary.get('nodes', {}).items()):
        emoji = node_emoji.get(node, '•')
        layer_strs = []
        for l in layers:
            status = '✅' if l['active'] else '⬜'
            layer_strs.append(f"L{l['layer']}:{l['version']}{status}")
        lines.append(f"{emoji} {node.upper()}: {' '.join(layer_strs)}")

    await update.message.reply_text("\n".join(lines))


async def _show_stale(update, node: str = None):
    """Show exchanges needing reprocessing."""
    from grid_manifest import VersionRegistry

    if not node:
        await update.message.reply_text("Usage: /grid stale <node>\nExample: /grid stale echo")
        return

    node = node.lower()
    valid = ['anchor', 'echo', 'beacon', 'synth', 'nexus', 'mirror', 'glyph', 'harmonia', 'gateway']
    if node not in valid:
        await update.message.reply_text(f"Unknown node: {node}\nValid: {', '.join(valid)}")
        return

    registry = VersionRegistry()
    stale = registry.find_stale_exchanges(node, layer=1, limit=10)
    current = registry.get_version(node, 1)

    if not stale:
        await update.message.reply_text(f"No stale exchanges for {node.upper()} L1 (current: v{current})")
        return

    lines = [
        f"🔄 Stale exchanges for {node.upper()} L1 (current: v{current})\n",
    ]
    for s in stale:
        lines.append(
            f"  {s['exchange_id'][:20]}... v{s['version']} "
            f"({s.get('extracted_count', 0)} extractions) "
            f"at {s.get('processed_at', '?')}"
        )
    lines.append(f"\n{len(stale)} exchange(s) found. Use /grid reprocess {node} to requeue.")

    await update.message.reply_text("\n".join(lines))
