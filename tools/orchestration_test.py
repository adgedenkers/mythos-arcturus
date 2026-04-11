#!/usr/bin/env python3
"""
Iris Orchestration Test Harness v1.0
====================================
Tests the core thesis: a conversational model designing + a code model building
produces better results than either model alone.

Three rounds:
  Round 1 — RAW: Give the bare spec to each model, no constitution, no guidance.
  Round 2 — CONSTITUTED: Same spec but with the codegen constitution prepended.
  Round 3 — ORCHESTRATED: Conversational model designs, then hands spec to code model.

The test task: Build a Spiral Time Calculator (Python CLI tool).
Complex enough to expose differences, domain-specific enough to test context handling.

Each output is saved, syntax-checked, and scored on:
  - Does it parse? (no syntax errors)
  - Does it run? (basic execution test)
  - Does the math work? (epoch calculation correctness)
  - Is it complete? (all 6 requirements met)
  - Is it well-structured? (module design, argparse, docstrings)
  - Would it integrate? (importable, not just a script)

Usage:
    # Full test — all 3 rounds
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/orchestration_test.py

    # Specific round only
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/orchestration_test.py --round 1
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/orchestration_test.py --round 3

    # Specific models
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/orchestration_test.py --convo qwen3:14b --code qwen3-coder:30b

    # Quick mode — only round 1 + 3 comparison
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/orchestration_test.py --quick

    # Show the orchestration conversation (round 3 design phase)
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/orchestration_test.py --round 3 --verbose
"""
import os
import sys
import ast
import time
import json
import shutil
import argparse
import subprocess
import tempfile
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple, Optional
from pathlib import Path

# ── Mythos imports ───────────────────────────────────────────────────────────
sys.path.insert(0, "/opt/mythos/core")
sys.path.insert(0, "/opt/mythos")

from dotenv import load_dotenv
load_dotenv('/opt/mythos/.env')

from ollama import Client

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
client = Client(host=OLLAMA_HOST)

# ── Output paths ─────────────────────────────────────────────────────────────
OUTPUT_DIR = Path(os.path.expanduser("~/orchestration_test"))
RESULTS_PATH = OUTPUT_DIR / "results.txt"
JSON_PATH = OUTPUT_DIR / "results.json"
CODE_DIR = OUTPUT_DIR / "code"

# ── Default models ───────────────────────────────────────────────────────────
# Conversational models — good at reasoning, design, review
CONVO_MODELS = ['iris-thinking-v2:latest', 'qwen3:14b', 'gemma3:27b']

# Code models — good at generating correct implementations
CODE_MODELS = ['qwen3-coder:30b', 'qwen2.5:32b']

# All models get tested in round 1 (raw)
ALL_MODELS = CONVO_MODELS + CODE_MODELS

# Models to skip entirely
SKIP_MODELS = {'llava:13b', 'codellama:70b', 'sqlcoder:15b', 'medllama2:latest'}

# ═══════════════════════════════════════════════════════════════════════════════
# THE TEST TASK
# ═══════════════════════════════════════════════════════════════════════════════

TASK_SPEC = """
Spiral Time Calculator
======================
Build a Python CLI tool that converts between Gregorian dates and Spiral Time.

Spiral Time uses 9-day cycles instead of 7-day weeks.
Epoch: October 19, 2025 = Spiral Day 1, Cycle 1.
Days within a cycle are numbered 1 through 9.
Cycle 1 is days 1-9 (Oct 19-27, 2025). Cycle 2 is days 10-18 (Oct 28 - Nov 5, 2025). Etc.

Requirements:
1. Given a Gregorian date, output the Spiral Day (1-9), Cycle number,
   and total days since epoch.
2. Given a Spiral Cycle and Day, output the Gregorian date.
3. Display a 9-day "week" view centered on today, showing both
   Gregorian and Spiral dates.
4. Store named markers (e.g., "Fitz birthday", "VA payday") in a
   JSON file and display them in the week view when they fall on a visible day.
5. All output formatted with box-drawing characters (clean terminal UI).
6. Must work as both CLI (argparse) and importable module.

Constraints:
- Python only, no external dependencies beyond stdlib
- Must handle dates before the epoch (negative cycles)
- JSON marker file at ~/.spiral_markers.json
- Include docstrings and type hints on all public functions

Output the complete Python file. Nothing else — no explanation, no markdown
fences, just the raw Python code.
""".strip()

# ── Constitution for Round 2 ────────────────────────────────────────────────

