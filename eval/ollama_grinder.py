#!/usr/bin/env python3
"""
Ollama Grinder — Multi-Pass Build Engine
==========================================

Takes a build plan (from a pattern or Claude), feeds each step to a local
Ollama model with cumulative context, tests after each step, and loops on
the final step until all tests pass.

Key difference from ollama_builder.py:
  - ollama_builder: single-shot, model writes entire file from scratch each iteration
  - ollama_grinder: multi-pass, each pass builds on the previous output,
    model never starts from zero after pass 1

Usage:
    /opt/mythos/.venv/bin/python3 /opt/mythos/eval/ollama_grinder.py \
        --plan /opt/mythos/eval/challenges/voice_memo_search/build_plan.json \
        --model qwen3-coder:30b \
        --verbose

    # Or use the convenience wrapper:
    chunk-grind voice_memo_search qwen3-coder:30b

Author: Ka'tuar'el
System: Arcturus
"""
import argparse
import ast
import json
import os
import re
import subprocess
import sys
import textwrap
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

EVAL_DIR = Path("/opt/mythos/eval")
PATTERNS_DIR = Path("/opt/mythos/patterns")
CHUNKS_DIR = Path("/opt/mythos/chunks")
RESULTS_DIR = EVAL_DIR / "results"

# ── Prompt Templates ──────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a Python developer building components for the Mythos system on Arcturus.
You receive code from previous build passes and instructions for the current pass.
Your job: take the existing code and ADD or MODIFY only what the current instruction asks for.

CRITICAL RULES:
- Output the COMPLETE updated Python file. Not a diff, not a fragment — the whole file.
- No markdown fences. No explanations. Just the Python code.
- Preserve everything from previous passes unless told to change it.
- The file must parse as valid Python at every step.
- Never leave empty blocks (if:, try:, finally:, except:) — always add at least 'pass'.
- Database connections must be closed in try/finally.
"""

def build_pass_prompt(pass_info: dict, current_code: str, context: dict,
                      errors: list = None) -> str:
    """Build the prompt for a single grinder pass."""
    instruction = pass_info["instruction"]

    # Build context block
    ctx_parts = []
    if context.get("system_context"):
        ctx_parts.append(f"SYSTEM CONTEXT:\n{json.dumps(context['system_context'], indent=2)}")
    if context.get("scaffold"):
        ctx_parts.append(f"ARCHITECTURE SCAFFOLD:\n{context['scaffold']}")
    if context.get("table_schema"):
        ctx_parts.append(f"TABLE SCHEMA:\n{context['table_schema']}")

    context_block = "\n\n".join(ctx_parts)

    if current_code:
        prompt = f"""CURRENT CODE (from previous passes):
```
{current_code}
```

PASS {pass_info['pass']} INSTRUCTION:
{instruction}

{context_block}

Take the current code above and apply ONLY this instruction.
Output the COMPLETE updated file. No fragments."""
    else:
        prompt = f"""BUILD PASS {pass_info['pass']}:
{instruction}

{context_block}

Output the COMPLETE Python file. No fragments. No markdown."""

    if errors:
        error_block = "\n".join(f"  - {e}" for e in errors)
        prompt += f"""

