#!/usr/bin/env python3
"""
Mythos Mission Runner — Claude-to-Iris delegation engine.

Reads a mission YAML file, gathers system context (files, directories,
Postgres, Neo4j, shell commands), runs multi-phase Ollama prompts with
injected context, validates outputs, and produces results.

Usage:
    mythos-mission run mission.yaml
    mythos-mission validate mission.yaml
    mythos-mission dry-run mission.yaml
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import yaml

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MISSION_LOG_DIR = "/opt/mythos/mission/logs"
STAGING_DIR = "/tmp/mythos-mission"
NEO4J_URI = "bolt://localhost:7687"

# Load Neo4j credentials from .env if available
_env_path = Path("/opt/mythos/.env")
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = None
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line.startswith("#"):
            continue
        if line.startswith("NEO4J_PASSWORD="):
            NEO4J_PASSWORD = line.split("=", 1)[1]
        elif line.startswith("NEO4J_USER="):
            NEO4J_USER = line.split("=", 1)[1]

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("mission")


# ---------------------------------------------------------------------------
# Context Gatherers
# ---------------------------------------------------------------------------

def read_file_context(spec: dict) -> str:
    """Read a file and optionally truncate."""
    path = spec["path"]
    max_lines = spec.get("max_lines")
    try:
        text = Path(path).read_text()
        if max_lines:
            lines = text.splitlines()
            if len(lines) > max_lines:
                text = "\n".join(lines[:max_lines]) + f"\n\n... [truncated, {len(lines) - max_lines} more lines]"
        return text
    except Exception as e:
        return f"[ERROR reading {path}: {e}]"


def list_directory_context(spec: dict) -> str:
    """List directory contents."""
    path = spec["path"]
    depth = spec.get("depth", 2)
    pattern = spec.get("pattern", "*")
    try:
        result = subprocess.run(
            ["find", path, "-maxdepth", str(depth), "-name", pattern, "-type", "f"],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip() or "[empty directory]"
    except Exception as e:
        return f"[ERROR listing {path}: {e}]"


def run_postgres_query(spec: dict) -> str:
    """Run a PostgreSQL query and return results."""
    query = spec["query"]
    try:
        result = subprocess.run(
            ["sudo", "-u", "postgres", "psql", "-d", "mythos", "-t", "-A", "-c", query],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return f"[POSTGRES ERROR: {result.stderr.strip()}]"
        return result.stdout.strip() or "[no results]"
    except Exception as e:
        return f"[POSTGRES ERROR: {e}]"


def run_graph_query(spec: dict) -> str:
    """Run a Neo4j Cypher query and return results."""
    cypher = spec["cypher"]
    if not NEO4J_PASSWORD:
        return "[NEO4J ERROR: No password found in /opt/mythos/.env]"
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session() as session:
            result = session.run(cypher)
            rows = []
            for record in result:
                rows.append(dict(record))
            driver.close()
            if not rows:
                return "[no results]"
            # Format as readable text
            if len(rows[0]) == 1:
                # Single column — just list values
                key = list(rows[0].keys())[0]
                return "\n".join(str(r[key]) for r in rows)
            else:
                # Multiple columns — tabular
                headers = list(rows[0].keys())
                lines = [" | ".join(headers)]
                lines.append("-" * len(lines[0]))
                for r in rows:
                    lines.append(" | ".join(str(r.get(h, "")) for h in headers))
                return "\n".join(lines)
    except ImportError:
        return "[NEO4J ERROR: neo4j driver not installed]"
    except Exception as e:
        return f"[NEO4J ERROR: {e}]"


def run_shell_command(spec: dict) -> str:
    """Run a shell command and return output."""
    command = spec["command"]
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True, timeout=30,
        )
        output = result.stdout.strip()
        if result.returncode != 0 and result.stderr.strip():
            output += f"\n[stderr: {result.stderr.strip()}]"
        return output or "[no output]"
    except subprocess.TimeoutExpired:
        return "[TIMEOUT after 30s]"
    except Exception as e:
        return f"[SHELL ERROR: {e}]"


# ---------------------------------------------------------------------------
# Context Assembly
# ---------------------------------------------------------------------------

def gather_context(context_spec: dict) -> dict:
    """Gather all context defined in the mission file."""
    ctx = {}

    if "files" in context_spec:
        ctx["files"] = {}
        for spec in context_spec["files"]:
            alias = spec.get("alias", Path(spec["path"]).stem)
            log.info(f"  Reading file: {spec['path']} -> {alias}")
            ctx["files"][alias] = read_file_context(spec)

    if "directories" in context_spec:
        ctx["directories"] = {}
        for spec in context_spec["directories"]:
            alias = spec.get("alias", Path(spec["path"]).name)
            log.info(f"  Listing dir: {spec['path']} -> {alias}")
            ctx["directories"][alias] = list_directory_context(spec)

    if "postgres" in context_spec:
        ctx["postgres"] = {}
        for spec in context_spec["postgres"]:
            alias = spec["alias"]
            log.info(f"  Postgres query: {alias}")
            ctx["postgres"][alias] = run_postgres_query(spec)

    if "graph" in context_spec:
        ctx["graph"] = {}
        for spec in context_spec["graph"]:
            alias = spec["alias"]
            log.info(f"  Neo4j query: {alias}")
            ctx["graph"][alias] = run_graph_query(spec)

    if "shell" in context_spec:
        ctx["shell"] = {}
        for spec in context_spec["shell"]:
            alias = spec["alias"]
            log.info(f"  Shell command: {alias}")
            ctx["shell"][alias] = run_shell_command(spec)

    return ctx


# ---------------------------------------------------------------------------
# Template Rendering
# ---------------------------------------------------------------------------

def resolve_value(path: str, data: dict) -> str:
    """Resolve a dot-path like 'context.files.chat_assistant' from nested dict."""
    parts = path.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return f"[UNRESOLVED: {path}]"
    if isinstance(current, (dict, list)):
        return json.dumps(current, indent=2, default=str)
    return str(current)


def render_template(template: str, data: dict) -> str:
    """Replace {path.to.value} placeholders in template with resolved values.

    Uses single braces {like.this} for substitution.
    Escaped double braces {{like.this}} are preserved as literal {like.this}.
    """
    # First, protect escaped double braces
    template = template.replace("{{", "\x00LBRACE\x00").replace("}}", "\x00RBRACE\x00")

    # Replace {path.to.value} with resolved values
    def replacer(match):
        path = match.group(1)
        return resolve_value(path, data)

    result = re.sub(r"\{([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\}", replacer, template)

    # Restore escaped braces
    result = result.replace("\x00LBRACE\x00", "{").replace("\x00RBRACE\x00", "}")
    return result


# ---------------------------------------------------------------------------
# Ollama Interface
# ---------------------------------------------------------------------------

def call_ollama(prompt: str, model: str, temperature: float = 0.3, system: str = None) -> str:
    """Call Ollama's generate endpoint and return the response text."""
    import urllib.request

    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }
    if system:
        payload["system"] = system

    data = json.dumps(payload).encode()
    req = urllib.request.Request(
        f"{OLLAMA_URL}/api/generate",
        data=data,
        headers={"Content-Type": "application/json"},
    )

    log.info(f"  Calling Ollama ({model}, temp={temperature})...")
    start = time.time()

    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            result = json.loads(resp.read())
            elapsed = time.time() - start
            response_text = result.get("response", "")
            log.info(f"  Response received ({elapsed:.1f}s, {len(response_text)} chars)")
            return response_text
    except Exception as e:
        log.error(f"  Ollama call failed: {e}")
        raise


