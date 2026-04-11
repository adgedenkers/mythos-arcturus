#!/usr/bin/env python3
"""
Module: generate_system_state.py
Biological System: iris-immune (Immune System — self-knowledge)
Subsystem: mythos-telemetry (v0.1.0)
Purpose: Generate live telemetry files from current system state.
         Creates/updates system-state.txt, patch-versions.txt,
         patch-install-history.txt, and CLAUDE_CONTEXT.md
Introduced: Patch 0169
Last Modified: Patch 0169

Dependencies:
  - git (for patch/version history)
  - systemctl (for service health)
  - PostgreSQL (for table counts)
  - Neo4j (optional, for node counts)

Part of: Live Telemetry Foundation
Owned by: manual / cron (no dedicated service yet)

Usage:
  /opt/mythos/.venv/bin/python3 /opt/mythos/tools/generate_system_state.py
  /opt/mythos/.venv/bin/python3 /opt/mythos/tools/generate_system_state.py --section all
  /opt/mythos/.venv/bin/python3 /opt/mythos/tools/generate_system_state.py --section context
"""

import subprocess
import os
import re
import json
from datetime import datetime
from pathlib import Path

# === Configuration ===
MYTHOS_ROOT = os.getenv("MYTHOS_ROOT", "/opt/mythos")
LIVE_DIR = os.path.join(MYTHOS_ROOT, "docs", "live")
DOCS_DIR = os.path.join(MYTHOS_ROOT, "docs")
PATCHES_DIR = os.path.join(MYTHOS_ROOT, "patches")

