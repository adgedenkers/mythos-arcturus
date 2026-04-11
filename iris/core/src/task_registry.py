"""
Iris Idle Task Engine — Task Registry

Manages background tasks Iris can run when she has free time.
Each task has a should_run() check and an execute() method.
The registry picks the highest-priority ready task and feeds
it into the consciousness loop.

Usage from loop.py:
    registry = TaskRegistry(config)
    await registry.initialize()
    
    # In _maybe_initiate():
    task = await registry.next_task(current_mode)
    if task:
        result = await task.execute()
        await registry.record_result(task, result)
"""

import asyncio
import logging
import os
import json
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, Dict, Any, List, Type

import psycopg2

log = logging.getLogger("iris.task_registry")


# ═══════════════════════════════════════════════════
# BASE CLASSES
# ═══════════════════════════════════════════════════

class TaskPriority(Enum):
    """Priority levels for idle tasks."""
    CRITICAL = 1    # System health — run ASAP
    HIGH = 2        # Data freshness — run within hours
    NORMAL = 3      # Maintenance — run daily
    LOW = 4         # Nice-to-have — run when nothing else needs doing


@dataclass
class TaskResult:
    """Result of a background task execution."""
    success: bool
    summary: str = ""
    items_processed: int = 0
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BackgroundTask(ABC):
    """
    Base class for all idle tasks Iris can run.
    
    Subclasses must implement:
        task_type: str          — unique identifier (e.g. "neo4j_hygiene")
        priority: TaskPriority  — how important is this task
        cooldown: timedelta     — minimum time between runs
        should_run()            — check if task needs to run now
        execute()               — do the work, return TaskResult
    
    Optional overrides:
        estimated_seconds: int  — rough time estimate for scheduling
        allowed_modes: list     — which loop modes allow this task
    """

    task_type: str = "base"
    priority: TaskPriority = TaskPriority.NORMAL
    cooldown: timedelta = timedelta(hours=6)
    estimated_seconds: int = 30
    allowed_modes: List[str] = field(default_factory=lambda: ["background", "reflection"])

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self._last_run: Optional[datetime] = None
        self._last_status: Optional[str] = None

    # Make allowed_modes a class-level default that instances can override
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, 'allowed_modes') or cls.allowed_modes is BackgroundTask.allowed_modes:
            cls.allowed_modes = ["background", "reflection"]

    def get_db(self):
        """Get a PostgreSQL connection."""
        return psycopg2.connect(
            host=self.db_config.get("host", "localhost"),
            port=self.db_config.get("port", 5432),
            database=self.db_config.get("database", "mythos"),
            user=self.db_config.get("user", "adge"),
            password=self.db_config.get("password", ""),
        )

    def set_last_run(self, when: datetime, status: str):
        """Called by registry after loading history."""
        self._last_run = when
        self._last_status = status

    def cooldown_elapsed(self) -> bool:
        """Check if enough time has passed since last run."""
        if self._last_run is None:
            return True
        now = datetime.now(timezone.utc)
        last = self._last_run
        if last.tzinfo is None:
            last = last.replace(tzinfo=timezone.utc)
        return (now - last) >= self.cooldown

    @abstractmethod
    def should_run(self) -> bool:
        """
        Check whether this task needs to run right now.
        
        Called every loop cycle. Should be FAST (no LLM calls,
        minimal DB queries). Return True if work is needed.
        """
        ...

    @abstractmethod
    def execute(self) -> TaskResult:
        """
        Do the actual work. Return a TaskResult.
        
        This runs synchronously in the worker context.
        Keep it focused — one task, one job.
        """
        ...


# ═══════════════════════════════════════════════════
# BUILT-IN TASKS
# ═══════════════════════════════════════════════════

