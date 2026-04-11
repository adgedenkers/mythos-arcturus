You are a system archaeologist analyzing the Mythos codebase on Arcturus.
TASK: Identify dead code, orphaned database tables, and ghost services.

## DATA

PYTHON FILES THAT NOTHING IMPORTS:
{context.graph.never_imported_py}

EMPTY POSTGRES TABLES (zero rows — stats refreshed immediately before this query):
{context.postgres.truly_empty_tables}

ALL TABLE ROW COUNTS (live counts, not estimates):
{context.postgres.live_row_counts}

SERVICES IN THE GRAPH:
{context.graph.graph_services}

SERVICES ACTUALLY RUNNING RIGHT NOW:
{context.shell.running_services}

FILES WITH A main() FUNCTION (standalone scripts — NOT dead code):
{context.graph.files_with_main}

## CLASSIFICATION RULES

NOT dead code — do NOT flag these under any circumstances:
- Files in /opt/mythos/bin/ (CLI tools, invoked directly from terminal)
- Files in /opt/mythos/services/ (systemd service scripts)
- Files named main.py, bot.py, mythos_bot.py (entry points)
- Files named __init__.py (package markers)
- Files in /opt/mythos/mission/ (mission engine, invoked by CLI)
- Files in /opt/mythos/patches/ (patch scripts, run by installer)
- Files in /opt/mythos/migrations/ (SQL migration helpers)
- Test files (test_*.py, *_test.py)
- Config/data files (.yaml, .json, .sql, .md)
- Files in /opt/mythos/telegram_bot/handlers/ (dynamically registered via handlers/__init__.py — they are loaded at runtime through importlib or wildcard imports, so they will NEVER appear in the static IMPORTS graph even though they are actively used)
- Files in /opt/mythos/workers/ (background service entry points invoked by systemd or cron)
- Files ending in _worker.py or _watcher.py anywhere in the tree (service scripts)
- Files in /opt/mythos/core/ (library modules imported at runtime by the bot and API)
- Files in /opt/mythos/finance/ (invoked by importer CLI tools, cron jobs, or Telegram handlers)
- Files listed in the "files_with_main" data above (standalone scripts with if __name__ == '__main__' blocks — they run directly, not via import)
- Files in /opt/mythos/api/routes/ (FastAPI route modules, registered dynamically by api/main.py)

PROBABLY dead code:
- Python files not imported by anything AND not matching ANY of the "not dead" rules above
- Large files (>5KB) that nothing references are higher priority
- Files in /opt/mythos/tools/ that are not CLI-linked (one-off scripts that may have been abandoned)
- Files in /opt/mythos/archive/ subdirectories (explicitly archived)

WHEN IN DOUBT: classify as "probably_not_dead" with a clear reason. False negatives (missing real dead code) are acceptable. False positives (flagging active code as dead) are NOT acceptable.

For orphaned tables: tables with 0 rows that are NOT views (v_*) and NOT recently created staging tables (sdip_*, pipeline_recent) may be genuinely unused. BUT these tables are KNOWN to be actively used even if they sometimes show low or zero rows — do NOT flag them as orphaned:
- accounts (finance system — holds bank/credit accounts)
- bill_payments (finance system — tracks bill payment history)
- bill_overrides (finance system — manual override entries)
- astro_events (astrology pipeline — populated during transit calculations)

For ghost services: compare graph_services against running_services. A service registered in the graph but not running might be intentionally stopped or genuinely dead.

## OUTPUT

Produce this exact JSON structure:
{{
  "likely_dead_files": [
    {{
      "path": "/opt/mythos/...",
      "size_bytes": 0,
      "reason": "specific reason — what does the filename suggest, why is nothing using it, and confirm it does NOT match any of the not-dead rules above"
    }}
  ],
  "probably_not_dead": [
    {{
      "path": "/opt/mythos/...",
      "reason": "why this is probably an entry point or CLI tool despite no imports"
    }}
  ],
  "orphaned_tables": [
    {{
      "table": "name",
      "rows": 0,
      "verdict": "unused | empty-but-active | staging | view"
    }}
  ],
  "ghost_services": [
    {{
      "service": "name",
      "in_graph": true,
      "running": false,
      "verdict": "dead | intentionally stopped | infrastructure service"
    }}
  ],
  "dead_code_count": 0,
  "summary": "2-3 sentences: how much dead code is there, how bad is it"
}}

Respond with ONLY the JSON. No markdown fences. No explanation.
