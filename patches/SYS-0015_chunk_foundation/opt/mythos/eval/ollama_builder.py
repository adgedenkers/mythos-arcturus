#!/usr/bin/env python3
"""
Ollama Chunk Builder — Recursive Eval Harness v3
==================================================

Reads a challenge spec, constructs a prompt with full system context,
calls a local Ollama model, captures its output, validates structurally,
runs behavioral tests (actually executes the skill against test cases),
diffs against gold standard, and loops with error feedback until it passes
or hits max iterations.

Scoring model:
  - Structural pass is the GATE (must pass to score above 30%)
  - If structural passes: base 70% + gold similarity bonus + behavioral bonus
  - Gold comparison is informational context, not punitive
  - A platinum solution (better than gold) is possible

Usage:
    /opt/mythos/.venv/bin/python3 /opt/mythos/eval/ollama_builder.py \
        --challenge /opt/mythos/eval/challenges/people_lookup/challenge_spec.json \
        --model qwen3-coder:30b \
        --max-iterations 5 \
        --verbose

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
from difflib import SequenceMatcher, unified_diff
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

EVAL_DIR = Path("/opt/mythos/eval")
CHALLENGES_DIR = EVAL_DIR / "challenges"
RESULTS_DIR = EVAL_DIR / "results"
SKILL_MD_PATH = EVAL_DIR / "skill_reference" / "SKILL.md"

# ── Prompt Construction ──────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are a Python developer building skills for the Mythos system on Arcturus.
You produce ONLY valid Python code. No markdown fences. No explanations before or after.
Your output must be a complete, runnable .py file that can be saved directly.

CRITICAL RULES:
- Output ONLY the Python file contents. Nothing else.
- No ```python``` markers. No preamble. No "here's the code" text.
- The file must parse as valid Python.
- The class must subclass SkillBase from engine.base.
- The execute() method must be async and return SkillResponse.
- The summary field in SkillResponse must NEVER be empty.
- Database connections must be closed in try/finally.
- The finally block MUST have a body — never write an empty finally.
- Use the exact column names from the schema provided.
"""

def build_prompt(spec: dict, skill_reference: str, errors: list = None) -> str:
    """Construct the full prompt for Ollama from challenge spec + skill reference."""
    req = spec["requirement"]
    ctx = spec["system_context"]

    # Build table schema description
    table_desc = ""
    if "table" in ctx:
        t = ctx["table"]
        cols = "\n".join(
            f"  - {c['name']} ({c['type']}, {'nullable' if c.get('nullable') else 'NOT NULL'})"
            + (f" — {c['note']}" if c.get("note") else "")
            for c in t.get("columns", [])
        )
        indexes = ", ".join(t.get("indexes", []))
        table_desc = f"""
DATABASE TABLE: {t.get('schema', 'public')}.{t['name']}
Columns:
{cols}
Indexes: {indexes}
"""

    prompt = f"""BUILD THIS MYTHOS SKILL:

{req['natural_language']}

REQUIREMENTS:
- Skill name: {req['skill_name']}
- Class name: {req['class_name']}
- Filename: {req['filename']}
- Category: {req.get('category', 'data')}
- Cache TTL: {req.get('cache_ttl', 300)} seconds
- Triggers: {json.dumps(req.get('triggers', []))}

SYSTEM CONTEXT:
- Database: {ctx.get('database', 'postgresql')} ({ctx.get('database_name', 'mythos')})
- Connection: {ctx.get('connection_pattern', 'psycopg2 with RealDictCursor')}
- Import: {ctx.get('engine_import', 'from engine.base import SkillBase, SkillRequest, SkillResponse')}
{table_desc}

SKILL REFERENCE (how to structure the code):
{skill_reference}

Output ONLY the complete Python file. No explanation. No markdown."""

    if errors:
        error_block = "\n".join(f"  - {e}" for e in errors)
        prompt += f"""

PREVIOUS ATTEMPT FAILED. Fix these errors:
{error_block}

Try again. Output ONLY the corrected Python file."""

    return prompt


# ── Ollama Integration ────────────────────────────────────────────────────────

def call_ollama(model: str, prompt: str, system: str = SYSTEM_PROMPT,
                temperature: float = 0.3, timeout: int = 300) -> str:
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
    except json.JSONDecodeError as e:
        return f"ERROR: Invalid JSON from Ollama: {e}"
    except Exception as e:
        return f"ERROR: {e}"