def run_cmd(cmd, default=""):
    """Run a shell command and return stdout, or default on failure."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=15,
            cwd=MYTHOS_ROOT
        )
        return result.stdout.strip() if result.returncode == 0 else default
    except Exception:
        return default


def get_git_tags():
    """Get all version git tags sorted by creation date."""
    raw = run_cmd("git tag --sort=creatordate")
    if not raw:
        return []
    return [t for t in raw.split("\n") if t.startswith("v")]


def get_patch_version_map():
    """
    Build patch_number → version mapping from git tags and commit messages.
    Returns list of (patch_number, version, description, date) tuples.
    """
    # Get all tags with their commit subjects and dates
    raw = run_cmd(
        'git log --oneline --decorate=short --all --grep="Applied patch:" --format="%H %s %d"'
    )
    if not raw:
        return []

    entries = []
    for line in raw.split("\n"):
        if not line.strip():
            continue
        # Extract patch number from commit message
        patch_match = re.search(r'patch[_\s]*(\d{4})', line, re.IGNORECASE)
        if not patch_match:
            continue
        patch_num = patch_match.group(1)

        # Extract version tag if present
        tag_match = re.search(r'tag: (v[\d.]+)', line)
        version = tag_match.group(1) if tag_match else ""

        # Extract description
        desc_match = re.search(r'patch_\d{4}_([^.]+)', line)
        description = desc_match.group(1).replace("_", " ") if desc_match else ""

        entries.append((patch_num, version, description))

    return entries


def get_service_health():
    """Get status of all mythos services."""
    raw = run_cmd("systemctl list-units 'mythos-*' --no-pager --plain --no-legend")
    services = []
    for line in raw.split("\n"):
        if not line.strip():
            continue
        parts = line.split()
        if len(parts) >= 4:
            name = parts[0].replace(".service", "")
            active = parts[2]  # active/activating/inactive
            sub = parts[3]     # running/auto-restart/dead
            services.append({
                "name": name,
                "active": active,
                "sub": sub,
                "healthy": active == "active" and sub == "running"
            })
    return services


def get_postgres_stats():
    """Get basic PostgreSQL stats."""
    table_count = run_cmd(
        "sudo -u postgres psql -d mythos -t -c \"SELECT count(*) FROM pg_tables WHERE schemaname='public';\""
    ).strip()
    return {"table_count": int(table_count) if table_count.isdigit() else 0}


def get_current_patch_info():
    """Get current patch number and version from get_next_patch_info.sh."""
    raw = run_cmd(f"bash {PATCHES_DIR}/scripts/get_next_patch_info.sh")
    try:
        data = json.loads(raw)
        return {
            "current_patch": data.get("latest_patch", {}).get("number", "unknown"),
            "current_version": data.get("version", {}).get("git_tag", "unknown"),
            "next_patch": data.get("next_patch", {}).get("number", "unknown"),
            "total_patches": data.get("system_status", {}).get("total_patches", 0),
        }
    except (json.JSONDecodeError, KeyError):
        return {
            "current_patch": "unknown",
            "current_version": "unknown",
            "next_patch": "unknown",
            "total_patches": 0,
        }


def get_disk_usage():
    """Get disk usage for /opt/mythos and root filesystem."""
    mythos_size = run_cmd("du -sh /opt/mythos/ 2>/dev/null | cut -f1").strip()
    disk_line = run_cmd("df -h / | tail -1")
    parts = disk_line.split()
    return {
        "mythos_size": mythos_size or "unknown",
        "disk_total": parts[1] if len(parts) > 1 else "unknown",
        "disk_used": parts[2] if len(parts) > 2 else "unknown",
        "disk_avail": parts[3] if len(parts) > 3 else "unknown",
        "disk_pct": parts[4] if len(parts) > 4 else "unknown",
    }


def get_active_work_from_todo():
    """Extract the Active Work section from TODO.md."""
    todo_path = os.path.join(DOCS_DIR, "TODO.md")
    if not os.path.exists(todo_path):
        return "TODO.md not found"

    with open(todo_path) as f:
        content = f.read()

    # Extract between "## 🔥 Active Work" and the next "## " or "---"
    match = re.search(
        r'## 🔥 Active Work\n(.*?)(?=\n## |\n---|\Z)',
        content,
        re.DOTALL
    )
    if match:
        text = match.group(1).strip()
        # Truncate if very long
        lines = text.split("\n")
        if len(lines) > 30:
            return "\n".join(lines[:30]) + "\n... (truncated)"
        return text
    return "No Active Work section found"


def get_known_issues_from_todo():
    """Extract Known Issues from TODO.md."""
    todo_path = os.path.join(DOCS_DIR, "TODO.md")
    if not os.path.exists(todo_path):
        return "TODO.md not found"

    with open(todo_path) as f:
        content = f.read()

    match = re.search(
        r'## 🔥 Known Issues\n(.*?)(?=\n## |\n---|\Z)',
        content,
        re.DOTALL
    )
    if match:
        return match.group(1).strip()
    return "No Known Issues section found"


def get_recent_git_log(count=5):
    """Get recent git commits."""
    return run_cmd(f"git log --oneline -{count}")


# === Generators ===

def generate_system_state():
    """Generate system-state.txt with current system snapshot."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    patch_info = get_current_patch_info()
    services = get_service_health()
    pg_stats = get_postgres_stats()
    disk = get_disk_usage()

    healthy = sum(1 for s in services if s["healthy"])
    unhealthy = [s for s in services if not s["healthy"]]

    lines = [
        f"# Mythos System State",
        f"# Generated: {now}",
        f"",
        f"## Patch & Version",
        f"Current Patch:   {patch_info['current_patch']}",
        f"Current Version: {patch_info['current_version']}",
        f"Next Patch:      {patch_info['next_patch']}",
        f"Total Patches:   {patch_info['total_patches']}",
        f"",
        f"## Services ({healthy}/{len(services)} healthy)",
    ]

    for s in services:
        icon = "✅" if s["healthy"] else "❌"
        lines.append(f"  {icon} {s['name']}: {s['active']}/{s['sub']}")

    if unhealthy:
        lines.append("")
        lines.append("## Unhealthy Services")
        for s in unhealthy:
            lines.append(f"  ⚠️  {s['name']}: {s['active']}/{s['sub']}")

    lines.extend([
        f"",
        f"## Database",
        f"PostgreSQL Tables: {pg_stats['table_count']}",
        f"",
        f"## Disk",
        f"Mythos Size:  {disk['mythos_size']}",
        f"Root Disk:    {disk['disk_used']} / {disk['disk_total']} ({disk['disk_pct']})",
        f"Available:    {disk['disk_avail']}",
    ])

    output = "\n".join(lines) + "\n"
    path = os.path.join(LIVE_DIR, "system-state.txt")
    with open(path, "w") as f:
        f.write(output)
    print(f"  ✅ system-state.txt ({len(lines)} lines)")
    return output