# ---------------------------------------------------------------------------
# Output Parsing
# ---------------------------------------------------------------------------

def parse_output(raw: str, output_format: str) -> Any:
    """Parse Ollama output according to expected format."""
    if output_format == "json":
        cleaned = raw.strip()
        # Strip markdown fences if present
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        # Also handle case where model wraps in ```json ... ```
        cleaned = cleaned.strip()
        return json.loads(cleaned)

    elif output_format == "code":
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines)
        return cleaned

    else:
        # Raw text
        return raw.strip()


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def run_validations(validations: list, phase_data: dict) -> tuple[bool, list[str]]:
    """Run validation checks. Returns (passed, list_of_errors)."""
    errors = []

    for v in validations:
        vtype = v["type"]

        if vtype == "python_syntax":
            filepath = v["file"]
            try:
                result = subprocess.run(
                    ["/opt/mythos/.venv/bin/python3", "-c",
                     f"import py_compile; py_compile.compile('{filepath}', doraise=True)"],
                    capture_output=True, text=True, timeout=10,
                )
                if result.returncode != 0:
                    errors.append(f"Syntax error in {filepath}: {result.stderr.strip()}")
            except Exception as e:
                errors.append(f"Syntax check failed for {filepath}: {e}")

        elif vtype == "contains":
            filepath = v["file"]
            try:
                content = Path(filepath).read_text()
                for s in v.get("strings", []):
                    if s not in content:
                        errors.append(f"Missing expected string in {filepath}: '{s}'")
            except Exception as e:
                errors.append(f"Cannot read {filepath}: {e}")

        elif vtype == "not_contains":
            filepath = v["file"]
            try:
                content = Path(filepath).read_text()
                for s in v.get("strings", []):
                    if s in content:
                        errors.append(f"Found forbidden string in {filepath}: '{s}'")
            except Exception as e:
                errors.append(f"Cannot read {filepath}: {e}")

        elif vtype == "shell":
            command = v["command"]
            try:
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True, timeout=30,
                )
                if result.returncode != 0:
                    errors.append(f"Shell validation failed: {command}\n{result.stderr.strip()}")
            except Exception as e:
                errors.append(f"Shell validation error: {e}")

        elif vtype == "file_exists":
            filepath = v["file"]
            if not Path(filepath).exists():
                errors.append(f"Expected file does not exist: {filepath}")

        else:
            errors.append(f"Unknown validation type: {vtype}")

    return (len(errors) == 0, errors)


