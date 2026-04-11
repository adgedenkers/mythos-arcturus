"""
mx_hooks.py — Pre/post operation hooks (SYS-0029)

Detects significant operations (deploys, service restarts, migrations)
and wraps them with:
  1. Pre-flight integrity scan  (python3 -m integrity scan --services --tables)
  2. Pre-flight snapshot
  3. Execute the operation (healing as needed)
  4. Post-operation integrity scan
  5. Post-operation snapshot
  6. Delta report
  7. Rollback offer if regressions detected

Significant operations detected by command pattern matching.
"""

import subprocess
import sys
import time
from pathlib import Path

# Colors
CYAN   = "\033[96m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

MYTHOS_PYTHON = "/opt/mythos/.venv/bin/python3"
MYTHOS_ROOT = "/opt/mythos"

# Patterns that trigger pre/post integrity wrapping
SIGNIFICANT_PATTERNS = [
    "patch-install",
    "patch_install",
    "systemctl restart",
    "systemctl start",
    "systemctl stop",
    "apply_patch.py",
    "psql -d mythos",
    "alembic upgrade",
    "migrate",
    "DROP TABLE",
    "ALTER TABLE",
    "CREATE TABLE",
]

# Fast scan args for pre/post (services + tables only, skip slow file scan)
INTEGRITY_FAST_ARGS = ["--services", "--tables"]


def is_significant(command: str) -> bool:
    """Check if a command warrants pre/post integrity wrapping."""
    cmd_lower = command.lower()
    return any(p.lower() in cmd_lower for p in SIGNIFICANT_PATTERNS)


def run_integrity_scan(label: str, fast: bool = True) -> bool:
    """
    Run integrity scan. Returns True if scan completed (not necessarily clean).
    fast=True runs only --services and --tables (3-5s).
    fast=False runs full scan including files (30-60s).
    """
    print(f"\n{CYAN}📸 {label} integrity scan...{RESET}", flush=True)
    args = [MYTHOS_PYTHON, "-m", "integrity", "scan"]
    if fast:
        args += INTEGRITY_FAST_ARGS

    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=MYTHOS_ROOT,
    )

    if result.returncode == 0:
        # Extract key stats from output
        for line in result.stdout.splitlines():
            if any(kw in line for kw in ["Services", "Tables", "Healthy", "Unhealthy", "Missing"]):
                print(f"  {DIM}{line.strip()}{RESET}")
        return True
    else:
        print(f"  {YELLOW}⚠ Integrity scan warning: {result.stderr.strip()[:150]}{RESET}")
        return False


def pre_flight(command: str, journal=None) -> tuple[str | None, dict | None]:
    """
    Run pre-flight checks before a significant operation.
    Returns (snapshot_path, snapshot_data) or (None, None) on failure.
    """
    sys.path.insert(0, "/opt/mythos/mx")
    from mx_snapshot import take_snapshot, load_snapshot

    # Run fast integrity scan first
    run_integrity_scan("Pre-flight", fast=True)

    # Take snapshot
    print(f"  {DIM}Taking pre-operation snapshot...{RESET}", flush=True)
    snap_path = take_snapshot(trigger="pre", label=_label_from_command(command))
    snap_data = load_snapshot(snap_path)

    # Show pre-flight summary
    svcs = snap_data.get("services", {})
    inactive = [s for s, state in svcs.items() if state == "inactive"]
    git = snap_data.get("git", {})
    pg = snap_data.get("postgres", {})

    print(f"\n  {BOLD}Pre-flight:{RESET}")
    print(f"  {DIM}Services: {len(svcs)} total, {len(inactive)} inactive{RESET}")
    if inactive:
        print(f"  {YELLOW}  ⚠ Already inactive: {', '.join(inactive)}{RESET}")
    print(f"  {DIM}Tables: {pg.get('table_count', '?')}  |  Git: {git.get('hash','?')} ({'' if git.get('clean') else 'dirty'}){RESET}")

    integrity = snap_data.get("integrity", {})
    if integrity.get("available"):
        missing = integrity.get("files_missing", 0)
        unhealthy = integrity.get("services_unhealthy", 0)
        if missing or unhealthy:
            print(f"  {YELLOW}  ⚠ Pre-existing: {missing} files missing, {unhealthy} services unhealthy{RESET}")

    if journal:
        journal.record_snapshot(pre_path=snap_path)

    return snap_path, snap_data


def post_flight(command: str, pre_snap_path: str, pre_snap_data: dict,
                journal=None, offer_rollback: bool = True) -> bool:
    """
    Run post-operation checks and produce delta report.
    Returns True if system is healthy (no regressions).
    """
    sys.path.insert(0, "/opt/mythos/mx")
    from mx_snapshot import take_snapshot, load_snapshot
    from mx_delta import diff_snapshots, print_delta_report

    # Run fast integrity scan
    run_integrity_scan("Post-operation", fast=True)

    # Take post snapshot
    print(f"  {DIM}Taking post-operation snapshot...{RESET}", flush=True)
    post_path = take_snapshot(trigger="post", label=_label_from_command(command))
    post_data = load_snapshot(post_path)

    if journal:
        journal.record_snapshot(post_path=post_path)

    # Delta
    report = diff_snapshots(pre_snap_data, post_data)
    print_delta_report(report, pre_label="pre", post_label="post")

    if journal:
        journal.record_delta(report.summary_line(), report.regressions)

    # Offer rollback on regressions
    if report.has_regressions and offer_rollback:
        print(f"{RED}  Rollback available (git stash / git reset HEAD~1){RESET}")
        try:
            answer = input(f"  {YELLOW}Show rollback options? [y/N]{RESET} ").strip().lower()
            if answer == "y":
                _show_rollback_options()
        except (EOFError, KeyboardInterrupt):
            pass

    return not report.has_regressions


def _label_from_command(command: str) -> str:
    """Extract a short label from a command for snapshot filename."""
    for pattern in ["patch-install", "systemctl restart", "systemctl start"]:
        if pattern in command:
            parts = command.replace(pattern, "").strip().split()
            if parts:
                return parts[0].replace(".service", "").replace("-", "_")[:20]
    return "op"


def _show_rollback_options():
    """Print rollback guidance."""
    print(f"\n{BOLD}  Rollback options:{RESET}")
    print(f"  {DIM}Git uncommitted changes:{RESET}  git -C /opt/mythos checkout -- .")
    print(f"  {DIM}Undo last commit:{RESET}          git -C /opt/mythos reset HEAD~1")
    print(f"  {DIM}Restart all services:{RESET}      sudo systemctl restart mythos-api.service mythos-bot.service")
    print(f"  {DIM}Check service logs:{RESET}        journalctl -u mythos-api.service -n 30 --no-pager")
    print()
