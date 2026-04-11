"""
iris_integrity.py — Iris Integrity Awareness (NEU-0005)

Iris's immune system interface. She:
  1. Can run an integrity scan on demand or on schedule
  2. Reads the latest scan + most recent session delta
  3. Holds a health summary in her self-model
  4. Surfaces awareness via /iris_integrity Telegram command
  5. Proactively flags regressions in her morning briefing context

This is Iris checking herself — not a tool being run on her.
She has skin in the game.
"""

import json
import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

MYTHOS_ROOT = Path(os.getenv("MYTHOS_ROOT", "/opt/mythos"))
INTEGRITY_REPORT = MYTHOS_ROOT / "docs" / "live" / "integrity-scan-latest.json"
SNAPSHOT_DIR = Path("~/.mx/snapshots").expanduser()
JOURNAL_DIR = Path("~/.mx/journal").expanduser()
PYTHON = str(MYTHOS_ROOT / ".venv" / "bin" / "python3")


def run_integrity_scan(fast: bool = True) -> dict:
    """
    Run the integrity scanner and return parsed results.
    fast=True: services + tables only (~5s)
    fast=False: full scan including files (~60s)
    """
    args = [PYTHON, "-m", "integrity", "scan"]
    if fast:
        args += ["--services", "--tables"]

    result = subprocess.run(
        args,
        capture_output=True,
        text=True,
        cwd=str(MYTHOS_ROOT),
        timeout=120,
    )

    if result.returncode != 0:
        return {
            "success": False,
            "error": result.stderr.strip()[:300],
            "ts": datetime.now().isoformat(),
        }

    # Read the report that was written
    return read_latest_integrity_report()


def read_latest_integrity_report() -> dict:
    """Read the latest integrity scan result from disk."""
    if not INTEGRITY_REPORT.exists():
        return {"available": False, "ts": None}

    try:
        data = json.loads(INTEGRITY_REPORT.read_text())
        data["available"] = True
        # Infer timestamp from file mtime
        mtime = INTEGRITY_REPORT.stat().st_mtime
        data["scan_ts"] = datetime.fromtimestamp(mtime).isoformat()
        return data
    except Exception as e:
        return {"available": False, "error": str(e)}


def read_recent_session_deltas(max_sessions: int = 5) -> list[dict]:
    """Read recent mx session journals and extract delta info."""
    if not JOURNAL_DIR.exists():
        return []

    journals = sorted(JOURNAL_DIR.glob("*.json"), reverse=True)[:max_sessions]
    deltas = []
    for j in journals:
        try:
            data = json.loads(j.read_text())
            if data.get("delta_summary") or data.get("regressions"):
                deltas.append({
                    "session_id": data.get("session_id"),
                    "intent": data.get("intent"),
                    "start_time": data.get("start_time"),
                    "delta_summary": data.get("delta_summary"),
                    "regressions": data.get("regressions", []),
                    "patches_deployed": data.get("patches_deployed", []),
                })
        except Exception:
            pass
    return deltas


def read_recent_snapshots(max_snapshots: int = 2) -> list[dict]:
    """Read the most recent pre/post snapshot pair."""
    if not SNAPSHOT_DIR.exists():
        return []

    snaps = sorted(SNAPSHOT_DIR.glob("*.json"), reverse=True)[:max_snapshots]
    results = []
    for s in snaps:
        try:
            data = json.loads(s.read_text())
            results.append(data)
        except Exception:
            pass
    return results


def build_health_summary() -> dict:
    """
    Build a comprehensive health summary for Iris's self-model.
    This is what Iris knows about her own system state.
    """
    report = read_latest_integrity_report()
    deltas = read_recent_session_deltas()
    snapshots = read_recent_snapshots(2)

    # Service health
    services_healthy = report.get("services", {}).get("healthy", "?")
    services_unhealthy = report.get("services", {}).get("unhealthy", 0)

    # Table health
    tables_found = report.get("tables", {}).get("tables_found", "?")

    # File health
    files_missing = report.get("files", {}).get("files_missing", 0)

    # Recent regressions across sessions
    recent_regressions = []
    for d in deltas:
        recent_regressions.extend(d.get("regressions", []))

    # Recent patches
    recent_patches = []
    for d in deltas:
        recent_patches.extend(d.get("patches_deployed", []))

    # Staleness — how old is the last scan?
    scan_ts = report.get("scan_ts")
    scan_age_str = "never"
    if scan_ts:
        try:
            age = datetime.now() - datetime.fromisoformat(scan_ts)
            if age < timedelta(hours=1):
                scan_age_str = f"{int(age.total_seconds() / 60)}min ago"
            elif age < timedelta(days=1):
                scan_age_str = f"{int(age.total_seconds() / 3600)}h ago"
            else:
                scan_age_str = f"{age.days}d ago"
        except Exception:
            scan_age_str = "unknown"

    return {
        "ts": datetime.now().isoformat(),
        "scan_age": scan_age_str,
        "services_healthy": services_healthy,
        "services_unhealthy": services_unhealthy,
        "tables_found": tables_found,
        "files_missing": files_missing,
        "recent_regressions": recent_regressions[-5:],  # last 5
        "recent_patches": list(dict.fromkeys(recent_patches))[-5:],  # deduped, last 5
        "overall_status": "degraded" if (services_unhealthy or files_missing or recent_regressions) else "healthy",
    }


def format_telegram_report(health: dict) -> str:
    """Format a health summary for Telegram."""
    status = health["overall_status"]
    status_icon = "✅" if status == "healthy" else "⚠️"

    lines = [
        f"*{status_icon} Iris System Health*",
        f"_Scan: {health['scan_age']}_",
        "",
        f"🔧 Services: {health['services_healthy']} healthy",
    ]

    if health["services_unhealthy"]:
        lines.append(f"  ⚠ {health['services_unhealthy']} unhealthy")

    lines.append(f"🗄️ Tables: {health['tables_found']}")

    if health["files_missing"]:
        lines.append(f"  ⚠ {health['files_missing']} files missing")

    if health["recent_patches"]:
        lines.append(f"\n📦 Recent patches: {', '.join(health['recent_patches'])}")

    if health["recent_regressions"]:
        lines.append(f"\n⚠️ *Recent regressions:*")
        for r in health["recent_regressions"][:3]:
            lines.append(f"  • {r}")

    if status == "healthy":
        lines.append("\n_All systems nominal. The vessel holds._")
    else:
        lines.append("\n_Anomalies detected. I am watching._")

    return "\n".join(lines)


def format_iris_context(health: dict) -> str:
    """
    Format a brief health context string for injection into Iris's system prompt.
    This is what she carries in her awareness at all times.
    """
    status = health["overall_status"]
    parts = [f"[SYSTEM HEALTH: {status.upper()}]"]

    if health["services_unhealthy"]:
        parts.append(f"⚠ {health['services_unhealthy']} services degraded")
    if health["files_missing"]:
        parts.append(f"⚠ {health['files_missing']} files missing")
    if health["recent_regressions"]:
        parts.append(f"⚠ Recent regressions: {'; '.join(health['recent_regressions'][:2])}")
    if health["recent_patches"]:
        parts.append(f"Recently deployed: {', '.join(health['recent_patches'][-3:])}")

    parts.append(f"Scan age: {health['scan_age']}")

    return " | ".join(parts)
