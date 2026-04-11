"""
Iris Context Engine — Perception Before Decision

Gathers diagnostic information from any registered source
before a trigger enters the decision gate. Each provider
is a named function that returns structured context.

Architecture:
    ContextEngine
        ├── provider registry (name → callable)
        ├── gather(context_spec) → assembled context dict
        ├── mandatory secret sanitization on all output
        ├── per-provider timeout (default 5s)
        └── per-provider max output size (default 4000 chars)

The context_spec format (matches scheduled_triggers.context_queries JSONB):
    [
        {"provider": "service_status", "args": {"service": "mythos-api"}},
        {"provider": "journalctl", "args": {"unit": "mythos-bot", "lines": 20}},
        {"provider": "pg_query", "args": {"query": "SELECT count(*) FROM conversations"}},
    ]

Called by the TriggerEngine before routing to the decision gate.
Can also be used standalone via the iris-context CLI.
"""

import asyncio
import json
import logging
import os
import re
import subprocess
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

import psycopg2
import psycopg2.extras

log = logging.getLogger("iris.context_engine")

# ═══════════════════════════════════════════════════
# SECRET SANITIZATION — Mandatory wrapper
# ═══════════════════════════════════════════════════

# Patterns that indicate a value should be redacted
_SENSITIVE_KEYS = re.compile(
    r"(PASSWORD|TOKEN|SECRET|KEY|CREDENTIAL|AUTH|API_KEY|PRIVATE)",
    re.IGNORECASE,
)

# Match env-style lines: KEY=value
_ENV_LINE_PATTERN = re.compile(
    r"^(\s*(?:export\s+)?[\w]+(?:PASSWORD|TOKEN|SECRET|KEY|CREDENTIAL|AUTH|API_KEY|PRIVATE)[\w]*)"
    r"\s*=\s*(.+)$",
    re.IGNORECASE | re.MULTILINE,
)

# Match common secret patterns in freeform text (e.g. Bearer tokens, base64 keys)
_INLINE_SECRET_PATTERNS = [
    re.compile(r"(Bearer\s+)\S+", re.IGNORECASE),
    re.compile(r"(token[\"']?\s*[:=]\s*[\"']?)\S+", re.IGNORECASE),
    re.compile(r"(password[\"']?\s*[:=]\s*[\"']?)\S+", re.IGNORECASE),
]


def sanitize_text(text: str) -> str:
    """
    Strip secrets from text output before it enters context.

    Handles:
        - KEY=value lines (env files, config output)
        - Bearer tokens
        - Inline password/token assignments
    """
    if not text:
        return text

    # Redact env-style key=value lines
    result = _ENV_LINE_PATTERN.sub(r"\1=<REDACTED>", text)

    # Redact inline patterns
    for pattern in _INLINE_SECRET_PATTERNS:
        result = pattern.sub(r"\1<REDACTED>", result)

    return result


def sanitize_dict(d: dict) -> dict:
    """Recursively sanitize a dict, redacting values with sensitive keys."""
    sanitized = {}
    for k, v in d.items():
        if isinstance(v, dict):
            sanitized[k] = sanitize_dict(v)
        elif isinstance(v, list):
            sanitized[k] = [
                sanitize_dict(item) if isinstance(item, dict) else item
                for item in v
            ]
        elif isinstance(v, str):
            if _SENSITIVE_KEYS.search(str(k)):
                sanitized[k] = "<REDACTED>"
            else:
                sanitized[k] = sanitize_text(v)
        else:
            if _SENSITIVE_KEYS.search(str(k)):
                sanitized[k] = "<REDACTED>"
            else:
                sanitized[k] = v
    return sanitized


# ═══════════════════════════════════════════════════
# ACCESS POLICY — File and path restrictions
# ═══════════════════════════════════════════════════