ERRORS FROM LAST ATTEMPT — fix these:
{error_block}"""

    return prompt


# ── Ollama Integration ────────────────────────────────────────────────────────

def call_ollama(model: str, prompt: str, system: str = SYSTEM_PROMPT,
                temperature: float = 0.2, timeout: int = 300) -> str:
    """Call Ollama and return the response text."""
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {
            "temperature": temperature,
            "num_predict": 4096,
        }
    }
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", "http://localhost:11434/api/generate",
             "-H", "Content-Type: application/json",
             "-d", json.dumps(payload)],
            capture_output=True, text=True, timeout=timeout
        )
        if result.returncode != 0:
            return f"ERROR: curl failed: {result.stderr}"
        response = json.loads(result.stdout)
        return response.get("response", "ERROR: No response field")
    except subprocess.TimeoutExpired:
        return "ERROR: Ollama request timed out"
    except Exception as e:
        return f"ERROR: {e}"


def extract_python(response: str) -> str:
    """Extract Python code from model response."""
    code = response.strip()

    # Try fenced blocks first
    matches = re.findall(r"```(?:python)?\s*\n(.+?)```", code, re.DOTALL)
    if matches:
        code = max(matches, key=len).strip()
        if any(m in code for m in ["import ", "class ", "def ", "from "]):
            return code

    # Find Python boundaries
    lines = code.split("\n")
    starters = ("#!", '"""', "'''", "import ", "from ", "class ", "def ")
    start = 0
    for i, line in enumerate(lines):
        if any(line.strip().startswith(s) for s in starters):
            start = i
            break

    end = len(lines)
    for i in range(len(lines) - 1, start, -1):
        stripped = lines[i].strip()
        if not stripped:
            continue
        if (lines[i][0:1].isspace() or
            any(stripped.startswith(k) for k in
                ["import ", "from ", "class ", "def ", "return ", "raise ",
                 "if ", "else:", "elif ", "except", "finally:", "try:",
                 "for ", "while ", "with ", "async ", "logger.", "print(", "#"])):
            end = i + 1
            break

    return "\n".join(lines[start:end]).strip()


# ── Testing ───────────────────────────────────────────────────────────────────

def run_parse_check(code: str) -> dict:
    """Check if code parses as valid Python."""
    try:
        ast.parse(code)
        return {"pass": True, "errors": []}
    except SyntaxError as e:
        lines = code.split("\n")
        context = []
        if e.lineno:
            s = max(0, e.lineno - 3)
            end = min(len(lines), e.lineno + 2)
            for i in range(s, end):
                marker = ">>>" if i == e.lineno - 1 else "   "
                context.append(f"  {marker} {i+1}: {lines[i]}")
        return {
            "pass": False,
            "errors": [f"Syntax error line {e.lineno}: {e.msg}\n" + "\n".join(context)]
        }


def run_import_check(code: str) -> dict:
    """Check if code can be parsed and has required SkillBase structure."""
    parse = run_parse_check(code)
    if not parse["pass"]:
        return parse

    errors = []
    tree = ast.parse(code)

    # Check for SkillBase subclass
    has_skillbase = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                name = getattr(base, 'id', getattr(base, 'attr', ''))
                if name == 'SkillBase':
                    has_skillbase = True

    if not has_skillbase:
        errors.append("No class subclassing SkillBase found")

    # Check for async execute
    for node in ast.walk(tree):
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "execute":
            break
    else:
        errors.append("No async def execute() method found")

    return {"pass": len(errors) == 0, "errors": errors}


