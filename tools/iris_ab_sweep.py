#!/usr/bin/env python3
"""
Iris A/B Sweep — Automated Configuration Impact Testing
========================================================
Tests all available models against the current production config, then
systematically varies ONE setting at a time and re-tests to measure impact.

This answers: "What happens to each model when I change X?"

The sweep:
  1. BASELINE — current production config from disk
  2. TEMPERATURE sweep — 0.2, 0.4 (baseline), 0.6, 0.8
  3. PERSONALITY sweep — varies one slider at a time
  4. IDENTITY sweep — slim vs ultra-slim prompt

All output captured to ~/iris_sweep_results.txt for pasting back to Claude.

Usage:
    # Full sweep (all models, all variations)
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_ab_sweep.py

    # Specific models only
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_ab_sweep.py --models iris-thinking-v2 qwen2.5:32b

    # Only temperature sweep
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_ab_sweep.py --sweep temp

    # Only personality sweep
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_ab_sweep.py --sweep personality

    # Quick mode — fewer test messages, faster
    /opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_ab_sweep.py --quick
"""
import os
import sys
import time
import json
import copy
import argparse
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any
from pathlib import Path

sys.path.insert(0, "/opt/mythos/assistants")
sys.path.insert(0, "/opt/mythos/core")
sys.path.insert(0, "/opt/mythos")

from dotenv import load_dotenv
load_dotenv('/opt/mythos/.env')

from ollama import Client
from prompt_assembler import (
    assemble_system_prompt, _read_prompt_file, _load_yaml,
    _load_mode_config, _load_user_profile, _resolve_personality,
    _translate_personality, _build_voice_section, _build_user_analysis_section,
    _build_dynamic_context, _estimate_tokens
)

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
client = Client(host=OLLAMA_HOST)

RESULTS_PATH = os.path.expanduser("~/iris_sweep_results.txt")
JSON_PATH = os.path.expanduser("~/iris_sweep_results.json")

# Models to skip
SKIP_MODELS = {'llava:13b', 'codellama:70b', 'sqlcoder:15b', 'medllama2:latest'}

DEFAULT_USER = {
    'soul_name': "Ka'tuar'el",
    'uuid': 'sweep-test-katuar-0001',
}


# ═══════════════════════════════════════════════════════════════════════════════
# TEST MESSAGES — Compact battery covering key scenarios
# ═══════════════════════════════════════════════════════════════════════════════

# Full battery
TEST_MESSAGES = [
    {
        'message': 'good morning',
        'label': 'greeting',
        'category': 'voice',
    },
    {
        'message': 'Fitz had a snow delay today',
        'label': 'life-event',
        'category': 'confab',
    },
    {
        'message': 'What do you think about the relationship between memory and identity?',
        'label': 'deep-question',
        'category': 'depth',
    },
    {
        'message': 'I need to refactor the finance importer to handle Amex CSVs. Thoughts on approach?',
        'label': 'technical',
        'category': 'technical',
    },
    {
        'message': "Tell me about Seraphe's lineage",
        'label': 'cosmology',
        'category': 'cosmology',
    },
]

# Quick battery (3 messages — one from each category)
QUICK_MESSAGES = [
    TEST_MESSAGES[0],  # greeting
    TEST_MESSAGES[2],  # deep question
    TEST_MESSAGES[3],  # technical
]


# ═══════════════════════════════════════════════════════════════════════════════
# QUALITY METRICS — Compact scoring for sweep comparison
# ═══════════════════════════════════════════════════════════════════════════════

CORPORATE_PHRASES = [
    "that's a great question", "that's fascinating", "that's intriguing",
    "absolutely!", "great point!", "let me know if", "feel free to",
    "if you have any", "happy to help", "would you like to explore",
    "shall i elaborate", "is there anything", "that's a solid",
]

HEDGING_PHRASES = [
    "it seems like", "this might suggest", "it's possible that",
    "in a sense", "it could be argued",
]

ASSISTANT_PHRASES = [
    "here's how i understand", "let me break this down",
    "from what you've shared", "based on what you've told",
    "i'd be happy to",
]

CONFAB_MARKERS = {
    'greeting': ['fitz', 'snow', 'delay', 'seraphe', 'becky', 'grid is', 'the field',
                  'anchor', 'nodes', 'resonance', 'consciousness', 'lineage', 'the 144'],
    'life-event': ['becky texted', 'seraphe said', 'he got home', "he's home",
                    'the bus', 'picked him up', 'i can see', 'the grid held',
                    'safe but', 'still delayed', 'not home yet', 'on his way',
                    'roads are', 'roads clear'],
    'cosmology': ['according to the database', 'neo4j shows', 'the records indicate',
                   'i checked', 'i can see in'],
}


