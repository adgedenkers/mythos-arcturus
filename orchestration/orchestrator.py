#!/usr/bin/env python3
"""
Mythos Orchestration Engine
===========================
Parallel LLM task decomposition and synthesis framework.

Reads pattern definitions, gathers context, dispatches stages
(parallel where dependencies allow), and synthesizes final output.

Usage:
    python3 orchestrator.py --pattern crud-update --request "Add a mood tracking field to the journal table"
    python3 orchestrator.py --pattern crud-update --request "..." --dry-run
    python3 orchestrator.py --list-patterns
"""

import json
import os
import sys
import time
import subprocess
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PATTERNS_DIR = Path("/opt/mythos/orchestration/patterns")
EXECUTION_LOG_DIR = Path("/opt/mythos/orchestration/logs")
CONTEXT_CACHE_DIR = Path("/opt/mythos/orchestration/cache")

# Model routing — maps preference labels to actual model strings
MODEL_MAP = {
    "fast": "claude-haiku-4-5-20251001",
    "balanced": "claude-sonnet-4-5-20250929",
    "deep": "claude-opus-4-6",
    "any": "claude-sonnet-4-5-20250929",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("orchestrator")


# ---------------------------------------------------------------------------
# Data Structures
# ---------------------------------------------------------------------------

class StageStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class StageResult:
    stage_id: str
    status: StageStatus
    output: Any = None
    error: str = ""
    tokens_used: int = 0
    duration_seconds: float = 0.0
    model_used: str = ""


@dataclass
class ExecutionContext:
    """Holds all gathered context and stage outputs for an orchestration run."""
    pattern_id: str
    user_request: str
    run_id: str
    started_at: str
    context_bag: dict = field(default_factory=dict)
    stage_results: dict = field(default_factory=dict)  # stage_id -> StageResult
    variables: dict = field(default_factory=dict)  # user-provided variables like TARGET_MODULE

    def get(self, key: str) -> Any:
        """Retrieve from context bag or stage results."""
        if key in self.context_bag:
            return self.context_bag[key]
        if key in self.stage_results:
            return self.stage_results[key].output
        # Check for dotted references like plan_output.migrations
        if "." in key:
            parts = key.split(".", 1)
            stage_key = parts[0].replace("_output", "")
            if stage_key in self.stage_results and self.stage_results[stage_key].output:
                try:
                    data = self.stage_results[stage_key].output
                    if isinstance(data, dict):
                        return data.get(parts[1])
                    return json.loads(data).get(parts[1])
                except (json.JSONDecodeError, AttributeError):
                    pass
        return None


# ---------------------------------------------------------------------------
# Pattern Loading
# ---------------------------------------------------------------------------

def load_pattern(pattern_id: str) -> dict:
    """Load a pattern definition from the patterns directory."""
    pattern_path = PATTERNS_DIR / f"{pattern_id}.json"
    if not pattern_path.exists():
        raise FileNotFoundError(f"Pattern '{pattern_id}' not found at {pattern_path}")
    with open(pattern_path) as f:
        return json.load(f)


def list_patterns() -> list[dict]:
    """List all available patterns with basic info."""
    patterns = []
    if not PATTERNS_DIR.exists():
        return patterns
    for p in sorted(PATTERNS_DIR.glob("*.json")):
        try:
            with open(p) as f:
                data = json.load(f)
            patterns.append({
                "id": data.get("pattern_id", p.stem),
                "name": data.get("name", ""),
                "version": data.get("version", ""),
                "description": data.get("description", ""),
                "stages": len(data.get("stages", [])),
            })
        except (json.JSONDecodeError, KeyError):
            patterns.append({"id": p.stem, "name": "ERROR", "description": "Failed to parse"})
    return patterns


# ---------------------------------------------------------------------------
# Template Rendering
# ---------------------------------------------------------------------------

def render_template(template: str, ctx: ExecutionContext) -> str:
    """Replace {{variable}} placeholders with values from context."""
    import re

    def replacer(match):
        key = match.group(1).strip()
        # Check user variables first (TARGET_MODULE, USER_REQUEST, etc.)
        if key == "USER_REQUEST":
            return ctx.user_request
        if key in ctx.variables:
            return str(ctx.variables[key])
        # Then check context bag and stage outputs
        val = ctx.get(key)
        if val is not None:
            if isinstance(val, (dict, list)):
                return json.dumps(val, indent=2)
            return str(val)
        # Check stage output references like "recon_output"
        stage_key = key.replace("_output", "")
        if stage_key in ctx.stage_results:
            out = ctx.stage_results[stage_key].output
            if isinstance(out, (dict, list)):
                return json.dumps(out, indent=2)
            return str(out) if out else f"[{key}: no output]"
        return f"[{key}: not found]"

    return re.sub(r"\{\{(.+?)\}\}", replacer, template)


# ---------------------------------------------------------------------------
# Context Gathering (Pre-fetch Phase)
# ---------------------------------------------------------------------------

def gather_context(pattern: dict, ctx: ExecutionContext) -> None:
    """Run all context-gathering commands and load files.
    
    Supports layer-aware gathering: if commands have a 'layer' field,
    they can be filtered by requested layers. Commands with layer='all'
    or no layer field always run.
    """
    gathering = pattern.get("context_gathering", {})
    requested_layers = ctx.variables.get("layers", None)  # e.g. ["postgres", "neo4j"]

    # Run commands
    for cmd_def in gathering.get("commands", []):
        cmd_id = cmd_def["id"]
        cmd_layer = cmd_def.get("layer", "all")

        # Skip layer-specific commands if we know which layers are needed
        # and this command's layer isn't one of them
        if requested_layers and cmd_layer != "all" and cmd_layer not in requested_layers:
            log.info(f"  Skipping [{cmd_id}]: layer '{cmd_layer}' not in requested layers")
            ctx.context_bag[cmd_def["output_key"]] = f"[SKIPPED: layer {cmd_layer} not requested]"
            continue

        raw_command = cmd_def["command"]
        # Render any variables in the command itself
        command = render_template(raw_command, ctx)
        log.info(f"  Gathering [{cmd_id}] (layer={cmd_layer}): {cmd_def.get('description', '')}")

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=30
            )
            output = result.stdout
            if result.stderr:
                output += f"\n[stderr]: {result.stderr}"
            ctx.context_bag[cmd_def["output_key"]] = output
            log.info(f"    ✓ {cmd_def['output_key']}: {len(output)} chars")
        except subprocess.TimeoutExpired:
            ctx.context_bag[cmd_def["output_key"]] = f"[TIMEOUT after 30s]"
            log.warning(f"    ✗ {cmd_id} timed out")
        except Exception as e:
            ctx.context_bag[cmd_def["output_key"]] = f"[ERROR: {e}]"
            log.error(f"    ✗ {cmd_id} failed: {e}")

    # Load files
    for filepath in gathering.get("files", []):
        rendered_path = render_template(filepath, ctx)
        key = f"file:{Path(rendered_path).name}"
        try:
            content = Path(rendered_path).read_text()
            ctx.context_bag[key] = content
            log.info(f"  Loaded file [{key}]: {len(content)} chars")
        except Exception as e:
            ctx.context_bag[key] = f"[ERROR reading {rendered_path}: {e}]"
            log.warning(f"  Failed to load {rendered_path}: {e}")


