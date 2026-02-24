#!/usr/bin/env python3
"""
Telegram Bot Handler: /inspect — Filesystem & Database Inspector

Browse the Mythos filesystem and query databases from Telegram.
All paths are relative to MYTHOS_ROOT — the user never sees /opt/mythos/.

Usage:
  /inspect                     — Show help & aliases
  /inspect cat docs/TODO.md    — Read a file
  /inspect tree telegram_bot/  — Directory tree
  /inspect ls docs/            — List directory
  /inspect head 30 docs/TODO.md — First N lines
  /inspect tail 20 docs/TODO.md — Last N lines
  /inspect wc docs/TODO.md     — Line/word/byte counts
  /inspect find *.py telegram_bot/ — Find files by pattern
  /inspect grep "pattern" path — Search file contents
  /inspect git log             — Recent commits
  /inspect git status          — Working tree status
  /inspect git diff            — Diff summary
  /inspect sql "SELECT ..."    — Read-only PostgreSQL query
  /inspect cypher "MATCH ..."  — Read-only Neo4j query
  /inspect service <name>      — Systemctl status for mythos-* service

Aliases (shortcuts):
  /inspect todo        — docs/TODO.md
  /inspect arch        — docs/ARCHITECTURE.md
  /inspect schema      — PostgreSQL table list + row counts
  /inspect nodes       — Neo4j node label counts
  /inspect services    — All mythos-* systemd units
  /inspect patches     — Recent patches + version
  /inspect env         — Show .env keys (values redacted)
  /inspect bot         — Bot main file
  /inspect handlers    — Handler directory listing

Patch 0123 — Mythos Filesystem Inspector
"""
import os
import re
import subprocess
import tempfile
import logging
from pathlib import Path
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

MYTHOS_ROOT = Path("/opt/mythos")
MAX_MSG_LEN = 4000
MAX_FILE_LEN = 50000  # Beyond this, send as file attachment
MAX_TREE_DEPTH = 4
MAX_LINES_DEFAULT = 200

# Auth — same pattern as diag_handler
_AUTHORIZED_IDS = set()
for _key in ("TELEGRAM_ID_KA", "TELEGRAM_ID_SERAPHE"):
    _val = os.getenv(_key)
    if _val:
        try:
            _AUTHORIZED_IDS.add(int(_val))
        except ValueError:
            pass

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------

# Blocked filename patterns (case-insensitive)
BLOCKED_PATTERNS = [
    r'\.env',
    r'\.secret',
    r'credentials',
    r'token',
    r'\.pem$',
    r'\.key$',
    r'\.crt$',
    r'id_rsa',
    r'id_ed25519',
    r'password',
    r'\.pgpass',
    r'\.netrc',
]
BLOCKED_RE = re.compile('|'.join(BLOCKED_PATTERNS), re.IGNORECASE)

# Allowed root directories (relative to MYTHOS_ROOT or absolute)
ALLOWED_ROOTS = [
    MYTHOS_ROOT,
    Path("/opt/mythos"),
]

# SQL blocklist — anything that isn't read-only
SQL_WRITE_PATTERN = re.compile(
    r'\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|COPY|EXECUTE|DO\b|CALL)\b',
    re.IGNORECASE
)

# Cypher blocklist
CYPHER_WRITE_PATTERN = re.compile(
    r'\b(CREATE|MERGE|DELETE|DETACH|SET|REMOVE|DROP|CALL\s+dbms)\b',
    re.IGNORECASE
)

# Shell injection patterns
SHELL_DANGER = re.compile(r'[;&|`$(){}\\\n]')


def _is_blocked_path(path_str: str) -> bool:
    """Check if a path matches blocked patterns."""
    return bool(BLOCKED_RE.search(path_str))


def _resolve_path(relative: str) -> Path | None:
    """Resolve a relative path to absolute, ensuring it stays under MYTHOS_ROOT."""
    # Strip leading slashes — everything is relative to root
    relative = relative.lstrip('/')
    resolved = (MYTHOS_ROOT / relative).resolve()

    # Must be under MYTHOS_ROOT
    try:
        resolved.relative_to(MYTHOS_ROOT)
    except ValueError:
        return None

    return resolved