def extract_python(response: str) -> str:
    """Extract Python code from model response, stripping any markdown fences.

    Strategy:
    1. If fenced code blocks exist, extract the longest one (greedy).
    2. Otherwise, find Python code by looking for shebang/import/class markers.
    3. Keep ALL content from first Python line to last Python line — never
       trim indented blocks after keywords like finally/except.
    """
    code = response.strip()

    # Strategy 1: Extract from markdown fences (use GREEDY match to get full block)
    fence_greedy = r"```(?:python)?\s*\n(.+?)```"
    matches = re.findall(fence_greedy, code, re.DOTALL)
    if matches:
        # Take the longest match
        code = max(matches, key=len).strip()
        if any(marker in code for marker in
               ["import ", "class ", "def ", "from ", "#!/"]):
            return code

    # Strategy 2: Find Python code boundaries by markers
    lines = code.split("\n")

    # Find start: first line that looks like Python
    start = 0
    python_starters = ("#!", '"""', "'''", "import ", "from ", "class ",
                        "def ", "#!/usr/bin/env python", "# ", "import")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if any(stripped.startswith(s) for s in python_starters):
            start = i
            break
        if not stripped:
            continue
        if any(stripped.lower().startswith(w) for w in
               ["here", "this", "below", "the ", "i ", "sure", "certainly",
                "note", "output", "let me"]):
            continue

    # Find end: last line that is Python code (indented or code-like)
    end = len(lines)
    for i in range(len(lines) - 1, start, -1):
        stripped = lines[i].strip()
        if not stripped:
            continue
        if (not lines[i][0:1].isspace() and
            stripped[0:1].isalpha() and
            not any(stripped.startswith(k) for k in
                    ["import ", "from ", "class ", "def ", "return ",
                     "raise ", "if ", "else:", "elif ", "except",
                     "finally:", "try:", "for ", "while ", "with ",
                     "async ", "logger.", "print("])):
            continue
        end = i + 1
        break

    return "\n".join(lines[start:end]).strip()


# ── Validation ────────────────────────────────────────────────────────────────

class ValidationResult:
    def __init__(self):
        self.passed: List[str] = []
        self.failed: List[str] = []
        self.warnings: List[str] = []

    @property
    def ok(self) -> bool:
        return len(self.failed) == 0

    @property
    def score(self) -> float:
        total = len(self.passed) + len(self.failed)
        return len(self.passed) / total if total > 0 else 0.0

    def to_dict(self) -> dict:
        return {
            "ok": self.ok,
            "score": self.score,
            "passed": self.passed,
            "failed": self.failed,
            "warnings": self.warnings,
        }