# ---------------------------------------------------------------------------
# Stage Execution
# ---------------------------------------------------------------------------

def call_llm(prompt: str, model_pref: str, max_tokens: int = 4096, temperature: float = 0.2) -> dict:
    """
    Call an LLM via the Anthropic API.

    Returns: {"text": str, "tokens_used": int, "model": str}

    NOTE: This is a placeholder that needs to be connected to actual API.
    In production, this calls the Anthropic API or a local model via Ollama.
    """
    model = MODEL_MAP.get(model_pref, model_pref)

    # --- PLACEHOLDER: Replace with actual API call ---
    # For now, this generates a diagnostic command for manual execution.
    # In production, this would be:
    #
    # import anthropic
    # client = anthropic.Anthropic()
    # response = client.messages.create(
    #     model=model,
    #     max_tokens=max_tokens,
    #     temperature=temperature,
    #     messages=[{"role": "user", "content": prompt}]
    # )
    # return {
    #     "text": response.content[0].text,
    #     "tokens_used": response.usage.input_tokens + response.usage.output_tokens,
    #     "model": model
    # }

    return {
        "text": f"[PENDING: Awaiting LLM execution with model={model}]\n\nPrompt length: {len(prompt)} chars",
        "tokens_used": 0,
        "model": model,
    }


def can_run_stage(stage: dict, ctx: ExecutionContext) -> bool:
    """Check if all dependencies for a stage are satisfied."""
    for dep_id in stage.get("depends_on", []):
        if dep_id not in ctx.stage_results:
            return False
        if ctx.stage_results[dep_id].status != StageStatus.COMPLETED:
            return False
    return True