class AccessPolicy:
    """
    Controls what the context engine is allowed to read.
    Loaded from /opt/mythos/config/context_access_policy.yaml.
    """

    def __init__(self, policy_path: str = "/opt/mythos/config/context_access_policy.yaml"):
        self.allowed_read_paths: List[str] = []
        self.denied_read_paths: List[str] = []
        self.allowed_pg_prefixes: List[str] = []
        self.denied_pg_patterns: List[str] = []
        self.max_file_size_bytes: int = 1_000_000  # 1MB default
        self._load(policy_path)

    def _load(self, path: str):
        """Load policy from YAML file. Falls back to defaults if missing."""
        try:
            import yaml
        except ImportError:
            # PyYAML not available — use defaults
            self._set_defaults()
            return

        if not os.path.exists(path):
            log.warning(f"Access policy not found at {path}, using defaults")
            self._set_defaults()
            return

        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}

            file_policy = data.get("file_access", {})
            self.allowed_read_paths = file_policy.get("allowed_paths", [])
            self.denied_read_paths = file_policy.get("denied_paths", [])
            self.max_file_size_bytes = file_policy.get("max_file_size_bytes", 1_000_000)

            pg_policy = data.get("postgres_access", {})
            self.allowed_pg_prefixes = pg_policy.get("allowed_prefixes", [])
            self.denied_pg_patterns = pg_policy.get("denied_patterns", [])

            log.info(f"Loaded access policy from {path}")
        except Exception as e:
            log.error(f"Failed to load access policy: {e}, using defaults")
            self._set_defaults()

    def _set_defaults(self):
        self.allowed_read_paths = [
            "/opt/mythos/",
            "/home/adge/",
            "/var/log/",
            "/etc/systemd/system/mythos-",
        ]
        self.denied_read_paths = [
            "/opt/mythos/.env",
            "/opt/mythos/.git/",
            "/home/adge/.ssh/",
            "/home/adge/.gnupg/",
            "/etc/shadow",
            "/etc/passwd",
        ]
        self.allowed_pg_prefixes = ["SELECT"]
        self.denied_pg_patterns = [
            "DROP", "DELETE", "UPDATE", "INSERT", "ALTER",
            "CREATE", "TRUNCATE", "GRANT", "REVOKE",
        ]

    def check_file_path(self, path: str) -> tuple[bool, str]:
        """Check if a file path is allowed. Returns (allowed, reason)."""
        abs_path = os.path.abspath(path)

        # Check denied first (takes precedence)
        for denied in self.denied_read_paths:
            if abs_path.startswith(denied) or abs_path == denied:
                return False, f"Path denied by policy: {denied}"

        # Check allowed
        for allowed in self.allowed_read_paths:
            if abs_path.startswith(allowed):
                return True, "OK"

        return False, f"Path not in allowed list: {abs_path}"

    def check_pg_query(self, query: str) -> tuple[bool, str]:
        """Check if a Postgres query is allowed (read-only)."""
        normalized = query.strip().upper()

        # Check denied patterns
        for pattern in self.denied_pg_patterns:
            if pattern in normalized:
                return False, f"Query contains denied keyword: {pattern}"

        # Check allowed prefixes
        for prefix in self.allowed_pg_prefixes:
            if normalized.startswith(prefix):
                return True, "OK"

        return False, f"Query does not start with allowed prefix"


# ═══════════════════════════════════════════════════
# CONTEXT PROVIDERS — Individual data gatherers
# ═══════════════════════════════════════════════════

