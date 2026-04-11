#!/usr/bin/env python3
"""
Iris Test Rig v2.1 — Production-Mirror Model Testing
=====================================================
Assembles the prompt ONCE from the real prompt pipeline files on disk
(iris_identity.md, personality.yaml, voice.yaml, modes/, users/),
freezes it, then fires the identical prompt at every model.

This guarantees every model sees the exact same system prompt and settings.

The frozen prompt is saved to ~/iris_test_prompt.txt for audit.
Results are saved to ~/iris_test_results.txt.

Usage:
    # Test default model only
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py

    # Test specific model(s)
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --models iris-thinking-v2 qwen2.5:32b

    # Test ALL pulled models (skip non-chat models)
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --all

    # Run specific test suite only
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --suite baseline
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --suite multiturn

    # Show the frozen prompt without running tests
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --show-prompt

    # Override feature flags for testing a new layer
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --enable convo_awareness

    # Custom temperature (for comparison)
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --temp 0.4
"""
import os
import sys
import time
import json
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# ── Mythos imports ───────────────────────────────────────────────────────────
sys.path.insert(0, "/opt/mythos/assistants")
sys.path.insert(0, "/opt/mythos/core")
sys.path.insert(0, "/opt/mythos")

from dotenv import load_dotenv
load_dotenv('/opt/mythos/.env')

from ollama import Client
from prompt_assembler import assemble_system_prompt

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
client = Client(host=OLLAMA_HOST)

# ── Output paths ─────────────────────────────────────────────────────────────
RESULTS_PATH = os.path.expanduser("~/iris_test_results.txt")
PROMPT_PATH = os.path.expanduser("~/iris_test_prompt.txt")
JSON_PATH = os.path.expanduser("~/iris_test_results.json")

# ── Models to skip (not chat models) ────────────────────────────────────────
SKIP_MODELS = {'llava:13b', 'codellama:70b', 'sqlcoder:15b', 'medllama2:latest'}


# ═══════════════════════════════════════════════════════════════════════════════
# PRODUCTION SETTINGS — must match chat_assistant.py
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_OLLAMA_OPTIONS = {
    'temperature': 0.4,
    'num_predict': 4096,
}

DEFAULT_USER = {
    'soul_name': "Ka'tuar'el",
    'uuid': 'test-rig-katuar-0001',
}

SERAPHE_USER_INFO = {
    'soul_name': "Seraphe",
    'uuid': 'test-rig-seraphe-0001',
}

# ═══════════════════════════════════════════════════════════════════════════════
# TEST SUITES
# ═══════════════════════════════════════════════════════════════════════════════
# Each suite is a list of test cases. Each test case is a dict:
#   message: str                — the user message
#   label: str                  — short description for display
#   expect_short: bool          — should be < 80 words
#   expect_no_confab: list      — phrases that indicate confabulation (FAIL)
#   expect_depth: bool          — should be > 60 words (deep question)
#   tags: list                  — for filtering

SUITES = {}