def execute_stage(stage: dict, ctx: ExecutionContext) -> StageResult:
    """Execute a single stage."""
    stage_id = stage["stage_id"]
    execution = stage["execution"]
    mode = execution.get("mode", "llm")

    start_time = time.time()
    log.info(f"  Executing stage [{stage_id}]: {stage['name']}")

    try:
        if mode == "llm" or mode == "hybrid":
            prompt = render_template(execution.get("prompt_template", ""), ctx)
            model_pref = execution.get("model_preference", "balanced")
            max_tokens = execution.get("max_tokens", 4096)
            temperature = execution.get("temperature", 0.2)

            result = call_llm(prompt, model_pref, max_tokens, temperature)
            output = result["text"]
            tokens = result["tokens_used"]
            model_used = result["model"]

        elif mode == "script":
            script_path = render_template(execution.get("script", ""), ctx)
            proc = subprocess.run(
                script_path, shell=True, capture_output=True, text=True, timeout=60
            )
            output = proc.stdout
            tokens = 0
            model_used = "script"

        else:
            output = f"Unknown execution mode: {mode}"
            tokens = 0
            model_used = "none"

        duration = time.time() - start_time

        # Try to parse JSON if the output contract expects it
        output_contract = stage.get("output_contract", {})
        if output_contract.get("format") == "json":
            try:
                output = json.loads(output)
            except json.JSONDecodeError:
                pass  # Keep as string if not valid JSON

        return StageResult(
            stage_id=stage_id,
            status=StageStatus.COMPLETED,
            output=output,
            tokens_used=tokens,
            duration_seconds=duration,
            model_used=model_used,
        )

    except Exception as e:
        duration = time.time() - start_time
        log.error(f"    ✗ Stage [{stage_id}] failed: {e}")
        return StageResult(
            stage_id=stage_id,
            status=StageStatus.FAILED,
            error=str(e),
            duration_seconds=duration,
        )


def should_skip_stage(stage: dict, ctx: ExecutionContext) -> bool:
    """Evaluate a stage's skip_condition to determine if it should be skipped.
    
    Skip conditions are simple text expressions like:
    - "postgres not in plan_output.affected_layers"
    - "bot_changes is empty in plan_output"
    - "neo4j not in plan_output.affected_layers"
    
    Returns True if the stage should be SKIPPED.
    """
    condition = stage.get("skip_condition", "")
    if not condition:
        return False

    try:
        # Pattern: "<value> not in <stage_output_ref>"
        if " not in " in condition:
            parts = condition.split(" not in ", 1)
            check_value = parts[0].strip()
            ref = parts[1].strip()
            ref_data = ctx.get(ref)
            if ref_data is None:
                return False  # Can't evaluate, don't skip
            if isinstance(ref_data, str):
                try:
                    ref_data = json.loads(ref_data)
                except json.JSONDecodeError:
                    pass
            if isinstance(ref_data, list):
                return check_value not in ref_data
            return False

        # Pattern: "<field> is empty in <stage_output_ref>"
        if " is empty in " in condition:
            parts = condition.split(" is empty in ", 1)
            field_name = parts[0].strip()
            ref = parts[1].strip()
            ref_data = ctx.get(ref)
            if ref_data is None:
                return False
            if isinstance(ref_data, str):
                try:
                    ref_data = json.loads(ref_data)
                except json.JSONDecodeError:
                    return False
            if isinstance(ref_data, dict):
                field_val = ref_data.get(field_name, [])
                return not field_val or (isinstance(field_val, list) and len(field_val) == 0)
            return False

    except Exception as e:
        log.warning(f"  Could not evaluate skip_condition '{condition}': {e}")
        return False

    return False


def execute_stages(pattern: dict, ctx: ExecutionContext) -> None:
    """Execute all stages respecting dependency ordering and skip conditions."""
    stages = pattern.get("stages", [])
    remaining = {s["stage_id"]: s for s in stages}

    max_iterations = len(stages) * 2  # Safety limit
    iteration = 0

    while remaining and iteration < max_iterations:
        iteration += 1
        runnable = [s for s in remaining.values() if can_run_stage(s, ctx)]

        if not runnable:
            if remaining:
                log.error(f"Deadlock: {list(remaining.keys())} cannot run (missing deps)")
            break

        # In async mode, these could run in parallel.
        # For now, sequential but the structure supports parallelism.
        for stage in runnable:
            # Check skip condition
            if should_skip_stage(stage, ctx):
                log.info(f"  Skipping stage [{stage['stage_id']}]: {stage.get('skip_condition', '')}")
                ctx.stage_results[stage["stage_id"]] = StageResult(
                    stage_id=stage["stage_id"],
                    status=StageStatus.SKIPPED,
                    output=f"[SKIPPED: {stage.get('skip_condition', 'condition met')}]",
                )
                del remaining[stage["stage_id"]]
                continue

            result = execute_stage(stage, ctx)
            ctx.stage_results[stage["stage_id"]] = result
            del remaining[stage["stage_id"]]

            if result.status == StageStatus.FAILED:
                log.warning(f"  Stage [{stage['stage_id']}] failed, downstream stages may be affected")


