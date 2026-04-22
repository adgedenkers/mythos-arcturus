#!/usr/bin/env python3
"""
AutoDoc2 Scheduled Re-crawl Worker — SYS-0094
/opt/mythos/workers/autodoc2_worker.py

AutoDoc2 Letter G: Reliability — keeps the Neo4j codebase graph current.

Runs as a one-shot service triggered by a systemd timer (weekly by default).
Crawls /opt/mythos, computes a diff against the previous crawl, and sends
a summary to Telegram.

Also supports --now flag for on-demand crawl from command line or Telegram bot.

Diff tracks:
  - Files added since last crawl
  - Files removed since last crawl
  - Functions added/removed (count only)
  - Languages breakdown

Architecture:
  - Uses autodoc2 CLI directly via subprocess (clean separation)
  - Reads diff from Neo4j by comparing AutodocCrawl file counts and file lists
  - Sends Telegram notification with diff summary
  - Writes crawl report to /opt/mythos/docs/live/autodoc2-crawl-latest.json

Usage:
  /opt/mythos/.venv/bin/python3 /opt/mythos/workers/autodoc2_worker.py
  /opt/mythos/.venv/bin/python3 /opt/mythos/workers/autodoc2_worker.py --now
  /opt/mythos/.venv/bin/python3 /opt/mythos/workers/autodoc2_worker.py --target /some/path
"""
import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, '/opt/mythos')
from dotenv import load_dotenv
load_dotenv('/opt/mythos/.env')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [autodoc2_worker] %(levelname)s %(message)s',
    handlers=[
        logging.StreamHandler(),
    ]
)
log = logging.getLogger('autodoc2_worker')

MYTHOS = Path('/opt/mythos')
DEFAULT_TARGET = MYTHOS
CRAWL_REPORT_PATH = MYTHOS / 'docs' / 'live' / 'autodoc2-crawl-latest.json'
AUTODOC2_BIN = MYTHOS / 'bin' / 'autodoc2'


# ── Neo4j helpers ─────────────────────────────────────────────────────────────

def get_driver():
    from neo4j import GraphDatabase
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', '')
    return GraphDatabase.driver(uri, auth=(user, password))


def get_previous_crawl_stats(driver, crawl_id: str) -> dict:
    """Get stats from the most recent completed crawl for this target."""
    with driver.session() as s:
        result = s.run(
            """
            MATCH (c:AutodocCrawl {crawl_id: $crawl_id})
            RETURN c.file_count AS file_count,
                   c.finished_at AS finished_at,
                   c.status AS status
            """,
            crawl_id=crawl_id,
        ).single()
        if result:
            return dict(result)
        return {}


def get_file_list(driver, crawl_id: str) -> set:
    """Get the set of relative paths from the current graph state."""
    with driver.session() as s:
        results = s.run(
            """
            MATCH (c:AutodocCrawl {crawl_id: $crawl_id})-[:CONTAINS]->(f:AutodocFile)
            RETURN f.relative_path AS path
            """,
            crawl_id=crawl_id,
        ).data()
        return {r['path'] for r in results}


def get_function_count(driver, crawl_id: str) -> int:
    with driver.session() as s:
        result = s.run(
            """
            MATCH (c:AutodocCrawl {crawl_id: $crawl_id})-[:CONTAINS]->(f:AutodocFile)
                  -[:CONTAINS]->(fn:AutodocFunction)
            RETURN count(fn) AS cnt
            """,
            crawl_id=crawl_id,
        ).single()
        return result['cnt'] if result else 0


def get_language_breakdown(driver, crawl_id: str) -> dict:
    with driver.session() as s:
        results = s.run(
            """
            MATCH (c:AutodocCrawl {crawl_id: $crawl_id})-[:CONTAINS]->(f:AutodocFile)
            RETURN f.language AS lang, count(f) AS cnt
            ORDER BY cnt DESC
            """,
            crawl_id=crawl_id,
        ).data()
        return {r['lang']: r['cnt'] for r in results}


# ── Crawl ID helper (mirrors engine.py logic) ─────────────────────────────────

def make_crawl_id(target: Path) -> str:
    import hashlib
    h = hashlib.sha1(str(target.resolve()).encode()).hexdigest()[:12]
    return f"autodoc2_{target.name}_{h}"


# ── Telegram notification ─────────────────────────────────────────────────────

def send_telegram(message: str):
    try:
        import requests as req
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
        if not bot_token or not chat_id:
            log.warning('Telegram credentials not configured')
            return
        req.post(
            f'https://api.telegram.org/bot{bot_token}/sendMessage',
            json={'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'},
            timeout=10,
        )
        log.info('Telegram notification sent')
    except Exception as e:
        log.warning(f'Telegram notification failed: {e}')


# ── Main crawl + diff logic ───────────────────────────────────────────────────