def run_behavioral_test(code: str, test_cases: list, results_dir: Path) -> dict:
    """Run the skill against test cases (reuses logic from ollama_builder v3)."""
    temp_dir = results_dir / "temp_skill"
    temp_dir.mkdir(exist_ok=True)
    skill_file = temp_dir / "test_skill.py"
    skill_file.write_text(code)

    # Write test cases to a JSON file (avoids true/false vs True/False issues)
    test_cases_file = temp_dir / "_test_cases.json"
    test_cases_file.write_text(json.dumps(test_cases, indent=2))

    test_script = temp_dir / "_run_tests.py"
    test_script.write_text(f'''#!/usr/bin/env python3
import sys, json, asyncio, traceback
sys.path.insert(0, '/opt/mythos/skills')
sys.path.insert(0, '{temp_dir}')
results = []
try:
    import importlib.util
    spec_obj = importlib.util.spec_from_file_location("test_skill", "{skill_file}")
    module = importlib.util.module_from_spec(spec_obj)
    spec_obj.loader.exec_module(module)
    from engine.base import SkillBase, SkillRequest
    skill_class = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, SkillBase) and attr is not SkillBase:
            skill_class = attr
            break
    if not skill_class:
        print(json.dumps({{"error": "No SkillBase subclass", "results": []}}))
        sys.exit(0)
    instance = skill_class()
    with open("{test_cases_file}") as _tc_f:
        test_cases = json.load(_tc_f)
    async def run():
        for i, tc in enumerate(test_cases):
            tr = {{"test_index": i, "message": tc["message"], "passed": [], "failed": []}}
            try:
                req = SkillRequest(message=tc["message"])
                resp = await instance.run(req)
                if "expect_ok" in tc:
                    if resp.ok == tc["expect_ok"]:
                        tr["passed"].append(f"ok={{resp.ok}}")
                    else:
                        tr["failed"].append(f"Expected ok={{tc['expect_ok']}}, got {{resp.ok}} (error: {{resp.error}})")
                for kw in tc.get("expect_summary_contains", []):
                    if kw.lower() in resp.summary.lower():
                        tr["passed"].append(f"summary has '{{kw}}'")
                    else:
                        tr["failed"].append(f"summary missing '{{kw}}': {{resp.summary[:200]}}")
                for key in tc.get("expect_data_has", []):
                    if key in resp.data:
                        tr["passed"].append(f"data has '{{key}}'")
                    else:
                        tr["failed"].append(f"data missing '{{key}}': {{list(resp.data.keys())}}")
                if resp.summary:
                    tr["passed"].append("summary non-empty")
                else:
                    tr["failed"].append("summary empty")
            except Exception as e:
                tr["failed"].append(f"Error: {{e}}")
            results.append(tr)
    asyncio.run(run())
except Exception as e:
    results = [{{"test_index": -1, "passed": [], "failed": [f"Setup error: {{e}}"]}}]
print(json.dumps({{"results": results}}))
''')

    try:
        result = subprocess.run(
            ["/opt/mythos/.venv/bin/python3", str(test_script)],
            capture_output=True, text=True, timeout=30, cwd=str(temp_dir)
        )
        if result.returncode != 0 and not result.stdout.strip():
            return {"pass": False, "errors": [f"Test runner crash: {result.stderr[:500]}"]}
        output = json.loads(result.stdout.strip())
        tests = output.get("results", [])
        all_errors = []
        total_pass = 0
        total_fail = 0
        for t in tests:
            total_pass += len(t.get("passed", []))
            total_fail += len(t.get("failed", []))
            all_errors.extend(t.get("failed", []))
        return {
            "pass": total_fail == 0,
            "errors": all_errors,
            "passed": total_pass,
            "failed": total_fail,
            "total": total_pass + total_fail,
        }
    except Exception as e:
        return {"pass": False, "errors": [str(e)]}


TEST_RUNNERS = {
    "parse_check": run_parse_check,
    "import_check": run_import_check,
}


# ── Grinder Engine ────────────────────────────────────────────────────────────