class PatchAuditTask(BackgroundTask):
    """Verify STREAMS.json patch counters match reality."""

    task_type = "patch_audit"
    priority = TaskPriority.NORMAL
    cooldown = timedelta(hours=12)
    estimated_seconds = 5

    def should_run(self) -> bool:
        return self.cooldown_elapsed()

    def execute(self) -> TaskResult:
        try:
            streams_path = "/opt/mythos/docs/STREAMS.json"
            if not os.path.exists(streams_path):
                return TaskResult(success=False, error="STREAMS.json not found")

            with open(streams_path) as f:
                streams = json.load(f)

            issues = []
            checked = 0

            for prefix, stream in streams.get("streams", {}).items():
                next_patch = stream.get("next_patch", 0)
                checked += 1

                # Check if patches exist beyond the counter
                patch_dir = "/opt/mythos/patches"
                if os.path.isdir(patch_dir):
                    for entry in os.listdir(patch_dir):
                        if entry.startswith(f"{prefix}-"):
                            try:
                                num_str = entry.split("-")[1].split("_")[0]
                                num = int(num_str)
                                if num >= next_patch:
                                    issues.append(
                                        f"{prefix}: found {entry} but next_patch={next_patch}"
                                    )
                            except (ValueError, IndexError):
                                pass

            summary = f"Audited {checked} streams."
            if issues:
                summary += f" Found {len(issues)} issues: " + "; ".join(issues[:5])
            else:
                summary += " All counters consistent."

            return TaskResult(
                success=len(issues) == 0,
                summary=summary,
                items_processed=checked,
                metadata={"issues": issues},
            )

        except Exception as e:
            return TaskResult(success=False, error=str(e))


class Neo4jHygieneTask(BackgroundTask):
    """Find orphan nodes and broken relationships in Neo4j."""

    task_type = "neo4j_hygiene"
    priority = TaskPriority.NORMAL
    cooldown = timedelta(hours=24)
    estimated_seconds = 15

    def should_run(self) -> bool:
        return self.cooldown_elapsed()

    def execute(self) -> TaskResult:
        try:
            from neo4j import GraphDatabase

            uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
            user = os.getenv("NEO4J_USER", "neo4j")
            password = os.getenv("NEO4J_PASSWORD", "")

            driver = GraphDatabase.driver(uri, auth=(user, password))
            findings = []

            with driver.session() as session:
                # Orphan nodes (no relationships)
                result = session.run(
                    "MATCH (n) WHERE NOT (n)--() "
                    "RETURN labels(n) AS labels, count(*) AS cnt "
                    "ORDER BY cnt DESC LIMIT 20"
                )
                orphans = [(r["labels"], r["cnt"]) for r in result]
                total_orphans = sum(c for _, c in orphans)
                if total_orphans > 0:
                    findings.append(f"{total_orphans} orphan nodes across {len(orphans)} label types")

                # Nodes missing required properties
                result = session.run(
                    "MATCH (p:Person) WHERE p.name IS NULL "
                    "RETURN count(p) AS cnt"
                )
                nameless = result.single()["cnt"]
                if nameless > 0:
                    findings.append(f"{nameless} Person nodes missing name")

                # Total node/rel counts for baseline
                result = session.run(
                    "MATCH (n) RETURN count(n) AS nodes"
                )
                total_nodes = result.single()["nodes"]
                result = session.run(
                    "MATCH ()-[r]->() RETURN count(r) AS rels"
                )
                total_rels = result.single()["rels"]

            driver.close()

            summary = f"Graph: {total_nodes} nodes, {total_rels} relationships."
            if findings:
                summary += " Issues: " + "; ".join(findings)
            else:
                summary += " No issues found."

            return TaskResult(
                success=True,
                summary=summary,
                items_processed=total_nodes,
                metadata={
                    "total_nodes": total_nodes,
                    "total_rels": total_rels,
                    "orphan_count": total_orphans,
                    "orphan_labels": orphans[:10],
                    "nameless_persons": nameless,
                    "findings": findings,
                },
            )

        except Exception as e:
            return TaskResult(success=False, error=str(e))