def run_crawl(target: Path, skip_llm: bool = True) -> bool:
    """Run autodoc2 on the target. Returns True on success."""
    cmd = [str(AUTODOC2_BIN), str(target)]
    if skip_llm:
        cmd.append('--skip-llm')
    log.info(f'Starting crawl: {" ".join(cmd)}')
    t0 = time.time()
    result = subprocess.run(cmd, capture_output=False, text=True)
    elapsed = time.time() - t0
    if result.returncode != 0:
        log.error(f'Crawl failed after {elapsed:.1f}s (exit {result.returncode})')
        return False
    log.info(f'Crawl completed in {elapsed:.1f}s')
    return True


def compute_diff(driver, crawl_id: str, prev_files: set, prev_fn_count: int) -> dict:
    """Compare current graph state against previous snapshot."""
    current_files = get_file_list(driver, crawl_id)
    current_fn_count = get_function_count(driver, crawl_id)
    languages = get_language_breakdown(driver, crawl_id)

    added = current_files - prev_files
    removed = prev_files - current_files
    fn_delta = current_fn_count - prev_fn_count

    return {
        'files_total': len(current_files),
        'files_added': sorted(added),
        'files_removed': sorted(removed),
        'functions_total': current_fn_count,
        'functions_delta': fn_delta,
        'languages': languages,
        'n_added': len(added),
        'n_removed': len(removed),
    }


def format_telegram_message(target: Path, diff: dict, elapsed_s: float) -> str:
    lines = [
        f'\U0001f4ca <b>AutoDoc2 Crawl Complete</b>',
        f'Target: <code>{target}</code>',
        f'Files: {diff["files_total"]} total',
    ]
    if diff['n_added']:
        lines.append(f'\u2795 {diff["n_added"]} file(s) added')
    if diff['n_removed']:
        lines.append(f'\u2796 {diff["n_removed"]} file(s) removed')
    if diff['functions_delta'] != 0:
        sign = '+' if diff['functions_delta'] > 0 else ''
        lines.append(f'\u0192 Functions: {sign}{diff["functions_delta"]} ({diff["functions_total"]} total)')
    if diff['languages']:
        lang_str = ', '.join(f'{k} ({v})' for k, v in list(diff['languages'].items())[:5])
        lines.append(f'\U0001f4c4 Languages: {lang_str}')
    lines.append(f'\u23f1 {elapsed_s:.0f}s')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='AutoDoc2 scheduled re-crawl worker')
    parser.add_argument('--now', action='store_true', help='Run immediately (default)')
    parser.add_argument('--target', default=str(DEFAULT_TARGET),
                        help=f'Directory to crawl (default: {DEFAULT_TARGET})')
    parser.add_argument('--skip-analyze', action='store_true', default=True,
                        help='Skip gemma4 analysis (default: True — analysis is opt-in)')
    args = parser.parse_args()

    target = Path(args.target).resolve()
    crawl_id = make_crawl_id(target)

    log.info(f'AutoDoc2 worker starting — target: {target}, crawl_id: {crawl_id}')

    # Snapshot pre-crawl state from Neo4j
    try:
        driver = get_driver()
        prev_files = get_file_list(driver, crawl_id)
        prev_fn_count = get_function_count(driver, crawl_id)
        prev_stats = get_previous_crawl_stats(driver, crawl_id)
        log.info(f'Pre-crawl snapshot: {len(prev_files)} files, {prev_fn_count} functions')
    except Exception as e:
        log.error(f'Neo4j pre-crawl snapshot failed: {e}')
        driver = None
        prev_files = set()
        prev_fn_count = 0
        prev_stats = {}

    # Run the crawl
    t0 = time.time()
    success = run_crawl(target, skip_llm=True)
    elapsed = time.time() - t0

    if not success:
        msg = f'\u274c AutoDoc2 crawl FAILED\nTarget: <code>{target}</code>'
        send_telegram(msg)
        sys.exit(1)

    # Compute diff
    report = {
        'crawl_id': crawl_id,
        'target': str(target),
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'elapsed_seconds': round(elapsed, 1),
        'success': True,
    }

    if driver:
        try:
            diff = compute_diff(driver, crawl_id, prev_files, prev_fn_count)
            report.update(diff)
            driver.close()
            msg = format_telegram_message(target, diff, elapsed)
            send_telegram(msg)
            log.info(
                f'Diff: +{diff["n_added"]} -{diff["n_removed"]} files, '
                f'{diff["functions_delta"]:+d} functions'
            )
        except Exception as e:
            log.error(f'Diff computation failed: {e}')
            send_telegram(
                f'\u2705 AutoDoc2 crawl complete\n'
                f'Target: <code>{target}</code>\n'
                f'\u23f1 {elapsed:.0f}s\n'
                f'(diff unavailable: {e})'
            )
    else:
        send_telegram(
            f'\u2705 AutoDoc2 crawl complete\n'
            f'Target: <code>{target}</code>\n'
            f'\u23f1 {elapsed:.0f}s'
        )

    # Write report
    try:
        CRAWL_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        CRAWL_REPORT_PATH.write_text(json.dumps(report, indent=2, default=str))
        log.info(f'Report written: {CRAWL_REPORT_PATH}')
    except Exception as e:
        log.warning(f'Could not write report: {e}')

    log.info('AutoDoc2 worker complete')


if __name__ == '__main__':
    main()
