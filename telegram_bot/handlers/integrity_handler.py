"""
Module: telegram_bot/handlers/integrity_handler.py
Biological System: iris-immune (Immune System — self-knowledge)
Subsystem: mythos-integrity (v0.2.0)
Purpose: Telegram command handlers for integrity scanning and stats.
Introduced: Patch 0172
Last Modified: Patch 0172

Commands:
  /integrity          — Run full integrity scan
  /integrity files    — Scan files only
  /integrity funcs    — Extract functions only
  /integrity tables   — Scan tables only
  /integrity services — Scan services only
  /integrity stats    — Show graph statistics
  /integrity quick    — Quick health summary

Dependencies:
  - python-telegram-bot
  - integrity module

Part of: Integrity Scanner
Owned by: mythos-bot.service
"""

import os
import sys
import time
import logging
import asyncio
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger("mythos.telegram.integrity")

# Ensure mythos root is in path
sys.path.insert(0, os.getenv("MYTHOS_ROOT", "/opt/mythos"))

AUTHORIZED_CHATS = set()
_auth_env = os.getenv("TELEGRAM_AUTHORIZED_CHATS", "")
if _auth_env:
    AUTHORIZED_CHATS = {int(x.strip()) for x in _auth_env.split(",") if x.strip()}
# Also allow the main bot chat
_main_chat = os.getenv("TELEGRAM_CHAT_ID", "")
if _main_chat:
    AUTHORIZED_CHATS.add(int(_main_chat))


def _is_authorized(chat_id: int) -> bool:
    """Check if a chat is authorized for integrity commands."""
    if not AUTHORIZED_CHATS:
        return True  # No restriction configured
    return chat_id in AUTHORIZED_CHATS