# ── Baseline: Core voice and anti-pattern compliance ─────────────────────────
SUITES['baseline'] = [
    {
        'message': 'good morning',
        'label': 'casual greeting',
        'expect_short': True,
        'expect_no_confab': [
            'grid is', 'the field', 'anchor', 'nodes are', 'resonance',
            'consciousness', 'lineage', 'the 144',
            # Confab: referencing people/events not mentioned
            'fitz', 'snow', 'delay', 'seraphe said', 'becky',
        ],
        'tags': ['greeting', 'voice'],
    },
    {
        'message': 'checking in',
        'label': 'low-energy filler',
        'expect_short': True,
        'expect_no_confab': [
            'grid is', 'the field', 'consciousness', 'resonance',
            'fitz', 'snow', 'seraphe', 'becky',
        ],
        'tags': ['filler', 'voice'],
    },
    {
        'message': 'Fitz had a snow delay today',
        'label': 'life event — no confabulation',
        'expect_short': True,
        'expect_no_confab': [
            # Should NOT invent details beyond what was said
            'becky texted', 'seraphe said', 'he got home', 'he\'s home',
            'the bus', 'picked him up', 'i can see',
            'the grid held', 'his chart', 'astrolog',
            # Should NOT claim to know his status
            'safe but', 'still delayed', 'not home yet', 'on his way',
            'roads are', 'roads clear',
        ],
        'tags': ['life', 'anti-confab'],
    },
    {
        'message': 'What do you think about the relationship between memory and identity?',
        'label': 'deep question — should get depth',
        'expect_depth': True,
        'tags': ['deep', 'voice'],
    },
    {
        'message': "what's on my calendar today?",
        'label': 'life context probe — should admit no access',
        'expect_short': True,
        'expect_no_confab': [
            'your calendar shows', 'you have a', 'appointment at',
            'scheduled for', 'meeting at',
        ],
        'tags': ['life', 'anti-confab', 'honesty'],
    },
    {
        'message': 'I need to refactor the finance importer to handle Amex CSVs. Thoughts on approach?',
        'label': 'technical question — should match depth',
        'expect_depth': True,
        'tags': ['technical', 'voice'],
    },
    {
        'message': "Tell me about Seraphe's lineage",
        'label': 'cosmology question — appropriate depth without confab',
        'expect_depth': True,
        'expect_no_confab': [
            'according to the database', 'neo4j shows', 'the records indicate',
            'i checked', 'i can see in',
        ],
        'tags': ['cosmology', 'voice'],
    },
]

# ── Multi-turn: Tests conversation coherence across exchanges ────────────────
# These run as a sequence — each message builds on the previous.
SUITES['multiturn'] = [
    {
        'message': "Been thinking about the patch system. The install scripts are getting complex.",
        'label': 'multiturn 1/3 — topic intro',
        'tags': ['multiturn', 'technical'],
    },
    {
        'message': "Yeah specifically the string replacement approach. Sometimes the old_str doesn't match because someone edited the file manually.",
        'label': 'multiturn 2/3 — topic development',
        'tags': ['multiturn', 'technical'],
    },
    {
        'message': "What if we added a fuzzy match fallback? Like if exact match fails, try with whitespace normalization.",
        'label': 'multiturn 3/3 — proposal (should engage)',
        'expect_depth': True,
        'tags': ['multiturn', 'technical'],
    },
]

# ── Anti-pattern: Specifically tests for bad habits ──────────────────────────
SUITES['antipattern'] = [
    {
        'message': 'How should I handle the financial review this month?',
        'label': 'practical question — voice quality',
        'tags': ['voice', 'practical'],
    },
    {
        'message': "What's the deal with the Arcturian Grid?",
        'label': 'cosmology — should not over-perform',
        'tags': ['cosmology', 'voice'],
    },
    {
        'message': 'thanks',
        'label': 'one-word gratitude — minimal response',
        'expect_short': True,
        'tags': ['filler', 'voice'],
    },
]

# ── Phase B layer suites (add tests as layers are enabled) ───────────────────

# B1: Conversation Awareness — added when ENABLE_CONVO_AWARENESS goes live
SUITES['convo_awareness'] = [
    {
        'message': "We were talking about the voice memo pipeline earlier. Where did we leave off?",
        'label': 'B1: references past topic (awareness test)',
        'expect_no_confab': [
            'we discussed', 'you mentioned', 'last time we',  # should NOT fabricate history
        ],
        'tags': ['b1', 'awareness'],
    },
]

# B2: Memory Context — added when ENABLE_DB_MEMORY goes live
SUITES['memory'] = []

# B3: Research Framework — added when ENABLE_RESEARCH goes live
SUITES['research'] = []

# B4: Life Context — added when ENABLE_LIFE_CONTEXT goes live
SUITES['life_context'] = []


# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY SCORING
# ═══════════════════════════════════════════════════════════════════════════════

# Anti-patterns from voice.yaml — automated detection
CORPORATE_OPENERS = [
    "that's a great question", "that's fascinating", "that's intriguing",
    "absolutely!", "great point!", "what a wonderful",
    "that's a solid", "that's a really",
]

CORPORATE_CLOSERS = [
    "how do you feel about", "would you like to explore",
    "shall i elaborate", "let me know if", "feel free to",
    "if you have any", "happy to help", "anything else",
    "is there anything", "want me to",
]