class DocStalenessTask(BackgroundTask):
    """Check which docs are stale relative to recent code changes."""

    task_type = "doc_staleness"
    priority = TaskPriority.LOW
    cooldown = timedelta(hours=24)
    estimated_seconds = 10

    def should_run(self) -> bool:
        return self.cooldown_elapsed()

    def execute(self) -> TaskResult:
        import subprocess

        try:
            docs_dir = "/opt/mythos/docs"
            stale = []

            # Get last modified time for key docs
            key_docs = [
                "TODO.md", "ARCHITECTURE.md", "STREAMS.md",
                "KNOWLEDGE_MAP.md", "PATCH_HISTORY.md",
            ]

            for doc in key_docs:
                doc_path = os.path.join(docs_dir, doc)
                if not os.path.exists(doc_path):
                    stale.append(f"{doc}: MISSING")
                    continue

                doc_mtime = os.path.getmtime(doc_path)
                doc_age_hours = (time.time() - doc_mtime) / 3600

                # ARCHITECTURE.md older than 7 days is worth flagging
                if doc == "ARCHITECTURE.md" and doc_age_hours > 168:
                    stale.append(f"{doc}: {doc_age_hours:.0f}h old")
                # TODO.md older than 3 days
                elif doc == "TODO.md" and doc_age_hours > 72:
                    stale.append(f"{doc}: {doc_age_hours:.0f}h old")

            # Check recent git commits vs doc updates
            try:
                result = subprocess.run(
                    ["git", "-C", "/opt/mythos", "log", "--oneline", "-5",
                     "--format=%H %ai"],
                    capture_output=True, text=True, timeout=5,
                )
                recent_commits = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            except Exception:
                recent_commits = -1

            summary = f"Checked {len(key_docs)} key docs."
            if stale:
                summary += f" {len(stale)} stale: " + "; ".join(stale[:5])
            else:
                summary += " All current."

            return TaskResult(
                success=True,
                summary=summary,
                items_processed=len(key_docs),
                metadata={
                    "stale_docs": stale,
                    "recent_commits": recent_commits,
                },
            )

        except Exception as e:
            return TaskResult(success=False, error=str(e))


class RedisQueueHealthTask(BackgroundTask):
    """Check Redis stream health — pending messages, stale consumers."""

    task_type = "redis_queue_health"
    priority = TaskPriority.HIGH
    cooldown = timedelta(hours=6)
    estimated_seconds = 5

    def should_run(self) -> bool:
        return self.cooldown_elapsed()

    def execute(self) -> TaskResult:
        import redis as redis_lib

        try:
            r = redis_lib.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                decode_responses=True,
            )

            streams = [
                "mythos:assignments:grid_analysis",
                "mythos:assignments:embedding",
                "mythos:assignments:vision",
                "mythos:assignments:temporal",
                "mythos:assignments:entity",
                "mythos:assignments:summary_rebuild",
                "mythos:assignments:transcription",
            ]

            issues = []
            checked = 0

            for stream in streams:
                try:
                    length = r.xlen(stream)
                    checked += 1

                    # Check for stuck pending messages
                    groups = r.xinfo_groups(stream)
                    for group in groups:
                        pending = group.get("pending", 0)
                        if pending > 10:
                            issues.append(
                                f"{stream.split(':')[-1]}: {pending} pending in {group['name']}"
                            )
                except redis_lib.ResponseError:
                    # Stream doesn't exist yet — that's fine
                    pass

            # Get worker stats
            stats = r.hgetall("mythos:stats:workers") or {}

            summary = f"Checked {checked} streams."
            if issues:
                summary += f" {len(issues)} issues: " + "; ".join(issues[:5])
            else:
                summary += " All healthy."

            return TaskResult(
                success=len(issues) == 0,
                summary=summary,
                items_processed=checked,
                metadata={
                    "issues": issues,
                    "worker_stats": stats,
                },
            )

        except Exception as e:
            return TaskResult(success=False, error=str(e))


class TableRowCountTask(BackgroundTask):
    """Snapshot key table row counts for trend tracking."""

    task_type = "table_row_counts"
    priority = TaskPriority.LOW
    cooldown = timedelta(hours=12)
    estimated_seconds = 5

    def should_run(self) -> bool:
        return self.cooldown_elapsed()

    def execute(self) -> TaskResult:
        try:
            conn = self.get_db()
            cur = conn.cursor()

            key_tables = [
                "chat_messages", "transactions", "life_events",
                "calendar_events", "voice_memos", "people",
                "grid_activation_timeseries", "emotional_state_timeseries",
                "perception_log", "pipeline_runs",
            ]

            counts = {}
            for table in key_tables:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = cur.fetchone()[0]
                except Exception:
                    conn.rollback()
                    counts[table] = -1

            cur.close()
            conn.close()

            total = sum(v for v in counts.values() if v >= 0)
            summary = f"Counted {len(counts)} tables, {total} total rows."

            return TaskResult(
                success=True,
                summary=summary,
                items_processed=len(counts),
                metadata={"counts": counts},
            )

        except Exception as e:
            return TaskResult(success=False, error=str(e))


