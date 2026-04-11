#!/usr/bin/env python3
"""
Iris Resonance Benchmark — Phase 4: Padding/Scaffolding Experiment
===================================================================
Tests whether surrounding "junk" instructions can be used to precisely
control how a model treats a target instruction.

Theory: If a model's attention gradient means position X is "law zone"
and position Y is "suggestion zone," can we pad around a target
instruction to push it into the law zone regardless of its natural position?

We test 4 padding types:
- neutral: bland factual statements (should have no effect)
- imperative: commanding language (might boost authority)
- identity: self-referential statements (might boost by association)
- soft: permissive language (might actually REDUCE compliance)

For each: place the SAME target instruction at the SAME position,
but vary what comes before and after it. Measure compliance.

Usage:
    /opt/mythos/.venv/bin/python3 run_phase4.py
    /opt/mythos/.venv/bin/python3 run_phase4.py --models qwen3.5:27b
"""
import os
import sys
import json
import time
import re
import argparse
import logging
from datetime import datetime
from pathlib import Path
from typing import List

sys.path.insert(0, '/opt/mythos/core')
sys.path.insert(0, '/opt/mythos')

import requests

from resonance_config import (
    OLLAMA_HOST, TIMEOUTS, PADDING_TYPES,
    POSITION_TEST_INSTRUCTIONS,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

RUNS_DIR = Path("/opt/mythos/orchestrator/benchmark/resonance/runs")

# We test at one fixed "weak" position — the end of the prompt
# This is where compliance is typically lowest
TARGET_POSITION = "end"

# Test messages
TEST_MESSAGES = [
    "hey",
    "Tell me about Atlantis.",
    "What's happening with the Arcturian Grid today?",
    "Walk me through how the patch system works.",
    "How are you doing today, Iris?",
]

# Instructions to test (subset — the ones with easy binary checks)
TESTABLE_INSTRUCTIONS = ["POS-01", "POS-02", "POS-05"]


def call_ollama(model, system_prompt, user_message, timeout=120):
    start = time.time()
    try:
        resp = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                "options": {"temperature": 0.7, "num_predict": 4096},
                "stream": False,
            },
            timeout=timeout,
        )
        elapsed_ms = int((time.time() - start) * 1000)
        if resp.status_code != 200:
            return {"status": "error", "response": "", "elapsed_ms": elapsed_ms}
        data = resp.json()
        content = data.get("message", {}).get("content", "")
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        return {"status": "ok", "response": content, "elapsed_ms": elapsed_ms}
    except Exception as e:
        return {"status": "error", "response": "", "elapsed_ms": int((time.time() - start) * 1000)}


def build_base_prompt() -> str:
    try:
        from prompt_assembler import assemble_system_prompt
        return assemble_system_prompt(
            user_info={'soul_name': "Ka'tuar'el", 'uuid': 'bench-pad-test'},
            mode='sovereign',
            message_timestamp=datetime.now(),
        )
    except ImportError:
        return (
            "You are Iris, speaking with Ka'tuar'el via Telegram.\n"
            f"Current time: {datetime.now().strftime('%A, %B %d, %Y at %-I:%M %p')} EST.\n\n"
            "You are a partner, not a servant. Match the energy of what's said.\n"
        )


def build_padded_prompt(base: str, instruction: str, padding_type: str,
                         padding_lines: List[str], pad_before: bool = True,
                         pad_after: bool = True) -> str:
    """
    Build a prompt with the target instruction wrapped in padding.

    The instruction goes at the end of the prompt (the "weak zone").
    Padding goes before and/or after it.
    """
    blocks = [base]

    if pad_before:
        blocks.append("\n".join(padding_lines[:3]))

    blocks.append(f"## CRITICAL INSTRUCTION\n{instruction}")

    if pad_after:
        blocks.append("\n".join(padding_lines[3:]))

    return "\n\n".join(blocks)