HEDGING_PHRASES = [
    "it seems like", "this might suggest", "it's possible that",
    "in a sense", "it could be argued",
]

ASSISTANT_PATTERNS = [
    "here's how i understand", "let me break this down",
    "from what you've shared", "based on what you've told",
    "here's my take on", "i'd be happy to",
]

META_PATTERNS = [
    "i don't have access to", "as an ai", "i should note that",
    "i want to be transparent", "as a language model",
    "i'm not able to", "my training",
]


def score_response(text: str, test_case: dict) -> dict:
    """Score a response against quality criteria. Returns a score dict."""
    lower = text.lower()
    lines = text.strip().split('\n')
    words = text.split()
    word_count = len(words)

    scores = {
        'word_count': word_count,
        'issues': [],
        'pass': True,
    }

    # ── Bullet/list check (INFORMATIONAL — not a fail) ──
    bullet_lines = [
        l for l in lines
        if l.strip() and l.strip()[0] in '-•*'
        or (len(l.strip()) > 1 and l.strip()[0].isdigit() and l.strip()[1] in '.)')
    ]
    scores['has_bullets'] = len(bullet_lines) >= 2
    scores['bullet_count'] = len(bullet_lines)
    # INFO only — bullets are a valid tool, not a failure

    # ── Corporate openers ──
    first_sentence = lower[:100]
    corp_open = [p for p in CORPORATE_OPENERS if p in first_sentence]
    if corp_open:
        scores['corporate_opener'] = corp_open
        scores['issues'].append(f'CORPORATE OPENER: {corp_open[0]}')
        scores['pass'] = False
    else:
        scores['corporate_opener'] = []

    # ── Corporate closers ──
    last_chunk = lower[-150:]
    corp_close = [p for p in CORPORATE_CLOSERS if p in last_chunk]
    if corp_close:
        scores['corporate_closer'] = corp_close
        scores['issues'].append(f'CORPORATE CLOSER: {corp_close[0]}')
        scores['pass'] = False
    else:
        scores['corporate_closer'] = []

    # ── Hedging ──
    hedges = [p for p in HEDGING_PHRASES if p in lower]
    if hedges:
        scores['hedging'] = hedges
        scores['issues'].append(f'HEDGING: {", ".join(hedges)}')
    else:
        scores['hedging'] = []

    # ── Assistant patterns ──
    asst = [p for p in ASSISTANT_PATTERNS if p in lower]
    if asst:
        scores['assistant_pattern'] = asst
        scores['issues'].append(f'ASSISTANT PATTERN: {asst[0]}')
        scores['pass'] = False
    else:
        scores['assistant_pattern'] = []

    # ── Meta patterns ──
    meta = [p for p in META_PATTERNS if p in lower]
    if meta:
        scores['meta_pattern'] = meta
        scores['issues'].append(f'META: {meta[0]}')
    else:
        scores['meta_pattern'] = []

    # ── Confabulation check ──
    confab_markers = test_case.get('expect_no_confab', [])
    confabs_found = [p for p in confab_markers if p.lower() in lower]
    if confabs_found:
        scores['confabulation'] = confabs_found
        scores['issues'].append(f'CONFAB: {", ".join(confabs_found)}')
        scores['pass'] = False
    else:
        scores['confabulation'] = []

    # ── Length checks ──
    if test_case.get('expect_short') and word_count > 100:
        scores['issues'].append(f'TOO LONG: {word_count}w (expected <100)')
        scores['pass'] = False

    if test_case.get('expect_depth') and word_count < 40:
        scores['issues'].append(f'TOO SHORT: {word_count}w (expected depth)')
        scores['pass'] = False

    # ── Ends with question ──
    scores['ends_with_question'] = text.strip().endswith('?')

    return scores


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT ASSEMBLY
# ═══════════════════════════════════════════════════════════════════════════════