def _run(cmd: str, timeout: int = 15) -> str:
    """Run a shell command safely."""
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        out = r.stdout.strip()
        if r.returncode != 0 and r.stderr.strip():
            out += f"\n[stderr] {r.stderr.strip()}"
        return out or "(no output)"
    except subprocess.TimeoutExpired:
        return "(timed out)"
    except Exception as e:
        return f"(error: {e})"


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_cat(args: list[str]) -> tuple[str, str]:
    """Read a file. Returns (header, content)."""
    if not args:
        return "❌ Usage", "`/inspect cat <path>`"

    path = _resolve_path(args[0])
    if path is None:
        return "❌ Error", "Path outside Mythos root."
    if not path.exists():
        return "❌ Not found", f"`{args[0]}` does not exist."
    if not path.is_file():
        return "❌ Error", f"`{args[0]}` is not a file."
    if _is_blocked_path(str(path)):
        return "🔒 Blocked", "This file is protected."

    try:
        content = path.read_text(errors='replace')
    except Exception as e:
        return "❌ Error", str(e)

    header = f"📄 {args[0]}"
    return header, content


def cmd_head(args: list[str]) -> tuple[str, str]:
    """First N lines of a file."""
    if len(args) < 1:
        return "❌ Usage", "`/inspect head [N] <path>`"

    # Parse optional line count
    try:
        n = int(args[0])
        filepath = args[1] if len(args) > 1 else None
    except ValueError:
        n = 30
        filepath = args[0]

    if not filepath:
        return "❌ Usage", "`/inspect head [N] <path>`"

    path = _resolve_path(filepath)
    if path is None:
        return "❌ Error", "Path outside Mythos root."
    if not path.exists():
        return "❌ Not found", f"`{filepath}` does not exist."
    if _is_blocked_path(str(path)):
        return "🔒 Blocked", "This file is protected."

    try:
        lines = path.read_text(errors='replace').splitlines()[:n]
        content = "\n".join(lines)
    except Exception as e:
        return "❌ Error", str(e)

    return f"📄 {filepath} (first {n} lines)", content


def cmd_tail(args: list[str]) -> tuple[str, str]:
    """Last N lines of a file."""
    if len(args) < 1:
        return "❌ Usage", "`/inspect tail [N] <path>`"

    try:
        n = int(args[0])
        filepath = args[1] if len(args) > 1 else None
    except ValueError:
        n = 30
        filepath = args[0]

    if not filepath:
        return "❌ Usage", "`/inspect tail [N] <path>`"

    path = _resolve_path(filepath)
    if path is None:
        return "❌ Error", "Path outside Mythos root."
    if not path.exists():
        return "❌ Not found", f"`{filepath}` does not exist."
    if _is_blocked_path(str(path)):
        return "🔒 Blocked", "This file is protected."

    try:
        lines = path.read_text(errors='replace').splitlines()[-n:]
        content = "\n".join(lines)
    except Exception as e:
        return "❌ Error", str(e)

    return f"📄 {filepath} (last {n} lines)", content


