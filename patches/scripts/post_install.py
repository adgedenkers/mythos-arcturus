#!/usr/bin/env python3
"""
/opt/mythos/patches/scripts/post_install.py
Post-install pipeline — runs automatically after every patch.

Pipeline steps:
  1. Integrity scan (file hashes + function extraction → Neo4j)
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
    print("  ⟳ Integrity scan...")
    ok, output = run_cmd(
        ['/opt/mythos/.venv/bin/python3', '-m', 'integrity', 'scan'],
        "integrity scan",
        timeout=120,
        cwd=str(MYTHOS)
    )
    if ok:
        # Extract key stats from output
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
        print(f"  ✓ Integrity scan: {new} new, {updated} updated")
        return True, stats
    else:
        print(f"  ⚠ Integrity scan failed: {output}")
        return False, output


def step_git_commit(patch_id, description, files_deployed):
    """Git add changed files, commit with patch ID, tag."""
    print("  ⟳ Git commit...")

    # Stage all changes in /opt/mythos
    ok, _ = run_cmd(
        ['git', '-C', str(MYTHOS), 'add', '-A'],
        "git add"
    )
    if not ok:
        print("  ⚠ Git add failed")
        return False

    # Commit
    commit_msg = f"{patch_id}: {description}"
    ok, output = run_cmd(
        ['git', '-C', str(MYTHOS), 'commit', '-m', commit_msg, '--allow-empty'],
        "git commit"
    )
    if ok:
        print(f"  ✓ Git commit: {commit_msg}")
    else:
        # "nothing to commit" is fine
        if 'nothing to commit' in output:
            print(f"  ✓ Git: nothing to commit")
        else:
            print(f"  ⚠ Git commit: {output}")
            return False

    # Tag
    tag = patch_id.lower().replace('-', '_')
    ok, output = run_cmd(
        ['git', '-C', str(MYTHOS), 'tag', '-f', tag],
        "git tag"
    )
    if ok:
        print(f"  ✓ Git tag: {tag}")

    # Push (non-blocking — failure is OK)
    ok, output = run_cmd(
        ['git', '-C', str(MYTHOS), 'push', '--follow-tags', '-u', 'origin', 'main'],
        "git push",
        timeout=30
    )
    if ok:
        print(f"  ✓ Git push")
    else:
        print(f"  ⊘ Git push skipped: {output[:80]}")

    return True


def step_log_to_graph(patch_id, stream, number, description, patch_type,
                      files_deployed, services_restarted, sql_run):
    """Create/update a Patch node in Neo4j with relationships to changed files."""
    print("  ⟳ Graph update...")

    try:
        from integrity.graph import get_driver, run_write

        driver = get_driver()

        # Create Patch node
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

        # Create relationships to deployed files
        for filepath in files_deployed:
            run_write(driver, """
                MATCH (p:Patch {patch_id: $patch_id})
                MERGE (f:File {path: $path})
                MERGE (p)-[:DEPLOYED]->(f)
            """, {
                'patch_id': patch_id,
                'path': filepath,
            })

        # Link to stream
        run_write(driver, """
            MATCH (p:Patch {patch_id: $patch_id})
            MERGE (s:Stream {name: $stream})
            MERGE (p)-[:BELONGS_TO]->(s)
        """, {
            'patch_id': patch_id,
            'stream': stream,
        })

        driver.close()
        print(f"  ✓ Graph: Patch node + {len(files_deployed)} file relationships")
        return True

    except ImportError:
        print("  ⊘ Graph: integrity.graph not available")
        return False
    except Exception as e:
        print(f"  ⚠ Graph update failed: {e}")
        return False


def step_telegram_notify(patch_id, description, files_deployed,
                         services_restarted, errors, scan_stats=None):
    """Send a Telegram notification about the installed patch."""
    print("  ⟳ Telegram notify...")

    try:
        import requests
        from dotenv import load_dotenv
        load_dotenv('/opt/mythos/.env')

        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_ADMIN_CHAT_ID')

        if not bot_token or not chat_id:
            print("  ⊘ Telegram: no bot token or chat ID")
            return False

        # Build message
        status = "✅" if not errors else "⚠️"
        lines = [f"{status} <b>{patch_id}</b>: {description}"]

        if files_deployed:
            lines.append(f"📁 {len(files_deployed)} files deployed")

        if services_restarted:
            lines.append(f"🔄 {', '.join(services_restarted)}")

        if scan_stats:
            new = scan_stats.get('New', 0)
            updated = scan_stats.get('Updated', 0)
            if new or updated:
                lines.append(f"🔍 Integrity: {new} new, {updated} updated")

        if errors:
            lines.append(f"⚠️ {len(errors)} errors")

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
        print(f"  ✓ Telegram notification sent")
        return True

    except Exception as e:
        print(f"  ⊘ Telegram notify failed: {e}")
        return False


def run_pipeline(patch_id, stream, number, description, patch_type,
                 files_deployed, services_restarted, sql_run, errors):
    """
    Execute the full post-install pipeline.
    Called by PatchBase.finish() after all patch operations complete.
    """
    print("")
    print(f"── Post-install pipeline ──")

    results = {}

    # 1. Integrity scan
    scan_ok, scan_stats = step_integrity_scan()
    results['integrity_scan'] = scan_ok

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
    print(f"── Pipeline: {passed}/{total} steps completed ──")
    print("")

    return results
