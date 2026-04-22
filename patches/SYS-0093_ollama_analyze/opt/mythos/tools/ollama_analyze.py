#!/opt/mythos/.venv/bin/python3
"""
/opt/mythos/tools/ollama_analyze.py
LLM-powered file/code analysis tool for use during patch builds.

Sends a prompt + optional file contents to a local Ollama model and
returns structured JSON. Designed to be called from apply_patch.py via
PatchBase.ollama_analyze() or directly from the CLI.

SYS-0093: Initial implementation.

Usage (CLI):
    ollama-analyze --task sql-drift --files migration.sql
    ollama-analyze --task py-signatures --files my_module.py
    ollama-analyze --task review --files patch_base.py --prompt "Check for footguns"
    ollama-analyze --prompt "Does this SQL have any ON DELETE CASCADE?" --files schema.sql
    ollama-analyze --json  # output raw JSON only (no pretty-print)

Usage (from PatchBase):
    result = patch.ollama_analyze(
        prompt="Check this SQL for schema drift vs existing tables",
        files=['/opt/mythos/migrations/SYS-0093_schema.sql'],
        task='sql-drift',
    )
    if result and result.get('issues'):
        patch.errors.append(f"SQL drift: {result['issues']}")

Environment:
    OLLAMA_HOST            Ollama server (default: http://localhost:11434)
    OLLAMA_ANALYZE_MODEL   Override model (default: qwen3:30b-a3b)
    MYTHOS_PATCH_DRY_RUN   If '1', skip Ollama call, return stub response
"""

import argparse
import json
import os
import sys
from pathlib import Path

MYTHOS = Path('/opt/mythos')
DEFAULT_MODEL = os.getenv('OLLAMA_ANALYZE_MODEL', 'qwen3:30b-a3b')
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
DRY_RUN = os.getenv('MYTHOS_PATCH_DRY_RUN', '0') == '1'

# ── Task presets ──────────────────────────────────────────────────────────────

TASKS = {
    'sql-drift': {
        'description': 'Check SQL migration for schema drift and issues',
        'system': (
            'You are a PostgreSQL schema reviewer. Analyze the provided SQL migration. '
            'Return ONLY a JSON object with these keys: '
            '"safe" (bool), "issues" (list of strings), "warnings" (list of strings), '
            '"summary" (one sentence). No markdown, no explanation, just the JSON object.'
        ),
        'prompt': (
            'Review this SQL migration for: schema drift, missing constraints, '
            'dangerous operations (DROP, TRUNCATE without WHERE), missing indexes '
            'on foreign keys, and any operations that could fail on a live database. '
            'Return JSON only.'
        ),
    },
    'py-signatures': {
        'description': 'Extract function/class signatures from Python source',
        'system': (
            'You are a Python code analyzer. Extract all public function and class '
            'signatures from the provided source. '
            'Return ONLY a JSON object with key "signatures": a list of objects, each '
            'with "name", "type" (function/class/method), "signature", "docstring_first_line". '
            'No markdown, no explanation, just the JSON object.'
        ),
        'prompt': (
            'Extract all public functions, classes, and methods from this Python source. '
            'Include type hints in signatures. Skip private members (prefixed with _). '
            'Return JSON only.'
        ),
    },
    'review': {
        'description': 'General code/config review for issues and improvements',
        'system': (
            'You are a senior software engineer doing a code review. '
            'Return ONLY a JSON object with keys: '
            '"approved" (bool), "blocking" (list of strings — must-fix issues), '
            '"suggestions" (list of strings — nice-to-have improvements), '
            '"summary" (one sentence). No markdown, no explanation, just the JSON object.'
        ),
        'prompt': 'Review this code for correctness, safety, and maintainability. Return JSON only.',
    },
    'sql-analyze': {
        'description': 'Analyze SQL for correctness and performance',
        'system': (
            'You are a PostgreSQL performance and correctness expert. '
            'Return ONLY a JSON object with keys: '
            '"correct" (bool), "performance_issues" (list of strings), '
            '"correctness_issues" (list of strings), "summary" (one sentence). '
            'No markdown, no explanation, just the JSON object.'
        ),
        'prompt': 'Analyze this SQL for correctness and performance. Return JSON only.',
    },
}

# ── Core analysis function ────────────────────────────────────────────────────

