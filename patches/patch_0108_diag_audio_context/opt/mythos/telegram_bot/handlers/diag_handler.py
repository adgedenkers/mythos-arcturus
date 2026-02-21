"""
Mythos Diagnostic System — Telegram Handler
=============================================
Composable diagnostic blocks run via /diag command.

Usage:
  /diag help              — List available blocks
  /diag bot               — Bot service status + recent logs
  /diag db                — PostgreSQL + Neo4j status
  /diag redis             — Redis keys, queues, memory
  /diag net               — Ports, tunnel, proxy
  /diag hw                — Disk, memory, GPU, uptime
  /diag files             — /opt/mythos tree + recent git
  /diag services          — All mythos systemd services
  /diag fastapi           — API routes + entry points
  /diag audio             — Audio pipeline inbox status
  /diag env               — .env keys (values redacted)
  /diag all               — Everything
  /diag log <service> [N] — Tail N lines of a service log

Combine: /diag bot db hw
"""

import os
import subprocess
import tempfile
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes


# ---------------------------------------------------------------------------
# Shell runner
# ---------------------------------------------------------------------------

def _run(cmd: str, timeout: int = 15) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=timeout
        )
        output = result.stdout.strip()
        if result.stderr.strip():
            output += f"\n[stderr] {result.stderr.strip()}"
        return output if output else "(no output)"
    except subprocess.TimeoutExpired:
        return "(command timed out)"
    except Exception as e:
        return f"(error: {e})"


# ---------------------------------------------------------------------------
# Diagnostic blocks
# ---------------------------------------------------------------------------

def diag_bot() -> str:
    lines = ["═══ BOT SERVICE ═══"]
    lines.append(_run("systemctl is-active mythos-bot.service"))
    lines.append("")
    lines.append("── Status ──")
    lines.append(_run("systemctl status mythos-bot.service --no-pager -l 2>&1 | head -25"))
    lines.append("")
    lines.append("── Recent Logs (last 30 lines) ──")
    lines.append(_run("journalctl -u mythos-bot.service --no-pager -n 30"))
    return "\n".join(lines)


def diag_db() -> str:
    lines = ["═══ DATABASES ═══"]
    lines.append("── PostgreSQL ──")
    lines.append(_run("systemctl is-active postgresql"))
    lines.append("")
    lines.append("Tables:")
    lines.append(_run(
        'sudo -u postgres psql -d mythos -c '
        '"SELECT tablename FROM pg_tables WHERE schemaname=\'public\' ORDER BY tablename;"'
    ))
    lines.append("")
    lines.append("Row counts:")
    lines.append(_run(
        'sudo -u postgres psql -d mythos -t -c '
        '"SELECT tablename || \': \' || n_live_tup FROM pg_stat_user_tables ORDER BY tablename;"'
    ))
    lines.append("")
    lines.append("── Neo4j ──")
    lines.append(_run("systemctl is-active neo4j"))
    neo4j_pw = os.environ.get("NEO4J_PASSWORD", "neo4j")
    lines.append(_run(
        f'cypher-shell -u neo4j -p "{neo4j_pw}" '
        '"CALL db.labels() YIELD label '
        'CALL {{ WITH label MATCH (n) WHERE label IN labels(n) RETURN count(n) AS cnt }} '
        'RETURN label, cnt ORDER BY label" 2>&1 || echo "(cypher-shell unavailable)"'
    ))
    return "\n".join(lines)


def diag_redis() -> str:
    lines = ["═══ REDIS ═══"]
    lines.append("── Server ──")
    lines.append(_run("redis-cli info server 2>&1 | head -15"))
    lines.append("")
    lines.append("── Keyspace ──")
    lines.append(_run("redis-cli info keyspace"))
    lines.append("")
    lines.append("── All Keys ──")
    lines.append(_run("redis-cli keys '*' 2>&1 | head -50"))
    lines.append("")
    lines.append("── Queue Lengths ──")
    keys = _run("redis-cli keys '*'").strip().split("\n")
    for key in keys:
        key = key.strip()
        if key and not key.startswith("("):
            ktype = _run(f"redis-cli type '{key}'").strip()
            if ktype == "stream":
                length = _run(f"redis-cli XLEN '{key}'").strip()
                lines.append(f"  {key} (stream): {length} entries")
            elif ktype == "list":
                length = _run(f"redis-cli LLEN '{key}'").strip()
                lines.append(f"  {key} (list): {length} items")
            elif ktype == "hash":
                length = _run(f"redis-cli HLEN '{key}'").strip()
                lines.append(f"  {key} (hash): {length} fields")
            else:
                lines.append(f"  {key} ({ktype})")
    lines.append("")
    lines.append("── Memory ──")
    lines.append(_run("redis-cli info memory 2>&1 | grep -E 'used_memory_human|maxmemory_human|mem_fragmentation'"))
    return "\n".join(lines)