def validate_structural(code: str, spec: dict) -> ValidationResult:
    """Validate the generated code structurally without executing it."""
    result = ValidationResult()
    req = spec["requirement"]
    ctx = spec.get("system_context", {})

    # 1. Parse as Python
    try:
        tree = ast.parse(code)
        result.passed.append("Valid Python syntax")
    except SyntaxError as e:
        error_msg = f"Syntax error: {e.msg} (line {e.lineno})"
        if e.lineno and code:
            lines = code.split("\n")
            start = max(0, e.lineno - 4)
            end = min(len(lines), e.lineno + 2)
            context_lines = []
            for i in range(start, end):
                marker = ">>>" if i == e.lineno - 1 else "   "
                context_lines.append(f"  {marker} {i+1}: {lines[i]}")
            error_msg += "\n    Context:\n" + "\n".join(context_lines)
        result.failed.append(error_msg)
        return result

    # 2. Find class definitions
    classes = [n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    if not classes:
        result.failed.append("No class definition found")
        return result
    result.passed.append(f"Found {len(classes)} class(es)")

    # 3. Check for SkillBase subclass
    skill_class = None
    for cls in classes:
        for base in cls.bases:
            base_name = ""
            if isinstance(base, ast.Name):
                base_name = base.id
            elif isinstance(base, ast.Attribute):
                base_name = base.attr
            if base_name == "SkillBase":
                skill_class = cls
                break
    if skill_class is None:
        result.failed.append("No class subclasses SkillBase")
        return result
    result.passed.append(f"Class '{skill_class.name}' subclasses SkillBase")

    # 4. Check class name matches spec
    expected_class = req.get("class_name", "")
    if expected_class and skill_class.name != expected_class:
        result.warnings.append(
            f"Class name mismatch: got '{skill_class.name}', expected '{expected_class}'"
        )

    # 5. Check required class attributes
    assigns = {}
    for node in ast.walk(skill_class):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    assigns[target.id] = node.value

    required_attrs = ["name", "version", "category", "description", "triggers", "cache_ttl"]
    for attr in required_attrs:
        if attr in assigns:
            result.passed.append(f"Has attribute: {attr}")
        else:
            result.failed.append(f"Missing required attribute: {attr}")

    # 6. Check for execute method
    methods = {
        n.name: n for n in ast.walk(skill_class)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    if "execute" in methods:
        exec_method = methods["execute"]
        if isinstance(exec_method, ast.AsyncFunctionDef):
            result.passed.append("Has async def execute()")
        else:
            result.failed.append("execute() must be async (use 'async def')")
    else:
        result.failed.append("Missing execute() method")

    # 7. Check imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                imports.append(f"{module}.{alias.name}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

    import_str = " ".join(imports)
    if "SkillBase" in import_str:
        result.passed.append("Imports SkillBase")
    else:
        result.failed.append("Missing import of SkillBase")

    if "SkillRequest" in import_str:
        result.passed.append("Imports SkillRequest")
    else:
        result.failed.append("Missing import of SkillRequest")

    if "SkillResponse" in import_str:
        result.passed.append("Imports SkillResponse")
    else:
        result.failed.append("Missing import of SkillResponse")

    # 8. Check for _get_conn pattern (if database skill)
    if ctx.get("database"):
        code_text = code
        if "_get_conn" in code_text or "psycopg2" in code_text:
            result.passed.append("Uses database connection pattern")
        else:
            result.warnings.append("No database connection pattern found (expected for data skill)")

    # 9. Check for error handling
    has_try = any(isinstance(n, ast.Try) for n in ast.walk(skill_class))
    if has_try:
        result.passed.append("Has try/except error handling")
    else:
        result.warnings.append("No try/except in execute() — fragile")

    # 10. Check for finally (connection cleanup)
    for node in ast.walk(skill_class):
        if isinstance(node, ast.Try) and node.finalbody:
            result.passed.append("Has finally block (connection cleanup)")
            break
    else:
        if ctx.get("database"):
            result.warnings.append("No finally block for connection cleanup")

    return result


# ── Behavioral Testing ────────────────────────────────────────────────────────

def run_behavioral_tests(code: str, spec: dict, results_dir: Path,
                         iteration: int, verbose: bool = False) -> dict:
    """Actually execute the generated skill against test cases.

    Writes the code to a temp file, imports it, instantiates the class,
    and runs execute() against each test case in the challenge spec.

    Returns a dict with pass/fail per test case and overall behavioral score.
    """
    test_cases = spec.get("expected_behavior", {}).get("test_cases", [])
    if not test_cases:
        return {"available": False, "reason": "No test cases in challenge spec"}

    # Write the code to a temp location we can import
    temp_dir = results_dir / "temp_skill"
    temp_dir.mkdir(exist_ok=True)

    skill_file = temp_dir / spec["requirement"]["filename"]
    skill_file.write_text(code)

    # Create the test runner script that runs in the Mythos venv
    test_script = temp_dir / "_run_tests.py"
    test_cases_json = json.dumps(test_cases)

    test_script.write_text(f'''#!/usr/bin/env python3
"""Auto-generated behavioral test runner."""
import sys
import json
import asyncio
import traceback

# Add skill engine to path
sys.path.insert(0, '/opt/mythos/skills')
sys.path.insert(0, '{temp_dir}')

results = []

try:
    # Import the generated skill module
    import importlib.util
    spec_obj = importlib.util.spec_from_file_location("test_skill", "{skill_file}")
    module = importlib.util.module_from_spec(spec_obj)
    spec_obj.loader.exec_module(module)

    # Find the SkillBase subclass
    from engine.base import SkillBase, SkillRequest
    skill_class = None
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if (isinstance(attr, type) and issubclass(attr, SkillBase)
                and attr is not SkillBase):
            skill_class = attr
            break

    if skill_class is None:
        print(json.dumps({{"error": "No SkillBase subclass found", "results": []}}))
        sys.exit(0)

    instance = skill_class()

    # Run test cases
    test_cases = {test_cases_json}

    async def run_tests():
        for i, tc in enumerate(test_cases):
            test_result = {{
                "test_index": i,
                "message": tc["message"],
                "passed": [],
                "failed": [],
            }}
            try:
                request = SkillRequest(message=tc["message"])
                response = await instance.run(request)

                # Check expect_ok
                if "expect_ok" in tc:
                    if response.ok == tc["expect_ok"]:
                        test_result["passed"].append(f"ok={response.ok} as expected")
                    else:
                        test_result["failed"].append(
                            f"Expected ok={tc['expect_ok']}, got ok={response.ok}"
                            + (f" (error: {{response.error}})" if response.error else "")
                        )

                # Check expect_summary_contains
                for keyword in tc.get("expect_summary_contains", []):
                    if keyword.lower() in response.summary.lower():
                        test_result["passed"].append(f"Summary contains '{{keyword}}'")
                    else:
                        test_result["failed"].append(
                            f"Summary missing '{{keyword}}'. Got: {{response.summary[:200]}}"
                        )

                # Check expect_data_has
                for key in tc.get("expect_data_has", []):
                    if key in response.data:
                        test_result["passed"].append(f"Data has key '{{key}}'")
                    else:
                        test_result["failed"].append(
                            f"Data missing key '{{key}}'. Keys: {{list(response.data.keys())}}"
                        )

                # Check summary is non-empty
                if response.summary:
                    test_result["passed"].append("Summary is non-empty")
                else:
                    test_result["failed"].append("Summary is empty")

                test_result["summary_preview"] = response.summary[:300]
                test_result["data_keys"] = list(response.data.keys())

            except Exception as e:
                test_result["failed"].append(f"Execution error: {{e}}")
                test_result["traceback"] = traceback.format_exc()

            results.append(test_result)

    asyncio.run(run_tests())

except Exception as e:
    results = [{{"test_index": -1, "error": str(e), "traceback": traceback.format_exc(),
                 "passed": [], "failed": [f"Import/setup error: {{e}}"]}}]

print(json.dumps({{"results": results}}))
''')

    # Run the test script using Mythos venv
    try:
        result = subprocess.run(
            ["/opt/mythos/.venv/bin/python3", str(test_script)],
            capture_output=True, text=True, timeout=30,
            cwd=str(temp_dir),
        )

        if result.returncode != 0 and not result.stdout.strip():
            return {
                "available": True,
                "error": f"Test runner crashed: {result.stderr[:500]}",
                "tests": [],
                "score": 0.0,
                "passed": 0,
                "failed": 1,
                "total": 1,
            }

        # Parse output
        try:
            output = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            return {
                "available": True,
                "error": f"Invalid JSON from test runner. stdout: {result.stdout[:500]}",
                "tests": [],
                "score": 0.0,
                "passed": 0,
                "failed": 1,
                "total": 1,
            }

        if "error" in output and not output.get("results"):
            return {
                "available": True,
                "error": output["error"],
                "tests": [],
                "score": 0.0,
                "passed": 0,
                "failed": 1,
                "total": 1,
            }

        # Tally results
        tests = output.get("results", [])
        total_checks = 0
        passed_checks = 0

        for t in tests:
            total_checks += len(t.get("passed", [])) + len(t.get("failed", []))
            passed_checks += len(t.get("passed", []))

        score = passed_checks / total_checks if total_checks > 0 else 0.0

        return {
            "available": True,
            "tests": tests,
            "score": round(score, 4),
            "passed": passed_checks,
            "failed": total_checks - passed_checks,
            "total": total_checks,
        }

    except subprocess.TimeoutExpired:
        return {
            "available": True,
            "error": "Behavioral tests timed out (30s)",
            "tests": [],
            "score": 0.0,
            "passed": 0,
            "failed": 1,
            "total": 1,
        }
    except Exception as e:
        return {
            "available": True,
            "error": str(e),
            "tests": [],
            "score": 0.0,
            "passed": 0,
            "failed": 1,
            "total": 1,
        }


# ── Scoring ───────────────────────────────────────────────────────────────────

def compute_composite_score(validation: 'ValidationResult',
                            gold_comparison: dict,
                            behavioral: dict) -> Tuple[float, dict]:
    """Compute the composite score with the new scoring model.

    Scoring:
      - Structural pass is the GATE.
        If structural fails → score = structural_ratio * 0.30 (capped low)
      - If structural passes:
        base = 0.70 (you built a working cell)
        + gold_similarity * 0.15 (convergence bonus, informational)
        + behavioral_score * 0.15 (test case coverage)

    Returns (score, breakdown_dict)
    """
    breakdown = {
        "structural_pass": validation.ok,
        "structural_ratio": validation.score,
    }

    if not validation.ok:
        # Gate failed — cap the score low
        score = validation.score * 0.30
        breakdown["gate"] = "FAILED"
        breakdown["score_formula"] = f"structural_ratio({validation.score:.2f}) * 0.30"
        return round(score, 4), breakdown

    # Gate passed — start at 70%
    base = 0.70
    breakdown["gate"] = "PASSED"
    breakdown["base"] = base

    # Gold similarity bonus (0–15%)
    gold_bonus = 0.0
    if gold_comparison.get("available"):
        gold_sim = gold_comparison.get("similarity", 0.0)
        gold_bonus = gold_sim * 0.15
        breakdown["gold_similarity"] = gold_sim
        breakdown["gold_bonus"] = round(gold_bonus, 4)

    # Behavioral test bonus (0–15%)
    behavioral_bonus = 0.0
    if behavioral.get("available") and not behavioral.get("error"):
        beh_score = behavioral.get("score", 0.0)
        behavioral_bonus = beh_score * 0.15
        breakdown["behavioral_score"] = beh_score
        breakdown["behavioral_bonus"] = round(behavioral_bonus, 4)
        breakdown["behavioral_passed"] = behavioral.get("passed", 0)
        breakdown["behavioral_total"] = behavioral.get("total", 0)
    elif behavioral.get("error"):
        breakdown["behavioral_error"] = behavioral["error"]

    score = base + gold_bonus + behavioral_bonus
    breakdown["score_formula"] = (
        f"base(0.70) + gold({gold_bonus:.4f}) + behavioral({behavioral_bonus:.4f})"
    )

    return round(min(score, 1.0), 4), breakdown


def compare_to_gold(generated: str, gold_path: str) -> dict:
    """Compare generated code to gold standard."""
    if not os.path.exists(gold_path):
        return {"available": False, "reason": f"Gold file not found: {gold_path}"}

    with open(gold_path) as f:
        gold = f.read()

    similarity = SequenceMatcher(None, generated, gold).ratio()

    gen_lines = generated.splitlines(keepends=True)
    gold_lines = gold.splitlines(keepends=True)
    diff = list(unified_diff(gold_lines, gen_lines,
                             fromfile="gold", tofile="generated", lineterm=""))

    structural_match = {}
    try:
        gen_tree = ast.parse(generated)
        gold_tree = ast.parse(gold)

        gen_classes = {n.name: n for n in ast.walk(gen_tree) if isinstance(n, ast.ClassDef)}
        gold_classes = {n.name: n for n in ast.walk(gold_tree) if isinstance(n, ast.ClassDef)}

        structural_match["class_names_match"] = set(gen_classes.keys()) == set(gold_classes.keys())

        for cls_name in gold_classes:
            if cls_name in gen_classes:
                gold_methods = {n.name for n in ast.walk(gold_classes[cls_name])
                                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
                gen_methods = {n.name for n in ast.walk(gen_classes[cls_name])
                               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
                structural_match["methods_match"] = gold_methods == gen_methods
                structural_match["gold_methods"] = sorted(gold_methods)
                structural_match["generated_methods"] = sorted(gen_methods)
                structural_match["missing_methods"] = sorted(gold_methods - gen_methods)
                structural_match["extra_methods"] = sorted(gen_methods - gold_methods)
    except Exception:
        structural_match["parse_error"] = True

    return {
        "available": True,
        "similarity": round(similarity, 4),
        "diff_lines": len(diff),
        "diff_preview": diff[:50],
        "structural": structural_match,
    }


# ── Orchestrator ──────────────────────────────────────────────────────────────

def run_challenge(challenge_path: str, model: str, max_iterations: int = 5,
                  verbose: bool = False, temperature: float = 0.3) -> dict:
    """Run a complete challenge evaluation loop."""

    with open(challenge_path) as f:
        spec = json.load(f)

    challenge_id = spec["challenge_id"]
    challenge_dir = Path(challenge_path).parent

    # Load skill reference
    skill_ref = ""
    if SKILL_MD_PATH.exists():
        skill_ref = SKILL_MD_PATH.read_text()
    else:
        skill_ref = "Follow the system_context and requirement sections exactly."

    # Resolve gold path
    gold_path = None
    if spec.get("gold_path"):
        gold_path = str(challenge_dir.parent.parent / spec["gold_path"])
        if not os.path.exists(gold_path):
            gold_path = str(challenge_dir / spec["gold_path"])

    # Create results directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = RESULTS_DIR / challenge_id / timestamp
    results_dir.mkdir(parents=True, exist_ok=True)

    has_test_cases = bool(spec.get("expected_behavior", {}).get("test_cases"))

    if verbose:
        print(f"\n{'='*60}")
        print(f"CHUNK FACTORY v3 — Challenge: {challenge_id}")
        print(f"Model: {model}")
        print(f"Max iterations: {max_iterations}")
        print(f"Behavioral tests: {'YES' if has_test_cases else 'NO'}")
        print(f"Results: {results_dir}")
        print(f"{'='*60}\n")

    # Iteration loop
    all_iterations = []
    errors_to_feed_back = []
    best_score = 0.0
    best_code = ""
    best_iteration = 0

    for iteration in range(1, max_iterations + 1):
        if verbose:
            print(f"\n--- Iteration {iteration}/{max_iterations} ---")

        iter_start = time.time()

        # Build prompt
        prompt = build_prompt(spec, skill_ref, errors=errors_to_feed_back or None)

        # Call Ollama
        if verbose:
            print(f"  Calling {model}...")
        raw_response = call_ollama(model, prompt, temperature=temperature)

        if raw_response.startswith("ERROR:"):
            iter_result = {
                "iteration": iteration,
                "error": raw_response,
                "elapsed_seconds": round(time.time() - iter_start, 2),
            }
            all_iterations.append(iter_result)
            if verbose:
                print(f"  ERROR: {raw_response}")
            continue

        # Extract Python
        code = extract_python(raw_response)

        # Save raw response and extracted code
        (results_dir / f"iter{iteration:02d}_raw.txt").write_text(raw_response)
        (results_dir / f"iter{iteration:02d}_code.py").write_text(code)

        # Structural validation
        if verbose:
            print("  Validating structure...")
        validation = validate_structural(code, spec)

        # Gold comparison
        gold_comparison = {}
        if gold_path:
            gold_comparison = compare_to_gold(code, gold_path)

        # Behavioral tests (only if structural passes — no point running broken code)
        behavioral = {"available": False, "reason": "Structural validation failed"}
        if validation.ok and has_test_cases:
            if verbose:
                print("  Running behavioral tests...")
            behavioral = run_behavioral_tests(
                code, spec, results_dir, iteration, verbose
            )

        # Compute composite score
        composite, score_breakdown = compute_composite_score(
            validation, gold_comparison, behavioral
        )

        # Track best
        if composite > best_score:
            best_score = composite
            best_code = code
            best_iteration = iteration

        elapsed = round(time.time() - iter_start, 2)

        iter_result = {
            "iteration": iteration,
            "elapsed_seconds": elapsed,
            "validation": validation.to_dict(),
            "gold_comparison": gold_comparison,
            "behavioral": behavioral if behavioral.get("available") else {"available": False},
            "composite_score": composite,
            "score_breakdown": score_breakdown,
        }
        all_iterations.append(iter_result)

        if verbose:
            gate = "PASS ✓" if validation.ok else "FAIL ✗"
            print(f"  Structural: {gate} "
                  f"({len(validation.passed)} passed, {len(validation.failed)} failed)")
            if gold_comparison.get("available"):
                print(f"  Gold similarity: {gold_comparison['similarity']:.1%}")
            if behavioral.get("available") and not behavioral.get("error"):
                beh = behavioral
                print(f"  Behavioral: {beh['passed']}/{beh['total']} checks passed "
                      f"({beh['score']:.0%})")
            elif behavioral.get("error"):
                print(f"  Behavioral: ERROR — {behavioral['error'][:80]}")
            print(f"  Composite: {composite:.1%} "
                  f"[{score_breakdown.get('score_formula', '')}]")
            if validation.failed:
                for f in validation.failed:
                    first_line = f.split("\n")[0]
                    print(f"    ✗ {first_line}")
            if validation.warnings:
                for w in validation.warnings:
                    print(f"    ⚠ {w}")

        # Check if we passed — structural must pass + composite >= 0.80
        if validation.ok and composite >= 0.80:
            if verbose:
                print(f"\n  ✓ PASSED on iteration {iteration}!")
            break

        # Feed errors back for next iteration
        errors_to_feed_back = validation.failed.copy()
        if validation.warnings:
            errors_to_feed_back.extend([f"Warning: {w}" for w in validation.warnings])
        if gold_comparison.get("structural", {}).get("missing_methods"):
            errors_to_feed_back.append(
                f"Missing methods from gold standard: "
                f"{', '.join(gold_comparison['structural']['missing_methods'])}"
            )
        # Add behavioral failures as feedback too
        if behavioral.get("available") and not behavioral.get("error"):
            for t in behavioral.get("tests", []):
                for fail_msg in t.get("failed", []):
                    errors_to_feed_back.append(f"Behavioral test failed: {fail_msg}")

    # Save best output
    if best_code:
        (results_dir / "best.py").write_text(best_code)

    # Determine final pass
    final_pass = False
    if all_iterations:
        last = all_iterations[-1]
        final_pass = (last.get("validation", {}).get("ok", False)
                      and last.get("composite_score", 0) >= 0.80)

    # Build final report
    report = {
        "challenge_id": challenge_id,
        "model": model,
        "timestamp": timestamp,
        "max_iterations": max_iterations,
        "iterations_used": len(all_iterations),
        "best_iteration": best_iteration,
        "best_composite_score": round(best_score, 4),
        "final_pass": final_pass,
        "iterations": all_iterations,
    }

    report_path = results_dir / "report.json"
    report_path.write_text(json.dumps(report, indent=2, default=str))

    if verbose:
        print(f"\n{'='*60}")
        print(f"RESULTS: {challenge_id}")
        print(f"  Model: {model}")
        print(f"  Iterations: {len(all_iterations)}/{max_iterations}")
        print(f"  Best score: {best_score:.1%} (iteration {best_iteration})")
        print(f"  Final pass: {'YES ✓' if report['final_pass'] else 'NO ✗'}")
        print(f"  Report: {report_path}")
        print(f"{'='*60}\n")

    return report


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Ollama Chunk Builder — Recursive Eval Harness v3",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          %(prog)s --challenge challenges/people_lookup/challenge_spec.json --model qwen3-coder:30b
          %(prog)s --challenge challenges/people_lookup/challenge_spec.json --model llama3.3:70b --max-iterations 10
          %(prog)s --list-challenges
          %(prog)s --list-models
        """)
    )
    parser.add_argument("--challenge", type=str, help="Path to challenge_spec.json")
    parser.add_argument("--model", type=str, default="qwen3-coder:30b",
                        help="Ollama model to use (default: qwen3-coder:30b)")
    parser.add_argument("--max-iterations", type=int, default=5,
                        help="Maximum retry iterations (default: 5)")
    parser.add_argument("--temperature", type=float, default=0.3,
                        help="Model temperature (default: 0.3)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    parser.add_argument("--list-challenges", action="store_true",
                        help="List available challenges")
    parser.add_argument("--list-models", action="store_true",
                        help="List available Ollama models")

    args = parser.parse_args()

    if args.list_challenges:
        print("\nAvailable challenges:")
        for spec_file in sorted(CHALLENGES_DIR.rglob("challenge_spec.json")):
            with open(spec_file) as f:
                spec = json.load(f)
            print(f"  {spec['challenge_id']}: {spec['description']}")
            print(f"    Difficulty: {spec.get('difficulty', 'unknown')}")
            print(f"    Path: {spec_file}")
        return

    if args.list_models:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        print(result.stdout)
        return

    if not args.challenge:
        parser.error("--challenge is required (or use --list-challenges)")

    challenge_path = Path(args.challenge)
    if not challenge_path.is_absolute():
        challenge_path = CHALLENGES_DIR / challenge_path
    if not challenge_path.exists():
        print(f"Challenge not found: {challenge_path}")
        sys.exit(1)

    report = run_challenge(
        str(challenge_path),
        model=args.model,
        max_iterations=args.max_iterations,
        verbose=args.verbose,
        temperature=args.temperature,
    )

    sys.exit(0 if report.get("final_pass") else 1)


if __name__ == "__main__":
    main()
