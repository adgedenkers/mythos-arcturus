"""
mx_snapshot.py — System state snapshot serializer (SYS-0028)

Captures a point-in-time snapshot of Mythos system state:
  - Services (name, active/inactive)
  - PostgreSQL table count + row counts for key tables
  - Git state (hash, message, clean/dirty)
  - Integrity scan results (from docs/live/integrity-scan-latest.json)
  - Active Ollama model

Snapshots written to ~/.mx/snapshots/ as JSON.
Does NOT run the integrity scanner itself — reads the latest result.
The integrity scanner is invoked by mx_hooks.py pre/post operation.
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path

SNAPSHOT_DIR = Path("~/.mx/snapshots").expanduser()
INTEGRITY_REPORT = Path("/opt/mythos/docs/live/integrity-scan-latest.json")
MYTHOS_ROOT = Path("/opt/mythos")


def _run(cmd: str, default: str = "") -> str:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
        return r.stdout.strip() if r.returncode == 0 else default
    except Exception:
        return default


def capture_services() -> dict:
    """Get status of all mythos-* services."""
    raw = _run("systemctl list-units --type=service --all | grep mythos-")
    services = {}
    for line in raw.splitlines():
        parts = line.split()
        if not parts:
            continue
        name = parts[0].replace(".service", "")
        active = "active" in line
        services[name] = "active" if active else "inactive"
    return services


def capture_git() -> dict:
    """Get current git state of /opt/mythos."""
    git_hash = _run("git -C /opt/mythos rev-parse --short HEAD", "unknown")
    git_msg = _run("git -C /opt/mythos log -1 --pretty=%s", "")
    git_clean = _run("git -C /opt/mythos status --porcelain", "clean") == ""
    git_branch = _run("git -C /opt/mythos rev-parse --abbrev-ref HEAD", "unknown")
    return {
        "hash": git_hash,
        "message": git_msg,
        "clean": git_clean,
        "branch": git_branch,
    }


def capture_postgres() -> dict:
    """Get table count and row counts for key tables."""
    def pg(sql: str) -> str:
        return _run(f"sudo -u postgres psql -d mythos -tAc \"{sql}\" 2>/dev/null")

    table_count_raw = pg("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'")
    try:
        table_count = int(table_count_raw.strip())
    except ValueError:
        table_count = -1

    # Key table row counts for regression detection
    key_tables = [
        "transactions", "recurring_bills", "accounts", "people",
        "chat_messages", "life_events", "routines", "calendar_events",
    ]
    row_counts = {}
    for t in key_tables:
        raw = pg(f"SELECT COUNT(*) FROM {t}")
        try:
            row_counts[t] = int(raw.strip())
        except ValueError:
            row_counts[t] = -1

    return {"table_count": table_count, "row_counts": row_counts}


def capture_ollama_model() -> str:
    """Get the currently active Ollama model."""
    override_file = Path("/opt/mythos/.model_overrides.json")
    if override_file.exists():
        try:
            data = json.loads(override_file.read_text())
            if data.get("model"):
                return data["model"]
        except Exception:
            pass
    return "gemma3:27b"


def capture_integrity() -> dict:
    """
    Read the latest integrity scan result.
    Returns summary stats, not the full report.
    """
    if not INTEGRITY_REPORT.exists():
        return {"available": False}
    try:
        data = json.loads(INTEGRITY_REPORT.read_text())
        summary = {"available": True}
        if "services" in data:
            summary["services_healthy"] = data["services"].get("healthy", 0)
            summary["services_unhealthy"] = data["services"].get("unhealthy", 0)
        if "tables" in data:
            summary["tables_found"] = data["tables"].get("tables_found", 0)
        if "files" in data:
            summary["files_active"] = data["files"].get("files_scanned", 0)
            summary["files_missing"] = data["files"].get("files_missing", 0)
        return summary
    except Exception as e:
        return {"available": False, "error": str(e)}


def take_snapshot(trigger: str = "manual", label: str = "") -> str:
    """
    Capture full system state snapshot.
    Returns path to the snapshot JSON file.
    """
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    ts = datetime.now()
    ts_str = ts.strftime("%Y-%m-%d_%H%M%S")
    filename = f"{ts_str}_{label or trigger}.json"
    filepath = SNAPSHOT_DIR / filename

    snapshot = {
        "ts": ts.isoformat(),
        "trigger": trigger,
        "label": label,
        "services": capture_services(),
        "git": capture_git(),
        "postgres": capture_postgres(),
        "ollama_model": capture_ollama_model(),
        "integrity": capture_integrity(),
    }

    filepath.write_text(json.dumps(snapshot, indent=2))
    return str(filepath)


def load_snapshot(path: str) -> dict:
    return json.loads(Path(path).read_text())