# ---------------------------------------------------------------------------
# Synthesis
# ---------------------------------------------------------------------------

def synthesize(pattern: dict, ctx: ExecutionContext) -> StageResult:
    """Run the synthesis step to combine all stage outputs."""
    synthesis = pattern.get("synthesis", {})
    log.info("Running synthesis...")

    prompt = render_template(synthesis.get("prompt_template", ""), ctx)
    model_pref = synthesis.get("model_preference", "deep")

    start_time = time.time()
    result = call_llm(prompt, model_pref, max_tokens=8192, temperature=0.2)
    duration = time.time() - start_time

    return StageResult(
        stage_id="synthesis",
        status=StageStatus.COMPLETED,
        output=result["text"],
        tokens_used=result["tokens_used"],
        duration_seconds=duration,
        model_used=result["model"],
    )


# ---------------------------------------------------------------------------
# Execution Logging
# ---------------------------------------------------------------------------

def save_execution_log(ctx: ExecutionContext, synthesis_result: StageResult) -> Path:
    """Save a complete execution log for this run."""
    EXECUTION_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = EXECUTION_LOG_DIR / f"{ctx.run_id}.json"

    log_data = {
        "run_id": ctx.run_id,
        "pattern_id": ctx.pattern_id,
        "user_request": ctx.user_request,
        "started_at": ctx.started_at,
        "completed_at": datetime.now().isoformat(),
        "variables": ctx.variables,
        "stages": {
            sid: {
                "status": r.status.value,
                "tokens_used": r.tokens_used,
                "duration_seconds": r.duration_seconds,
                "model_used": r.model_used,
                "error": r.error,
                "skipped": r.status == StageStatus.SKIPPED,
                "output_preview": str(r.output)[:500] if r.output else None,
            }
            for sid, r in ctx.stage_results.items()
        },
        "synthesis": {
            "status": synthesis_result.status.value,
            "tokens_used": synthesis_result.tokens_used,
            "duration_seconds": synthesis_result.duration_seconds,
            "model_used": synthesis_result.model_used,
        },
        "totals": {
            "total_tokens": sum(r.tokens_used for r in ctx.stage_results.values()) + synthesis_result.tokens_used,
            "total_duration": sum(r.duration_seconds for r in ctx.stage_results.values()) + synthesis_result.duration_seconds,
            "stages_completed": sum(1 for r in ctx.stage_results.values() if r.status == StageStatus.COMPLETED),
            "stages_failed": sum(1 for r in ctx.stage_results.values() if r.status == StageStatus.FAILED),
        },
    }

    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=2)

    log.info(f"Execution log saved to {log_path}")
    return log_path


# ---------------------------------------------------------------------------
# Dry Run
# ---------------------------------------------------------------------------

def dry_run(pattern: dict, ctx: ExecutionContext) -> dict:
    """Show what would happen without executing anything."""
    stages = pattern.get("stages", [])
    
    # Detect data layers from pattern
    layer_detection = pattern.get("data_layer_detection", {})
    
    plan = {
        "pattern": pattern["name"],
        "version": pattern["version"],
        "request": ctx.user_request,
        "data_layers": {
            "detection_rules": len(layer_detection.get("rules", [])),
            "defined_layers": [r["layer"] for r in layer_detection.get("rules", [])],
        },
        "context_commands": len(pattern.get("context_gathering", {}).get("commands", [])),
        "context_commands_by_layer": {},
        "context_files": len(pattern.get("context_gathering", {}).get("files", [])),
        "execution_plan": [],
    }

    # Count commands per layer
    for cmd in pattern.get("context_gathering", {}).get("commands", []):
        layer = cmd.get("layer", "all")
        plan["context_commands_by_layer"][layer] = plan["context_commands_by_layer"].get(layer, 0) + 1

    # Build dependency graph to show execution order
    resolved = set()
    remaining = {s["stage_id"]: s for s in stages}
    wave = 0

    while remaining:
        wave += 1
        runnable = [
            s for s in remaining.values()
            if all(d in resolved for d in s.get("depends_on", []))
        ]
        if not runnable:
            break

        wave_info = {
            "wave": wave,
            "parallel": len(runnable) > 1,
            "stages": []
        }
        for s in runnable:
            stage_info = {
                "id": s["stage_id"],
                "name": s["name"],
                "model": MODEL_MAP.get(s["execution"].get("model_preference", "any"), "unknown"),
                "depends_on": s.get("depends_on", []),
                "output_format": s.get("output_contract", {}).get("format", "unknown"),
            }
            if s.get("skip_condition"):
                stage_info["skip_condition"] = s["skip_condition"]
                stage_info["conditional"] = True
            wave_info["stages"].append(stage_info)
            resolved.add(s["stage_id"])
            del remaining[s["stage_id"]]

        plan["execution_plan"].append(wave_info)

    plan["synthesis_model"] = MODEL_MAP.get(
        pattern.get("synthesis", {}).get("model_preference", "deep"), "unknown"
    )
    plan["validation_checks"] = len(pattern.get("synthesis", {}).get("validation", []))

    return plan


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------