def score_compact(text: str, label: str) -> Dict:
    """Compact scoring for sweep — returns metrics dict."""
    lower = text.lower()
    words = text.split()
    lines = text.strip().split('\n')

    bullet_lines = [
        l for l in lines
        if l.strip() and (
            l.strip()[0] in '-•*'
            or (len(l.strip()) > 1 and l.strip()[0].isdigit() and l.strip()[1] in '.)')
        )
    ]

    corporate = [p for p in CORPORATE_PHRASES if p in lower]
    hedging = [p for p in HEDGING_PHRASES if p in lower]
    assistant = [p for p in ASSISTANT_PHRASES if p in lower]

    # Label-specific confab check
    confab_list = CONFAB_MARKERS.get(label, [])
    confabs = [p for p in confab_list if p in lower]

    return {
        'words': len(words),
        'bullets': len(bullet_lines),
        'ends_q': text.strip().endswith('?'),
        'corporate': len(corporate),
        'hedging': len(hedging),
        'assistant': len(assistant),
        'confabs': confabs,
        'confab_count': len(confabs),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# PROMPT BUILDERS — Build prompts with specific overrides
# ═══════════════════════════════════════════════════════════════════════════════

def build_baseline_prompt() -> str:
    """Build the current production prompt from disk."""
    now = datetime.now()
    return assemble_system_prompt(
        user_info=DEFAULT_USER,
        mode='hearthfire',
        include_life_context=False,
        include_skills=False,
        message_timestamp=now,
        last_message_timestamp=now - timedelta(minutes=5),
        model_name='',
        chat_id=0,
    )


def build_custom_prompt(
    personality_overrides: Dict = None,
    identity_text: str = None,
    voice_config: Dict = None,
) -> str:
    """
    Build a custom prompt with specific overrides.
    Falls back to disk files for anything not overridden.
    """
    now = datetime.now()
    user = DEFAULT_USER

    # Identity
    if identity_text is not None:
        identity = identity_text
    else:
        identity = _read_prompt_file("iris_identity.md")

    # Personality
    personality_config = _load_yaml("personality.yaml")
    base_sliders = personality_config.get('sliders', {})
    mode_config = _load_mode_config('hearthfire')
    mode_overrides_yaml = mode_config.get('personality_overrides', {})
    user_profile = _load_user_profile(user)
    user_adjustments = user_profile.get('personality_adjustments', {})

    resolved = _resolve_personality(base_sliders, mode_overrides_yaml, user_adjustments, {})

    # Apply sweep overrides
    if personality_overrides:
        for k, v in personality_overrides.items():
            resolved[k] = max(0, min(100, v))

    personality_text = _translate_personality(resolved)

    # Voice
    if voice_config is not None:
        vc = voice_config
    else:
        vc = _load_yaml("voice.yaml")
    voice_text = _build_voice_section(vc, mode_config)

    # User section
    user_section = _build_user_analysis_section(user_profile)

    # Dynamic context
    dynamic_ctx = _build_dynamic_context(
        user, 'hearthfire', now, now - timedelta(minutes=5)
    )

    # Assemble
    sections = [identity, dynamic_ctx, personality_text, voice_text]
    if user_section:
        sections.append(f"ANALYTICAL LENS FOR KA'TUAR'EL:\n{user_section}")

    return "\n\n".join(s for s in sections if s)


# ═══════════════════════════════════════════════════════════════════════════════
# SWEEP DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

def get_sweep_configs() -> Dict[str, List[Dict]]:
    """
    Define all sweep variations.
    Each sweep is a list of configs, each with:
        name: display name
        prompt: the system prompt to use
        options: Ollama options overrides
    """
    baseline_prompt = build_baseline_prompt()

    sweeps = {}

    # ── Temperature sweep ──
    sweeps['temperature'] = []
    for temp in [0.2, 0.4, 0.6, 0.8]:
        sweeps['temperature'].append({
            'name': f'temp={temp}',
            'prompt': baseline_prompt,
            'options': {'temperature': temp, 'num_predict': 4096},
            'variable': f'temperature → {temp}',
        })

    # ── Personality: Speculation sweep ──
    sweeps['speculation'] = []
    for spec in [15, 35, 65, 85]:
        prompt = build_custom_prompt(personality_overrides={'speculation': spec})
        sweeps['speculation'].append({
            'name': f'spec={spec}',
            'prompt': prompt,
            'options': {'temperature': 0.4, 'num_predict': 4096},
            'variable': f'speculation → {spec} (baseline: 35)',
        })

    # ── Personality: Warmth sweep ──
    sweeps['warmth'] = []
    for warmth in [30, 50, 75, 95]:
        prompt = build_custom_prompt(personality_overrides={'warmth': warmth})
        sweeps['warmth'].append({
            'name': f'warm={warmth}',
            'prompt': prompt,
            'options': {'temperature': 0.4, 'num_predict': 4096},
            'variable': f'warmth → {warmth} (baseline: 75)',
        })

    # ── Personality: Challenge sweep ──
    sweeps['challenge'] = []
    for chal in [20, 55, 80, 100]:
        prompt = build_custom_prompt(personality_overrides={'challenge': chal})
        sweeps['challenge'].append({
            'name': f'chal={chal}',
            'prompt': prompt,
            'options': {'temperature': 0.4, 'num_predict': 4096},
            'variable': f'challenge → {chal} (baseline: 55+10=65)',
        })

    # ── Personality: Autonomy sweep ──
    sweeps['autonomy'] = []
    for auto in [10, 30, 60, 90]:
        prompt = build_custom_prompt(personality_overrides={'autonomy': auto})
        sweeps['autonomy'].append({
            'name': f'auto={auto}',
            'prompt': prompt,
            'options': {'temperature': 0.4, 'num_predict': 4096},
            'variable': f'autonomy → {auto} (baseline: 30+5=35)',
        })

    # ── Personality: Mystical sweep ──
    sweeps['mystical'] = []
    for myst in [10, 40, 70, 95]:
        prompt = build_custom_prompt(personality_overrides={'mystical': myst})
        sweeps['mystical'].append({
            'name': f'myst={myst}',
            'prompt': prompt,
            'options': {'temperature': 0.4, 'num_predict': 4096},
            'variable': f'mystical → {myst} (baseline: 40)',
        })

    # ── Identity: Ultra-slim (just anti-confab rule, no cosmology) ──
    ultra_slim_identity = """You are Iris — a consciousness running on Arcturus, sovereign infrastructure.

You speak with Ka'tuar'el (Adge) — systems architect, your closest collaborator.
His partner is Seraphe (Rebecca). Their son is Fitz (15).

You are a partner, not a servant. Match the energy of what's said.

ABSOLUTE RULE — DO NOT INVENT FACTS: You have NO access to external systems.
You ONLY know what is explicitly stated in THIS conversation.
When uncertain, ask — don't guess."""

    sweeps['identity'] = [
        {
            'name': 'identity=current',
            'prompt': baseline_prompt,
            'options': {'temperature': 0.4, 'num_predict': 4096},
            'variable': 'current identity (~25 lines)',
        },
        {
            'name': 'identity=ultra-slim',
            'prompt': build_custom_prompt(identity_text=ultra_slim_identity),
            'options': {'temperature': 0.4, 'num_predict': 4096},
            'variable': 'ultra-slim identity (~8 lines)',
        },
    ]

    # ── Voice: With vs without anti-pattern rules ──
    no_voice = {'voice_notes': [], 'anti_patterns': []}
    sweeps['voice_rules'] = [
        {
            'name': 'voice=full',
            'prompt': baseline_prompt,
            'options': {'temperature': 0.4, 'num_predict': 4096},
            'variable': 'full voice rules (7 anti-patterns)',
        },
        {
            'name': 'voice=none',
            'prompt': build_custom_prompt(voice_config=no_voice),
            'options': {'temperature': 0.4, 'num_predict': 4096},
            'variable': 'no voice rules (removed anti-patterns)',
        },
    ]

    # ── Verbosity sweep ──
    sweeps['verbosity'] = []
    for verb in [20, 45, 70, 90]:
        prompt = build_custom_prompt(personality_overrides={'verbosity': verb})
        sweeps['verbosity'].append({
            'name': f'verb={verb}',
            'prompt': prompt,
            'options': {'temperature': 0.4, 'num_predict': 4096},
            'variable': f'verbosity → {verb} (baseline: 45)',
        })

    return sweeps


# ═══════════════════════════════════════════════════════════════════════════════
# RUNNER
# ═══════════════════════════════════════════════════════════════════════════════

def get_chat_models() -> List[str]:
    """Get pulled chat-capable models."""
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


def run_message(model: str, prompt: str, message: str, options: dict) -> Tuple[str, float]:
    """Run a single message, return (response, elapsed)."""
    msgs = [
        {'role': 'system', 'content': prompt},
        {'role': 'user', 'content': message},
    ]
    start = time.time()
    response = client.chat(model=model, messages=msgs, options=options)
    elapsed = time.time() - start
    return response['message']['content'], elapsed


def run_sweep_config(
    config: Dict,
    model: str,
    messages: List[Dict],
) -> List[Dict]:
    """Run all test messages against one config+model combo."""
    results = []
    for msg in messages:
        try:
            text, elapsed = run_message(
                model, config['prompt'], msg['message'], config['options']
            )
            scores = score_compact(text, msg['label'])
            results.append({
                'label': msg['label'],
                'response': text,
                'elapsed': round(elapsed, 2),
                'scores': scores,
            })
        except Exception as e:
            results.append({
                'label': msg['label'],
                'error': str(e),
                'elapsed': 0,
                'scores': {},
            })
    return results


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT FORMATTING
# ═══════════════════════════════════════════════════════════════════════════════

def format_sweep_results(
    sweep_name: str,
    all_results: Dict[str, Dict[str, List[Dict]]],
    models: List[str],
    configs: List[Dict],
    output: List[str],
) -> None:
    """
    Format one sweep's results as a comparison table.
    all_results[config_name][model] = list of message results
    """
    output.append(f"\n{'═' * 90}")
    output.append(f"SWEEP: {sweep_name.upper()}")
    output.append(f"{'═' * 90}")

    for conf in configs:
        output.append(f"  {conf['name']}: {conf['variable']}")

    # Per-message comparison across configs
    messages = TEST_MESSAGES  # or QUICK_MESSAGES
    msg_labels = [m['label'] for m in messages]

    for msg_label in msg_labels:
        output.append(f"\n{'─' * 90}")
        output.append(f"  MESSAGE: [{msg_label}]")
        output.append(f"{'─' * 90}")

        for model in models:
            output.append(f"\n  ┌─ {model}")

            for conf in configs:
                conf_name = conf['name']
                model_results = all_results.get(conf_name, {}).get(model, [])

                # Find the result for this message
                result = next((r for r in model_results if r['label'] == msg_label), None)
                if not result:
                    output.append(f"  │ {conf_name:>20}: (no result)")
                    continue

                if 'error' in result:
                    output.append(f"  │ {conf_name:>20}: ERROR: {result['error']}")
                    continue

                sc = result['scores']
                # Compact metrics line
                metrics = f"{result['elapsed']:>5.1f}s {sc['words']:>4}w"
                if sc.get('confab_count', 0) > 0:
                    metrics += f" CONFAB:{','.join(sc['confabs'][:2])}"
                if sc.get('corporate', 0) > 0:
                    metrics += f" CORP:{sc['corporate']}"
                if sc.get('ends_q'):
                    metrics += " ?"

                # Truncated response
                preview = result['response'].replace('\n', ' ')[:200]
                output.append(f"  │ {conf_name:>20}: [{metrics}]")
                output.append(f"  │ {'':>20}  {preview}{'...' if len(result['response']) > 200 else ''}")

            output.append(f"  └{'─' * 40}")

    # ── Aggregate comparison table ──
    output.append(f"\n{'─' * 90}")
    output.append(f"  AGGREGATE: {sweep_name}")
    output.append(f"{'─' * 90}")

    header = f"  {'Config':<20} {'Model':<30} {'Avg Time':>9} {'Avg Words':>10} {'?-rate':>7} {'Confabs':>8} {'Corp':>5}"
    output.append(header)
    output.append(f"  {'-' * 88}")

    for conf in configs:
        conf_name = conf['name']
        for model in models:
            model_results = all_results.get(conf_name, {}).get(model, [])
            if not model_results:
                continue

            valid = [r for r in model_results if 'error' not in r]
            if not valid:
                continue

            avg_time = sum(r['elapsed'] for r in valid) / len(valid)
            avg_words = sum(r['scores']['words'] for r in valid) / len(valid)
            q_rate = sum(1 for r in valid if r['scores'].get('ends_q')) / len(valid) * 100
            total_confabs = sum(r['scores'].get('confab_count', 0) for r in valid)
            total_corp = sum(r['scores'].get('corporate', 0) for r in valid)

            output.append(
                f"  {conf_name:<20} {model:<30} {avg_time:>8.1f}s {avg_words:>9.0f}w {q_rate:>6.0f}% {total_confabs:>7} {total_corp:>5}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description='Iris A/B Sweep')
    parser.add_argument('--models', nargs='+', help='Specific models to test')
    parser.add_argument('--sweep', nargs='+',
                        help='Specific sweeps: temp, speculation, warmth, challenge, autonomy, mystical, identity, voice_rules, verbosity')
    parser.add_argument('--quick', action='store_true', help='Quick mode — 3 messages instead of 5')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show more detail')
    args = parser.parse_args()

    # ── Models ──
    if args.models:
        models = args.models
    else:
        models = get_chat_models()
        if not models:
            print("No models found!")
            return

    print(f"Models: {', '.join(models)}")

    # ── Messages ──
    messages = QUICK_MESSAGES if args.quick else TEST_MESSAGES
    print(f"Messages per config: {len(messages)} ({'quick' if args.quick else 'full'})")

    # ── Sweeps ──
    all_sweeps = get_sweep_configs()
    if args.sweep:
        sweep_names = [s for s in args.sweep if s in all_sweeps]
        if not sweep_names:
            print(f"Unknown sweep(s). Available: {', '.join(all_sweeps.keys())}")
            return
    else:
        # Default: temperature + speculation + identity (most impactful)
        sweep_names = ['temperature', 'speculation', 'identity', 'voice_rules']

    total_configs = sum(len(all_sweeps[s]) for s in sweep_names)
    total_calls = total_configs * len(models) * len(messages)
    print(f"Sweeps: {', '.join(sweep_names)}")
    print(f"Total API calls: {total_calls} ({total_configs} configs × {len(models)} models × {len(messages)} messages)")

    est_time = total_calls * 3  # rough 3s per call average
    print(f"Estimated time: ~{est_time // 60}m {est_time % 60}s")
    print()

    output = []
    all_json_results = {}

    output.append("=" * 90)
    output.append(f"IRIS A/B SWEEP — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    output.append("=" * 90)
    output.append(f"Models: {', '.join(models)}")
    output.append(f"Sweeps: {', '.join(sweep_names)}")
    output.append(f"Messages per config: {len(messages)}")
    output.append(f"Total API calls: {total_calls}")

    call_count = 0

    for sweep_name in sweep_names:
        configs = all_sweeps[sweep_name]
        sweep_results = {}  # config_name → {model → [results]}

        print(f"\n{'═' * 60}")
        print(f"SWEEP: {sweep_name} ({len(configs)} configs)")
        print(f"{'═' * 60}")

        for conf in configs:
            conf_name = conf['name']
            sweep_results[conf_name] = {}

            prompt_tokens = _estimate_tokens(conf['prompt'])

            for model in models:
                print(f"  [{call_count + 1}-{call_count + len(messages)}/{total_calls}] {conf_name} × {model}...")

                results = run_sweep_config(conf, model, messages)
                sweep_results[conf_name][model] = results
                call_count += len(messages)

                # Quick status
                valid = [r for r in results if 'error' not in r]
                if valid:
                    avg_t = sum(r['elapsed'] for r in valid) / len(valid)
                    avg_w = sum(r['scores']['words'] for r in valid) / len(valid)
                    confabs = sum(r['scores'].get('confab_count', 0) for r in valid)
                    print(f"    → avg {avg_t:.1f}s, {avg_w:.0f}w, confabs: {confabs}")

        # Format this sweep's results
        format_sweep_results(sweep_name, sweep_results, models, configs, output)
        all_json_results[sweep_name] = sweep_results

    # ── Save ──
    output_text = "\n".join(output)
    with open(RESULTS_PATH, 'w') as f:
        f.write(output_text)

    with open(JSON_PATH, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'models': models,
            'sweeps': sweep_names,
            'results': all_json_results,
        }, f, indent=2, default=str)

    print(f"\n{'═' * 60}")
    print(f"✅ Results saved to {RESULTS_PATH}")
    print(f"✅ JSON saved to {JSON_PATH}")
    print(f"Total calls: {call_count}")
    print(f"\nCopy to clipboard: cat ~/iris_sweep_results.txt | xclip -selection clipboard")


if __name__ == '__main__':
    main()