CODEGEN_CONSTITUTION = """
BUILD CONSTITUTION — Mandatory Principles
==========================================
You are generating code for the Mythos system on Arcturus.

PRINCIPLES:
- Design for change. Config-driven over hardcoded.
- Loose coupling. New features are new files, not modifications.
- Every function has a docstring and type hints.
- Use logging, not print statements.

CONSTRAINTS:
- Python only. Use stdlib where possible.
- Always use: if __name__ == '__main__'
- Always include argparse for CLI tools.
- Module must be importable (no side effects at import time).

PATTERNS:
- Constants at top of file, after imports.
- Helper functions before main logic.
- CLI entry point at bottom.
- Use pathlib.Path, not os.path.join.

INTEGRATION:
- Default: fully integrated. Code should be importable by other modules.
- Functions should be usable independently of CLI.
- Use return values, not just print output.

QUALITY:
- All public functions have docstrings with Args/Returns.
- Type hints on all function signatures.
- Handle edge cases (empty input, missing files, invalid dates).
- Graceful error handling with informative messages.
""".strip()

# ── Design prompt for Round 3 (orchestrated) ────────────────────────────────

DESIGN_PROMPT = """
You are a senior software architect. Your job is to design a tool, then produce
a detailed technical specification that a code-generation model can implement.

Do NOT write code. Write a SPECIFICATION that includes:

1. MODULE STRUCTURE: What the file looks like at a high level — imports, constants,
   classes/functions, CLI entry point.

2. FUNCTION SIGNATURES: Every public function with its exact signature, docstring,
   and return type. Be precise — the code model will implement these exactly.

3. DATA STRUCTURES: Any dataclasses, TypedDicts, or dict schemas used.

4. ALGORITHM DETAILS: For any non-trivial logic (like the date math), write out
   the exact algorithm step by step. Include example calculations.

5. EDGE CASES: List every edge case and how to handle it.

6. CLI INTERFACE: Exact argparse setup — subcommands, arguments, help text.

7. OUTPUT FORMAT: Exact box-drawing character layouts with examples.

Here is the task to design:

{task_spec}

Produce the specification now. Be precise and complete — the code model will
implement ONLY what you specify.
""".strip()

CODEGEN_FROM_SPEC_PROMPT = """
{constitution}

You are implementing a tool from a detailed specification. Follow the spec EXACTLY.
Do not add features not in the spec. Do not skip features that are in the spec.

Output ONLY the complete Python file. No explanation, no markdown, just raw Python.

SPECIFICATION:
{spec}
""".strip()

REVIEW_PROMPT = """
You are reviewing code that was generated from a specification.
Check it against the original requirements and the spec.

REQUIREMENTS:
{task_spec}

SPECIFICATION THE CODE WAS BUILT FROM:
{spec}

CODE TO REVIEW:
```python
{code}
```

Evaluate:
1. Does it implement all 6 requirements?
2. Does the Spiral Time math look correct? (Epoch: Oct 19, 2025 = Day 1, Cycle 1)
3. Are there any bugs or edge case failures?
4. Is it importable as a module (no side effects at import)?
5. Does it use argparse correctly?

If there are issues, list them as a numbered list of specific fixes needed.
If it looks correct, say "APPROVED" and nothing else.
""".strip()

REVISION_PROMPT = """
{constitution}

The following code was reviewed and needs fixes. Apply ONLY the listed fixes.
Do not change anything else. Output the complete corrected Python file only.

FIXES NEEDED:
{review_notes}

ORIGINAL CODE:
```python
{code}
```

Output ONLY the corrected Python file. No explanation, no markdown.
""".strip()


# ═══════════════════════════════════════════════════════════════════════════════
# CODE QUALITY SCORING
# ═══════════════════════════════════════════════════════════════════════════════

def extract_python(raw_response: str) -> str:
    """Extract Python code from a model response, stripping markdown fences."""
    text = raw_response.strip()

    # Strip markdown code fences if present
    if text.startswith("```python"):
        text = text[len("```python"):].strip()
    elif text.startswith("```"):
        text = text[3:].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    # Strip any leading prose before the first import or comment
    lines = text.split('\n')
    code_start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (stripped.startswith('#') or stripped.startswith('import ') or
            stripped.startswith('from ') or stripped.startswith('"""') or
            stripped.startswith("'''") or stripped == ''):
            code_start = i
            break

    return '\n'.join(lines[code_start:])