# ---------------------------------------------------------------------------
# Dynamic Context (from prior phase outputs)
# ---------------------------------------------------------------------------

def _resolve_jsonpath(path: str, data: dict) -> Any:
    """Resolve a simple JSONPath like '$.files_to_modify' from a dict.

    Supports:
        $.key           -> data["key"]
        $.key.subkey    -> data["key"]["subkey"]
    """
    # Strip leading $. if present
    if path.startswith("$."):
        path = path[2:]
    elif path.startswith("$"):
        path = path[1:]

    current = data
    for part in path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def gather_dynamic_context(spec: dict, phase_outputs: dict) -> dict:
    """Gather additional context based on prior phase outputs."""
    dctx = {"files": {}}
    from_prior = spec.get("from_prior")
    if not from_prior or from_prior not in phase_outputs:
        return dctx

    prior = phase_outputs[from_prior]

    # read_files: JSONPath extraction from prior output
    read_files_path = spec.get("read_files")
    if read_files_path and isinstance(prior, dict):
        files_to_read = _resolve_jsonpath(read_files_path, prior)
        if isinstance(files_to_read, list):
            for fpath in files_to_read:
                if isinstance(fpath, str) and Path(fpath).exists():
                    alias = Path(fpath).stem
                    log.info(f"  Dynamic read: {fpath} -> {alias}")
                    dctx["files"][alias] = Path(fpath).read_text()

    return dctx


# ---------------------------------------------------------------------------
# Mission Runner
# ---------------------------------------------------------------------------