def diag_net() -> str:
    lines = ["═══ NETWORK ═══"]
    lines.append("── Listening Ports ──")
    lines.append(_run("sudo ss -tlnp | head -35"))
    lines.append("")
    lines.append("── Cloudflare Tunnel ──")
    lines.append(_run("systemctl is-active cloudflared 2>&1 || pgrep -a cloudflared 2>&1 || echo '(not found)'"))
    return "\n".join(lines)


def diag_hw() -> str:
    lines = ["═══ HARDWARE ═══"]
    lines.append("── Uptime ──")
    lines.append(_run("uptime"))
    lines.append("")
    lines.append("── Memory ──")
    lines.append(_run("free -h"))
    lines.append("")
    lines.append("── Disk ──")
    lines.append(_run("df -h / /opt /home 2>&1"))
    lines.append("")
    lines.append("── GPU ──")
    lines.append(_run(
        "nvidia-smi --query-gpu=name,memory.used,memory.total,temperature.gpu,utilization.gpu "
        "--format=csv,noheader 2>&1 || echo '(no nvidia-smi)'"
    ))
    lines.append("")
    lines.append("── CPU ──")
    lines.append(_run("lscpu | grep -E 'Model name|Socket|Core|Thread|CPU MHz'"))
    return "\n".join(lines)


def diag_files() -> str:
    lines = ["═══ FILES ═══"]
    lines.append("── Directory Tree (depth 2) ──")
    lines.append(_run("find /opt/mythos -maxdepth 2 -type d -not -path '*/.git/*' -not -path '*/.venv/*' -not -path '*/node_modules/*' -not -path '*/__pycache__/*' | sort"))
    lines.append("")
    lines.append("── Recent Git Log ──")
    lines.append(_run("cd /opt/mythos && git log --oneline -15 2>&1"))
    lines.append("")
    lines.append("── Git Tags (recent) ──")
    lines.append(_run("cd /opt/mythos && git tag --sort=-v:refname | head -10"))
    lines.append("")
    lines.append("── Recently Modified (24h) ──")
    lines.append(_run(
        "find /opt/mythos -type f -mtime -1 "
        "-not -path '*/.git/*' -not -path '*/__pycache__/*' -not -path '*/.venv/*' "
        "| sort | head -30"
    ))
    return "\n".join(lines)


def diag_services() -> str:
    lines = ["═══ MYTHOS SERVICES ═══"]
    lines.append(_run("systemctl list-units 'mythos-*' --no-pager --all"))
    lines.append("")
    lines.append("── Service Files ──")
    lines.append(_run("ls -la /etc/systemd/system/mythos-* 2>&1"))
    return "\n".join(lines)


def diag_fastapi() -> str:
    lines = ["═══ FASTAPI ═══"]
    lines.append("── API Service ──")
    lines.append(_run("systemctl is-active mythos-api.service"))
    lines.append("")
    lines.append("── Routers Included ──")
    lines.append(_run(
        "grep -n 'include_router\\|app\\.add' /opt/mythos/api/main.py 2>&1"
    ))
    lines.append("")
    lines.append("── Route Files ──")
    lines.append(_run("ls -la /opt/mythos/api/routes/ 2>&1"))
    return "\n".join(lines)


def diag_audio() -> str:
    lines = ["═══ AUDIO PIPELINE ═══"]
    inbox = "/opt/mythos/audio/inbox"
    processed = "/opt/mythos/audio/processed"

    if os.path.exists(inbox):
        audio_files = [f for f in os.listdir(inbox) if not f.endswith(".json")]
        lines.append(f"Inbox: {len(audio_files)} files")
        if audio_files:
            lines.append("")
            lines.append("── Recent Files ──")
            lines.append(_run(f"ls -lht {inbox} | head -15"))
    else:
        lines.append("Inbox: directory not created yet")

    if os.path.exists(processed):
        proc_files = [f for f in os.listdir(processed) if not f.endswith(".json")]
        lines.append(f"\nProcessed: {len(proc_files)} files")
    else:
        lines.append("\nProcessed: directory not created yet")

    return "\n".join(lines)