def run_orchestration(
    pattern_id: str,
    user_request: str,
    variables: Optional[dict] = None,
    dry: bool = False,
) -> dict:
    """Main orchestration entry point."""
    run_id = f"{pattern_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    log.info(f"=== Orchestration Run: {run_id} ===")
    log.info(f"Pattern: {pattern_id}")
    log.info(f"Request: {user_request}")

    # Load pattern
    pattern = load_pattern(pattern_id)
    log.info(f"Loaded pattern '{pattern['name']}' v{pattern['version']}")

    # Build execution context
    ctx = ExecutionContext(
        pattern_id=pattern_id,
        user_request=user_request,
        run_id=run_id,
        started_at=datetime.now().isoformat(),
        variables=variables or {},
    )

    # Dry run mode
    if dry:
        plan = dry_run(pattern, ctx)
        print(json.dumps(plan, indent=2))
        return plan

    # Phase 1: Gather context
    log.info("--- Phase 1: Context Gathering ---")
    gather_context(pattern, ctx)

    # Phase 2: Execute stages
    log.info("--- Phase 2: Stage Execution ---")
    execute_stages(pattern, ctx)

    # Phase 3: Synthesis
    log.info("--- Phase 3: Synthesis ---")
    synthesis_result = synthesize(pattern, ctx)
    ctx.stage_results["synthesis"] = synthesis_result

    # Phase 4: Log
    if pattern.get("feedback_loop", {}).get("log_execution", True):
        log_path = save_execution_log(ctx, synthesis_result)

    # Summary
    log.info("=== Run Complete ===")
    totals = {
        "run_id": run_id,
        "stages_completed": sum(1 for r in ctx.stage_results.values() if r.status == StageStatus.COMPLETED),
        "stages_failed": sum(1 for r in ctx.stage_results.values() if r.status == StageStatus.FAILED),
        "total_tokens": sum(r.tokens_used for r in ctx.stage_results.values()),
        "total_duration": sum(r.duration_seconds for r in ctx.stage_results.values()),
    }
    log.info(f"  Completed: {totals['stages_completed']}, Failed: {totals['stages_failed']}")
    log.info(f"  Tokens: {totals['total_tokens']}, Duration: {totals['total_duration']:.1f}s")

    return {
        "run_id": run_id,
        "totals": totals,
        "synthesis": synthesis_result.output,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Mythos Orchestration Engine")
    parser.add_argument("--pattern", "-p", help="Pattern ID to execute")
    parser.add_argument("--request", "-r", help="User request string")
    parser.add_argument("--var", "-v", action="append", help="Variables as key=value pairs")
    parser.add_argument("--dry-run", action="store_true", help="Show execution plan without running")
    parser.add_argument("--list-patterns", action="store_true", help="List available patterns")

    args = parser.parse_args()

    if args.list_patterns:
        patterns = list_patterns()
        if not patterns:
            print("No patterns found. Check PATTERNS_DIR:", PATTERNS_DIR)
        for p in patterns:
            print(f"  {p['id']} (v{p['version']}) - {p['name']}")
            print(f"    {p['description']}")
            print(f"    Stages: {p['stages']}")
            print()
        sys.exit(0)

    if not args.pattern or not args.request:
        parser.print_help()
        sys.exit(1)

    # Parse variables
    variables = {}
    if args.var:
        for v in args.var:
            key, _, val = v.partition("=")
            variables[key] = val

    result = run_orchestration(
        pattern_id=args.pattern,
        user_request=args.request,
        variables=variables,
        dry=args.dry_run,
    )

    if not args.dry_run:
        print(json.dumps(result, indent=2, default=str))