def analyze(
    prompt: str,
    files: list[str] = None,
    task: str = None,
    model: str = None,
    timeout: int = 120,
    verbose: bool = False,
) -> dict | None:
    """
    Run LLM analysis on a prompt + optional file contents.

    Args:
        prompt:  The analysis prompt. If task is set, this supplements the
                 task's built-in prompt.
        files:   List of file paths to include as context.
        task:    Preset task name (sql-drift, py-signatures, review, sql-analyze).
                 Sets system prompt and base prompt automatically.
        model:   Ollama model to use. Defaults to OLLAMA_ANALYZE_MODEL env or
                 qwen3:30b-a3b.
        timeout: Seconds before giving up on the Ollama call.
        verbose: Print progress to stderr.

    Returns:
        Parsed JSON dict on success, None on failure.
    """
    if DRY_RUN:
        if verbose:
            print('[ollama-analyze] DRY RUN -- skipping Ollama call', file=sys.stderr)
        return {
            'dry_run': True,
            'summary': 'Dry run -- no analysis performed',
            'safe': True,
            'issues': [],
            'warnings': [],
        }

    # Build system prompt
    system_prompt = (
        'You are a code and infrastructure analyst for the Mythos AI system on Arcturus. '
        'Always return valid JSON only. No markdown fences, no explanation text, '
        'just a raw JSON object.'
    )
    base_prompt = prompt

    if task:
        if task not in TASKS:
            print(f'[ollama-analyze] Unknown task: {task}. Available: {list(TASKS)}', file=sys.stderr)
            return None
        preset = TASKS[task]
        system_prompt = preset['system']
        base_prompt = preset['prompt']
        if prompt and prompt != preset['prompt']:
            base_prompt = f"{preset['prompt']}\n\nAdditional instructions: {prompt}"

    # Load file contents
    file_context = ''
    if files:
        parts = []
        for fpath in files:
            p = Path(fpath)
            if not p.exists():
                print(f'[ollama-analyze] WARNING: file not found: {fpath}', file=sys.stderr)
                continue
            try:
                content = p.read_text(encoding='utf-8')
                parts.append(f'=== {p.name} ===\n{content}')
            except Exception as e:
                print(f'[ollama-analyze] WARNING: could not read {fpath}: {e}', file=sys.stderr)
        if parts:
            file_context = '\n\n'.join(parts)

    # Assemble final user message
    if file_context:
        user_message = f'{base_prompt}\n\n{file_context}'
    else:
        user_message = base_prompt

    # Call Ollama
    try:
        import ollama
        client = ollama.Client(host=OLLAMA_HOST)
        active_model = model or DEFAULT_MODEL

        if verbose:
            print(f'[ollama-analyze] Calling {active_model} via {OLLAMA_HOST}...', file=sys.stderr)

        response = client.chat(
            model=active_model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_message},
            ],
            options={
                'temperature': 0.1,   # low temp for structured output
                'num_predict': 2048,  # enough for thinking mode
            },
        )
        raw = response.message.content.strip()

    except Exception as e:
        print(f'[ollama-analyze] Ollama call failed: {e}', file=sys.stderr)
        return None

    # Strip any accidental markdown fences
    if raw.startswith('```'):
        lines = raw.splitlines()
        raw = '\n'.join(lines[1:-1] if lines[-1].strip() == '```' else lines[1:])

    # Strip <think>...</think> blocks from qwen3 thinking mode
    import re
    raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()

    # Parse JSON
    try:
        result = json.loads(raw)
        if verbose:
            print(f'[ollama-analyze] OK -- got {len(result)} keys', file=sys.stderr)
        return result
    except json.JSONDecodeError as e:
        print(f'[ollama-analyze] JSON parse failed: {e}', file=sys.stderr)
        print(f'[ollama-analyze] Raw response:\n{raw[:500]}', file=sys.stderr)
        # Return raw as string in a wrapper so callers still get something
        return {'raw': raw, 'parse_error': str(e)}


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        prog='ollama-analyze',
        description='LLM-powered code/SQL analysis for Mythos patch builds',
    )
    parser.add_argument('--task', choices=list(TASKS), default=None,
                        help='Preset analysis task')
    parser.add_argument('--files', nargs='+', default=[],
                        help='Files to include as context')
    parser.add_argument('--prompt', default='',
                        help='Analysis prompt (supplements task prompt if --task set)')
    parser.add_argument('--model', default=None,
                        help=f'Ollama model to use (default: {DEFAULT_MODEL})')
    parser.add_argument('--timeout', type=int, default=120,
                        help='Timeout in seconds (default: 120)')
    parser.add_argument('--json', action='store_true', dest='json_only',
                        help='Output raw JSON only (no pretty-print header)')
    parser.add_argument('--verbose', action='store_true',
                        help='Print progress to stderr')
    parser.add_argument('--list-tasks', action='store_true',
                        help='List available task presets and exit')

    args = parser.parse_args()

    if args.list_tasks:
        print('Available tasks:')
        for name, preset in TASKS.items():
            print(f'  {name:<20} {preset["description"]}')
        return

    if not args.task and not args.prompt:
        parser.error('Provide --task and/or --prompt')

    result = analyze(
        prompt=args.prompt,
        files=args.files,
        task=args.task,
        model=args.model,
        timeout=args.timeout,
        verbose=args.verbose,
    )

    if result is None:
        print('[ollama-analyze] Analysis failed -- no result', file=sys.stderr)
        sys.exit(1)

    if args.json_only:
        print(json.dumps(result))
    else:
        if args.task:
            print(f'Task: {args.task} -- {TASKS[args.task]["description"]}')
        print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
