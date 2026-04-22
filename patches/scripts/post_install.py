#!/usr/bin/env python3
"""
/opt/mythos/patches/scripts/post_install.py
Post-install pipeline — runs automatically after every patch.
Pipeline steps:
  1. Integrity scan (file hashes + function extraction → Neo4j)
  1.5. Graph coverage gate (SYS-0091) — verify deployed files in Neo4j
  2. Git commit + tag the patch
  3. Log patch to Neo4j graph (Patch node with relationships)
  4. Send Telegram notification
Called by PatchBase.finish() — never run manually.
"""
import os
import sys
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("mythos.post_install")
MYTHOS = Path("/opt/mythos")


def run_cmd(cmd, description, timeout=120, cwd=None):
    """Run a shell command, return (success, output)."""
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = str(MYTHOS) + ":" + env.get("PYTHONPATH", "")
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            cwd=cwd, env=env
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, result.stderr.strip()[:200]
    except subprocess.TimeoutExpired:
        return False, f"Timeout after {timeout}s"
    except Exception as e:
        return False, str(e)


def step_integrity_scan():
    """Run the integrity scanner to update Neo4j with file/function changes."""
    print("  \u23f3 Integrity scan...")
    ok, output = run_cmd(
        ['/opt/mythos/.venv/bin/python3', '-m', 'integrity', 'scan'],
        "integrity scan",
        timeout=120,
        cwd=str(MYTHOS)
    )
    if ok:
        lines = output.split('\n')
        stats = {}
        for line in lines:
            for key in ('New:', 'Updated:', 'Unchanged:', 'Files scanned:',
                        'Functions:', 'Tables:'):
                if key in line:
                    parts = line.strip().split()
                    try:
                        stats[key.rstrip(':')] = int(parts[-1])
                    except (ValueError, IndexError):
                        pass
        new = stats.get('New', 0)
        updated = stats.get('Updated', 0)
        print(f"  \u2713 Integrity scan: {new} new, {updated} updated")
        return True, stats
    else:
        print(f"  \u26a0 Integrity scan failed: {output}")
        return False, output


def step_verify_graph_coverage(files_deployed):
    """Verify deployed files appear as active IntegrityFile nodes in Neo4j.

    SYS-0091: Graph coverage gate. Runs after integrity scan, before git commit.
    Uses the neo4j driver directly — does NOT import integrity.graph which has
    a known crash loop (mythos-obs-graph.service). Non-fatal: warns on missing
    files but does not block the patch.
    """
    print("  \u23f3 Graph coverage check...")
    if not files_deployed:
        print("  \u2713 Graph coverage: no files deployed, skipping")
        return True, {}
    try:
        from neo4j import GraphDatabase
        from dotenv import load_dotenv
        load_dotenv('/opt/mythos/.env')
        uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD', '')
        driver = GraphDatabase.driver(uri, auth=(user, password))
        missing = []
        found = []
        with driver.session() as session:
            for filepath in files_deployed:
                result = session.run(
                    "MATCH (f:IntegrityFile {path: $path, status: 'active'}) "
                    "RETURN f.path AS path LIMIT 1",
                    path=filepath,
                )
                record = result.single()
                if record:
                    found.append(filepath)
                else:
                    missing.append(filepath)
        driver.close()
        total = len(files_deployed)
        n_found = len(found)
        n_missing = len(missing)
        if n_missing == 0:
            print(f"  \u2713 Graph coverage: {n_found}/{total} deployed files verified in Neo4j")
            return True, {'found': n_found, 'missing': 0, 'total': total}
        else:
            print(f"  \u26a0 Graph coverage: {n_found}/{total} verified, {n_missing} missing from graph:")
            for m in missing[:5]:
                print(f"      \u26a0 not in graph: {m}")
            if len(missing) > 5:
                print(f"      ... and {len(missing) - 5} more")
            print("    (Non-fatal: integrity.graph crash loop tracked in REQUESTS.md)")
            return False, {'found': n_found, 'missing': n_missing, 'total': total,
                           'missing_paths': missing}
    except ImportError:
        print("  \u29d8 Graph coverage: neo4j driver not available")
        return False, {'error': 'neo4j driver not installed'}
    except Exception as e:
        print(f"  \u29d8 Graph coverage check failed: {e}")
        return False, {'error': str(e)}


def step_git_commit(patch_id, description, files_deployed):
    """Git add changed files, commit with patch ID, tag."""
    print("  \u23f3 Git commit...")
    ok, _ = run_cmd(
        ['git', '-C', str(MYTHOS), 'add', '-A'],
        "git add"
    )
    if not ok:
        print("  \u26a0 Git add failed")
        return False
    commit_msg = f"{patch_id}: {description}"
    ok, output = run_cmd(
        ['git', '-C', str(MYTHOS), 'commit', '-m', commit_msg, '--allow-empty'],
        "git commit"
    )
    if ok:
        print(f"  \u2713 Git commit: {commit_msg}")
    else:
        if 'nothing to commit' in output:
            print(f"  \u2713 Git: nothing to commit")
        else:
            print(f"  \u26a0 Git commit: {output}")
            return False
    tag = patch_id.lower().replace('-', '_')
    ok, output = run_cmd(
        ['git', '-C', str(MYTHOS), 'tag', '-f', tag],
        "git tag"
    )
    if ok:
        print(f"  \u2713 Git tag: {tag}")
    ok, output = run_cmd(
        ['git', '-C', str(MYTHOS), 'push', '--follow-tags', '-u', 'origin', 'main'],
        "git push",
        timeout=30
    )
    if ok:
        print(f"  \u2713 Git push")
    else:
        print(f"  \u29d8 Git push skipped: {output[:80]}")
    return True


