"""
Iris Trigger Engine — The Autonomic Heartbeat

Loads triggers from Postgres, computes next fire times,
executes actions on schedule, logs everything.

Runs as a standalone async loop. Can also be imported
as a subsystem of the consciousness loop.

Architecture:
    TriggerEngine
        ├── loads triggers from scheduled_triggers table
        ├── computes next_fire for cron/interval/once types
        ├── main loop: sleep until next → fire → log → recompute
        ├── listens on Redis pub/sub for event triggers
        └── dispatches actions: reflex, run_task, telegram_notify, etc.
"""

import asyncio
import json
import logging
import os
import subprocess
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any, List, Callable

import psycopg2
import psycopg2.extras

from .context_engine import ContextEngine
from .decision_gate import DecisionGate

log = logging.getLogger("iris.trigger_engine")


# ═══════════════════════════════════════════════════
# CRON PARSER — Lightweight, no external deps
# ═══════════════════════════════════════════════════

class CronParser:
    """
    Minimal cron expression parser.
    Supports: minute hour day_of_month month day_of_week
    Supports: *, */N, N, N-M, N,M,O
    Does NOT support: @yearly, @monthly, etc.
    """

    @staticmethod
    def parse_field(field: str, min_val: int, max_val: int) -> set:
        """Parse a single cron field into a set of valid values."""
        values = set()
        for part in field.split(","):
            part = part.strip()
            if part == "*":
                values.update(range(min_val, max_val + 1))
            elif part.startswith("*/"):
                step = int(part[2:])
                values.update(range(min_val, max_val + 1, step))
            elif "-" in part:
                start, end = part.split("-", 1)
                values.update(range(int(start), int(end) + 1))
            else:
                values.add(int(part))
        return values

    @staticmethod
    def next_fire(cron_expr: str, after: Optional[datetime] = None) -> datetime:
        """
        Compute the next fire time for a cron expression.
        Returns a UTC datetime.
        """
        if after is None:
            after = datetime.now(timezone.utc)
        elif after.tzinfo is None:
            after = after.replace(tzinfo=timezone.utc)

        fields = cron_expr.strip().split()
        if len(fields) != 5:
            raise ValueError(f"Invalid cron expression (need 5 fields): {cron_expr}")

        minutes = CronParser.parse_field(fields[0], 0, 59)
        hours = CronParser.parse_field(fields[1], 0, 23)
        days_of_month = CronParser.parse_field(fields[2], 1, 31)
        months = CronParser.parse_field(fields[3], 1, 12)
        days_of_week = CronParser.parse_field(fields[4], 0, 6)  # 0=Sunday

        # Start searching from the next minute
        candidate = after.replace(second=0, microsecond=0) + timedelta(minutes=1)

        # Search up to 366 days ahead
        max_search = after + timedelta(days=366)

        while candidate < max_search:
            if (candidate.month in months and
                candidate.day in days_of_month and
                candidate.weekday() in _cron_to_python_weekday(days_of_week) and
                candidate.hour in hours and
                candidate.minute in minutes):
                return candidate

            # Advance: skip quickly through non-matching months/days
            if candidate.month not in months:
                # Jump to first day of next month
                if candidate.month == 12:
                    candidate = candidate.replace(year=candidate.year + 1, month=1, day=1, hour=0, minute=0)
                else:
                    candidate = candidate.replace(month=candidate.month + 1, day=1, hour=0, minute=0)
                continue

            if (candidate.day not in days_of_month or
                candidate.weekday() not in _cron_to_python_weekday(days_of_week)):
                candidate = candidate.replace(hour=0, minute=0) + timedelta(days=1)
                continue

            if candidate.hour not in hours:
                candidate = candidate.replace(minute=0) + timedelta(hours=1)
                continue

            candidate += timedelta(minutes=1)

        raise ValueError(f"No next fire time found within 366 days for: {cron_expr}")


def _cron_to_python_weekday(cron_days: set) -> set:
    """Convert cron day-of-week (0=Sunday) to Python weekday (0=Monday)."""
    mapping = {0: 6, 1: 0, 2: 1, 3: 2, 4: 3, 5: 4, 6: 5}
    return {mapping.get(d, d) for d in cron_days}