def grind(plan_path: str, model: str, max_retries: int = 5,
          verbose: bool = False, temperature: float = 0.2) -> dict:
    """Execute a full build plan step by step."""

    with open(plan_path) as f:
        plan = json.load(f)

    plan_id = plan["plan_id"]
    build_steps = plan["build_plan"]
    context = plan.get("context", {})
    test_cases = plan.get("test_cases", [])

    # Create results dir
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = RESULTS_DIR / plan_id / timestamp
    results_dir.mkdir(parents=True, exist_ok=True)

    if verbose:
        print(f"\n{'='*60}")
        print(f"GRINDER — Plan: {plan_id}")
        print(f"Model: {model}")
        print(f"Steps: {len(build_steps)}")
        print(f"Results: {results_dir}")
        print(f"{'='*60}\n")

    current_code = ""
    all_steps = []
    total_ollama_calls = 0

    for step in build_steps:
        pass_num = step["pass"]
        instruction = step["instruction"]
        test_type = step.get("test", "parse_check")
        is_recursive = step.get("recursive", False)
        max_loops = max_retries if is_recursive else 3

        if verbose:
            print(f"\n{'─'*40}")
            print(f"Pass {pass_num}: {instruction[:80]}...")
            if is_recursive:
                print(f"  (recursive — up to {max_loops} attempts)")

        step_start = time.time()
        step_result = {
            "pass": pass_num,
            "instruction": instruction,
            "test_type": test_type,
            "recursive": is_recursive,
            "attempts": [],
        }

        errors = []
        for attempt in range(1, max_loops + 1):
            if verbose:
                suffix = f" (attempt {attempt}/{max_loops})" if max_loops > 1 else ""
                print(f"  Calling {model}{suffix}...")

            prompt = build_pass_prompt(step, current_code, context, errors or None)
            raw = call_ollama(model, prompt, temperature=temperature)
            total_ollama_calls += 1

            if raw.startswith("ERROR:"):
                step_result["attempts"].append({"attempt": attempt, "error": raw})
                if verbose:
                    print(f"  ERROR: {raw}")
                continue

            code = extract_python(raw)
            (results_dir / f"pass{pass_num:02d}_attempt{attempt:02d}.py").write_text(code)

            # Run the appropriate test
            if test_type == "full_behavioral" and test_cases:
                test_result = run_behavioral_test(code, test_cases, results_dir)
            elif test_type in TEST_RUNNERS:
                test_result = TEST_RUNNERS[test_type](code)
            else:
                test_result = run_parse_check(code)

            step_result["attempts"].append({
                "attempt": attempt,
                "test_pass": test_result["pass"],
                "errors": test_result.get("errors", []),
            })

            if verbose:
                status = "PASS ✓" if test_result["pass"] else "FAIL ✗"
                print(f"  Test ({test_type}): {status}")
                for e in test_result.get("errors", [])[:3]:
                    print(f"    ✗ {e.split(chr(10))[0]}")

            if test_result["pass"]:
                current_code = code
                break
            else:
                errors = test_result.get("errors", [])
                if not is_recursive:
                    # Non-recursive steps get a few retries but don't loop endlessly
                    if attempt >= max_loops:
                        current_code = code  # Keep best attempt and move on
                        if verbose:
                            print(f"  ⚠ Moving to next pass with imperfect code")

        step_result["elapsed_seconds"] = round(time.time() - step_start, 2)
        step_result["final_code_lines"] = len(current_code.split("\n")) if current_code else 0
        all_steps.append(step_result)

    # Save final output
    if current_code:
        (results_dir / "final.py").write_text(current_code)

    # Final validation
    final_parse = run_parse_check(current_code) if current_code else {"pass": False}
    final_import = run_import_check(current_code) if final_parse.get("pass") else {"pass": False}
    final_behavioral = {}
    if final_import.get("pass") and test_cases:
        final_behavioral = run_behavioral_test(current_code, test_cases, results_dir)

    report = {
        "plan_id": plan_id,
        "model": model,
        "timestamp": timestamp,
        "total_passes": len(build_steps),
        "total_ollama_calls": total_ollama_calls,
        "final_parse": final_parse.get("pass", False),
        "final_import": final_import.get("pass", False),
        "final_behavioral": final_behavioral,
        "steps": all_steps,
    }

    report_path = results_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str))

    if verbose:
        print(f"\n{'='*60}")
        print(f"GRINDER RESULTS: {plan_id}")
        print(f"  Model: {model}")
        print(f"  Ollama calls: {total_ollama_calls}")
        print(f"  Parse: {'✓' if report['final_parse'] else '✗'}")
        print(f"  Import: {'✓' if report['final_import'] else '✗'}")
        if final_behavioral:
            bp = final_behavioral.get('passed', 0)
            bt = final_behavioral.get('total', 0)
            print(f"  Behavioral: {bp}/{bt} checks")
        print(f"  Code: {len(current_code.split(chr(10)))} lines")
        print(f"  Report: {report_path}")
        print(f"{'='*60}\n")

    return report


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Ollama Grinder — Multi-Pass Build Engine"
    )
    parser.add_argument("--plan", type=str, help="Path to build_plan.json")
    parser.add_argument("--model", type=str, default="qwen3-coder:30b")
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--verbose", "-v", action="store_true")

    args = parser.parse_args()

    if not args.plan:
        parser.error("--plan is required")

    plan_path = Path(args.plan)
    if not plan_path.exists():
        # Try relative to eval dir
        plan_path = EVAL_DIR / "challenges" / args.plan / "build_plan.json"
    if not plan_path.exists():
        print(f"Build plan not found: {args.plan}")
        sys.exit(1)

    report = grind(
        str(plan_path),
        model=args.model,
        max_retries=args.max_retries,
        verbose=args.verbose,
        temperature=args.temperature,
    )

    passed = report.get("final_parse") and report.get("final_import")
    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