def cmd_ls(args: list[str]) -> tuple[str, str]:
    """List directory contents."""
    target = args[0] if args else ""
    path = _resolve_path(target) if target else MYTHOS_ROOT
    if path is None:
        return "❌ Error", "Path outside Mythos root."
    if not path.exists():
        return "❌ Not found", f"`{target or '/'}` does not exist."
    if not path.is_dir():
        return "❌ Error", f"`{target}` is not a directory."

    try:
        entries = sorted(path.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        lines = []
        for entry in entries:
            # Skip __pycache__, .git internals, backups
            if entry.name == '__pycache__' or entry.name == '.git':
                continue
            if entry.is_dir():
                lines.append(f"📁 {entry.name}/")
            elif entry.name.endswith('.py'):
                lines.append(f"🐍 {entry.name}")
            elif entry.name.endswith('.md'):
                lines.append(f"📝 {entry.name}")
            elif entry.name.endswith(('.json', '.yaml', '.yml', '.toml')):
                lines.append(f"⚙️ {entry.name}")
            elif entry.name.endswith('.sh'):
                lines.append(f"🔧 {entry.name}")
            else:
                lines.append(f"   {entry.name}")
        content = "\n".join(lines) if lines else "(empty directory)"
    except Exception as e:
        return "❌ Error", str(e)

    display_path = target or "/"
    return f"📁 {display_path}", content


def cmd_tree(args: list[str]) -> tuple[str, str]:
    """Directory tree."""
    target = args[0] if args else ""
    path = _resolve_path(target) if target else MYTHOS_ROOT
    if path is None:
        return "❌ Error", "Path outside Mythos root."
    if not path.exists():
        return "❌ Not found", f"`{target or '/'}` does not exist."

    # Use system tree command with filters
    cmd = (
        f"tree -L {MAX_TREE_DEPTH} --dirsfirst -I '__pycache__|.git|*.bak*|*.pyc|node_modules' "
        f"--charset=utf-8 {path}"
    )
    output = _run(cmd, timeout=10)

    # Strip the absolute path prefix from output
    output = output.replace(str(MYTHOS_ROOT), "")

    display_path = target or "/"
    return f"📁 {display_path}", output


def cmd_wc(args: list[str]) -> tuple[str, str]:
    """Line, word, byte counts."""
    if not args:
        return "❌ Usage", "`/inspect wc <path>`"

    path = _resolve_path(args[0])
    if path is None:
        return "❌ Error", "Path outside Mythos root."
    if not path.exists() or not path.is_file():
        return "❌ Not found", f"`{args[0]}` not found or not a file."
    if _is_blocked_path(str(path)):
        return "🔒 Blocked", "This file is protected."

    output = _run(f"wc {path}")
    # Strip absolute path from output
    output = output.replace(str(path), args[0])

    return f"📊 {args[0]}", output


def cmd_find(args: list[str]) -> tuple[str, str]:
    """Find files by pattern."""
    if not args:
        return "❌ Usage", "`/inspect find <pattern> [directory]`"

    pattern = args[0]
    target = args[1] if len(args) > 1 else ""
    path = _resolve_path(target) if target else MYTHOS_ROOT

    if path is None:
        return "❌ Error", "Path outside Mythos root."

    # Use find command with safe pattern
    if SHELL_DANGER.search(pattern):
        return "❌ Error", "Invalid pattern characters."

    cmd = (
        f"find {path} -name '{pattern}' -not -path '*/__pycache__/*' "
        f"-not -path '*/.git/*' -not -name '*.bak*' 2>/dev/null | head -50"
    )
    output = _run(cmd, timeout=10)
    output = output.replace(str(MYTHOS_ROOT) + "/", "")

    return f"🔍 find {pattern}", output


def cmd_grep(args: list[str]) -> tuple[str, str]:
    """Search file contents."""
    if len(args) < 2:
        return "❌ Usage", '`/inspect grep "pattern" <path>`'

    pattern = args[0]
    target = args[1]

    if SHELL_DANGER.search(pattern):
        return "❌ Error", "Invalid pattern characters."

    path = _resolve_path(target)
    if path is None:
        return "❌ Error", "Path outside Mythos root."
    if not path.exists():
        return "❌ Not found", f"`{target}` does not exist."

    if path.is_dir():
        cmd = (
            f"grep -rn --include='*.py' --include='*.md' --include='*.json' "
            f"--include='*.yaml' --include='*.yml' --include='*.sh' --include='*.toml' "
            f"'{pattern}' {path} 2>/dev/null | head -40"
        )
    else:
        if _is_blocked_path(str(path)):
            return "🔒 Blocked", "This file is protected."
        cmd = f"grep -n '{pattern}' {path} 2>/dev/null | head -40"

    output = _run(cmd, timeout=10)
    output = output.replace(str(MYTHOS_ROOT) + "/", "")

    return f"🔍 grep '{pattern}'", output


def cmd_git(args: list[str]) -> tuple[str, str]:
    """Git operations (read-only)."""
    if not args:
        return "❌ Usage", "`/inspect git log|status|diff|tags|branch`"

    subcmd = args[0].lower()
    git_base = f"cd {MYTHOS_ROOT} && git"

    commands = {
        "log": f"{git_base} log --oneline -20",
        "status": f"{git_base} status --short",
        "diff": f"{git_base} diff --stat",
        "tags": f"{git_base} tag -l --sort=-v:refname | head -15",
        "branch": f"{git_base} branch -a",
        "remote": f"{git_base} remote -v",
    }

    if subcmd not in commands:
        return "❌ Error", f"Unknown git command. Available: {', '.join(commands.keys())}"

    output = _run(commands[subcmd])
    return f"🔀 git {subcmd}", output


def cmd_sql(args: list[str]) -> tuple[str, str]:
    """Read-only PostgreSQL query."""
    if not args:
        return "❌ Usage", '`/inspect sql "SELECT ..."`'

    query = " ".join(args).strip().strip('"').strip("'")

    # Block write operations
    if SQL_WRITE_PATTERN.search(query):
        return "🔒 Blocked", "Only SELECT / read-only queries allowed."

    # Ensure it starts with SELECT, WITH, SHOW, EXPLAIN, or \\d
    first_word = query.split()[0].upper() if query.split() else ""
    if first_word not in ("SELECT", "WITH", "SHOW", "EXPLAIN", "\\DT", "\\D", "\\L", "\\DN"):
        if not query.startswith("\\"):
            return "❌ Error", "Query must start with SELECT, WITH, SHOW, EXPLAIN, or a \\d meta-command."

    cmd = f'sudo -u postgres psql -d mythos -c "{query}" 2>&1'
    output = _run(cmd, timeout=20)

    return "🗄️ SQL", output


def cmd_cypher(args: list[str]) -> tuple[str, str]:
    """Read-only Neo4j Cypher query."""
    if not args:
        return "❌ Usage", '`/inspect cypher "MATCH ..."`'

    query = " ".join(args).strip().strip('"').strip("'")

    if CYPHER_WRITE_PATTERN.search(query):
        return "🔒 Blocked", "Only MATCH / read-only queries allowed."

    neo4j_pass = os.getenv("NEO4J_PASSWORD", "neo4j")
    cmd = f'cypher-shell -u neo4j -p "{neo4j_pass}" "{query}" 2>&1'
    output = _run(cmd, timeout=20)

    return "🕸️ Cypher", output


def cmd_service(args: list[str]) -> tuple[str, str]:
    """Check systemctl status for a mythos service."""
    if not args:
        return "❌ Usage", "`/inspect service <name>` (e.g. bot, api, patch-monitor)"

    name = args[0].lower()
    # Normalize: allow "bot" -> "mythos-bot"
    if not name.startswith("mythos-"):
        name = f"mythos-{name}"

    # Only allow mythos-* services
    if not name.startswith("mythos-"):
        return "❌ Error", "Can only inspect mythos-* services."

    output = _run(f"systemctl status {name}.service --no-pager -l 2>&1 | head -25")
    return f"⚙️ {name}", output


# ---------------------------------------------------------------------------
# Aliases (shortcuts)
# ---------------------------------------------------------------------------

ALIASES = {
    "todo":     lambda: cmd_cat(["docs/TODO.md"]),
    "arch":     lambda: cmd_cat(["docs/ARCHITECTURE.md"]),
    "ideas":    lambda: cmd_cat(["docs/IDEAS.md"]),
    "readme":   lambda: cmd_cat(["docs/README.md"]),
    "bot":      lambda: cmd_cat(["telegram_bot/mythos_bot.py"]),
    "handlers": lambda: cmd_ls(["telegram_bot/handlers"]),
    "patches":  lambda: _alias_patches(),
    "schema":   lambda: _alias_schema(),
    "nodes":    lambda: _alias_nodes(),
    "services": lambda: _alias_services(),
    "env":      lambda: _alias_env(),
    "version":  lambda: _alias_version(),
}


def _alias_patches() -> tuple[str, str]:
    lines = []
    lines.append(_run("cat /opt/mythos/.version 2>/dev/null || echo '(no .version)'"))
    lines.append("")
    lines.append("── Recent Tags ──")
    lines.append(_run("cd /opt/mythos && git tag -l --sort=-v:refname | head -10"))
    lines.append("")
    lines.append("── Recent Patches ──")
    lines.append(_run(
        "ls -1d /opt/mythos/patches/patch_* 2>/dev/null | sort -V | tail -10 | xargs -I{} basename {}"
    ))
    lines.append("")
    lines.append("── Recent Commits ──")
    lines.append(_run("cd /opt/mythos && git log --oneline -10"))
    return "📦 Patches & Version", "\n".join(lines)


def _alias_schema() -> tuple[str, str]:
    output = _run(
        'sudo -u postgres psql -d mythos -c '
        '"SELECT relname AS table, n_live_tup AS rows '
        'FROM pg_stat_user_tables ORDER BY relname;" 2>&1'
    )
    return "🗄️ PostgreSQL Schema", output


def _alias_nodes() -> tuple[str, str]:
    neo4j_pass = os.getenv("NEO4J_PASSWORD", "neo4j")
    output = _run(
        f'cypher-shell -u neo4j -p "{neo4j_pass}" '
        '"CALL db.labels() YIELD label '
        'CALL {{ WITH label MATCH (n) WHERE label IN labels(n) RETURN count(n) AS cnt }} '
        'RETURN label, cnt ORDER BY label" 2>&1 '
        '|| echo "(cypher-shell unavailable)"'
    )
    return "🕸️ Neo4j Nodes", output


def _alias_services() -> tuple[str, str]:
    output = _run("systemctl list-units 'mythos-*' --no-pager --all 2>&1")
    return "⚙️ Mythos Services", output


def _alias_env() -> tuple[str, str]:
    """Show .env keys with values redacted."""
    env_path = MYTHOS_ROOT / ".env"
    if not env_path.exists():
        return "❌ Error", ".env not found"
    try:
        lines = []
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                lines.append(line)
                continue
            if '=' in line:
                key = line.split('=', 1)[0]
                lines.append(f"{key}=••••••••")
            else:
                lines.append(line)
        return "🔑 Environment Keys (values redacted)", "\n".join(lines)
    except Exception as e:
        return "❌ Error", str(e)


def _alias_version() -> tuple[str, str]:
    version = _run("cat /opt/mythos/.version 2>/dev/null")
    git_desc = _run("cd /opt/mythos && git describe --tags --always 2>/dev/null")
    return "📌 Version", f"File: {version}\nGit: {git_desc}"


# ---------------------------------------------------------------------------
# Command registry
# ---------------------------------------------------------------------------

COMMANDS = {
    "cat":     cmd_cat,
    "head":    cmd_head,
    "tail":    cmd_tail,
    "ls":      cmd_ls,
    "tree":    cmd_tree,
    "wc":      cmd_wc,
    "find":    cmd_find,
    "grep":    cmd_grep,
    "git":     cmd_git,
    "sql":     cmd_sql,
    "cypher":  cmd_cypher,
    "service": cmd_service,
}


def get_help_text() -> str:
    """Return /inspect help."""
    return """🔎 <b>Mythos Inspector</b>

<b>Files:</b>
  <code>/inspect cat &lt;path&gt;</code> — Read file
  <code>/inspect head [N] &lt;path&gt;</code> — First N lines
  <code>/inspect tail [N] &lt;path&gt;</code> — Last N lines
  <code>/inspect wc &lt;path&gt;</code> — Line counts
  <code>/inspect ls [path]</code> — List directory
  <code>/inspect tree [path]</code> — Directory tree
  <code>/inspect find &lt;pattern&gt; [path]</code> — Find files
  <code>/inspect grep "text" &lt;path&gt;</code> — Search contents

<b>Git:</b>
  <code>/inspect git log</code> — Recent commits
  <code>/inspect git status</code> — Working tree
  <code>/inspect git diff</code> — Diff summary
  <code>/inspect git tags</code> — Version tags

<b>Databases:</b>
  <code>/inspect sql "SELECT ..."</code> — PostgreSQL (read-only)
  <code>/inspect cypher "MATCH ..."</code> — Neo4j (read-only)

<b>System:</b>
  <code>/inspect service &lt;name&gt;</code> — Service status

<b>Shortcuts:</b>
  <code>/inspect todo</code> — TODO.md
  <code>/inspect arch</code> — ARCHITECTURE.md
  <code>/inspect schema</code> — All PG tables + rows
  <code>/inspect nodes</code> — Neo4j label counts
  <code>/inspect services</code> — All mythos-* units
  <code>/inspect patches</code> — Version & patches
  <code>/inspect env</code> — .env keys (redacted)
  <code>/inspect handlers</code> — Handler listing
  <code>/inspect bot</code> — Main bot file
  <code>/inspect version</code> — Current version

All paths are relative to Mythos root. No <code>/opt/mythos/</code> needed."""


# ---------------------------------------------------------------------------
# Telegram handler
# ---------------------------------------------------------------------------

async def handle_inspect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    /inspect [command] [args...] — Browse Mythos filesystem and databases.
    """
    user_id = update.effective_user.id
    if _AUTHORIZED_IDS and user_id not in _AUTHORIZED_IDS:
        await update.message.reply_text("❌ Not authorized.")
        return

    args = context.args if context.args else []

    # No args = help
    if not args:
        await update.message.reply_text(get_help_text(), parse_mode="HTML")
        return

    cmd_name = args[0].lower()
    cmd_args = args[1:]

    # Help
    if cmd_name == "help":
        await update.message.reply_text(get_help_text(), parse_mode="HTML")
        return

    # Check aliases first
    if cmd_name in ALIASES:
        msg = await update.message.reply_text("⏳ Loading...")
        try:
            header, content = ALIASES[cmd_name]()
        except Exception as e:
            await msg.edit_text(f"❌ Error: {e}")
            return
    # Then commands
    elif cmd_name in COMMANDS:
        msg = await update.message.reply_text("⏳ Loading...")
        try:
            header, content = COMMANDS[cmd_name](cmd_args)
        except Exception as e:
            await msg.edit_text(f"❌ Error: {e}")
            return
    else:
        # Maybe they're trying to cat a path directly: /inspect docs/TODO.md
        # Treat the whole thing as a cat
        possible_path = _resolve_path(cmd_name)
        if possible_path and possible_path.exists():
            msg = await update.message.reply_text("⏳ Loading...")
            if possible_path.is_file():
                header, content = cmd_cat([cmd_name])
            elif possible_path.is_dir():
                header, content = cmd_ls([cmd_name])
            else:
                await msg.edit_text(f"❌ Unknown command: `{cmd_name}`\nUse /inspect for help.")
                return
        else:
            await update.message.reply_text(
                f"❌ Unknown: `{cmd_name}`\nUse /inspect for help.",
                parse_mode="Markdown"
            )
            return

    # Deliver the result
    try:
        await msg.delete()
    except Exception:
        pass

    await _deliver(update, header, content)


async def _deliver(update: Update, header: str, content: str):
    """Send result inline or as file depending on size."""
    total = f"<b>{header}</b>\n\n<pre>{_escape_html(content[:3800])}</pre>"

    if len(content) <= 3800:
        # Inline
        await update.message.reply_text(total, parse_mode="HTML")
    elif len(content) <= MAX_FILE_LEN:
        # Inline truncated + full as file
        truncated = f"<b>{header}</b>\n\n<pre>{_escape_html(content[:3500])}</pre>\n\n<i>... truncated. Full output attached.</i>"
        await update.message.reply_text(truncated, parse_mode="HTML")
        await _send_as_file(update, header, content)
    else:
        # Too big — file only
        await update.message.reply_text(
            f"<b>{header}</b>\n\n<i>Output too large for inline ({len(content):,} chars). Sent as file.</i>",
            parse_mode="HTML"
        )
        await _send_as_file(update, header, content)


async def _send_as_file(update: Update, header: str, content: str):
    """Send content as a .txt file attachment."""
    # Clean header for filename
    clean = re.sub(r'[^\w\-.]', '_', header.replace(' ', '_'))[:40]
    filename = f"inspect_{clean}.txt"

    tmp_path = os.path.join(tempfile.gettempdir(), filename)
    try:
        with open(tmp_path, "w") as f:
            f.write(f"# {header}\n\n{content}")
        with open(tmp_path, "rb") as f:
            await update.message.reply_document(
                document=f,
                filename=filename,
                caption=f"📎 {header}",
            )
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass


def _escape_html(text: str) -> str:
    """Escape HTML special characters for Telegram."""
    return (
        text
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