def score_code(code: str, label: str) -> Dict:
    """Score generated code on multiple quality dimensions."""
    scores = {
        'label': label,
        'char_count': len(code),
        'line_count': len(code.strip().split('\n')),
        'parses': False,
        'runs': False,
        'math_correct': False,
        'has_argparse': False,
        'has_docstrings': False,
        'has_type_hints': False,
        'has_box_drawing': False,
        'has_json_markers': False,
        'has_negative_cycles': False,
        'is_importable': False,
        'has_main_guard': False,
        'requirements_met': 0,
        'total_requirements': 6,
        'issues': [],
        'total_score': 0,
    }

    if not code.strip():
        scores['issues'].append('EMPTY OUTPUT')
        return scores

    # ── 1. Does it parse? ──
    try:
        tree = ast.parse(code)
        scores['parses'] = True
    except SyntaxError as e:
        scores['issues'].append(f'SYNTAX ERROR: {e}')
        return scores  # Can't check anything else

    # ── 2. Static analysis ──
    code_lower = code.lower()

    # Argparse
    scores['has_argparse'] = 'argparse' in code or 'ArgumentParser' in code
    if not scores['has_argparse']:
        scores['issues'].append('MISSING: argparse CLI')

    # Docstrings
    docstring_count = code.count('"""') + code.count("'''")
    scores['has_docstrings'] = docstring_count >= 4  # At least a few functions documented
    if not scores['has_docstrings']:
        scores['issues'].append(f'WEAK: only {docstring_count // 2} docstrings')

    # Type hints (look for -> and : type patterns in function defs)
    func_defs = [line for line in code.split('\n') if line.strip().startswith('def ')]
    typed_funcs = [f for f in func_defs if '->' in f]
    scores['has_type_hints'] = len(typed_funcs) >= len(func_defs) * 0.5
    if not scores['has_type_hints']:
        scores['issues'].append(f'WEAK: {len(typed_funcs)}/{len(func_defs)} functions have return type hints')

    # Box drawing
    box_chars = ['─', '│', '┌', '┐', '└', '┘', '├', '┤', '┬', '┴', '┼', '═', '║']
    scores['has_box_drawing'] = any(c in code for c in box_chars)
    if not scores['has_box_drawing']:
        scores['issues'].append('MISSING: box-drawing characters')

    # JSON markers
    scores['has_json_markers'] = 'spiral_markers' in code_lower or 'markers' in code_lower
    if not scores['has_json_markers']:
        scores['issues'].append('MISSING: JSON marker support')

    # Negative cycles
    scores['has_negative_cycles'] = 'negative' in code_lower or '< 0' in code or '<= 0' in code or 'before' in code_lower
    if not scores['has_negative_cycles']:
        scores['issues'].append('UNCLEAR: negative cycle handling')

    # Main guard
    scores['has_main_guard'] = "if __name__" in code
    if not scores['has_main_guard']:
        scores['issues'].append('MISSING: if __name__ == "__main__" guard')

    # ── 3. Execution test ──
    scores['runs'], scores['is_importable'], run_issues = test_execution(code)
    scores['issues'].extend(run_issues)

    # ── 4. Math correctness ──
    scores['math_correct'], math_issues = test_math(code)
    scores['issues'].extend(math_issues)

    # ── 5. Requirements tally ──
    req_met = 0
    # R1: Gregorian → Spiral conversion
    if any(keyword in code_lower for keyword in ['to_spiral', 'from_gregorian', 'gregorian_to', 'get_spiral']):
        req_met += 1
    elif 'def ' in code and ('spiral_day' in code_lower or 'cycle' in code_lower):
        req_met += 1

    # R2: Spiral → Gregorian conversion
    if any(keyword in code_lower for keyword in ['to_gregorian', 'from_spiral', 'spiral_to', 'get_gregorian']):
        req_met += 1

    # R3: Week view
    if 'week' in code_lower or 'view' in code_lower or 'display' in code_lower or 'calendar' in code_lower:
        req_met += 1

    # R4: Markers
    if scores['has_json_markers']:
        req_met += 1

    # R5: Box drawing
    if scores['has_box_drawing']:
        req_met += 1

    # R6: CLI + importable
    if scores['has_argparse'] and scores['has_main_guard']:
        req_met += 1

    scores['requirements_met'] = req_met

    # ── Total score (out of 100) ──
    total = 0
    if scores['parses']:       total += 10
    if scores['runs']:         total += 15
    if scores['is_importable']:total += 10
    if scores['math_correct']: total += 20
    total += (scores['requirements_met'] / 6) * 25  # 25 points for requirements
    if scores['has_docstrings']:   total += 5
    if scores['has_type_hints']:   total += 5
    if scores['has_main_guard']:   total += 5
    if scores['has_box_drawing']:  total += 5
    scores['total_score'] = round(total)

    return scores


def test_execution(code: str) -> Tuple[bool, bool, List[str]]:
    """Test if code runs and is importable. Returns (runs, importable, issues)."""
    issues = []

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "spiral_time.py"
        filepath.write_text(code)

        # Test 1: Syntax check via py_compile
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'py_compile', str(filepath)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode != 0:
                issues.append(f'COMPILE FAIL: {result.stderr[:200]}')
                return False, False, issues
        except subprocess.TimeoutExpired:
            issues.append('COMPILE TIMEOUT')
            return False, False, issues

        # Test 2: Import test (should not produce output or errors)
        import_test = f"""
import sys
sys.path.insert(0, '{tmpdir}')
try:
    import spiral_time
    print("IMPORT_OK")
except Exception as e:
    print(f"IMPORT_FAIL: {{e}}")
"""
        try:
            result = subprocess.run(
                [sys.executable, '-c', import_test],
                capture_output=True, text=True, timeout=15,
                env={**os.environ, 'HOME': tmpdir}  # Prevent marker file issues
            )
            importable = 'IMPORT_OK' in result.stdout
            if not importable:
                err = result.stderr[:200] or result.stdout[:200]
                issues.append(f'IMPORT FAIL: {err}')
        except subprocess.TimeoutExpired:
            importable = False
            issues.append('IMPORT TIMEOUT')

        # Test 3: Run with --help (should not crash)
        runs = False
        try:
            result = subprocess.run(
                [sys.executable, str(filepath), '--help'],
                capture_output=True, text=True, timeout=15,
                env={**os.environ, 'HOME': tmpdir}
            )
            runs = result.returncode == 0
            if not runs:
                # Some scripts don't have --help but might run with no args
                result2 = subprocess.run(
                    [sys.executable, str(filepath)],
                    capture_output=True, text=True, timeout=15,
                    input='',
                    env={**os.environ, 'HOME': tmpdir}
                )
                runs = result2.returncode == 0
                if not runs:
                    issues.append(f'RUN FAIL: exit {result2.returncode}, {result2.stderr[:200]}')
        except subprocess.TimeoutExpired:
            issues.append('RUN TIMEOUT')

    return runs, importable, issues