def diag_env() -> str:
    lines = ["═══ ENV (keys only, values redacted) ═══"]
    env_path = "/opt/mythos/.env"
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    lines.append(line)
                elif "=" in line:
                    key = line.split("=", 1)[0]
                    lines.append(f"{key}=****")
                else:
                    lines.append(line)
    else:
        lines.append("(.env not found)")
    return "\n".join(lines)


def diag_log(service: str, n: int = 50) -> str:
    """Tail N lines of a specific service journal."""
    safe_service = "".join(c for c in service if c.isalnum() or c in "-_.")
    lines = [f"═══ LOG: {safe_service} (last {n} lines) ═══"]
    lines.append(_run(f"journalctl -u {safe_service} --no-pager -n {n}"))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Block registry
# ---------------------------------------------------------------------------

DIAG_BLOCKS = {
    "bot":      ("Bot service & logs", diag_bot),
    "db":       ("PostgreSQL & Neo4j", diag_db),
    "redis":    ("Redis keys, queues, memory", diag_redis),
    "net":      ("Network & tunnel", diag_net),
    "hw":       ("Hardware & resources", diag_hw),
    "files":    ("File tree & git log", diag_files),
    "services": ("All Mythos services", diag_services),
    "fastapi":  ("FastAPI routes", diag_fastapi),
    "audio":    ("Audio pipeline", diag_audio),
    "env":      ("Environment keys (redacted)", diag_env),
}


def run_diagnostics(blocks: list[str] | None = None) -> str:
    if not blocks or blocks == ["all"]:
        blocks = list(DIAG_BLOCKS.keys())

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    parts = [f"╔══ MYTHOS DIAGNOSTICS ══╗\n║ {timestamp}\n╚════════════════════════╝\n"]

    unknown = [b for b in blocks if b not in DIAG_BLOCKS]
    if unknown:
        available = ", ".join(DIAG_BLOCKS.keys())
        parts.append(f"⚠ Unknown: {', '.join(unknown)}")
        parts.append(f"Available: {available}\n")

    for name in blocks:
        if name in DIAG_BLOCKS:
            _, func = DIAG_BLOCKS[name]
            try:
                parts.append(func())
            except Exception as e:
                parts.append(f"═══ {name.upper()} ═══\n(error: {e})")
            parts.append("")

    return "\n".join(parts)


def get_help() -> str:
    lines = ["📊 Diagnostic Commands:\n"]
    for name, (desc, _) in DIAG_BLOCKS.items():
        lines.append(f"  /diag {name}  — {desc}")
    lines.append(f"\n  /diag all  — Run everything")
    lines.append(f"  /diag log <service> [N]  — Tail service log")
    lines.append(f"\nCombine: /diag bot db hw")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Telegram handler
# ---------------------------------------------------------------------------

async def handle_diag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /diag command."""
    args = context.args or []

    if not args or args[0] == "help":
        await update.message.reply_text(get_help())
        return

    # Special case: /diag log <service> [N]
    if args[0] == "log":
        if len(args) < 2:
            await update.message.reply_text("Usage: /diag log <service-name> [lines]\nExample: /diag log mythos-bot 50")
            return
        service = args[1]
        n = 50
        if len(args) >= 3:
            try:
                n = int(args[2])
            except ValueError:
                n = 50
        result = diag_log(service, n)
    else:
        result = run_diagnostics(args)

    # Send as message or file depending on length
    if len(result) <= 4000:
        await update.message.reply_text(f"```\n{result}\n```", parse_mode="Markdown")
    else:
        # Send as file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, prefix="diag_"
        ) as f:
            f.write(result)
            temp_path = f.name
        try:
            with open(temp_path, "rb") as f:
                await update.message.reply_document(
                    document=f,
                    filename=f"diag_{'_'.join(args)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    caption=f"📊 Diagnostics: {' '.join(args)}"
                )
        finally:
            os.unlink(temp_path)