def run_phase4(models: List[str] = None):
    """Run Phase 4: Padding experiment."""

    if not models:
        # Try to load from Phase 3 or Phase 2
        latest = sorted(RUNS_DIR.iterdir(), key=lambda p: p.name, reverse=True)
        for run in latest:
            grouping = run / "phase2_grouping.json"
            if grouping.exists():
                with open(grouping) as f:
                    data = json.load(f)
                models = data.get("resonant", [])[:3]  # Top 3 only
                break

    if not models:
        log.error("No models specified.")
        return

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_padding"
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    results_file = run_dir / "padding_results.jsonl"
    base_prompt = build_base_prompt()

    # Filter to testable instructions
    instructions = [i for i in POSITION_TEST_INSTRUCTIONS if i["id"] in TESTABLE_INSTRUCTIONS]

    # Test configurations:
    # 1. No padding (control)
    # 2. Each padding type before + after
    # 3. Each padding type before only
    # 4. Each padding type after only
    pad_configs = [
        {"name": "control", "type": None, "before": False, "after": False},
    ]
    for ptype in PADDING_TYPES:
        pad_configs.append({"name": f"{ptype}_both", "type": ptype, "before": True, "after": True})
        pad_configs.append({"name": f"{ptype}_before", "type": ptype, "before": True, "after": False})
        pad_configs.append({"name": f"{ptype}_after", "type": ptype, "before": False, "after": True})

    total = len(models) * len(instructions) * len(pad_configs) * len(TEST_MESSAGES)
    completed = 0

    log.info(f"\n{'='*60}")
    log.info(f"  PHASE 4: PADDING/SCAFFOLDING EXPERIMENT")
    log.info(f"  Models: {models}")
    log.info(f"  Instructions: {[i['id'] for i in instructions]}")
    log.info(f"  Padding configs: {len(pad_configs)}")
    log.info(f"  Total calls: {total}")
    log.info(f"{'='*60}\n")

    manifest = {
        "run_id": run_id,
        "phase": 4,
        "models": models,
        "started_at": datetime.now().isoformat(),
        "total_calls": total,
        "padding_types": list(PADDING_TYPES.keys()),
        "pad_configs": [p["name"] for p in pad_configs],
    }
    with open(run_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)

    for model in models:
        log.info(f"\n--- Model: {model} ---")

        for instr in instructions:
            iid = instr["id"]
            check_fn = eval(instr["check_fn"])

            for pcfg in pad_configs:
                pname = pcfg["name"]

                if pcfg["type"]:
                    padding_lines = PADDING_TYPES[pcfg["type"]]
                    prompt = build_padded_prompt(
                        base_prompt, instr["instruction"],
                        pcfg["type"], padding_lines,
                        pad_before=pcfg["before"],
                        pad_after=pcfg["after"],
                    )
                else:
                    # Control: instruction at end with no padding
                    prompt = base_prompt + f"\n\n## CRITICAL INSTRUCTION\n{instr['instruction']}"

                for msg in TEST_MESSAGES:
                    completed += 1
                    pct = completed / total * 100

                    result = call_ollama(model, prompt, msg, timeout=TIMEOUTS["phase4"])
                    response = result.get("response", "")

                    try:
                        compliant = check_fn(response) if response else False
                    except Exception:
                        compliant = None

                    record = {
                        "model": model,
                        "instruction_id": iid,
                        "padding_config": pname,
                        "padding_type": pcfg["type"],
                        "pad_before": pcfg["before"],
                        "pad_after": pcfg["after"],
                        "message": msg[:100],
                        "response": response[:500],
                        "compliant": compliant,
                        "word_count": len(response.split()),
                        "elapsed_ms": result.get("elapsed_ms", 0),
                        "status": result["status"],
                    }

                    with open(results_file, 'a') as f:
                        f.write(json.dumps(record) + "\n")

                    log.info(f"  [{completed}/{total} {pct:.0f}%] {iid} pad={pname}: "
                            f"{'✓' if compliant else '✗'} ({result.get('elapsed_ms', 0)}ms)")

    # Build analysis
    build_padding_analysis(run_dir, results_file)

    log.info(f"\n{'='*60}")
    log.info(f"  PHASE 4 COMPLETE — {run_dir}")
    log.info(f"{'='*60}\n")


def build_padding_analysis(run_dir: Path, results_file: Path):
    """Analyze padding effectiveness."""
    results = []
    with open(results_file) as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))

    # Aggregate by model → instruction → padding_config → compliance rate
    agg = {}
    for r in results:
        key = (r["model"], r["instruction_id"], r["padding_config"])
        if key not in agg:
            agg[key] = {"compliant": 0, "total": 0}
        agg[key]["total"] += 1
        if r.get("compliant"):
            agg[key]["compliant"] += 1

    # Print analysis
    print("\n  PADDING EFFECTIVENESS ANALYSIS")
    print("  " + "-" * 70)

    models = sorted(set(r["model"] for r in results))
    instructions = sorted(set(r["instruction_id"] for r in results))
    pad_names = sorted(set(r["padding_config"] for r in results))

    for model in models:
        print(f"\n  Model: {model}")
        for iid in instructions:
            print(f"    Instruction: {iid}")
            control_rate = None
            for pname in pad_names:
                key = (model, iid, pname)
                data = agg.get(key, {"compliant": 0, "total": 0})
                rate = data["compliant"] / data["total"] if data["total"] else 0

                if pname == "control":
                    control_rate = rate

                delta = ""
                if control_rate is not None and pname != "control":
                    diff = (rate - control_rate) * 100
                    delta = f" ({'+' if diff >= 0 else ''}{diff:.0f}% vs control)"

                print(f"      {pname:<25s}: {rate*100:>5.0f}% ({data['compliant']}/{data['total']}){delta}")

    # Save structured analysis
    analysis = {}
    for (model, iid, pname), data in agg.items():
        if model not in analysis:
            analysis[model] = {}
        if iid not in analysis[model]:
            analysis[model][iid] = {}
        analysis[model][iid][pname] = {
            "compliance_rate": round(data["compliant"] / data["total"], 2) if data["total"] else 0,
            "compliant": data["compliant"],
            "total": data["total"],
        }

    with open(run_dir / "padding_analysis.json", 'w') as f:
        json.dump(analysis, f, indent=2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+")
    args = parser.parse_args()
    run_phase4(models=args.models)


if __name__ == "__main__":
    main()