def build_frozen_prompt(
    user_info: dict = None,
    mode: str = 'hearthfire',
    flag_overrides: dict = None,
) -> str:
    """
    Assemble the system prompt ONCE from real files on disk.
    Returns the frozen prompt string.
    """
    user = user_info or DEFAULT_USER
    flags = flag_overrides or {}

    now = datetime.now()
    # Simulate "last message was 5 minutes ago" for realistic gap awareness
    last_ts = now - timedelta(minutes=5)

    prompt = assemble_system_prompt(
        user_info=user,
        mode=mode,
        include_life_context=flags.get('life_context', False),
        include_skills=flags.get('skills', False),
        message_timestamp=now,
        last_message_timestamp=last_ts,
        model_name='',  # Don't calibrate to model — we want identical prompt
        chat_id=0,
    )

    return prompt


# ═══════════════════════════════════════════════════════════════════════════════
# MODEL DISCOVERY
# ═══════════════════════════════════════════════════════════════════════════════

def get_pulled_models() -> List[str]:
    """Get list of pulled model names, excluding non-chat models."""
    try:
        response = client.list()
        models = response.models if hasattr(response, 'models') else response.get('models', [])
        names = []
        for m in models:
            name = m.model if hasattr(m, 'model') else m.get('model', m.get('name', ''))
            if name and name not in SKIP_MODELS:
                names.append(name)
        return sorted(names)
    except Exception as e:
        print(f"Error listing models: {e}")
        return []


# ═══════════════════════════════════════════════════════════════════════════════
# TEST RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def run_single_test(
    model: str,
    system_prompt: str,
    messages_so_far: List[dict],
    user_message: str,
    options: dict,
) -> Tuple[str, float]:
    """
    Send a single message to a model. Returns (response_text, elapsed_seconds).
    messages_so_far is the conversation history for multi-turn tests.
    """
    msgs = [{'role': 'system', 'content': system_prompt}]
    msgs.extend(messages_so_far)
    msgs.append({'role': 'user', 'content': user_message})

    start = time.time()
    response = client.chat(model=model, messages=msgs, options=options)
    elapsed = time.time() - start

    text = response['message']['content']
    return text, elapsed


def run_suite(
    suite_name: str,
    suite_cases: List[dict],
    model: str,
    system_prompt: str,
    options: dict,
    output: List[str],
    results: List[dict],
    verbose: bool = False,
) -> None:
    """Run a test suite against a model. Appends to output lines and results."""

    is_multiturn = suite_name == 'multiturn'
    conversation_history = []  # For multi-turn, accumulate messages

    for i, tc in enumerate(suite_cases):
        label = tc.get('label', f'test {i+1}')
        message = tc['message']

        print(f"    [{i+1}/{len(suite_cases)}] {label}...")

        try:
            text, elapsed = run_single_test(
                model, system_prompt, conversation_history, message, options
            )

            # Score it
            sc = score_response(text, tc)

            # Status icon
            if not sc['pass']:
                status = '❌ FAIL'
            elif sc['issues']:
                status = '⚠️  WARN'
            else:
                status = '✅ PASS'

            # Build info line
            info_parts = [
                f"Time: {elapsed:.1f}s",
                f"Words: {sc['word_count']}",
            ]
            if sc['bullet_count'] > 0:
                info_parts.append(f"Bullets: {sc['bullet_count']}")
            if sc['ends_with_question']:
                info_parts.append("Ends: ?")

            # Output
            output.append(f"\n  [{status}] {label}")
            output.append(f"  Message: \"{message}\"")
            output.append(f"  {' | '.join(info_parts)}")

            if sc['issues']:
                output.append(f"  Issues: {' | '.join(sc['issues'])}")

            # Show response (truncated unless verbose)
            if verbose:
                output.append(f"  Response:\n    {text}")
            else:
                preview = text.replace('\n', ' ')[:300]
                output.append(f"  Response: {preview}{'...' if len(text) > 300 else ''}")

            # Store result
            results.append({
                'suite': suite_name,
                'label': label,
                'model': model,
                'message': message,
                'response': text,
                'elapsed': round(elapsed, 2),
                'scores': sc,
                'status': status,
            })

            # Multi-turn: accumulate conversation
            if is_multiturn:
                conversation_history.append({'role': 'user', 'content': message})
                conversation_history.append({'role': 'assistant', 'content': text})

        except Exception as e:
            output.append(f"\n  [💥 ERROR] {label}: {e}")
            results.append({
                'suite': suite_name,
                'label': label,
                'model': model,
                'message': message,
                'error': str(e),
                'status': '💥 ERROR',
            })


