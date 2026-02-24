#!/usr/bin/env python3
"""
Telegram Bot Handler: /diag — Comprehensive System Diagnostics

Usage:
  /diag              — Full system diagnostic (returned as file)
  /diag bot          — Bot service status + recent logs
  /diag db           — PostgreSQL + Neo4j
  /diag docker       — All containers + Iris status
  /diag hw           — Disk, RAM, GPU, uptime
  /diag services     — All mythos-* systemd units
  /diag ollama       — Models + VRAM usage
  /diag net          — Listening ports
  /diag redis        — Redis keyspace + info
  /diag patches      — Recent patches, version, git tags
  /diag bot db hw    — Combine any blocks

Results always sent as a .txt file attachment.
Single-block results under 4000 chars also shown inline.

Patch 0121 — v1.19.0
"""

import os
import subprocess
import tempfile
import logging
from datetime import datetime
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

MYTHOS_ROOT = Path("/opt/mythos")

# Auth — loaded once on import
_AUTHORIZED_IDS = set()
for _key in ("TELEGRAM_ID_KA", "TELEGRAM_ID_SERAPHE"):
    _val = os.getenv(_key)
    if _val:
        try:
            _AUTHORIZED_IDS.add(int(_val))
        except ValueError:
            pass


# ---------------------------------------------------------------------------
# Shell helper
# ---------------------------------------------------------------------------