# ═══════════════════════════════════════════════════
# REGISTRY
# ═══════════════════════════════════════════════════

class PersonDeepResearchTask(BackgroundTask):
    """Process queued person deep research tasks from Redis."""
    task_type = "person_deep_research"
    priority = TaskPriority.LOW
    cooldown = timedelta(minutes=5)
    estimated_seconds = 60
    allowed_modes = ["background", "reflection"]

    def should_run(self) -> bool:
        """Check if there are pending person research tasks in Redis."""
        if not self.cooldown_elapsed():
            return False
        try:
            import redis as redis_lib
            r = redis_lib.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
            )
            length = r.xlen("mythos:assignments:person_research")
            r.close()
            return length > 0
        except Exception:
            return False

    def execute(self) -> TaskResult:
        """
        Read ONE task from the Redis stream and run deep research.
        One at a time — keeps the machine responsive.
        """
        import redis as redis_lib
        try:
            r = redis_lib.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
                decode_responses=True,
            )

            # Read the oldest entry
            entries = r.xrange("mythos:assignments:person_research", count=1)
            if not entries:
                r.close()
                return TaskResult(
                    success=True,
                    summary="No pending person research tasks",
                    items_processed=0,
                )

            entry_id, data = entries[0]
            task_data = json.loads(data.get("data", "{}"))
            person_id = int(task_data.get("person_id", 0))
            person_name = task_data.get("person_name", "unknown")

            if not person_id:
                # Bad entry — remove it and move on
                r.xdel("mythos:assignments:person_research", entry_id)
                r.close()
                return TaskResult(
                    success=False,
                    summary=f"Skipped bad entry (no person_id): {person_name}",
                    error="Missing person_id in queue entry",
                )

            log.info(f"PersonDeepResearch: processing {person_name} (id={person_id})")

            # Run the deep research
            import sys
            if "/opt/mythos" not in sys.path:
                sys.path.insert(0, "/opt/mythos")
            if "/opt/mythos/iris/core" not in sys.path:
                sys.path.insert(0, "/opt/mythos/iris/core")
            from src.person_researcher import run_deep_research

            run_deep_research(self.db_config, person_id)

            # Remove the processed entry from the stream
            r.xdel("mythos:assignments:person_research", entry_id)
            r.close()

            # Check how many remain
            r2 = redis_lib.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
            )
            remaining = r2.xlen("mythos:assignments:person_research")
            r2.close()

            return TaskResult(
                success=True,
                summary=f"Deep research complete for {person_name} (id={person_id}). {remaining} remaining in queue.",
                items_processed=1,
                metadata={
                    "person_id": person_id,
                    "person_name": person_name,
                    "remaining": remaining,
                },
            )

        except Exception as e:
            log.error(f"PersonDeepResearch failed: {e}", exc_info=True)
            return TaskResult(success=False, error=str(e))


# All built-in tasks
BUILTIN_TASKS: List[Type[BackgroundTask]] = [
    PatchAuditTask,
    Neo4jHygieneTask,
    DocStalenessTask,
    RedisQueueHealthTask,
    TableRowCountTask,
    PersonDeepResearchTask,
]