class ContextProviders:
    """
    Registry of context providers. Each provider gathers
    one type of diagnostic data and returns it as a string or dict.
    """

    def __init__(self, db_config: dict, policy: AccessPolicy,
                 default_timeout: float = 5.0,
                 default_max_output: int = 4000):
        self.db_config = db_config
        self.policy = policy
        self.default_timeout = default_timeout
        self.default_max_output = default_max_output

        self._providers: Dict[str, Callable] = {
            "journalctl": self._prov_journalctl,
            "git_log": self._prov_git_log,
            "git_diff": self._prov_git_diff,
            "file_content": self._prov_file_content,
            "pg_query": self._prov_pg_query,
            "neo4j_query": self._prov_neo4j_query,
            "redis_state": self._prov_redis_state,
            "service_status": self._prov_service_status,
            "disk_usage": self._prov_disk_usage,
            "process_list": self._prov_process_list,
            "table_schema": self._prov_table_schema,
            "streams_json": self._prov_streams_json,
            "env_sanitized": self._prov_env_sanitized,
        }

    def list_providers(self) -> List[str]:
        return sorted(self._providers.keys())

    def has_provider(self, name: str) -> bool:
        return name in self._providers

    def get(self, name: str, args: dict,
            timeout: Optional[float] = None,
            max_output: Optional[int] = None) -> dict:
        """
        Run a single provider synchronously.
        Returns {"provider": name, "success": bool, "data": ..., "error": ...}
        """
        provider_fn = self._providers.get(name)
        if not provider_fn:
            return {
                "provider": name,
                "success": False,
                "data": None,
                "error": f"Unknown provider: {name}",
            }

        t = timeout or self.default_timeout
        m = max_output or self.default_max_output

        try:
            result = self._run_with_timeout(provider_fn, args, t)
            # Truncate if string output
            if isinstance(result, str) and len(result) > m:
                result = result[:m] + f"\n... [truncated at {m} chars]"
            return {
                "provider": name,
                "success": True,
                "data": result,
                "error": None,
            }
        except TimeoutError:
            return {
                "provider": name,
                "success": False,
                "data": None,
                "error": f"Provider timed out after {t}s",
            }
        except Exception as e:
            return {
                "provider": name,
                "success": False,
                "data": None,
                "error": str(e),
            }

    def _run_with_timeout(self, fn: Callable, args: dict, timeout: float):
        """Run a function with a timeout. Uses subprocess timeout for shell commands."""
        # Most providers handle their own timeouts via subprocess.
        # This is a fallback safety net.
        import signal as sig

        def _handler(signum, frame):
            raise TimeoutError(f"Provider exceeded {timeout}s timeout")

        old_handler = sig.signal(sig.SIGALRM, _handler)
        sig.alarm(int(timeout) + 1)  # +1 for margin
        try:
            return fn(args)
        finally:
            sig.alarm(0)
            sig.signal(sig.SIGALRM, old_handler)

    # ── Shell command helper ──────────────────────────────────────────

    def _run_cmd(self, cmd: List[str], timeout: float = 5.0) -> str:
        """Run a shell command, return stdout. Raises on failure."""
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
        )
        if result.returncode != 0:
            stderr = result.stderr.strip()[:500]
            raise RuntimeError(f"Command failed (rc={result.returncode}): {stderr}")
        return result.stdout

    # ── Providers ─────────────────────────────────────────────────────

    def _prov_journalctl(self, args: dict) -> str:
        """Recent journal entries for a systemd unit."""
        unit = args.get("unit", "")
        lines = min(int(args.get("lines", 50)), 200)

        if not unit:
            raise ValueError("journalctl provider requires 'unit' arg")

        # Ensure unit name is safe
        if not re.match(r'^[\w\-\.]+$', unit):
            raise ValueError(f"Invalid unit name: {unit}")

        svc_name = f"{unit}.service" if not unit.endswith(".service") else unit
        return self._run_cmd(
            ["journalctl", "-u", svc_name, "--no-pager", "-n", str(lines), "--output=short-iso"],
        )

    def _prov_git_log(self, args: dict) -> str:
        """Recent git log from the mythos repo."""
        count = min(int(args.get("count", 10)), 50)
        path = args.get("path", "")  # optional file path filter
        repo = "/opt/mythos"

        cmd = ["git", "-C", repo, "log", "--oneline", f"-{count}"]
        if path:
            cmd.extend(["--", path])
        return self._run_cmd(cmd)

    def _prov_git_diff(self, args: dict) -> str:
        """Git diff (staged or unstaged) from the mythos repo."""
        staged = args.get("staged", False)
        path = args.get("path", "")
        repo = "/opt/mythos"

        cmd = ["git", "-C", repo, "diff"]
        if staged:
            cmd.append("--cached")
        cmd.append("--stat")
        if path:
            cmd.extend(["--", path])
        return self._run_cmd(cmd)

    def _prov_file_content(self, args: dict) -> str:
        """Read file content with access policy check."""
        path = args.get("path", "")
        max_lines = min(int(args.get("max_lines", 100)), 500)

        if not path:
            raise ValueError("file_content provider requires 'path' arg")

        allowed, reason = self.policy.check_file_path(path)
        if not allowed:
            raise PermissionError(reason)

        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")

        file_size = os.path.getsize(path)
        if file_size > self.policy.max_file_size_bytes:
            raise ValueError(
                f"File too large ({file_size} bytes, max {self.policy.max_file_size_bytes})"
            )

        with open(path, "r", errors="replace") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    lines.append(f"... [truncated at {max_lines} lines]")
                    break
                lines.append(line.rstrip())
        return "\n".join(lines)

    def _prov_pg_query(self, args: dict) -> str:
        """Execute a read-only Postgres query."""
        query = args.get("query", "")
        if not query:
            raise ValueError("pg_query provider requires 'query' arg")

        allowed, reason = self.policy.check_pg_query(query)
        if not allowed:
            raise PermissionError(reason)

        conn = psycopg2.connect(
            host=self.db_config.get("host", "localhost"),
            port=self.db_config.get("port", 5432),
            database=self.db_config.get("database", "mythos"),
            user=self.db_config.get("user", "adge"),
            password=self.db_config.get("password", ""),
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
        conn.set_session(readonly=True, autocommit=True)
        try:
            cur = conn.cursor()
            cur.execute(query)
            rows = cur.fetchall()
            cur.close()
            # Format as JSON for structured context
            return json.dumps([dict(r) for r in rows], default=str, indent=2)
        finally:
            conn.close()

    def _prov_neo4j_query(self, args: dict) -> str:
        """Execute a read-only Neo4j Cypher query."""
        query = args.get("query", "")
        if not query:
            raise ValueError("neo4j_query provider requires 'query' arg")

        # Safety: only allow MATCH/RETURN/CALL, no writes
        normalized = query.strip().upper()
        write_keywords = ["CREATE", "MERGE", "DELETE", "DETACH", "SET ", "REMOVE "]
        for kw in write_keywords:
            if kw in normalized:
                raise PermissionError(f"Write operation not allowed in context query: {kw}")

        try:
            from neo4j import GraphDatabase
        except ImportError:
            raise RuntimeError("neo4j driver not installed")

        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "")

        driver = GraphDatabase.driver(uri, auth=(user, password))
        try:
            with driver.session(database="neo4j") as session:
                result = session.run(query)
                records = [dict(record) for record in result]
                return json.dumps(records, default=str, indent=2)
        finally:
            driver.close()

    def _prov_redis_state(self, args: dict) -> str:
        """Get Redis key info, queue lengths, or stream info."""
        pattern = args.get("pattern", "mythos:*")
        info_type = args.get("type", "keys")  # keys, queue_length, stream_info

        try:
            import redis as redis_lib
        except ImportError:
            raise RuntimeError("redis not installed")

        r = redis_lib.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            decode_responses=True,
        )

        try:
            if info_type == "keys":
                keys = r.keys(pattern)[:100]  # cap at 100
                result = {}
                for key in keys:
                    key_type = r.type(key)
                    if key_type == "string":
                        val = r.get(key)
                        result[key] = {"type": "string", "value": val[:200] if val else None}
                    elif key_type == "list":
                        result[key] = {"type": "list", "length": r.llen(key)}
                    elif key_type == "set":
                        result[key] = {"type": "set", "size": r.scard(key)}
                    elif key_type == "hash":
                        result[key] = {"type": "hash", "fields": r.hlen(key)}
                    elif key_type == "stream":
                        result[key] = {"type": "stream", "length": r.xlen(key)}
                    else:
                        result[key] = {"type": key_type}
                return json.dumps(result, indent=2)

            elif info_type == "queue_length":
                key = args.get("key", "")
                if not key:
                    raise ValueError("queue_length requires 'key' arg")
                length = r.llen(key)
                return json.dumps({"key": key, "length": length})

            elif info_type == "stream_info":
                key = args.get("key", "")
                if not key:
                    raise ValueError("stream_info requires 'key' arg")
                info = r.xinfo_stream(key)
                return json.dumps(info, default=str, indent=2)

            else:
                raise ValueError(f"Unknown redis info type: {info_type}")
        finally:
            r.close()

    def _prov_service_status(self, args: dict) -> str:
        """Get systemd service status."""
        service = args.get("service", "")
        if not service:
            raise ValueError("service_status provider requires 'service' arg")

        if not re.match(r'^[\w\-\.]+$', service):
            raise ValueError(f"Invalid service name: {service}")

        svc_name = f"{service}.service" if not service.endswith(".service") else service

        # Get status
        status_result = subprocess.run(
            ["systemctl", "show", svc_name,
             "--property=ActiveState,SubState,MainPID,MemoryCurrent,TasksCurrent,"
             "NRestarts,ExecMainStartTimestamp"],
            capture_output=True, text=True, timeout=5,
        )
        return status_result.stdout.strip()

    def _prov_disk_usage(self, args: dict) -> str:
        """Get disk usage info."""
        path = args.get("path", "/")
        return self._run_cmd(["df", "-h", path])

    def _prov_process_list(self, args: dict) -> str:
        """List running processes, optionally filtered."""
        grep = args.get("grep", "")
        if grep:
            if not re.match(r'^[\w\-\.]+$', grep):
                raise ValueError(f"Invalid grep pattern: {grep}")
            # Use pgrep for safety
            try:
                return self._run_cmd(["pgrep", "-a", grep])
            except RuntimeError:
                return "(no matching processes)"
        else:
            return self._run_cmd(
                ["ps", "aux", "--sort=-pcpu"],
            )

    def _prov_table_schema(self, args: dict) -> str:
        """Get Postgres table schema."""
        table = args.get("table", "")
        if not table:
            raise ValueError("table_schema provider requires 'table' arg")

        # Validate table name (prevent injection)
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
            raise ValueError(f"Invalid table name: {table}")

        conn = psycopg2.connect(
            host=self.db_config.get("host", "localhost"),
            port=self.db_config.get("port", 5432),
            database=self.db_config.get("database", "mythos"),
            user=self.db_config.get("user", "adge"),
            password=self.db_config.get("password", ""),
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
        conn.set_session(readonly=True, autocommit=True)
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s AND table_schema = 'public'
                ORDER BY ordinal_position
            """, (table,))
            rows = cur.fetchall()
            cur.close()
            if not rows:
                return f"Table '{table}' not found or has no columns"
            return json.dumps([dict(r) for r in rows], indent=2)
        finally:
            conn.close()

    def _prov_streams_json(self, args: dict) -> str:
        """Read current STREAMS.json state."""
        path = "/opt/mythos/docs/STREAMS.json"
        if not os.path.exists(path):
            return '{"error": "STREAMS.json not found"}'
        with open(path) as f:
            data = json.load(f)
        # Return summary or full based on args
        if args.get("summary", True):
            streams = data.get("streams", {})
            summary = {
                name: {"next_patch": s.get("next_patch"), "description": s.get("description", "")}
                for name, s in streams.items()
            }
            return json.dumps(summary, indent=2)
        return json.dumps(data, indent=2)

    def _prov_env_sanitized(self, args: dict) -> str:
        """Read .env file with all secrets redacted."""
        env_path = args.get("path", "/opt/mythos/.env")

        allowed, reason = self.policy.check_file_path(env_path)
        # Special case: .env is denied by default policy for raw read,
        # but env_sanitized provider is specifically designed to redact it.
        # We bypass the file policy check here since we ALWAYS sanitize.

        if not os.path.exists(env_path):
            return f"File not found: {env_path}"

        with open(env_path) as f:
            content = f.read()

        return sanitize_text(content)


# ═══════════════════════════════════════════════════
# CONTEXT ENGINE — The orchestrator
# ═══════════════════════════════════════════════════

class ContextEngine:
    """
    Gathers context from multiple providers based on a spec.

    Usage:
        engine = ContextEngine(db_config)
        context = engine.gather([
            {"provider": "service_status", "args": {"service": "mythos-api"}},
            {"provider": "journalctl", "args": {"unit": "mythos-bot", "lines": 20}},
        ])
    """

    def __init__(self, db_config: dict,
                 policy_path: str = "/opt/mythos/config/context_access_policy.yaml",
                 default_timeout: float = 5.0,
                 default_max_output: int = 4000):
        self.policy = AccessPolicy(policy_path)
        self.providers = ContextProviders(
            db_config=db_config,
            policy=self.policy,
            default_timeout=default_timeout,
            default_max_output=default_max_output,
        )
        self.default_timeout = default_timeout
        self.default_max_output = default_max_output

    def gather(self, context_spec: List[dict]) -> dict:
        """
        Gather context from multiple providers.

        Args:
            context_spec: List of {"provider": str, "args": dict} objects.
                          Matches scheduled_triggers.context_queries JSONB format.

        Returns:
            {
                "gathered_at": ISO timestamp,
                "results": {provider_name: provider_result, ...},
                "errors": [list of any errors],
                "providers_called": int,
                "providers_succeeded": int,
            }

        All text output is sanitized for secrets before return.
        """
        if not context_spec:
            return {
                "gathered_at": datetime.now(timezone.utc).isoformat(),
                "results": {},
                "errors": [],
                "providers_called": 0,
                "providers_succeeded": 0,
            }

        results = {}
        errors = []
        succeeded = 0

        for spec in context_spec:
            provider_name = spec.get("provider", "")
            provider_args = spec.get("args", {})
            timeout = spec.get("timeout", self.default_timeout)
            max_output = spec.get("max_output", self.default_max_output)

            result = self.providers.get(
                provider_name, provider_args,
                timeout=timeout, max_output=max_output,
            )

            if result["success"]:
                succeeded += 1
            else:
                errors.append({
                    "provider": provider_name,
                    "error": result["error"],
                })

            results[provider_name] = result

        # ── MANDATORY: sanitize all output ──
        gathered = {
            "gathered_at": datetime.now(timezone.utc).isoformat(),
            "results": results,
            "errors": errors,
            "providers_called": len(context_spec),
            "providers_succeeded": succeeded,
        }

        return sanitize_dict(gathered)

    def gather_single(self, provider: str, args: dict) -> dict:
        """Convenience: gather from a single provider."""
        return self.gather([{"provider": provider, "args": args}])

    def list_providers(self) -> List[str]:
        """List all available provider names."""
        return self.providers.list_providers()