def _run(cmd: str, timeout: int = 20) -> str:
    """Run a shell command, return combined stdout+stderr."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        out = r.stdout.strip()
        if r.stderr.strip():
            out += f"\n[stderr] {r.stderr.strip()}"
        return out or "(no output)"
    except subprocess.TimeoutExpired:
        return "(timed out)"
    except Exception as e:
        return f"(error: {e})"


# ---------------------------------------------------------------------------
# Diagnostic blocks
# ---------------------------------------------------------------------------

def diag_hw() -> str:
    """Hardware: disk, memory, GPU, uptime, load."""
    lines = ["═══ HARDWARE ═══"]

    lines.append("── Uptime & Load ──")
    lines.append(_run("uptime"))

    lines.append("\n── Disk ──")
    lines.append(_run("df -h / /opt /home 2>/dev/null | sort -u"))

    lines.append("\n── Memory ──")
    lines.append(_run("free -h"))

    lines.append("\n── Swap ──")
    lines.append(_run("swapon --show 2>/dev/null || echo '(no swap info)'"))

    lines.append("\n── GPU ──")
    lines.append(_run(
        "nvidia-smi --query-gpu=name,temperature.gpu,memory.used,memory.total,utilization.gpu "
        "--format=csv,noheader 2>/dev/null || echo '(no nvidia-smi)'"
    ))

    lines.append("\n── CPU ──")
    lines.append(_run("lscpu | grep -E 'Model name|CPU\\(s\\)|Thread|Core' | head -5"))

    return "\n".join(lines)


def diag_services() -> str:
    """All mythos-* systemd services."""
    lines = ["═══ SYSTEMD SERVICES ═══"]
    lines.append(_run("systemctl list-units 'mythos-*' --no-pager --all"))
    return "\n".join(lines)


def diag_bot() -> str:
    """Bot service status and recent journal entries."""
    lines = ["═══ BOT SERVICE ═══"]

    lines.append("── Status ──")
    lines.append(_run("systemctl status mythos-bot.service --no-pager -l 2>&1 | head -20"))

    lines.append("\n── Recent Logs (40 lines) ──")
    lines.append(_run("journalctl -u mythos-bot.service --no-pager -n 40 --output=short-iso"))

    return "\n".join(lines)


def diag_db() -> str:
    """PostgreSQL and Neo4j status."""
    lines = ["═══ DATABASES ═══"]

    lines.append("── PostgreSQL ──")
    lines.append(_run("systemctl is-active postgresql"))
    lines.append("")
    lines.append("Tables + row counts:")
    lines.append(_run(
        'sudo -u postgres psql -d mythos -t -c '
        '"SELECT relname || \': \' || n_live_tup '
        'FROM pg_stat_user_tables ORDER BY relname;" 2>&1'
    ))

    lines.append("\n── Database Size ──")
    lines.append(_run(
        "sudo -u postgres psql -d mythos -t -c "
        "\"SELECT pg_size_pretty(pg_database_size('mythos'));\" 2>&1"
    ))

    lines.append("\n── Neo4j ──")
    lines.append(_run("systemctl is-active neo4j"))
    lines.append("")
    lines.append("Node counts:")
    lines.append(_run(
        'cypher-shell -u neo4j -p "${NEO4J_PASSWORD:-neo4j}" '
        '"CALL db.labels() YIELD label '
        'CALL { WITH label MATCH (n) WHERE label IN labels(n) RETURN count(n) AS cnt } '
        'RETURN label, cnt ORDER BY label" 2>&1 '
        '|| echo "(cypher-shell unavailable)"'
    ))

    return "\n".join(lines)


def diag_docker() -> str:
    """Docker containers and Iris status."""
    lines = ["═══ DOCKER ═══"]

    lines.append("── All Containers ──")
    lines.append(_run(
        'docker ps -a --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}" 2>&1'
    ))

    lines.append("\n── Docker Disk Usage ──")
    lines.append(_run("docker system df 2>&1"))

    lines.append("\n── Iris Core Status ──")
    lines.append(_run(
        'curl -s --max-time 5 http://localhost:8100/status 2>/dev/null '
        '| python3 -m json.tool 2>/dev/null '
        '|| echo "(iris-core unreachable)"'
    ))

    lines.append("\n── Iris Logs (last 20) ──")
    lines.append(_run("docker logs iris-core --tail 20 2>&1"))

    return "\n".join(lines)


def diag_ollama() -> str:
    """Ollama models and running models."""
    lines = ["═══ OLLAMA ═══"]

    lines.append("── Installed Models ──")
    lines.append(_run("ollama list 2>&1"))

    lines.append("\n── Currently Loaded (VRAM) ──")
    lines.append(_run("ollama ps 2>&1"))

    lines.append("\n── Ollama Service ──")
    lines.append(_run("systemctl is-active ollama 2>/dev/null || echo '(not a systemd service)'"))

    return "\n".join(lines)


def diag_redis() -> str:
    """Redis status and keyspace."""
    lines = ["═══ REDIS ═══"]

    lines.append("── Ping ──")
    lines.append(_run("redis-cli ping 2>&1"))

    lines.append("\n── Keyspace ──")
    lines.append(_run("redis-cli info keyspace 2>&1"))

    lines.append("\n── All Keys ──")
    lines.append(_run("redis-cli keys '*' 2>&1"))

    lines.append("\n── Memory ──")
    lines.append(_run("redis-cli info memory 2>&1 | grep -E 'used_memory_human|maxmemory_human|mem_fragmentation'"))

    return "\n".join(lines)


def diag_net() -> str:
    """Listening ports and network info."""
    lines = ["═══ NETWORK ═══"]

    lines.append("── Listening Ports (mythos-related) ──")
    lines.append(_run(
        "ss -tlnp 2>/dev/null | grep -E ':(5432|7474|7687|6379|6333|6334|8100|8000|8080|2283|11434)' "
        "|| echo '(no matches)'"
    ))

    lines.append("\n── All Listening TCP ──")
    lines.append(_run("ss -tlnp 2>/dev/null | head -30"))

    return "\n".join(lines)


def diag_patches() -> str:
    """Patch system state, version, recent tags."""
    lines = ["═══ PATCHES & VERSION ═══"]

    lines.append("── Version ──")
    lines.append(_run("cat /opt/mythos/.version 2>&1"))

    lines.append("\n── Recent Git Tags ──")
    lines.append(_run("cd /opt/mythos && git tag -l --sort=-v:refname | head -10"))

    lines.append("\n── Latest Patches (by directory) ──")
    lines.append(_run(
        "ls -1d /opt/mythos/patches/patch_* 2>/dev/null | sort -V | tail -10 | xargs -I{} basename {}"
    ))

    lines.append("\n── Git Status ──")
    lines.append(_run("cd /opt/mythos && git status --short | head -20"))

    lines.append("\n── Recent Commits ──")
    lines.append(_run("cd /opt/mythos && git log --oneline -10"))

    # Next patch info if script exists
    npi = Path("/opt/mythos/patches/scripts/get_next_patch_info.sh")
    if npi.exists():
        lines.append("\n── Next Patch Info ──")
        lines.append(_run(str(npi)))

    return "\n".join(lines)


def diag_api() -> str:
    """FastAPI gateway status."""
    lines = ["═══ API GATEWAY ═══"]

    lines.append("── Service ──")
    lines.append(_run("systemctl status mythos-api.service --no-pager -l 2>&1 | head -15"))

    lines.append("\n── Health Check ──")
    lines.append(_run(
        'curl -s --max-time 5 http://localhost:8000/health 2>/dev/null '
        '| python3 -m json.tool 2>/dev/null '
        '|| curl -s --max-time 5 http://localhost:8000/ 2>/dev/null '
        '| python3 -m json.tool 2>/dev/null '
        '|| echo "(API unreachable)"'
    ))

    return "\n".join(lines)


def diag_workers() -> str:
    """All worker services status."""
    lines = ["═══ WORKERS ═══"]

    worker_services = [
        "mythos-worker-embedding",
        "mythos-worker-entity",
        "mythos-worker-grid",
        "mythos-worker-summary",
        "mythos-worker-temporal",
        "mythos-worker-vision",
        "mythos-transcription-worker",
        "mythos-voice-watcher",
        "mythos-knowledge-map",
    ]

    for svc in worker_services:
        status = _run(f"systemctl is-active {svc}.service 2>&1")
        emoji = "✅" if status.strip() == "active" else "❌"
        lines.append(f"  {emoji} {svc}: {status.strip()}")

    lines.append("\n── Worker Logs (last errors) ──")
    lines.append(_run(
        "journalctl -u 'mythos-worker-*' --no-pager -p err -n 15 --output=short-iso 2>&1 "
        "|| echo '(no recent errors)'"
    ))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Block registry
# ---------------------------------------------------------------------------

DIAG_BLOCKS = {
    "hw":       ("Hardware, disk, RAM, GPU",   diag_hw),
    "services": ("All mythos systemd units",   diag_services),
    "bot":      ("Bot service & logs",         diag_bot),
    "db":       ("PostgreSQL & Neo4j",         diag_db),
    "docker":   ("Containers & Iris",          diag_docker),
    "ollama":   ("LLM models & VRAM",          diag_ollama),
    "redis":    ("Redis keyspace & memory",    diag_redis),
    "net":      ("Listening ports & network",  diag_net),
    "patches":  ("Version, tags, patches",     diag_patches),
    "api":      ("FastAPI gateway",            diag_api),
    "workers":  ("Worker services status",     diag_workers),
}

# "all" runs these in this order
ALL_ORDER = ["hw", "services", "workers", "bot", "api", "db", "docker", "ollama", "redis", "net", "patches"]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_diagnostics(blocks: list[str] | None = None) -> str:
    """Run diagnostic blocks, return combined output string."""
    if not blocks:
        blocks = ALL_ORDER

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts = [
        f"╔══════════════════════════════════════╗",
        f"║   MYTHOS SYSTEM DIAGNOSTIC           ║",
        f"║   {ts}                ║",
        f"║   Blocks: {', '.join(blocks):<25s} ║",
        f"╚══════════════════════════════════════╝",
        "",
    ]

    for block_name in blocks:
        if block_name not in DIAG_BLOCKS:
            parts.append(f"⚠ Unknown block: {block_name}")
            continue
        _desc, func = DIAG_BLOCKS[block_name]
        try:
            parts.append(func())
        except Exception as e:
            parts.append(f"═══ {block_name.upper()} ═══\n(error: {e})")
        parts.append("")

    return "\n".join(parts)


def get_help_text() -> str:
    """Return /diag help."""
    lines = [
        "🔍 <b>System Diagnostics</b>",
        "",
        "<b>Usage:</b>",
        "  /diag          — Full diagnostic (as file)",
        "  /diag &lt;blocks&gt; — Specific blocks (as file)",
        "",
        "<b>Available blocks:</b>",
    ]
    for name, (desc, _) in DIAG_BLOCKS.items():
        lines.append(f"  <code>{name:10s}</code> {desc}")
    lines.append("")
    lines.append("<b>Combine:</b> <code>/diag bot db hw</code>")
    lines.append("<b>Everything:</b> <code>/diag all</code>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Telegram command handler
# ---------------------------------------------------------------------------

async def handle_diag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /diag [block1 block2 ...] — Run system diagnostics.
    No args or 'all' = full diagnostic. 'help' = show blocks.
    Always returns a .txt file. Small results also shown inline.
    """
    user_id = update.effective_user.id
    if _AUTHORIZED_IDS and user_id not in _AUTHORIZED_IDS:
        await update.message.reply_text("❌ Not authorized.")
        return

    args = context.args if context.args else []
    args = [a.lower().strip() for a in args]

    # Help
    if args == ["help"]:
        await update.message.reply_text(get_help_text(), parse_mode="HTML")
        return

    # Determine blocks
    if not args or args == ["all"]:
        blocks = None  # = all
        label = "full"
    else:
        blocks = args
        label = "-".join(blocks)

    # Send "working" indicator
    msg = await update.message.reply_text("⏳ Running diagnostics...")

    try:
        output = run_diagnostics(blocks)
    except Exception as e:
        await msg.edit_text(f"❌ Diagnostic failed: {e}")
        return

    # Write to temp file
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"diag_{label}_{ts}.txt"

    tmp_path = os.path.join(tempfile.gettempdir(), filename)
    with open(tmp_path, "w") as f:
        f.write(output)

    # Send as file
    try:
        with open(tmp_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=filename,
                caption=f"📊 Diagnostic: {label} ({len(output)} bytes)",
            )
    finally:
        os.unlink(tmp_path)

    # Also send inline if small enough and single-block
    if blocks and len(blocks) == 1 and len(output) < 4000:
        await update.message.reply_text(
            f"<pre>{output[:3900]}</pre>",
            parse_mode="HTML",
        )

    # Clean up "working" message
    try:
        await msg.delete()
    except Exception:
        pass