def step_log_to_graph(patch_id, stream, number, description, patch_type,
                      files_deployed, services_restarted, sql_run):
    """Create/update a Patch node in Neo4j with relationships to changed files."""
    print("  \u23f3 Graph update...")
    try:
        from integrity.graph import get_driver, run_write
        driver = get_driver()
        run_write(driver, """
            MERGE (p:Patch {patch_id: $patch_id})
            SET p.stream = $stream,
                p.number = $number,
                p.description = $description,
                p.patch_type = $patch_type,
                p.installed_at = datetime(),
                p.files_count = $files_count,
                p.services_restarted = $services,
                p.sql_files = $sql_files
        """, {
            'patch_id': patch_id,
            'stream': stream,
            'number': number,
            'description': description,
            'patch_type': patch_type,
            'files_count': len(files_deployed),
            'services': services_restarted,
            'sql_files': sql_run,
        })
        for filepath in files_deployed:
            run_write(driver, """
                MATCH (p:Patch {patch_id: $patch_id})
                MERGE (f:File {path: $path})
                MERGE (p)-[:DEPLOYED]->(f)
            """, {
                'patch_id': patch_id,
                'path': filepath,
            })
        run_write(driver, """
            MATCH (p:Patch {patch_id: $patch_id})
            MERGE (s:Stream {name: $stream})
            MERGE (p)-[:BELONGS_TO]->(s)
        """, {
            'patch_id': patch_id,
            'stream': stream,
        })
        driver.close()
        print(f"  \u2713 Graph: Patch node + {len(files_deployed)} file relationships")
        return True
    except ImportError:
        print("  \u29d8 Graph: integrity.graph not available")
        return False
    except Exception as e:
        print(f"  \u26a0 Graph update failed: {e}")
        return False


def step_telegram_notify(patch_id, description, files_deployed,
                         services_restarted, errors, scan_stats=None):
    """Send a Telegram notification about the installed patch."""
    print("  \u23f3 Telegram notify...")
    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv('/opt/mythos/.env')
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
        if not bot_token or not chat_id:
            print("  \u29d8 Telegram: no bot token or chat ID")
            return False
        status = "\u2705" if not errors else "\u26a0\ufe0f"
        lines = [f"{status} <b>{patch_id}</b>: {description}"]
        if files_deployed:
            lines.append(f"\U0001f4c1 {len(files_deployed)} files deployed")
        if services_restarted:
            lines.append(f"\U0001f504 {', '.join(services_restarted)}")
        if scan_stats:
            new = scan_stats.get('New', 0)
            updated = scan_stats.get('Updated', 0)
            if new or updated:
                lines.append(f"\U0001f50d Integrity: {new} new, {updated} updated")
        if errors:
            lines.append(f"\u26a0\ufe0f {len(errors)} errors")
        msg = "\n".join(lines)
        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                'chat_id': chat_id,
                'text': msg,
                'parse_mode': 'HTML',
            },
            timeout=10
        )
        print(f"  \u2713 Telegram notification sent")
        return True
    except Exception as e:
        print(f"  \u29d8 Telegram notify failed: {e}")
        return False


def run_pipeline(patch_id, stream, number, description, patch_type,
                 files_deployed, services_restarted, sql_run, errors):
    """
    Execute the full post-install pipeline.
    Called by PatchBase.finish() after all patch operations complete.
    """
    print("")
    print(f"\u2500\u2500 Post-install pipeline \u2500\u2500")

    results = {}

    # 1. Integrity scan
    scan_ok, scan_stats = step_integrity_scan()
    results['integrity_scan'] = scan_ok

    # 1.5. Graph coverage gate (SYS-0091)
    coverage_ok, coverage_report = step_verify_graph_coverage(files_deployed)
    results['graph_coverage'] = coverage_ok

    # 2. Git commit
    git_ok = step_git_commit(patch_id, description, files_deployed)
    results['git_commit'] = git_ok

    # 3. Graph update
    graph_ok = step_log_to_graph(
        patch_id, stream, number, description, patch_type,
        files_deployed, services_restarted, sql_run
    )
    results['graph_update'] = graph_ok

    # 4. Telegram notification
    tg_ok = step_telegram_notify(
        patch_id, description, files_deployed, services_restarted,
        errors, scan_stats if scan_ok else None
    )
    results['telegram'] = tg_ok

    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"\u2500\u2500 Pipeline: {passed}/{total} steps completed \u2500\u2500")
    print("")

    return results