# ═══════════════════════════════════════════════════
# ACTION HANDLERS — What triggers actually do
# ═══════════════════════════════════════════════════

class ActionHandlers:
    """
    Registry of action handlers.

    Each handler takes (trigger_row, payload) and returns a result dict.
    """

    def __init__(self, db_config: dict, task_registry=None):
        self.db_config = db_config
        self.task_registry = task_registry
        self._handlers: Dict[str, Callable] = {
            "reflex": self._handle_reflex,
            "run_task": self._handle_run_task,
            "telegram_notify": self._handle_telegram_notify,
            "run_command": self._handle_run_command,
            "redis_push": self._handle_redis_push,
        }

    def can_handle(self, action_type: str) -> bool:
        return action_type in self._handlers

    async def execute(self, action_type: str, trigger: dict, payload: dict) -> dict:
        handler = self._handlers.get(action_type)
        if not handler:
            return {"success": False, "error": f"No handler for action_type: {action_type}"}
        try:
            return await handler(trigger, payload)
        except Exception as e:
            log.exception(f"Action handler {action_type} failed", exc_info=e)
            return {"success": False, "error": str(e)}

    async def _handle_reflex(self, trigger: dict, payload: dict) -> dict:
        """Execute a reflex action — fast, no thinking."""
        reflex_type = payload.get("reflex", "")

        if reflex_type == "check_all_services":
            return await self._reflex_check_services(payload)
        elif reflex_type == "log_only":
            return {"success": True, "action": "logged"}
        else:
            return {"success": False, "error": f"Unknown reflex: {reflex_type}"}

    async def _reflex_check_services(self, payload: dict) -> dict:
        """Check all listed services are running."""
        services = payload.get("services", [])
        down = []
        checked = 0

        for svc in services:
            svc_name = f"{svc}.service" if not svc.endswith(".service") else svc
            try:
                result = subprocess.run(
                    ["systemctl", "is-active", svc_name],
                    capture_output=True, text=True, timeout=5,
                )
                checked += 1
                if result.stdout.strip() != "active":
                    down.append(svc_name)
            except Exception as e:
                down.append(f"{svc_name} (check failed: {e})")

        result = {
            "success": len(down) == 0,
            "checked": checked,
            "down": down,
        }

        if down:
            log.warning(f"Services down: {down}")
            # Emit events for escalation
            try:
                import redis as redis_lib
                r = redis_lib.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", 6379)),
                )
                for svc in down:
                    r.publish("mythos:events", json.dumps({
                        "event_type": "crash",
                        "entity": svc.replace(".service", ""),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }))
                r.close()
            except Exception as e:
                log.warning(f"Failed to emit service-down events: {e}")

        return result

    async def _handle_run_task(self, trigger: dict, payload: dict) -> dict:
        """Run a task from the idle task registry."""
        task_name = payload.get("task", "")

        if task_name == "next_idle_task" and self.task_registry:
            from .task_registry import TaskResult
            task = self.task_registry.next_task("background")
            if task:
                start = time.time()
                try:
                    result = task.execute()
                except Exception as e:
                    result = TaskResult(success=False, error=str(e))
                elapsed = int((time.time() - start) * 1000)
                result.metadata["_duration_ms"] = elapsed
                self.task_registry.record_result(task, result)
                return {
                    "success": result.success,
                    "task_type": task.task_type,
                    "summary": result.summary,
                    "duration_ms": elapsed,
                }
            else:
                return {"success": True, "action": "no_tasks_ready"}

        # Generic task placeholder — future phases will route these
        return {
            "success": True,
            "action": "task_placeholder",
            "task": task_name,
            "note": "Task routing not yet implemented — logged for future phases",
        }

    async def _handle_telegram_notify(self, trigger: dict, payload: dict) -> dict:
        """Send a Telegram notification."""
        message = payload.get("message", payload.get("template", "Trigger fired"))

        try:
            import redis as redis_lib
            r = redis_lib.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
            )
            # Push to a notification queue that the bot can consume
            r.rpush("mythos:notifications:telegram", json.dumps({
                "message": message,
                "trigger": trigger.get("name", "unknown"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }))
            r.close()
            return {"success": True, "action": "telegram_queued"}
        except Exception as e:
            return {"success": False, "error": f"Telegram notify failed: {e}"}

    async def _handle_run_command(self, trigger: dict, payload: dict) -> dict:
        """Run a shell command."""
        command = payload.get("command", "")
        if not command:
            return {"success": False, "error": "No command specified"}

        # Safety: only allow commands under /opt/mythos
        if not command.startswith("/opt/mythos/"):
            return {"success": False, "error": f"Command must be under /opt/mythos/: {command}"}

        try:
            result = subprocess.run(
                command.split(),
                capture_output=True, text=True, timeout=60,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout[:2000],
                "stderr": result.stderr[:500] if result.returncode != 0 else "",
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out (60s)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _handle_redis_push(self, trigger: dict, payload: dict) -> dict:
        """Push a message to a Redis stream or channel."""
        try:
            import redis as redis_lib
            r = redis_lib.Redis(
                host=os.getenv("REDIS_HOST", "localhost"),
                port=int(os.getenv("REDIS_PORT", 6379)),
            )
            stream = payload.get("stream")
            channel = payload.get("channel")
            data = payload.get("data", {})

            if stream:
                r.xadd(stream, {"data": json.dumps(data)})
                r.close()
                return {"success": True, "action": f"pushed to stream {stream}"}
            elif channel:
                r.publish(channel, json.dumps(data))
                r.close()
                return {"success": True, "action": f"published to {channel}"}
            else:
                r.close()
                return {"success": False, "error": "No stream or channel specified"}
        except Exception as e:
            return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════
# TRIGGER ENGINE — The main scheduler
# ═══════════════════════════════════════════════════

class TriggerEngine:
    """
    The autonomic trigger scheduler.

    Loads triggers from Postgres, computes next fire times,
    runs a loop that fires triggers on schedule, and logs everything.

    Can run standalone (via run()) or be polled from the
    consciousness loop (via poll_and_fire()).
    """

    def __init__(self, db_config: dict, task_registry=None):
        self.db_config = db_config
        self.triggers: List[dict] = []
        self.handlers = ActionHandlers(db_config, task_registry)
        self.context_engine = ContextEngine(db_config)
        self.decision_gate = DecisionGate(db_config)
        self._running = False
        self._reload_interval = 300  # reload triggers from DB every 5 min
        self._last_reload: Optional[datetime] = None

    def _get_db(self):
        return psycopg2.connect(
            host=self.db_config.get("host", "localhost"),
            port=self.db_config.get("port", 5432),
            database=self.db_config.get("database", "mythos"),
            user=self.db_config.get("user", "adge"),
            password=self.db_config.get("password", ""),
            cursor_factory=psycopg2.extras.RealDictCursor,
        )

    def load_triggers(self):
        """Load all enabled triggers from Postgres and compute next fire times."""
        conn = self._get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, name, trigger_type, schedule, action_type,
                   action_payload, context_queries, decision_prompt,
                   enabled, priority, last_fired, next_fire, fire_count,
                   metadata
            FROM scheduled_triggers
            WHERE enabled = true
            ORDER BY
                CASE priority
                    WHEN 'critical' THEN 0
                    WHEN 'high' THEN 1
                    WHEN 'normal' THEN 2
                    WHEN 'low' THEN 3
                END
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        self.triggers = [dict(row) for row in rows]

        # Compute next_fire for any that need it
        now = datetime.now(timezone.utc)
        updates = []
        for t in self.triggers:
            if t["trigger_type"] == "cron" and (t["next_fire"] is None or t["next_fire"] <= now):
                try:
                    nxt = CronParser.next_fire(t["schedule"], after=now)
                    t["next_fire"] = nxt
                    updates.append((nxt, t["id"]))
                except Exception as e:
                    log.error(f"Failed to compute next_fire for {t['name']}: {e}")

            elif t["trigger_type"] == "interval":
                interval_secs = int(t["schedule"])
                last = t["last_fired"]
                if last:
                    if last.tzinfo is None:
                        last = last.replace(tzinfo=timezone.utc)
                    nxt = last + timedelta(seconds=interval_secs)
                else:
                    nxt = now  # fire immediately on first load
                t["next_fire"] = nxt
                updates.append((nxt, t["id"]))

            elif t["trigger_type"] == "once":
                try:
                    nxt = datetime.fromisoformat(t["schedule"])
                    if nxt.tzinfo is None:
                        nxt = nxt.replace(tzinfo=timezone.utc)
                    t["next_fire"] = nxt
                    updates.append((nxt, t["id"]))
                except Exception as e:
                    log.error(f"Invalid once schedule for {t['name']}: {e}")

        # Write computed next_fire values back
        if updates:
            conn = self._get_db()
            cur = conn.cursor()
            for nxt, tid in updates:
                cur.execute(
                    "UPDATE scheduled_triggers SET next_fire = %s WHERE id = %s",
                    (nxt, tid),
                )
            conn.commit()
            cur.close()
            conn.close()

        self._last_reload = now
        log.info(f"Loaded {len(self.triggers)} triggers, updated {len(updates)} next_fire times")

    def _should_reload(self) -> bool:
        if self._last_reload is None:
            return True
        elapsed = (datetime.now(timezone.utc) - self._last_reload).total_seconds()
        return elapsed >= self._reload_interval

    def get_due_triggers(self) -> List[dict]:
        """Return all triggers whose next_fire is now or past."""
        now = datetime.now(timezone.utc)
        due = []
        for t in self.triggers:
            if t["trigger_type"] == "event":
                continue  # event triggers are handled via Redis pub/sub
            nxt = t.get("next_fire")
            if nxt is None:
                continue
            if nxt.tzinfo is None:
                nxt = nxt.replace(tzinfo=timezone.utc)
            if nxt <= now:
                due.append(t)
        return due

    async def fire_trigger(self, trigger: dict) -> dict:
        """Fire a single trigger: execute action, log result, update state."""
        name = trigger["name"]
        action_type = trigger["action_type"]
        payload = trigger.get("action_payload", {})

        log.info(f"Firing trigger: {name} (action={action_type})")

        start_time = time.time()

        # ── Decision gate routing ─────────────────────────────────
        # If trigger has both context_queries AND decision_prompt,
        # route through the decision gate before action dispatch.
        context_queries = trigger.get("context_queries") or []
        decision_prompt = trigger.get("decision_prompt")
        context_gathered = None
        decision_result = None

        if context_queries and decision_prompt:
            route = "decision_gate"
            log.info(f"Trigger '{name}' entering decision gate")

            # Gather context
            context_gathered = self.context_engine.gather(context_queries)

            # Evaluate via LLM
            decision_result = self.decision_gate.evaluate(trigger, context_gathered)

            if decision_result.auto_executed:
                # Gate approved execution — dispatch the decided action
                decided_action = decision_result.action
                decided_params = decision_result.params

                # Map the LLM's decided action to a handler
                if decided_action in ("restart", "restart_service"):
                    svc = decided_params.get("service", "")
                    result = await self.handlers.execute(
                        "run_command", trigger,
                        {"command": f"/opt/mythos/bin/mythos-svc-restart {svc}" if svc else ""},
                    )
                elif decided_action in ("alert", "warn", "notify_human"):
                    msg = (
                        f"🧠 Decision Gate [{name}]\n"
                        f"Action: {decided_action}\n"
                        f"Confidence: {decision_result.confidence:.2f}\n"
                        f"Reasoning: {decision_result.reasoning}"
                    )
                    result = await self.handlers.execute(
                        "telegram_notify", trigger, {"message": msg},
                    )
                elif decided_action == "log_only":
                    result = {"success": True, "action": "log_only", "reasoning": decision_result.reasoning}
                else:
                    # Unknown action from LLM — notify human
                    msg = (
                        f"🧠 Decision Gate [{name}] — unknown action '{decided_action}'\n"
                        f"Confidence: {decision_result.confidence:.2f}\n"
                        f"Reasoning: {decision_result.reasoning}"
                    )
                    result = await self.handlers.execute(
                        "telegram_notify", trigger, {"message": msg},
                    )

                # If gate also said to notify, send notification
                if decision_result.notify and decided_action != "notify_human":
                    notify_msg = (
                        f"🧠 Decision Gate auto-executed [{name}]\n"
                        f"Action: {decided_action} (confidence: {decision_result.confidence:.2f})\n"
                        f"Reasoning: {decision_result.reasoning}"
                    )
                    await self.handlers.execute(
                        "telegram_notify", trigger, {"message": notify_msg},
                    )
            else:
                # Gate deferred — notify human, do NOT execute
                msg = (
                    f"🧠 Decision Gate deferred [{name}]\n"
                    f"Suggested: {decision_result.action} (confidence: {decision_result.confidence:.2f})\n"
                    f"Reasoning: {decision_result.reasoning}\n"
                    f"Action NOT taken — awaiting human decision."
                )
                result = await self.handlers.execute(
                    "telegram_notify", trigger, {"message": msg},
                )
                result["deferred"] = True

            elapsed_ms = int((time.time() - start_time) * 1000)

            # Log with full decision data
            self._log_firing(
                trigger_name=name,
                route=route,
                actions_taken=result,
                duration_ms=elapsed_ms,
                success=result.get("success", False),
                error=result.get("error"),
                context=context_gathered,
                decision_prompt=decision_prompt,
                decision_response=decision_result.raw_response,
                decision_parsed=decision_result.to_dict(),
                llm_duration_ms=decision_result.llm_duration_ms,
            )
        else:
            # ── Standard dispatch (no decision gate) ──────────────
            result = await self.handlers.execute(action_type, trigger, payload)
            elapsed_ms = int((time.time() - start_time) * 1000)

            # Determine route
            route = "reflex" if action_type == "reflex" else (
                "task" if action_type == "run_task" else "direct"
            )

            # Log to trigger_log
            self._log_firing(
                trigger_name=name,
                route=route,
                actions_taken=result,
                duration_ms=elapsed_ms,
                success=result.get("success", False),
                error=result.get("error"),
            )

        # Update trigger state
        now = datetime.now(timezone.utc)
        self._update_trigger_state(trigger, now, result)

        log.info(f"Trigger {name} completed: success={result.get('success')} ({elapsed_ms}ms)")
        return result

    def _log_firing(self, trigger_name: str, route: str,
                    actions_taken: dict, duration_ms: int,
                    success: bool, error: Optional[str] = None,
                    context: Optional[dict] = None,
                    decision_prompt: Optional[str] = None,
                    decision_response: Optional[str] = None,
                    decision_parsed: Optional[dict] = None,
                    llm_duration_ms: Optional[int] = None):
        """Write to trigger_log table."""
        try:
            conn = self._get_db()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO trigger_log
                    (trigger_name, fired_at, context_gathered, route,
                     decision_prompt, decision_response, decision_parsed,
                     actions_taken, duration_ms, llm_duration_ms,
                     success, error)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                trigger_name,
                datetime.now(timezone.utc),
                json.dumps(context) if context else None,
                route,
                decision_prompt,
                decision_response,
                json.dumps(decision_parsed) if decision_parsed else None,
                json.dumps(actions_taken, default=str),
                duration_ms,
                llm_duration_ms,
                success,
                error,
            ))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            log.error(f"Failed to log trigger firing: {e}")

    def _update_trigger_state(self, trigger: dict, fired_at: datetime, result: dict):
        """Update last_fired, next_fire, fire_count in DB and in-memory."""
        trigger["last_fired"] = fired_at
        trigger["fire_count"] = trigger.get("fire_count", 0) + 1
        trigger["last_result"] = result

        # Compute next fire
        new_next = None
        if trigger["trigger_type"] == "cron":
            try:
                new_next = CronParser.next_fire(trigger["schedule"], after=fired_at)
            except Exception as e:
                log.error(f"Failed to compute next cron fire for {trigger['name']}: {e}")

        elif trigger["trigger_type"] == "interval":
            interval_secs = int(trigger["schedule"])
            new_next = fired_at + timedelta(seconds=interval_secs)

        elif trigger["trigger_type"] == "once":
            new_next = None  # one-shot, don't reschedule

        trigger["next_fire"] = new_next

        try:
            conn = self._get_db()
            cur = conn.cursor()
            cur.execute("""
                UPDATE scheduled_triggers
                SET last_fired = %s,
                    next_fire = %s,
                    fire_count = fire_count + 1,
                    last_result = %s
                WHERE id = %s
            """, (
                fired_at,
                new_next,
                json.dumps(result, default=str),
                trigger["id"],
            ))
            conn.commit()
            cur.close()
            conn.close()
        except Exception as e:
            log.error(f"Failed to update trigger state: {e}")

    # ── Standalone run mode ───────────────────────────────────────────────

    async def run(self, shutdown_event: asyncio.Event):
        """
        Main loop — run as a standalone service.

        Loads triggers, fires due ones, sleeps until next,
        periodically reloads from DB.
        """
        self._running = True
        log.info("Trigger engine starting")

        self.load_triggers()

        while not shutdown_event.is_set():
            try:
                # Reload triggers periodically
                if self._should_reload():
                    self.load_triggers()

                # Find and fire due triggers
                due = self.get_due_triggers()
                for trigger in due:
                    try:
                        await self.fire_trigger(trigger)
                    except Exception as e:
                        log.exception(f"Error firing trigger {trigger['name']}", exc_info=e)

                # Calculate sleep time until next trigger
                sleep_secs = self._seconds_until_next()
                sleep_secs = min(sleep_secs, 60)  # wake up at least every 60s
                sleep_secs = max(sleep_secs, 1)   # never spin faster than 1s

                try:
                    await asyncio.wait_for(shutdown_event.wait(), timeout=sleep_secs)
                    break  # shutdown was signaled
                except asyncio.TimeoutError:
                    pass  # normal timeout, continue loop

            except Exception as e:
                log.exception("Trigger engine cycle error", exc_info=e)
                await asyncio.sleep(5)

        self._running = False
        log.info("Trigger engine stopped")

    def _seconds_until_next(self) -> float:
        """How long until the next trigger fires?"""
        now = datetime.now(timezone.utc)
        soonest = None

        for t in self.triggers:
            nxt = t.get("next_fire")
            if nxt is None:
                continue
            if nxt.tzinfo is None:
                nxt = nxt.replace(tzinfo=timezone.utc)
            delta = (nxt - now).total_seconds()
            if delta <= 0:
                return 0  # something is due now
            if soonest is None or delta < soonest:
                soonest = delta

        return soonest if soonest is not None else 60

    # ── Poll mode (for consciousness loop integration) ────────────────────

    async def poll_and_fire(self) -> List[dict]:
        """
        Non-blocking poll: fire any due triggers and return results.

        Call this from the consciousness loop's _perceive() or
        _maybe_initiate() method.
        """
        if self._should_reload():
            self.load_triggers()

        due = self.get_due_triggers()
        results = []
        for trigger in due:
            try:
                result = await self.fire_trigger(trigger)
                results.append({"trigger": trigger["name"], "result": result})
            except Exception as e:
                log.exception(f"Error firing trigger {trigger['name']}")
                results.append({"trigger": trigger["name"], "error": str(e)})

        return results

    # ── Health check ──────────────────────────────────────────────────────

    def get_state(self) -> dict:
        """State for health checks."""
        now = datetime.now(timezone.utc)
        return {
            "running": self._running,
            "trigger_count": len(self.triggers),
            "last_reload": self._last_reload.isoformat() if self._last_reload else None,
            "next_fires": [
                {"name": t["name"], "next": t["next_fire"].isoformat() if t.get("next_fire") else None}
                for t in sorted(self.triggers, key=lambda x: x.get("next_fire") or now)[:5]
            ],
        }