class MissionRunner:
    """Execute a mission from a YAML specification."""

    def __init__(self, mission_path: str, dry_run: bool = False):
        self.mission_path = Path(mission_path)
        self.dry_run = dry_run
        self.mission = yaml.safe_load(self.mission_path.read_text())
        self.context = {}
        self.phase_outputs = {}
        self.run_log = {
            "mission": self.mission.get("mission", "unnamed"),
            "started": datetime.now().isoformat(),
            "phases": [],
            "status": "pending",
        }

    def run(self) -> bool:
        """Execute the full mission. Returns True on success."""
        mission_name = self.mission.get("mission", "unnamed")
        log.info(f"{'[DRY RUN] ' if self.dry_run else ''}Mission: {mission_name}")
        log.info(f"Description: {self.mission.get('description', 'none')}")

        # Ensure staging directory exists
        os.makedirs(STAGING_DIR, exist_ok=True)
        os.makedirs(MISSION_LOG_DIR, exist_ok=True)

        # Phase 0: Gather context
        log.info("=" * 60)
        log.info("GATHERING CONTEXT")
        log.info("=" * 60)
        if "context" in self.mission:
            self.context = gather_context(self.mission["context"])
        else:
            self.context = {}

        # Build the template data namespace
        template_data = {
            "mission": self.mission,
            "context": self.context,
            "phases": self.phase_outputs,
        }

        # Execute phases
        phases = self.mission.get("phases", [])
        success = True

        for i, phase in enumerate(phases):
            phase_name = phase.get("name", f"phase_{i}")
            log.info("")
            log.info("=" * 60)
            log.info(f"PHASE {i + 1}/{len(phases)}: {phase_name}")
            log.info(f"  {phase.get('description', '')}")
            log.info("=" * 60)

            phase_log = {
                "name": phase_name,
                "started": datetime.now().isoformat(),
                "status": "pending",
            }

            # Handle dynamic context
            if "dynamic_context" in phase:
                dctx = gather_dynamic_context(phase["dynamic_context"], self.phase_outputs)
                template_data["dynamic_context"] = dctx

            # Validation-only phase (no prompt)
            if "validate" in phase and "prompt" not in phase:
                log.info("  Running validation checks...")
                passed, errors = run_validations(phase["validate"], template_data)
                phase_log["validation_passed"] = passed
                phase_log["validation_errors"] = errors
                if not passed:
                    log.error(f"  Validation failed: {errors}")
                    on_fail = phase.get("on_fail", "halt")
                    if on_fail == "halt":
                        phase_log["status"] = "failed"
                        self.run_log["phases"].append(phase_log)
                        success = False
                        break
                    elif on_fail == "skip":
                        phase_log["status"] = "skipped"
                        self.run_log["phases"].append(phase_log)
                        continue
                else:
                    log.info("  Validation passed!")
                    phase_log["status"] = "completed"
                    self.run_log["phases"].append(phase_log)
                    continue

            # Prompt phase
            if "prompt" in phase:
                model = phase.get("model", self.mission.get("model", "qwen2.5:32b"))
                temperature = phase.get("temperature", self.mission.get("temperature", 0.3))
                output_format = phase.get("output_format", "text")
                output_alias = phase.get("output_alias", phase_name)

                # Render the prompt
                prompt = render_template(phase["prompt"], template_data)

                if self.dry_run:
                    log.info(f"  [DRY RUN] Would call {model} with {len(prompt)} char prompt")
                    log.info(f"  Prompt preview (first 500 chars):")
                    log.info(f"  {prompt[:500]}")
                    phase_log["status"] = "dry_run"
                    self.run_log["phases"].append(phase_log)
                    continue

                # Call Ollama
                max_retries = phase.get("max_retries", 0)
                retry_count = 0
                phase_success = False

                while retry_count <= max_retries:
                    try:
                        raw_response = call_ollama(prompt, model, temperature)
                        parsed = parse_output(raw_response, output_format)

                        # Store output
                        self.phase_outputs[output_alias] = parsed
                        template_data["phases"][output_alias] = parsed

                        # Write to file if specified
                        output_path = phase.get("output_path")
                        if output_path:
                            os.makedirs(Path(output_path).parent, exist_ok=True)
                            if isinstance(parsed, str):
                                Path(output_path).write_text(parsed)
                            else:
                                Path(output_path).write_text(json.dumps(parsed, indent=2, default=str))
                            log.info(f"  Output written to {output_path}")

                        # Run validation if specified
                        if "validate" in phase:
                            template_data["validation"] = {}
                            passed, errors = run_validations(phase["validate"], template_data)
                            if not passed:
                                template_data["validation"]["errors"] = "\n".join(errors)
                                log.warning(f"  Validation failed (attempt {retry_count + 1}): {errors}")
                                if retry_count < max_retries and "retry_prompt" in phase:
                                    retry_count += 1
                                    prompt = render_template(phase["retry_prompt"], template_data)
                                    log.info(f"  Retrying with corrective prompt...")
                                    continue
                                else:
                                    on_fail = phase.get("on_fail", "halt")
                                    if on_fail == "halt":
                                        phase_log["status"] = "failed"
                                        phase_log["errors"] = errors
                                        success = False
                                        break
                                    elif on_fail == "skip":
                                        phase_log["status"] = "skipped"
                                        break
                            else:
                                log.info("  Validation passed!")

                        phase_success = True
                        break

                    except json.JSONDecodeError as e:
                        log.warning(f"  JSON parse failed (attempt {retry_count + 1}): {e}")
                        if retry_count < max_retries:
                            retry_count += 1
                            prompt += "\n\nYour previous response was not valid JSON. Respond with ONLY valid JSON."
                            continue
                        else:
                            phase_log["status"] = "failed"
                            phase_log["errors"] = [f"JSON parse failed after {max_retries + 1} attempts: {e}"]
                            success = False
                            break

                    except Exception as e:
                        log.error(f"  Phase failed: {e}")
                        log.error(traceback.format_exc())
                        phase_log["status"] = "failed"
                        phase_log["errors"] = [str(e)]
                        success = False
                        break

                if phase_success:
                    phase_log["status"] = "completed"

                if not success:
                    self.run_log["phases"].append(phase_log)
                    break

            phase_log["completed"] = datetime.now().isoformat()
            self.run_log["phases"].append(phase_log)

        # Mission complete
        self.run_log["status"] = "success" if success else "failed"
        self.run_log["completed"] = datetime.now().isoformat()

        # Run on_success / on_failure hooks
        hook_key = "success" if success else "failure"
        hooks = self.mission.get(hook_key, {})
        for cmd_spec in hooks.get(f"on_{hook_key}", []):
            command = render_template(cmd_spec["command"], template_data)
            log.info(f"  Running {hook_key} hook: {command}")
            if not self.dry_run:
                subprocess.run(command, shell=True, timeout=10)

        # Write run log
        log_path = Path(MISSION_LOG_DIR) / f"{mission_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_path.write_text(json.dumps(self.run_log, indent=2, default=str))
        log.info(f"\nRun log: {log_path}")

        if success:
            log.info("\n  MISSION COMPLETE")
            if "success" in self.mission:
                for out in self.mission["success"].get("outputs", []):
                    log.info(f"  Output: {out}")
        else:
            log.error("\n  MISSION FAILED")
            if self.mission.get("failure", {}).get("diagnostic"):
                self._write_diagnostic()

        return success

    def _write_diagnostic(self):
        """Write diagnostic report on failure."""
        diag = {
            "mission": self.mission.get("mission"),
            "run_log": self.run_log,
            "context_keys": {k: list(v.keys()) if isinstance(v, dict) else type(v).__name__
                             for k, v in self.context.items()},
            "phase_outputs": {k: type(v).__name__ for k, v in self.phase_outputs.items()},
        }
        diag_path = Path(MISSION_LOG_DIR) / f"diagnostic_{self.mission.get('mission', 'unnamed')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        diag_path.write_text(json.dumps(diag, indent=2, default=str))
        log.info(f"  Diagnostic: {diag_path}")

    def validate_mission(self) -> bool:
        """Validate the mission YAML without executing."""
        errors = []

        if "mission" not in self.mission:
            errors.append("Missing 'mission' field (name)")
        if "phases" not in self.mission:
            errors.append("Missing 'phases' list")
        elif not isinstance(self.mission["phases"], list):
            errors.append("'phases' must be a list")
        else:
            for i, phase in enumerate(self.mission["phases"]):
                if "name" not in phase:
                    errors.append(f"Phase {i}: missing 'name'")
                if "prompt" not in phase and "validate" not in phase:
                    errors.append(f"Phase {i} ({phase.get('name', '?')}): needs 'prompt' or 'validate'")

        if "context" in self.mission:
            ctx = self.mission["context"]
            for key in ["files", "directories", "postgres", "graph", "shell"]:
                if key in ctx:
                    for spec in ctx[key]:
                        if key == "files" and "path" not in spec:
                            errors.append(f"Context file missing 'path': {spec}")
                        if key == "graph" and "cypher" not in spec:
                            errors.append(f"Context graph missing 'cypher': {spec}")
                        if key not in ["files", "directories"] and "alias" not in spec:
                            errors.append(f"Context {key} missing 'alias': {spec}")

        if errors:
            log.error("Mission validation FAILED:")
            for e in errors:
                log.error(f"  - {e}")
            return False
        else:
            log.info("Mission validation passed")
            return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Mythos Mission Runner — Claude-to-Iris delegation engine",
        prog="mythos-mission",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # run
    run_parser = subparsers.add_parser("run", help="Execute a mission")
    run_parser.add_argument("mission_file", help="Path to mission YAML file")
    run_parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    # validate
    val_parser = subparsers.add_parser("validate", help="Validate a mission file without executing")
    val_parser.add_argument("mission_file", help="Path to mission YAML file")

    # dry-run
    dry_parser = subparsers.add_parser("dry-run", help="Gather context and render prompts without calling Ollama")
    dry_parser.add_argument("mission_file", help="Path to mission YAML file")

    # list
    list_parser = subparsers.add_parser("list", help="List recent mission runs")
    list_parser.add_argument("-n", type=int, default=10, help="Number of runs to show")

    args = parser.parse_args()

    if args.command in ("run", "validate", "dry-run"):
        mission_path = args.mission_file
        if not Path(mission_path).exists():
            log.error(f"Mission file not found: {mission_path}")
            sys.exit(1)

    if args.command == "validate":
        runner = MissionRunner(mission_path)
        success = runner.validate_mission()
        sys.exit(0 if success else 1)

    elif args.command == "dry-run":
        runner = MissionRunner(mission_path, dry_run=True)
        runner.validate_mission()
        runner.run()
        sys.exit(0)

    elif args.command == "run":
        if hasattr(args, "verbose") and args.verbose:
            logging.getLogger().setLevel(logging.DEBUG)
        runner = MissionRunner(mission_path)
        if not runner.validate_mission():
            sys.exit(1)
        success = runner.run()
        sys.exit(0 if success else 1)

    elif args.command == "list":
        log_dir = Path(MISSION_LOG_DIR)
        if not log_dir.exists():
            print("No mission logs found.")
            sys.exit(0)
        logs = sorted(log_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        for log_file in logs[:args.n]:
            try:
                data = json.loads(log_file.read_text())
                status = data.get("status", "?")
                icon = "+" if status == "success" else "X" if status == "failed" else "-"
                print(f"  [{icon}] {data.get('mission', '?'):30s}  {data.get('started', '?')[:19]}  {status}")
            except Exception:
                print(f"  [!] {log_file.name} (corrupt)")


if __name__ == "__main__":
    main()