def generate_patch_versions():
    """Generate patch-versions.txt mapping patch numbers to versions."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get mapping from git log
    raw = run_cmd(
        'git log --oneline --all --format="%s %d"'
    )

    entries = []
    for line in raw.split("\n"):
        if "Applied patch:" not in line:
            continue
        patch_match = re.search(r'patch_(\d{4})_([^.]+)', line)
        tag_match = re.search(r'tag: (v[\d.]+)', line)
        if patch_match:
            num = patch_match.group(1)
            desc = patch_match.group(2).replace("_", " ")
            ver = tag_match.group(1) if tag_match else "—"
            entries.append(f"{num} | {ver:12s} | {desc}")

    # Sort by patch number
    entries.sort()

    lines = [
        f"# Patch → Version Mapping",
        f"# Generated: {now}",
        f"# Format: PATCH | VERSION | DESCRIPTION",
        f"",
    ] + entries

    output = "\n".join(lines) + "\n"
    path = os.path.join(LIVE_DIR, "patch-versions.txt")
    with open(path, "w") as f:
        f.write(output)
    print(f"  ✅ patch-versions.txt ({len(entries)} entries)")
    return output


def generate_patch_install_history():
    """Generate patch-install-history.txt from git log."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get applied patches with dates
    raw = run_cmd(
        'git log --all --format="%ai | %s" --grep="Applied patch:"'
    )

    entries = []
    for line in raw.split("\n"):
        if not line.strip():
            continue
        # Clean up the date format
        parts = line.split(" | ", 1)
        if len(parts) == 2:
            date_str = parts[0][:19]  # trim timezone
            msg = parts[1].replace("Applied patch: ", "")
            entries.append(f"{date_str} | {msg} | SUCCESS")

    # Sort chronologically
    entries.sort()

    lines = [
        f"# Patch Install History",
        f"# Generated: {now}",
        f"# Format: TIMESTAMP | PATCH | STATUS",
        f"",
    ] + entries

    output = "\n".join(lines) + "\n"
    path = os.path.join(LIVE_DIR, "patch-install-history.txt")
    with open(path, "w") as f:
        f.write(output)
    print(f"  ✅ patch-install-history.txt ({len(entries)} entries)")
    return output


def generate_claude_context():
    """Generate CLAUDE_CONTEXT.md — the session bootstrap file."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    patch_info = get_current_patch_info()
    services = get_service_health()
    pg_stats = get_postgres_stats()
    disk = get_disk_usage()
    active_work = get_active_work_from_todo()
    known_issues = get_known_issues_from_todo()
    recent_commits = get_recent_git_log(5)

    healthy = sum(1 for s in services if s["healthy"])
    unhealthy = [s for s in services if not s["healthy"]]

    lines = [
        f"# Mythos System Context",
        f"> Auto-generated: {now}",
        f"> Current Patch: {patch_info['current_patch']} / {patch_info['current_version']}",
        f"",
        f"## System Health",
        f"- Services: {healthy}/{len(services)} active"
            + (f" — ⚠️ DOWN: {', '.join(s['name'] for s in unhealthy)}" if unhealthy else ""),
        f"- PostgreSQL Tables: {pg_stats['table_count']}",
        f"- Disk: {disk['disk_used']} / {disk['disk_total']} ({disk['disk_pct']}), "
            f"{disk['disk_avail']} available",
        f"- Mythos Size: {disk['mythos_size']}",
        f"",
        f"## Current Patch/Version",
        f"- Current: {patch_info['current_patch']} / {patch_info['current_version']}",
        f"- Next available: {patch_info['next_patch']}",
        f"- Total patches deployed: {patch_info['total_patches']}",
        f"",
        f"## Active Work",
        active_work,
        f"",
        f"## Known Issues",
        known_issues,
        f"",
        f"## Recent Patches (last 5 commits)",
        f"```",
        recent_commits,
        f"```",
        f"",
        f"## Services",
    ]

    for s in services:
        icon = "✅" if s["healthy"] else "❌"
        lines.append(f"- {icon} `{s['name']}`: {s['active']}/{s['sub']}")

    lines.extend([
        f"",
        f"---",
        f"*To regenerate: `/opt/mythos/.venv/bin/python3 /opt/mythos/tools/generate_system_state.py`*",
    ])

    output = "\n".join(lines) + "\n"
    path = os.path.join(LIVE_DIR, "CLAUDE_CONTEXT.md")
    with open(path, "w") as f:
        f.write(output)
    print(f"  ✅ CLAUDE_CONTEXT.md")
    return output


def main():
    """Generate all live telemetry files."""
    import argparse
    parser = argparse.ArgumentParser(description="Generate Mythos live telemetry files")
    parser.add_argument("--section", default="all",
                        choices=["all", "state", "versions", "history", "context"],
                        help="Which section to generate (default: all)")
    args = parser.parse_args()

    print(f"🔄 Generating live telemetry ({args.section})...")
    os.makedirs(LIVE_DIR, exist_ok=True)
    os.makedirs(os.path.join(LIVE_DIR, "archive"), exist_ok=True)

    if args.section in ("all", "state"):
        generate_system_state()
    if args.section in ("all", "versions"):
        generate_patch_versions()
    if args.section in ("all", "history"):
        generate_patch_install_history()
    if args.section in ("all", "context"):
        generate_claude_context()

    print("✅ Done.")


if __name__ == "__main__":
    main()