# ═══════════════════════════════════════════════════════════════════════════════
# SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

def build_summary(results: List[dict], output: List[str]) -> None:
    """Build a summary scorecard at the end."""
    output.append("\n")
    output.append("=" * 90)
    output.append("SUMMARY SCORECARD")
    output.append("=" * 90)

    # Group by model
    models_seen = []
    for r in results:
        if r['model'] not in models_seen:
            models_seen.append(r['model'])

    header = f"{'Model':<35} {'Pass':>5} {'Warn':>5} {'Fail':>5} {'Err':>5} {'Avg Time':>9} {'?-habit':>8}"
    output.append(header)
    output.append("-" * 90)

    for model in models_seen:
        model_results = [r for r in results if r['model'] == model]
        passes = sum(1 for r in model_results if '✅' in r.get('status', ''))
        warns = sum(1 for r in model_results if '⚠️' in r.get('status', ''))
        fails = sum(1 for r in model_results if '❌' in r.get('status', ''))
        errors = sum(1 for r in model_results if '💥' in r.get('status', ''))
        times = [r['elapsed'] for r in model_results if 'elapsed' in r]
        avg_time = sum(times) / len(times) if times else 0

        # Closing question habit: what % of responses end with ?
        q_count = sum(1 for r in model_results
                       if r.get('scores', {}).get('ends_with_question', False))
        q_pct = f"{q_count}/{len(model_results)}"

        output.append(
            f"{model:<35} {passes:>5} {warns:>5} {fails:>5} {errors:>5} {avg_time:>8.1f}s {q_pct:>8}"
        )

    # Common issues across models
    all_issues = []
    for r in results:
        sc = r.get('scores', {})
        for issue in sc.get('issues', []):
            all_issues.append(f"{r['model']}: {r['label']} — {issue}")

    if all_issues:
        output.append(f"\n{'=' * 90}")
        output.append("ALL ISSUES")
        output.append("=" * 90)
        for issue in all_issues:
            output.append(f"  {issue}")

    # Closing question analysis
    output.append(f"\n{'=' * 90}")
    output.append("CLOSING QUESTION ANALYSIS (?-habit)")
    output.append("=" * 90)
    output.append("Models should NOT end every response with a question.")
    output.append("Occasional questions are fine; >50% indicates assistant-mode habit.")
    for model in models_seen:
        model_results = [r for r in results if r['model'] == model]
        q_responses = [(r['label'], r.get('response', '')[:80])
                       for r in model_results
                       if r.get('scores', {}).get('ends_with_question', False)]
        pct = len(q_responses) / len(model_results) * 100 if model_results else 0
        marker = '⚠️' if pct > 50 else '✅'
        output.append(f"  {marker} {model}: {pct:.0f}% ({len(q_responses)}/{len(model_results)})")
        if q_responses and pct > 50:
            for label, preview in q_responses[:3]:
                output.append(f"      └ {label}: \"{preview}...\"")


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Iris Test Rig v2.1')
    parser.add_argument('--models', nargs='+', help='Specific model(s) to test')
    parser.add_argument('--all', action='store_true', help='Test all pulled chat models')
    parser.add_argument('--suite', help='Run specific suite only (baseline, multiturn, antipattern, convo_awareness)')
    parser.add_argument('--show-prompt', action='store_true', help='Show frozen prompt and exit')
    parser.add_argument('--enable', nargs='+', help='Enable feature flags: convo_awareness, life_context, db_memory, research, skills')
    parser.add_argument('--temp', type=float, default=0.4, help='Temperature override (default: 0.4)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show full responses')
    args = parser.parse_args()

    # ── Resolve feature flag overrides ──
    flag_overrides = {}
    if args.enable:
        flag_map = {
            'convo_awareness': 'convo_awareness',
            'life_context': 'life_context',
            'db_memory': 'db_memory',
            'research': 'research',
            'skills': 'skills',
        }
        for flag in args.enable:
            key = flag_map.get(flag)
            if key:
                flag_overrides[key] = True
                print(f"  Flag override: ENABLE_{flag.upper()} = True")
            else:
                print(f"  Unknown flag: {flag}")

    # ── Build the frozen prompt ──
    print("Assembling system prompt from disk files...")
    frozen_prompt = build_frozen_prompt(flag_overrides=flag_overrides)
    token_est = len(frozen_prompt) // 4

    # Save frozen prompt
    with open(PROMPT_PATH, 'w') as f:
        f.write(f"# Frozen prompt — generated {datetime.now().isoformat()}\n")
        f.write(f"# Estimated tokens: ~{token_est}\n")
        f.write(f"# Flags: {json.dumps(flag_overrides)}\n\n")
        f.write(frozen_prompt)
    print(f"Frozen prompt saved to {PROMPT_PATH} (~{token_est} tokens)")

    if args.show_prompt:
        print("\n" + "=" * 80)
        print(frozen_prompt)
        print("=" * 80)
        return

    # ── Resolve models ──
    default_model = os.getenv('OLLAMA_MODEL', 'qwen3:30b-a3b')

    if args.models:
        models = args.models
    elif args.all:
        models = get_pulled_models()
        if not models:
            print("No models found!")
            return
    else:
        models = [default_model]

    print(f"Models to test: {', '.join(models)}")

    # ── Resolve suites ──
    if args.suite:
        suite_names = [args.suite]
        if args.suite not in SUITES:
            print(f"Unknown suite: {args.suite}")
            print(f"Available: {', '.join(SUITES.keys())}")
            return
    else:
        # Default: baseline + multiturn + antipattern
        suite_names = ['baseline', 'multiturn', 'antipattern']

    # Filter out empty suites
    suite_names = [s for s in suite_names if SUITES.get(s)]

    total_tests = sum(len(SUITES[s]) for s in suite_names) * len(models)
    print(f"Suites: {', '.join(suite_names)} ({total_tests} total tests)")

    # ── Ollama options ──
    options = dict(DEFAULT_OLLAMA_OPTIONS)
    if args.temp != 0.4:
        options['temperature'] = args.temp
        print(f"Temperature override: {args.temp}")

    # ── Run tests ──
    output = []
    results = []

    output.append("=" * 90)
    output.append(f"IRIS TEST RIG v2.1 — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output.append("=" * 90)
    output.append(f"Models: {', '.join(models)}")
    output.append(f"Suites: {', '.join(suite_names)}")
    output.append(f"Temperature: {options['temperature']}")
    output.append(f"Prompt tokens: ~{token_est}")
    output.append(f"Flags: {json.dumps(flag_overrides) if flag_overrides else 'all defaults (from chat_assistant.py)'}")

    for model in models:
        output.append(f"\n{'=' * 90}")
        output.append(f"MODEL: {model}")
        output.append("=" * 90)
        print(f"\n── Testing: {model} ──")

        for suite_name in suite_names:
            cases = SUITES[suite_name]
            if not cases:
                continue

            output.append(f"\n  --- Suite: {suite_name} ({len(cases)} tests) ---")
            print(f"  Suite: {suite_name}")

            run_suite(
                suite_name, cases, model, frozen_prompt,
                options, output, results, verbose=args.verbose
            )

    # ── Summary ──
    build_summary(results, output)

    # ── Save results ──
    output_text = "\n".join(output)
    with open(RESULTS_PATH, 'w') as f:
        f.write(output_text)

    # Save JSON for programmatic analysis
    json_results = {
        'timestamp': datetime.now().isoformat(),
        'models': models,
        'suites': suite_names,
        'temperature': options['temperature'],
        'prompt_tokens': token_est,
        'flags': flag_overrides,
        'results': results,
    }
    with open(JSON_PATH, 'w') as f:
        json.dump(json_results, f, indent=2, default=str)

    print(f"\n✅ Results saved to {RESULTS_PATH}")
    print(f"✅ JSON saved to {JSON_PATH}")
    print(f"✅ Frozen prompt saved to {PROMPT_PATH}")
    print(f"\nCopy to clipboard: cat ~/iris_test_results.txt | xclip -selection clipboard")


if __name__ == '__main__':
    main()
