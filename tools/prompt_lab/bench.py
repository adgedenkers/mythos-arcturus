#!/usr/bin/env python3
"""
bench.py — Iris Prompt Workbench
=================================
Test and compare prompt configurations against standardized messages.

Usage:
  bench.py -m "hey what's up"                          # Quick test, default profile
  bench.py --profile naked -m "hey what's up"           # Naked model
  bench.py --profile identity_only --test greeting      # Single test from suite
  bench.py --profile full_stack --suite calibration     # Full suite
  bench.py --profile full_stack --personality tars_75 --suite calibration
  bench.py --profile full_stack --dry-run               # Show prompt, don't send
  bench.py --profile full_stack --model qwen2:72b --suite calibration
  bench.py --compare naked identity_only --test greeting
  bench.py --list-models                                # Show available Ollama models
  bench.py --list-profiles                              # Show available profiles
  bench.py --list-personalities                         # Show available presets
  bench.py --list-suites                                # Show available test suites
  bench.py --results                                    # Show saved runs
  bench.py --diff run_a.json run_b.json                 # Compare two runs
"""
import argparse
import sys
import os
import json
from pathlib import Path
from datetime import datetime

# Add lib to path
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from assembler import load_profile, load_personality_preset, load_test_messages, assemble
from runner import run_prompt, list_models
from scorer import score_response, format_scorecard
from store import save_run, list_runs, diff_runs, load_run

LAB_DIR = Path(__file__).parent
PROFILES_DIR = LAB_DIR / "profiles"
PERSONALITIES_DIR = LAB_DIR / "personalities"
MESSAGES_DIR = LAB_DIR / "messages"