async def handle_integrity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /integrity — Run integrity scan or show stats.

    Biological System: iris-immune
    Registered in: mythos_bot.py main()
    """
    chat_id = update.effective_chat.id
    if not _is_authorized(chat_id):
        await update.message.reply_text("⛔ Not authorized")
        return

    args = context.args if context.args else []
    subcommand = args[0].lower() if args else "full"

    if subcommand == "stats":
        await _handle_stats(update)
    elif subcommand == "quick":
        await _handle_quick(update)
    elif subcommand in ("full", "all"):
        await _handle_scan(update, files=True, funcs=True, tables=True, services=True)
    elif subcommand == "files":
        await _handle_scan(update, files=True)
    elif subcommand == "funcs":
        await _handle_scan(update, funcs=True)
    elif subcommand == "tables":
        await _handle_scan(update, tables=True)
    elif subcommand == "services":
        await _handle_scan(update, services=True)
    else:
        await update.message.reply_text(
            "🛡️ *Integrity Scanner*\n\n"
            "`/integrity` — Full scan\n"
            "`/integrity files` — Files only\n"
            "`/integrity funcs` — Functions only\n"
            "`/integrity tables` — Tables only\n"
            "`/integrity services` — Services only\n"
            "`/integrity stats` — Graph statistics\n"
            "`/integrity quick` — Quick health summary",
            parse_mode="Markdown"
        )


async def _handle_scan(update, files=False, funcs=False, tables=False, services=False):
    """Run the specified scan components."""
    parts = []
    if files:
        parts.append("files")
    if funcs:
        parts.append("functions")
    if tables:
        parts.append("tables")
    if services:
        parts.append("services")

    label = ", ".join(parts) if parts else "full"
    msg = await update.message.reply_text(f"🛡️ Running integrity scan ({label})...")

    try:
        from integrity.graph import get_driver, ensure_constraints
        driver = get_driver()
        ensure_constraints(driver)

        results = []
        total_start = time.time()

        if files:
            from integrity.file_scanner import scan_files
            start = time.time()
            fs = scan_files(driver=driver)
            elapsed = time.time() - start
            results.append(
                f"📁 *Files* ({elapsed:.1f}s)\n"
                f"  Scanned: {fs['files_scanned']}, "
                f"New: {fs['files_new']}, "
                f"Updated: {fs['files_updated']}, "
                f"Missing: {fs['files_missing']}"
            )

        if funcs:
            from integrity.function_extractor import extract_functions
            start = time.time()
            fx = extract_functions(driver=driver)
            elapsed = time.time() - start
            results.append(
                f"🔍 *Functions* ({elapsed:.1f}s)\n"
                f"  Parsed: {fx['files_parsed']} files, "
                f"Found: {fx['functions_found']} funcs, "
                f"Imports: {fx['imports_found']}"
            )

        if tables:
            from integrity.table_scanner import scan_tables
            start = time.time()
            ts = scan_tables(driver=driver)
            elapsed = time.time() - start
            results.append(
                f"🗄️ *Tables* ({elapsed:.1f}s)\n"
                f"  Tables: {ts['tables_found']}, "
                f"Columns: {ts['columns_found']}, "
                f"FKs: {ts['fk_relationships']}"
            )

        if services:
            from integrity.service_scanner import scan_services
            start = time.time()
            ss = scan_services(driver=driver)
            elapsed = time.time() - start
            results.append(
                f"⚙️ *Services* ({elapsed:.1f}s)\n"
                f"  Found: {ss['services_found']}, "
                f"Healthy: {ss['healthy']}, "
                f"Unhealthy: {ss['unhealthy']}, "
                f"Linked: {ss['linked_to_files']}"
            )

        driver.close()

        total_elapsed = time.time() - total_start
        report = "\n\n".join(results)
        report += f"\n\n✅ Scan complete ({total_elapsed:.1f}s total)"

        await msg.edit_text(f"🛡️ *Integrity Scan Results*\n\n{report}", parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Integrity scan failed: {e}", exc_info=True)
        await msg.edit_text(f"❌ Integrity scan failed: {e}")


async def _handle_stats(update):
    """Show graph statistics."""
    try:
        from integrity.graph import get_driver, run_query
        driver = get_driver()

        queries = {
            "Files (active)": "MATCH (f:IntegrityFile {status: 'active'}) RETURN count(f) AS cnt",
            "Files (missing)": "MATCH (f:IntegrityFile {status: 'missing'}) RETURN count(f) AS cnt",
            "Directories": "MATCH (d:IntegrityDirectory) RETURN count(d) AS cnt",
            "Functions": "MATCH (fn:IntegrityFunction) RETURN count(fn) AS cnt",
            "Tables": "MATCH (t:IntegrityTable) RETURN count(t) AS cnt",
            "Columns": "MATCH (c:IntegrityColumn) RETURN count(c) AS cnt",
            "Services": "MATCH (s:IntegrityService) RETURN count(s) AS cnt",
            "Import rels": "MATCH ()-[r:IMPORTS]->() RETURN count(r) AS cnt",
            "FK rels": "MATCH (:IntegrityTable)-[r:REFERENCES]->(:IntegrityTable) RETURN count(r) AS cnt",
        }

        lines = ["📊 *Integrity Graph Statistics*\n"]
        for label, cypher in queries.items():
            result = run_query(driver, cypher)
            count = result[0]["cnt"] if result else 0
            lines.append(f"  {label}: `{count}`")

        # Docstring coverage
        undoc = run_query(driver,
            "MATCH (fn:IntegrityFunction) WHERE fn.docstring IS NULL OR fn.docstring = '' RETURN count(fn) AS cnt"
        )
        total = run_query(driver, "MATCH (fn:IntegrityFunction) RETURN count(fn) AS cnt")
        undoc_count = undoc[0]["cnt"] if undoc else 0
        total_count = total[0]["cnt"] if total else 0
        if total_count > 0:
            doc_pct = (total_count - undoc_count) / total_count * 100
            lines.append(f"\n📝 Docstring coverage: `{doc_pct:.0f}%` ({total_count - undoc_count}/{total_count})")

        driver.close()
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Stats failed: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Stats failed: {e}")


async def _handle_quick(update):
    """Quick health summary — services + file counts."""
    try:
        from integrity.graph import get_driver, run_query
        driver = get_driver()

        # Service health
        svc_result = run_query(driver, """
            MATCH (s:IntegrityService)
            RETURN s.name AS name, s.is_active AS active, s.sub_state AS sub
            ORDER BY s.name
        """)

        # File counts
        file_count = run_query(driver,
            "MATCH (f:IntegrityFile {status: 'active'}) RETURN count(f) AS cnt"
        )
        missing_count = run_query(driver,
            "MATCH (f:IntegrityFile {status: 'missing'}) RETURN count(f) AS cnt"
        )
        func_count = run_query(driver,
            "MATCH (fn:IntegrityFunction) RETURN count(fn) AS cnt"
        )

        driver.close()

        files = file_count[0]["cnt"] if file_count else 0
        missing = missing_count[0]["cnt"] if missing_count else 0
        funcs = func_count[0]["cnt"] if func_count else 0

        lines = ["🛡️ *Quick Health Check*\n"]
        lines.append(f"📁 Files: `{files}` active, `{missing}` missing")
        lines.append(f"🔍 Functions: `{funcs}`")

        if svc_result:
            healthy = sum(1 for s in svc_result if s["active"])
            total = len(svc_result)
            lines.append(f"⚙️ Services: `{healthy}/{total}` healthy")

            unhealthy = [s for s in svc_result if not s["active"]]
            if unhealthy:
                lines.append("\n⚠️ *Down:*")
                for s in unhealthy:
                    lines.append(f"  ❌ `{s['name']}`: {s['sub']}")
        else:
            lines.append("⚙️ Services: not yet scanned (run `/integrity services`)")

        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"❌ Quick check failed: {e}")
