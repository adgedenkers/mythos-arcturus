import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=9,
    description='decision_gate',
    patch_type='MINOR',
)
patch.begin()

# ── Deploy new files ──────────────────────────────────────────────────

patch.deploy_file(
    'opt/mythos/iris/core/src/decision_gate.py',
    '/opt/mythos/iris/core/src/decision_gate.py',
)

patch.deploy_file(
    'opt/mythos/bin/iris-decide',
    '/opt/mythos/bin/iris-decide',
)

# Make CLI executable and symlink
import os
import stat
cli_path = '/opt/mythos/bin/iris-decide'
os.chmod(cli_path, os.stat(cli_path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

# ── Run SQL migration ─────────────────────────────────────────────────

patch.run_sql('opt/mythos/migrations/neu_0009_decision_gate_triggers.sql')

# ── Modify trigger_engine.py — 3 targeted str.replace edits ──────────

te_path = '/opt/mythos/iris/core/src/trigger_engine.py'

with open(te_path, 'r') as f:
    content = f.read()

# ── Edit 1: Add imports after the existing psycopg2 imports ──────────

old_import = """import psycopg2
import psycopg2.extras

log = logging.getLogger("iris.trigger_engine")"""

new_import = """import psycopg2
import psycopg2.extras

from .context_engine import ContextEngine
from .decision_gate import DecisionGate

log = logging.getLogger("iris.trigger_engine")"""

assert old_import in content, f"Edit 1 FAILED: import block not found in {te_path}"
content = content.replace(old_import, new_import, 1)

# ── Edit 2: Add ContextEngine + DecisionGate init in TriggerEngine.__init__ ──

old_init = """    def __init__(self, db_config: dict, task_registry=None):
        self.db_config = db_config
        self.triggers: List[dict] = []
        self.handlers = ActionHandlers(db_config, task_registry)
        self._running = False
        self._reload_interval = 300  # reload triggers from DB every 5 min
        self._last_reload: Optional[datetime] = None"""

new_init = """    def __init__(self, db_config: dict, task_registry=None):
        self.db_config = db_config
        self.triggers: List[dict] = []
        self.handlers = ActionHandlers(db_config, task_registry)
        self.context_engine = ContextEngine(db_config)
        self.decision_gate = DecisionGate(db_config)
        self._running = False
        self._reload_interval = 300  # reload triggers from DB every 5 min
        self._last_reload: Optional[datetime] = None"""

assert old_init in content, f"Edit 2 FAILED: __init__ block not found in {te_path}"
content = content.replace(old_init, new_init, 1)

# ── Edit 3: Add decision gate routing in fire_trigger() ──────────────
# Insert the gate logic between the log.info and the handlers.execute call.
# The existing fire_trigger dispatches directly to handlers. We intercept
# triggers that have both context_queries (non-empty) and decision_prompt.

old_fire = """    async def fire_trigger(self, trigger: dict) -> dict:
        \"\"\"Fire a single trigger: execute action, log result, update state.\"\"\"
        name = trigger["name"]
        action_type = trigger["action_type"]
        payload = trigger.get("action_payload", {})

        log.info(f"Firing trigger: {name} (action={action_type})")

        start_time = time.time()
        result = await self.handlers.execute(action_type, trigger, payload)
        elapsed_ms = int((time.time() - start_time) * 1000)

        # Determine route
        route = "reflex" if action_type == "reflex" else (
            "decision_gate" if action_type == "decision_gate" else
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
        )"""

new_fire = """    async def fire_trigger(self, trigger: dict) -> dict:
        \"\"\"Fire a single trigger: execute action, log result, update state.\"\"\"
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
                        f"🧠 Decision Gate [{name}]\\n"
                        f"Action: {decided_action}\\n"
                        f"Confidence: {decision_result.confidence:.2f}\\n"
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
                        f"🧠 Decision Gate [{name}] — unknown action '{decided_action}'\\n"
                        f"Confidence: {decision_result.confidence:.2f}\\n"
                        f"Reasoning: {decision_result.reasoning}"
                    )
                    result = await self.handlers.execute(
                        "telegram_notify", trigger, {"message": msg},
                    )

                # If gate also said to notify, send notification
                if decision_result.notify and decided_action != "notify_human":
                    notify_msg = (
                        f"🧠 Decision Gate auto-executed [{name}]\\n"
                        f"Action: {decided_action} (confidence: {decision_result.confidence:.2f})\\n"
                        f"Reasoning: {decision_result.reasoning}"
                    )
                    await self.handlers.execute(
                        "telegram_notify", trigger, {"message": notify_msg},
                    )
            else:
                # Gate deferred — notify human, do NOT execute
                msg = (
                    f"🧠 Decision Gate deferred [{name}]\\n"
                    f"Suggested: {decision_result.action} (confidence: {decision_result.confidence:.2f})\\n"
                    f"Reasoning: {decision_result.reasoning}\\n"
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
            )"""

assert old_fire in content, f"Edit 3 FAILED: fire_trigger block not found in {te_path}"
content = content.replace(old_fire, new_fire, 1)

# ── Write modified file ──────────────────────────────────────────────

with open(te_path, 'w') as f:
    f.write(content)

# ── Validate Python syntax ───────────────────────────────────────────

import py_compile
py_compile.compile(te_path, doraise=True)
py_compile.compile('/opt/mythos/iris/core/src/decision_gate.py', doraise=True)
py_compile.compile('/opt/mythos/bin/iris-decide', doraise=True)

print("✓ All Python files pass syntax check")

# ── Restart trigger service ──────────────────────────────────────────

patch.restart_service('mythos-trigger.service')

patch.finish()