def cmd_run(args):
    """Run a test (single message, single test, or full suite)."""
    # Load profile
    profile_name = args.profile or 'full_no_life'
    profile = load_profile(profile_name)
    if not profile:
        print(f"❌ Profile not found: {profile_name}")
        print(f"   Available: {', '.join(p.stem for p in PROFILES_DIR.glob('*.yaml'))}")
        sys.exit(1)

    # Load personality preset (optional)
    personality = {}
    personality_name = args.personality or 'default'
    if args.personality:
        personality = load_personality_preset(personality_name)
        if not personality:
            print(f"❌ Personality preset not found: {args.personality}")
            sys.exit(1)

    model = args.model or 'qwen2.5:32b'
    mode = args.mode or 'hearthfire'
    user = args.user or 'ka_tuar_el'

    # Determine test messages
    messages_to_run = []

    if args.message:
        messages_to_run = [{'id': 'adhoc', 'text': args.message, 'notes': 'Ad-hoc message'}]
    elif args.test:
        # Find the test in a suite
        suite_name = args.suite or 'calibration'
        all_msgs = load_test_messages(suite_name)
        found = [m for m in all_msgs if m['id'] == args.test]
        if not found:
            print(f"❌ Test '{args.test}' not found in suite '{suite_name}'")
            print(f"   Available: {', '.join(m['id'] for m in all_msgs)}")
            sys.exit(1)
        messages_to_run = found
    elif args.suite:
        messages_to_run = load_test_messages(args.suite)
        if not messages_to_run:
            print(f"❌ Suite not found: {args.suite}")
            sys.exit(1)
    else:
        print("❌ Specify one of: -m MESSAGE, --test TEST_ID, --suite SUITE_NAME")
        sys.exit(1)

    # Assemble prompt
    system_prompt = assemble(
        profile=profile,
        personality_preset=personality,
        mode=mode,
        user=user,
    )

    # Dry run?
    if args.dry_run:
        print(f"{'='*70}")
        print(f"PROFILE: {profile_name} | PERSONALITY: {personality_name} | MODE: {mode}")
        print(f"PROMPT LENGTH: {len(system_prompt)} chars (~{len(system_prompt)//4} tokens)")
        print(f"{'='*70}")
        print(system_prompt)
        print(f"{'='*70}")
        if messages_to_run:
            print(f"\nWould send {len(messages_to_run)} message(s):")
            for m in messages_to_run:
                print(f"  [{m['id']}] {m['text'][:80]}...")
        return

    # Run tests
    results = []
    total = len(messages_to_run)

    print(f"{'='*70}")
    print(f"BENCH: {profile_name} | {personality_name} | {model} | {mode}")
    print(f"Prompt: {len(system_prompt)} chars | Tests: {total}")
    print(f"{'='*70}")

    for i, msg in enumerate(messages_to_run):
        test_id = msg['id']
        text = msg['text']
        notes = msg.get('notes', '')

        print(f"\n[{i+1}/{total}] {test_id}: {text[:60]}...")

        result = run_prompt(
            system_prompt=system_prompt,
            user_message=text,
            model=model,
        )

        score_data = score_response(result.get('response', ''), msg)

        # Print scorecard
        print(f"\n{format_scorecard(result, score_data)}")
        print(f"\nRESPONSE:\n{result.get('response', result.get('error', '?'))}")

        results.append({
            'test_id': test_id,
            'message': text,
            'notes': notes,
            'response': result.get('response', ''),
            'success': result.get('success', False),
            'elapsed_seconds': result.get('elapsed_seconds', 0),
            'word_count': result.get('word_count', 0),
            'score': score_data,
            'error': result.get('error'),
        })

    # Summary
    if total > 1:
        print(f"\n{'='*70}")
        print("SUMMARY")
        print(f"{'='*70}")
        print(f"{'Test':<20} {'Score':>6} {'Words':>6} {'Time':>7} {'Penalties'}")
        print(f"{'-'*70}")
        for r in results:
            s = r['score']
            penalty_str = ', '.join(s.get('penalties', [])[:2]) or '✅ clean'
            print(f"{r['test_id']:<20} {s['score']:>5}/100 {s['word_count']:>5}w {r['elapsed_seconds']:>6.1f}s {penalty_str[:40]}")

        scores = [r['score']['score'] for r in results]
        avg = sum(scores) / len(scores) if scores else 0
        print(f"\nAVERAGE SCORE: {avg:.1f}/100")

    # Save if requested
    if args.save or args.suite:
        tag = f"{profile_name}_{personality_name}_{model.replace(':', '_')}"
        run_data = {
            'profile': profile_name,
            'personality_preset': personality_name,
            'model': model,
            'mode': mode,
            'user': user,
            'system_prompt_length': len(system_prompt),
            'timestamp': datetime.now().isoformat(),
            'results': results,
        }
        path = save_run(run_data, tag)
        print(f"\n💾 Results saved: {path}")


def cmd_compare(args):
    """Run same test(s) across two profiles and show diff."""
    if len(args.compare) != 2:
        print("❌ --compare needs exactly 2 profile names")
        sys.exit(1)

    profile_a, profile_b = args.compare
    model = args.model or 'qwen2.5:32b'
    personality_name = args.personality or 'default'
    personality = load_personality_preset(personality_name) if args.personality else {}

    # Determine messages
    if args.test:
        suite = args.suite or 'calibration'
        all_msgs = load_test_messages(suite)
        messages = [m for m in all_msgs if m['id'] == args.test]
    elif args.suite:
        messages = load_test_messages(args.suite)
    elif args.message:
        messages = [{'id': 'adhoc', 'text': args.message}]
    else:
        messages = load_test_messages('calibration')

    for msg in messages:
        print(f"\n{'='*70}")
        print(f"TEST: {msg['id']} — {msg['text'][:60]}...")
        print(f"{'='*70}")

        for pname in [profile_a, profile_b]:
            profile = load_profile(pname)
            if not profile:
                print(f"❌ Profile not found: {pname}")
                continue

            prompt = assemble(profile=profile, personality_preset=personality, mode=args.mode or 'hearthfire', user=args.user or 'ka_tuar_el')
            result = run_prompt(system_prompt=prompt, user_message=msg['text'], model=model)
            score_data = score_response(result.get('response', ''), msg)

            print(f"\n--- {pname} (score: {score_data['score']}/100, {result.get('elapsed_seconds',0):.1f}s, {score_data['word_count']}w) ---")
            print(result.get('response', result.get('error', '?')))