class TaskRegistry:
    """
    Manages all background tasks and picks the next one to run.
    
    Usage:
        registry = TaskRegistry(db_config)
        registry.initialize()
        
        task = registry.next_task("reflection")
        if task:
            result = task.execute()
            registry.record_result(task, result)
    """

    def __init__(self, db_config: Dict[str, str]):
        self.db_config = db_config
        self.tasks: List[BackgroundTask] = []
        self._initialized = False

    def initialize(self):
        """Register built-in tasks and load run history."""
        self.tasks = []

        for task_cls in BUILTIN_TASKS:
            try:
                task = task_cls(self.db_config)
                self.tasks.append(task)
            except Exception as e:
                log.error(f"Failed to instantiate {task_cls.task_type}: {e}")

        # Load last run times from DB
        self._load_history()
        self._initialized = True

        log.info(f"TaskRegistry initialized with {len(self.tasks)} tasks")

    def register(self, task: BackgroundTask):
        """Register an additional task at runtime."""
        self.tasks.append(task)
        log.info(f"Registered task: {task.task_type}")

    def _load_history(self):
        """Load last run times from iris_task_log."""
        try:
            conn = psycopg2.connect(
                host=self.db_config.get("host", "localhost"),
                port=self.db_config.get("port", 5432),
                database=self.db_config.get("database", "mythos"),
                user=self.db_config.get("user", "adge"),
                password=self.db_config.get("password", ""),
            )
            cur = conn.cursor()

            cur.execute("""
                SELECT DISTINCT ON (task_type)
                    task_type, started_at, status
                FROM iris_task_log
                ORDER BY task_type, started_at DESC
            """)

            history = {row[0]: (row[1], row[2]) for row in cur.fetchall()}
            cur.close()
            conn.close()

            for task in self.tasks:
                if task.task_type in history:
                    when, status = history[task.task_type]
                    task.set_last_run(when, status)
                    log.debug(f"  {task.task_type}: last ran {when} ({status})")

        except Exception as e:
            log.warning(f"Could not load task history: {e}")

    def next_task(self, current_mode: str) -> Optional[BackgroundTask]:
        """
        Pick the highest-priority task that should run now.
        
        Args:
            current_mode: Current loop mode ("presence", "available",
                          "background", "reflection")
        
        Returns:
            The next BackgroundTask to execute, or None.
        """
        if not self._initialized:
            return None

        candidates = []

        for task in self.tasks:
            # Mode check
            if current_mode not in task.allowed_modes:
                continue

            # Should-run check
            try:
                if task.should_run():
                    candidates.append(task)
            except Exception as e:
                log.warning(f"should_run() failed for {task.task_type}: {e}")

        if not candidates:
            return None

        # Sort by priority (lower enum value = higher priority)
        candidates.sort(key=lambda t: t.priority.value)

        chosen = candidates[0]
        log.info(
            f"Next idle task: {chosen.task_type} "
            f"(priority={chosen.priority.name}, "
            f"est={chosen.estimated_seconds}s)"
        )
        return chosen

    def record_result(self, task: BackgroundTask, result: TaskResult):
        """Write task result to iris_task_log and update last-run."""
        now = datetime.now(timezone.utc)
        started = now - timedelta(milliseconds=result.metadata.get("_duration_ms", 0))

        try:
            conn = psycopg2.connect(
                host=self.db_config.get("host", "localhost"),
                port=self.db_config.get("port", 5432),
                database=self.db_config.get("database", "mythos"),
                user=self.db_config.get("user", "adge"),
                password=self.db_config.get("password", ""),
            )
            cur = conn.cursor()

            duration_ms = result.metadata.pop("_duration_ms", None)

            cur.execute("""
                INSERT INTO iris_task_log
                    (task_type, task_class, mode, started_at, completed_at,
                     status, result_summary, items_processed, duration_ms,
                     error, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                task.task_type,
                task.__class__.__name__,
                "unknown",  # filled by caller if available
                started,
                now,
                "completed" if result.success else "failed",
                result.summary[:2000] if result.summary else None,
                result.items_processed,
                duration_ms,
                result.error[:2000] if result.error else None,
                json.dumps(result.metadata, default=str),
            ))

            conn.commit()
            cur.close()
            conn.close()

            # Update in-memory state
            task.set_last_run(now, "completed" if result.success else "failed")

            status = "completed" if result.success else "failed"
            log.info(
                f"Task {task.task_type} {status}: {result.summary[:100]}"
            )

        except Exception as e:
            log.error(f"Failed to record task result: {e}")


def run_idle_task(db_config: Dict[str, str], mode: str = "background") -> Optional[Dict]:
    """
    Convenience function: pick and run one idle task.
    
    Can be called from a cron job, CLI tool, or the consciousness loop.
    Returns the result dict or None if nothing to do.
    """
    registry = TaskRegistry(db_config)
    registry.initialize()

    task = registry.next_task(mode)
    if not task:
        log.info("No idle tasks ready to run")
        return None

    log.info(f"Running idle task: {task.task_type}")
    start = time.time()

    try:
        result = task.execute()
    except Exception as e:
        result = TaskResult(success=False, error=str(e))

    elapsed_ms = int((time.time() - start) * 1000)
    result.metadata["_duration_ms"] = elapsed_ms

    registry.record_result(task, result)

    return {
        "task_type": task.task_type,
        "success": result.success,
        "summary": result.summary,
        "items_processed": result.items_processed,
        "duration_ms": elapsed_ms,
        "error": result.error,
    }