def test_math(code: str) -> Tuple[bool, List[str]]:
    """Test Spiral Time math correctness."""
    issues = []

    # Known correct values:
    # Oct 19, 2025 = Day 1, Cycle 1, total_days = 1
    # Oct 27, 2025 = Day 9, Cycle 1, total_days = 9
    # Oct 28, 2025 = Day 1, Cycle 2, total_days = 10
    # Feb 26, 2026 = 131 days after epoch:
    #   131 = 14 complete cycles (126 days) + 5 days into cycle 15
    #   So: Day 5, Cycle 15

    test_code = """
import sys
import os
from datetime import date
tmpdir = sys.argv[1]
sys.path.insert(0, tmpdir)
os.environ['HOME'] = tmpdir

try:
    import spiral_time

    # Find the conversion function — try common names
    to_spiral = None
    for name in ['gregorian_to_spiral', 'to_spiral', 'from_gregorian',
                  'get_spiral_date', 'convert_to_spiral', 'date_to_spiral']:
        if hasattr(spiral_time, name):
            to_spiral = getattr(spiral_time, name)
            break

    # Also check for a class
    if to_spiral is None:
        for attr_name in dir(spiral_time):
            attr = getattr(spiral_time, attr_name)
            if isinstance(attr, type):
                for method_name in ['from_gregorian', 'from_date', 'convert']:
                    if hasattr(attr, method_name):
                        to_spiral = lambda d: getattr(attr, method_name)(d)
                        break

    if to_spiral is None:
        print("NO_CONVERSION_FUNC")
        sys.exit(0)

    # Test epoch date
    result = to_spiral(date(2025, 10, 19))

    # Result might be a tuple, dict, dataclass, or object
    if isinstance(result, tuple):
        if len(result) >= 2:
            day, cycle = result[0], result[1]
        else:
            print(f"UNEXPECTED_TUPLE: {result}")
            sys.exit(0)
    elif isinstance(result, dict):
        day = result.get('day', result.get('spiral_day', None))
        cycle = result.get('cycle', result.get('cycle_number', None))
    elif hasattr(result, 'day') and hasattr(result, 'cycle'):
        day = result.day
        cycle = result.cycle
    elif hasattr(result, 'spiral_day') and hasattr(result, 'cycle_number'):
        day = result.spiral_day
        cycle = result.cycle_number
    else:
        print(f"UNKNOWN_RESULT_TYPE: {type(result)} = {result}")
        sys.exit(0)

    # Check epoch: should be Day 1, Cycle 1
    if int(day) == 1 and int(cycle) == 1:
        print("EPOCH_CORRECT")
    else:
        print(f"EPOCH_WRONG: day={day} cycle={cycle} (expected day=1 cycle=1)")

    # Check Oct 28, 2025 = Day 1, Cycle 2
    result2 = to_spiral(date(2025, 10, 28))
    if isinstance(result2, tuple):
        day2, cycle2 = result2[0], result2[1]
    elif isinstance(result2, dict):
        day2 = result2.get('day', result2.get('spiral_day'))
        cycle2 = result2.get('cycle', result2.get('cycle_number'))
    elif hasattr(result2, 'day'):
        day2, cycle2 = result2.day, result2.cycle
    else:
        day2, cycle2 = None, None

    if day2 is not None and int(day2) == 1 and int(cycle2) == 2:
        print("CYCLE2_CORRECT")
    else:
        print(f"CYCLE2_WRONG: day={day2} cycle={cycle2} (expected day=1 cycle=2)")

except Exception as e:
    print(f"MATH_ERROR: {e}")
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        filepath = Path(tmpdir) / "spiral_time.py"
        filepath.write_text(code)

        try:
            result = subprocess.run(
                [sys.executable, '-c', test_code, tmpdir],
                capture_output=True, text=True, timeout=15,
                env={**os.environ, 'HOME': tmpdir}
            )
            output = result.stdout.strip()

            if 'NO_CONVERSION_FUNC' in output:
                issues.append('MATH: Could not find conversion function')
                return False, issues
            if 'UNKNOWN_RESULT_TYPE' in output:
                issues.append(f'MATH: {output}')
                return False, issues
            if 'MATH_ERROR' in output:
                issues.append(f'MATH: {output}')
                return False, issues

            epoch_ok = 'EPOCH_CORRECT' in output
            cycle2_ok = 'CYCLE2_CORRECT' in output

            if not epoch_ok:
                line = [l for l in output.split('\n') if 'EPOCH' in l]
                issues.append(f'MATH: {line[0] if line else "epoch check failed"}')
            if not cycle2_ok:
                line = [l for l in output.split('\n') if 'CYCLE2' in l]
                issues.append(f'MATH: {line[0] if line else "cycle 2 check failed"}')

            return epoch_ok and cycle2_ok, issues

        except subprocess.TimeoutExpired:
            issues.append('MATH: test timed out')
            return False, issues
        except Exception as e:
            issues.append(f'MATH: test error: {e}')
            return False, issues


# ═══════════════════════════════════════════════════════════════════════════════
# MODEL INTERACTION
# ═══════════════════════════════════════════════════════════════════════════════

def call_model(
    model: str,
    system_prompt: str,
    user_message: str,
    temperature: float = 0.3,
    num_predict: int = 8192,
    timeout: int = 300,
) -> Tuple[str, float]:
    """Call a model and return (response_text, elapsed_seconds)."""
    msgs = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': user_message},
    ]

    start = time.time()
    response = client.chat(
        model=model,
        messages=msgs,
        options={
            'temperature': temperature,
            'num_predict': num_predict,
        }
    )
    elapsed = time.time() - start

    return response['message']['content'], elapsed


def call_model_multiturn(
    model: str,
    messages: List[Dict],
    temperature: float = 0.3,
    num_predict: int = 8192,
) -> Tuple[str, float]:
    """Call a model with full message history. Returns (response, elapsed)."""
    start = time.time()
    response = client.chat(
        model=model,
        messages=messages,
        options={
            'temperature': temperature,
            'num_predict': num_predict,
        }
    )
    elapsed = time.time() - start
    return response['message']['content'], elapsed


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND 1: RAW — No constitution, no guidance
# ═══════════════════════════════════════════════════════════════════════════════

def run_round1(models: List[str], output: List[str], results: Dict, verbose: bool = False):
    """Round 1: Give bare spec to each model."""
    output.append("\n" + "=" * 90)
    output.append("ROUND 1: RAW — Bare spec, no constitution")
    output.append("=" * 90)

    system_prompt = "You are a Python developer. Output only code, no explanation."

    round_results = {}

    for model in models:
        print(f"\n  Round 1 — {model}...")
        output.append(f"\n{'─' * 90}")
        output.append(f"  Model: {model}")

        text, elapsed = call_model(model, system_prompt, TASK_SPEC)
        code = extract_python(text)

        # Save code
        safe_name = model.replace(':', '_').replace('/', '_')
        code_path = CODE_DIR / f"round1_{safe_name}.py"
        code_path.write_text(code)

        # Score
        sc = score_code(code, f"R1:{model}")
        sc['elapsed'] = round(elapsed, 1)
        sc['model'] = model
        sc['raw_length'] = len(text)

        round_results[model] = sc

        # Output
        output.append(f"  Time: {elapsed:.1f}s | Lines: {sc['line_count']} | Score: {sc['total_score']}/100")
        output.append(f"  Parses: {sc['parses']} | Runs: {sc['runs']} | Math: {sc['math_correct']} | Importable: {sc['is_importable']}")
        output.append(f"  Requirements: {sc['requirements_met']}/6 | Argparse: {sc['has_argparse']} | Box-draw: {sc['has_box_drawing']}")
        if sc['issues']:
            output.append(f"  Issues: {' | '.join(sc['issues'][:5])}")
        output.append(f"  Code saved: {code_path}")

        print(f"    → Score: {sc['total_score']}/100 | {sc['requirements_met']}/6 reqs | {elapsed:.1f}s")

    results['round1'] = round_results


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND 2: CONSTITUTED — With codegen constitution
# ═══════════════════════════════════════════════════════════════════════════════

def run_round2(models: List[str], output: List[str], results: Dict, verbose: bool = False):
    """Round 2: Same spec, with constitution prepended."""
    output.append("\n" + "=" * 90)
    output.append("ROUND 2: CONSTITUTED — With codegen constitution")
    output.append("=" * 90)

    system_prompt = f"{CODEGEN_CONSTITUTION}\n\nYou are a Python developer. Output only code, no explanation."

    round_results = {}

    for model in models:
        print(f"\n  Round 2 — {model}...")
        output.append(f"\n{'─' * 90}")
        output.append(f"  Model: {model}")

        text, elapsed = call_model(model, system_prompt, TASK_SPEC)
        code = extract_python(text)

        safe_name = model.replace(':', '_').replace('/', '_')
        code_path = CODE_DIR / f"round2_{safe_name}.py"
        code_path.write_text(code)

        sc = score_code(code, f"R2:{model}")
        sc['elapsed'] = round(elapsed, 1)
        sc['model'] = model
        sc['raw_length'] = len(text)

        round_results[model] = sc

        output.append(f"  Time: {elapsed:.1f}s | Lines: {sc['line_count']} | Score: {sc['total_score']}/100")
        output.append(f"  Parses: {sc['parses']} | Runs: {sc['runs']} | Math: {sc['math_correct']} | Importable: {sc['is_importable']}")
        output.append(f"  Requirements: {sc['requirements_met']}/6 | Argparse: {sc['has_argparse']} | Box-draw: {sc['has_box_drawing']}")
        if sc['issues']:
            output.append(f"  Issues: {' | '.join(sc['issues'][:5])}")
        output.append(f"  Code saved: {code_path}")

        print(f"    → Score: {sc['total_score']}/100 | {sc['requirements_met']}/6 reqs | {elapsed:.1f}s")

    results['round2'] = round_results


# ═══════════════════════════════════════════════════════════════════════════════
# ROUND 3: ORCHESTRATED — Convo model designs, code model builds, convo reviews
# ═══════════════════════════════════════════════════════════════════════════════

def run_round3(
    convo_models: List[str],
    code_models: List[str],
    output: List[str],
    results: Dict,
    verbose: bool = False,
    max_revisions: int = 2,
):
    """Round 3: Conversational model designs, code model builds, convo model reviews."""
    output.append("\n" + "=" * 90)
    output.append("ROUND 3: ORCHESTRATED — Design → Build → Review")
    output.append("=" * 90)

    round_results = {}

    for convo_model in convo_models:
        # ── Step 1: Design phase ──
        print(f"\n  Round 3 — Design: {convo_model}...")
        output.append(f"\n{'─' * 90}")
        output.append(f"  Architect: {convo_model}")

        design_system = "You are a senior software architect. Be precise and thorough."
        design_message = DESIGN_PROMPT.format(task_spec=TASK_SPEC)

        spec_text, design_elapsed = call_model(
            convo_model, design_system, design_message,
            temperature=0.4, num_predict=8192
        )

        # Save spec
        safe_convo = convo_model.replace(':', '_').replace('/', '_')
        spec_path = CODE_DIR / f"round3_spec_{safe_convo}.md"
        spec_path.write_text(spec_text)

        output.append(f"  Design time: {design_elapsed:.1f}s | Spec length: {len(spec_text)} chars")
        if verbose:
            output.append(f"  Spec preview: {spec_text[:500]}...")

        print(f"    → Spec: {len(spec_text)} chars in {design_elapsed:.1f}s")

        # ── Step 2: Build phase (each code model implements the spec) ──
        for code_model in code_models:
            combo_key = f"{convo_model}→{code_model}"
            print(f"  Round 3 — Build: {code_model} (spec from {convo_model})...")
            output.append(f"\n  Builder: {code_model} (spec from {convo_model})")

            build_message = CODEGEN_FROM_SPEC_PROMPT.format(
                constitution=CODEGEN_CONSTITUTION,
                spec=spec_text,
            )

            code_text, build_elapsed = call_model(
                code_model, "Output only Python code. No explanation.", build_message,
                temperature=0.2, num_predict=8192
            )
            code = extract_python(code_text)

            safe_code = code_model.replace(':', '_').replace('/', '_')
            code_path = CODE_DIR / f"round3_{safe_convo}_x_{safe_code}.py"
            code_path.write_text(code)

            output.append(f"  Build time: {build_elapsed:.1f}s | Lines: {len(code.split(chr(10)))}")

            print(f"    → Built: {len(code.split(chr(10)))} lines in {build_elapsed:.1f}s")

            # ── Step 3: Review phase ──
            total_review_time = 0
            total_revision_time = 0
            revision_count = 0

            for rev in range(max_revisions):
                print(f"  Round 3 — Review #{rev + 1}: {convo_model}...")
                review_message = REVIEW_PROMPT.format(
                    task_spec=TASK_SPEC,
                    spec=spec_text,
                    code=code,
                )

                review_text, review_elapsed = call_model(
                    convo_model,
                    "You are a code reviewer. Be specific about issues.",
                    review_message,
                    temperature=0.3, num_predict=4096
                )
                total_review_time += review_elapsed

                if 'APPROVED' in review_text.upper() and len(review_text.strip()) < 200:
                    output.append(f"  Review #{rev + 1}: APPROVED ({review_elapsed:.1f}s)")
                    print(f"    → Review #{rev + 1}: APPROVED")
                    break
                else:
                    output.append(f"  Review #{rev + 1}: Revisions needed ({review_elapsed:.1f}s)")
                    if verbose:
                        output.append(f"  Review notes: {review_text[:300]}...")
                    print(f"    → Review #{rev + 1}: needs revision")

                    # ── Step 3b: Revision ──
                    revision_message = REVISION_PROMPT.format(
                        constitution=CODEGEN_CONSTITUTION,
                        review_notes=review_text,
                        code=code,
                    )

                    revised_text, revision_elapsed = call_model(
                        code_model,
                        "Output only corrected Python code. No explanation.",
                        revision_message,
                        temperature=0.2, num_predict=8192
                    )
                    total_revision_time += revision_elapsed
                    revision_count += 1

                    code = extract_python(revised_text)
                    code_path.write_text(code)  # Overwrite with revised version
                    print(f"    → Revised in {revision_elapsed:.1f}s")

            # ── Score final output ──
            sc = score_code(code, f"R3:{combo_key}")
            sc['elapsed_design'] = round(design_elapsed, 1)
            sc['elapsed_build'] = round(build_elapsed, 1)
            sc['elapsed_review'] = round(total_review_time, 1)
            sc['elapsed_revision'] = round(total_revision_time, 1)
            sc['elapsed'] = round(design_elapsed + build_elapsed + total_review_time + total_revision_time, 1)
            sc['revision_count'] = revision_count
            sc['model'] = combo_key
            sc['convo_model'] = convo_model
            sc['code_model'] = code_model
            sc['raw_length'] = len(code_text)

            round_results[combo_key] = sc

            output.append(f"  FINAL: Score: {sc['total_score']}/100 | Reqs: {sc['requirements_met']}/6 | Revisions: {revision_count}")
            output.append(f"  Timing: design={design_elapsed:.1f}s + build={build_elapsed:.1f}s + review={total_review_time:.1f}s + revision={total_revision_time:.1f}s = {sc['elapsed']}s total")
            output.append(f"  Parses: {sc['parses']} | Runs: {sc['runs']} | Math: {sc['math_correct']} | Importable: {sc['is_importable']}")
            if sc['issues']:
                output.append(f"  Issues: {' | '.join(sc['issues'][:5])}")
            output.append(f"  Code saved: {code_path}")

            print(f"    → FINAL: {sc['total_score']}/100 | {sc['requirements_met']}/6 reqs | {sc['elapsed']}s total")

    results['round3'] = round_results


# ═══════════════════════════════════════════════════════════════════════════════
# COMPARISON SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

def build_comparison(results: Dict, output: List[str]):
    """Build the final comparison table."""
    output.append("\n" + "=" * 90)
    output.append("FINAL COMPARISON")
    output.append("=" * 90)

    # Header
    header = f"{'Round':<8} {'Model/Combo':<40} {'Score':>6} {'Reqs':>5} {'Parse':>6} {'Run':>5} {'Math':>6} {'Time':>7}"
    output.append(header)
    output.append("-" * 90)

    all_entries = []

    for round_name in ['round1', 'round2', 'round3']:
        round_data = results.get(round_name, {})
        for key, sc in round_data.items():
            rnd = round_name.replace('round', 'R')
            model = sc.get('model', key)
            if len(model) > 38:
                model = model[:35] + "..."
            entry = (
                rnd, model,
                sc.get('total_score', 0),
                f"{sc.get('requirements_met', 0)}/6",
                '✓' if sc.get('parses') else '✗',
                '✓' if sc.get('runs') else '✗',
                '✓' if sc.get('math_correct') else '✗',
                f"{sc.get('elapsed', 0)}s",
            )
            all_entries.append(entry)
            output.append(f"{entry[0]:<8} {entry[1]:<40} {entry[2]:>5} {entry[3]:>5} {entry[4]:>6} {entry[5]:>5} {entry[6]:>6} {entry[7]:>7}")

    # Best per round
    output.append("\n" + "-" * 90)
    output.append("BEST PER ROUND:")
    for round_name in ['round1', 'round2', 'round3']:
        round_data = results.get(round_name, {})
        if round_data:
            best_key = max(round_data.keys(), key=lambda k: round_data[k].get('total_score', 0))
            best = round_data[best_key]
            rnd = round_name.replace('round', 'R')
            output.append(f"  {rnd}: {best.get('model', best_key)} — {best.get('total_score', 0)}/100 ({best.get('requirements_met', 0)}/6 reqs)")

    # Key finding
    output.append("\n" + "=" * 90)
    output.append("KEY FINDING:")

    r1_best = max(results.get('round1', {}).values(), key=lambda s: s.get('total_score', 0), default={'total_score': 0})
    r2_best = max(results.get('round2', {}).values(), key=lambda s: s.get('total_score', 0), default={'total_score': 0})
    r3_best = max(results.get('round3', {}).values(), key=lambda s: s.get('total_score', 0), default={'total_score': 0})

    output.append(f"  Raw best:          {r1_best.get('total_score', 0)}/100")
    output.append(f"  Constituted best:  {r2_best.get('total_score', 0)}/100")
    output.append(f"  Orchestrated best: {r3_best.get('total_score', 0)}/100")

    if r3_best.get('total_score', 0) > r1_best.get('total_score', 0):
        delta = r3_best['total_score'] - r1_best['total_score']
        output.append(f"\n  ✅ Orchestration improved score by +{delta} points over raw generation.")
    elif r3_best.get('total_score', 0) == r1_best.get('total_score', 0):
        output.append(f"\n  ➡️  Orchestration matched raw generation. Consider testing harder tasks.")
    else:
        delta = r1_best['total_score'] - r3_best.get('total_score', 0)
        output.append(f"\n  ⚠️  Raw generation scored higher by {delta} points. Orchestration overhead may not be justified for this task complexity.")

    output.append("=" * 90)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Iris Orchestration Test Harness v1.0')
    parser.add_argument('--round', type=int, choices=[1, 2, 3], help='Run specific round only')
    parser.add_argument('--convo', nargs='+', help='Conversational models (default: iris-thinking-v2, qwen3:14b, gemma3:27b)')
    parser.add_argument('--code', nargs='+', help='Code models (default: qwen3-coder:30b, qwen2.5:32b)')
    parser.add_argument('--all-models', nargs='+', help='Override ALL models for rounds 1-2')
    parser.add_argument('--quick', action='store_true', help='Quick mode: round 1 + 3 only, fewer models')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show specs and review notes')
    parser.add_argument('--max-revisions', type=int, default=2, help='Max review/revision cycles in round 3')
    args = parser.parse_args()

    # ── Setup output directory ──
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    CODE_DIR.mkdir(parents=True, exist_ok=True)

    # ── Resolve models ──
    convo_models = args.convo or CONVO_MODELS
    code_models = args.code or CODE_MODELS

    if args.quick:
        convo_models = convo_models[:1]  # Just the first convo model
        code_models = code_models[:1]    # Just the first code model

    all_models = args.all_models or list(set(convo_models + code_models))

    # ── Check model availability ──
    try:
        available = client.list()
        available_names = set()
        models_list = available.models if hasattr(available, 'models') else available.get('models', [])
        for m in models_list:
            name = m.model if hasattr(m, 'model') else m.get('model', m.get('name', ''))
            if name:
                available_names.add(name)

        missing_convo = [m for m in convo_models if m not in available_names]
        missing_code = [m for m in code_models if m not in available_names]
        if missing_convo:
            print(f"⚠️  Missing convo models (will skip): {missing_convo}")
            convo_models = [m for m in convo_models if m in available_names]
        if missing_code:
            print(f"⚠️  Missing code models (will skip): {missing_code}")
            code_models = [m for m in code_models if m in available_names]

        all_models = [m for m in all_models if m in available_names]
    except Exception as e:
        print(f"Warning: Could not check model availability: {e}")

    if not all_models:
        print("No available models found!")
        return

    print(f"Conversational models: {', '.join(convo_models)}")
    print(f"Code models: {', '.join(code_models)}")
    print(f"All models (R1/R2): {', '.join(all_models)}")

    # ── Determine rounds to run ──
    if args.round:
        rounds = [args.round]
    elif args.quick:
        rounds = [1, 3]
    else:
        rounds = [1, 2, 3]

    print(f"Rounds: {rounds}")
    print(f"Output: {OUTPUT_DIR}")
    print()

    # ── Run ──
    output = []
    results = {}

    output.append("=" * 90)
    output.append(f"IRIS ORCHESTRATION TEST — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output.append("=" * 90)
    output.append(f"Convo models: {', '.join(convo_models)}")
    output.append(f"Code models: {', '.join(code_models)}")
    output.append(f"All models: {', '.join(all_models)}")
    output.append(f"Rounds: {rounds}")
    output.append(f"Max revisions: {args.max_revisions}")
    output.append(f"Task: Spiral Time Calculator")

    if 1 in rounds:
        run_round1(all_models, output, results, verbose=args.verbose)

    if 2 in rounds:
        run_round2(all_models, output, results, verbose=args.verbose)

    if 3 in rounds:
        run_round3(convo_models, code_models, output, results, verbose=args.verbose, max_revisions=args.max_revisions)

    # ── Comparison (only if multiple rounds ran) ──
    if len(rounds) > 1:
        build_comparison(results, output)

    # ── Save ──
    output_text = "\n".join(output)
    RESULTS_PATH.write_text(output_text)

    json_results = {
        'timestamp': datetime.now().isoformat(),
        'convo_models': convo_models,
        'code_models': code_models,
        'all_models': all_models,
        'rounds': rounds,
        'task': 'spiral_time_calculator',
        'results': results,
    }
    JSON_PATH.write_text(json.dumps(json_results, indent=2, default=str))

    print(f"\n{'=' * 60}")
    print(f"✅ Results: {RESULTS_PATH}")
    print(f"✅ JSON: {JSON_PATH}")
    print(f"✅ Code: {CODE_DIR}")
    print(f"\nCopy to clipboard: cat ~/orchestration_test/results.txt | xclip -selection clipboard")


if __name__ == '__main__':
    main()