def cmd_list(what: str):
    """List available resources."""
    if what == 'models':
        models = list_models()
        print(f"Available Ollama models ({len(models)}):")
        for m in models:
            print(f"  {m}")
    elif what == 'profiles':
        print("Available profiles:")
        for f in sorted(PROFILES_DIR.glob('*.yaml')):
            data = __import__('yaml').safe_load(f.read_text()) or {}
            desc = data.get('description', '')
            print(f"  {f.stem:<30} {desc}")
    elif what == 'personalities':
        print("Available personality presets:")
        for f in sorted(PERSONALITIES_DIR.glob('*.yaml')):
            data = __import__('yaml').safe_load(f.read_text()) or {}
            desc = data.get('description', '')
            print(f"  {f.stem:<20} {desc}")
    elif what == 'suites':
        print("Available test suites:")
        for f in sorted(MESSAGES_DIR.glob('*.yaml')):
            data = __import__('yaml').safe_load(f.read_text()) or {}
            desc = data.get('description', '')
            count = len(data.get('messages', []))
            print(f"  {f.stem:<20} ({count} tests) {desc}")
    elif what == 'results':
        runs = list_runs(20)
        if not runs:
            print("No saved runs yet.")
            return
        print("Recent runs:")
        for r in runs:
            print(f"  {r['file']:<50} profile={r.get('profile','?')} model={r.get('model','?')} tests={r.get('test_count','?')}")


def main():
    parser = argparse.ArgumentParser(
        description="Iris Prompt Workbench — Test and compare prompt configurations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bench.py -m "hey what's up"                           Quick test
  bench.py --profile naked -m "hey what's up"            Naked model
  bench.py --profile identity_only --test greeting       Single test
  bench.py --profile full_stack --suite calibration      Full suite
  bench.py --profile full_stack --personality tars_75 --suite calibration
  bench.py --compare naked identity_only --test greeting Side-by-side
  bench.py --profile full_stack --dry-run                Show prompt only
  bench.py --list-models                                 Available models
        """
    )

    # Test selection
    parser.add_argument('-m', '--message', help='Ad-hoc message to send')
    parser.add_argument('--test', help='Run a specific test ID from a suite')
    parser.add_argument('--suite', help='Run a full test suite')

    # Configuration
    parser.add_argument('--profile', help='Layer profile (default: full_no_life)')
    parser.add_argument('--personality', help='Personality preset name')
    parser.add_argument('--model', help='Ollama model (default: qwen2.5:32b)')
    parser.add_argument('--mode', default='hearthfire', help='Iris mode (default: hearthfire)')
    parser.add_argument('--user', default='ka_tuar_el', help='User profile (default: ka_tuar_el)')

    # Actions
    parser.add_argument('--dry-run', action='store_true', help='Show assembled prompt without sending')
    parser.add_argument('--save', action='store_true', help='Force save results to file')
    parser.add_argument('--compare', nargs=2, metavar='PROFILE', help='Compare two profiles')
    parser.add_argument('--diff', nargs=2, metavar='FILE', help='Diff two saved result files')

    # Listings
    parser.add_argument('--list-models', action='store_true')
    parser.add_argument('--list-profiles', action='store_true')
    parser.add_argument('--list-personalities', action='store_true')
    parser.add_argument('--list-suites', action='store_true')
    parser.add_argument('--results', action='store_true', help='Show saved runs')

    args = parser.parse_args()

    # Handle list commands
    if args.list_models:
        cmd_list('models')
        return
    if args.list_profiles:
        cmd_list('profiles')
        return
    if args.list_personalities:
        cmd_list('personalities')
        return
    if args.list_suites:
        cmd_list('suites')
        return
    if args.results:
        cmd_list('results')
        return

    # Handle diff
    if args.diff:
        print(diff_runs(args.diff[0], args.diff[1]))
        return

    # Handle compare
    if args.compare:
        cmd_compare(args)
        return

    # Default: run test
    cmd_run(args)


if __name__ == '__main__':
    main()
