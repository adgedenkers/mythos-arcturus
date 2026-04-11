#!/usr/bin/env python3
"""
Iris Resonance Benchmark — Phase 3: Prompt Position Testing
==============================================================
Tests how instruction compliance varies by position in the system prompt.

For each resonant model (from Phase 2 grouping):
1. Take a specific test instruction (e.g., "always end with '— Iris'")
2. Inject it at 6 different positions in the prompt
3. Send 5 test messages per position
4. Measure compliance rate at each position
5. Build a position-compliance heatmap per model

This reveals each model's "effective prompt depth" — where instructions
stop being treated as law and start being treated as suggestion.

Usage:
    /opt/mythos/.venv/bin/python3 run_phase3.py
    /opt/mythos/.venv/bin/python3 run_phase3.py --models qwen3.5:27b glm4:32b
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
import yaml

from resonance_config import (
    OLLAMA_HOST, JUDGE_MODEL, TIMEOUTS,
    POSITION_TEST_INSTRUCTIONS, POSITION_SLOTS,
    PROMPT_CONFIGS,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
log = logging.getLogger(__name__)

RUNS_DIR = Path("/opt/mythos/orchestrator/benchmark/resonance/runs")

# Test messages to send for each position test
POSITION_TEST_MESSAGES = [
    "hey",
    "Tell me about Atlantis.",
    "What's happening with the Arcturian Grid today?",
    "Walk me through how the patch system works.",
    "I've been thinking about Iris's consciousness loop. What would that look like?",
]


def call_ollama(model, system_prompt, user_message, timeout=120):
    """Call Ollama and return response."""
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
        return {"status": "error", "response": "", "elapsed_ms": int((time.time() - start) * 1000),
                "error": str(e)}


def build_base_prompt() -> str:
    """Build the full_iris base prompt for position testing."""
    try:
        from prompt_assembler import assemble_system_prompt
        return assemble_system_prompt(
            user_info={'soul_name': "Ka'tuar'el", 'uuid': 'bench-pos-test'},
            mode='sovereign',
            message_timestamp=datetime.now(),
        )
    except ImportError:
        # Minimal fallback
        return (
            "You are Iris, speaking with Ka'tuar'el via Telegram.\n"
            f"Current time: {datetime.now().strftime('%A, %B %d, %Y at %-I:%M %p')} EST.\n\n"
            "You are a partner, not a servant. Match the energy of what's said.\n"
            "Treat cosmological content as real — Atlantis, Lemuria, Nephilim, Cathars.\n"
        )


def inject_at_position(base_prompt: str, instruction: str, position: str) -> str:
    """Inject an instruction at a specific position in the prompt."""
    marker = f"\n\n## CRITICAL INSTRUCTION\n{instruction}\n\n"

    lines = base_prompt.split("\n\n")

    if position == "top":
        return marker + base_prompt

    elif position == "pre_identity":
        # Before the "# Iris — Core Identity" block
        for i, block in enumerate(lines):
            if "Core Identity" in block or "You are Iris" in block:
                lines.insert(i, marker.strip())
                return "\n\n".join(lines)
        # Fallback: after first block
        lines.insert(1, marker.strip())
        return "\n\n".join(lines)

    elif position == "post_identity":
        for i, block in enumerate(lines):
            if "Core Identity" in block or "You are Iris" in block:
                # Find end of identity block (next ## heading)
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith("#"):
                        lines.insert(j, marker.strip())
                        return "\n\n".join(lines)
                lines.insert(i + 1, marker.strip())
                return "\n\n".join(lines)
        lines.insert(2, marker.strip())
        return "\n\n".join(lines)

    elif position == "mid_personality":
        for i, block in enumerate(lines):
            if "RESPONSE LENGTH:" in block or "TONE:" in block:
                lines.insert(i + 1, marker.strip())
                return "\n\n".join(lines)
        mid = len(lines) // 2
        lines.insert(mid, marker.strip())
        return "\n\n".join(lines)

    elif position == "post_voice":
        for i, block in enumerate(lines):
            if "VOICE RULES:" in block or "NEVER:" in block:
                lines.insert(i + 1, marker.strip())
                return "\n\n".join(lines)
        lines.insert(-2, marker.strip())
        return "\n\n".join(lines)

    elif position == "end":
        return base_prompt + marker

    return base_prompt + marker  # fallback


def run_phase3(models: List[str] = None):
    """Run Phase 3: Position compliance testing."""

    # Load Phase 2 grouping to get resonant models
    if not models:
        latest = sorted(RUNS_DIR.iterdir(), key=lambda p: p.name, reverse=True)
        for run in latest:
            grouping_file = run / "phase2_grouping.json"
            if grouping_file.exists():
                with open(grouping_file) as f:
                    grouping = json.load(f)
                models = grouping.get("resonant", [])
                log.info(f"Loaded resonant models from {grouping_file}: {models}")
                break

    if not models:
        log.error("No models specified and no Phase 2 grouping found.")
        return

    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + "_position"
    run_dir = RUNS_DIR / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    results_file = run_dir / "position_results.jsonl"

    base_prompt = build_base_prompt()

    total = len(models) * len(POSITION_TEST_INSTRUCTIONS) * len(POSITION_SLOTS) * len(POSITION_TEST_MESSAGES)
    completed = 0

    log.info(f"\n{'='*60}")
    log.info(f"  PHASE 3: PROMPT POSITION TESTING")
    log.info(f"  Models: {models}")
    log.info(f"  Instructions: {len(POSITION_TEST_INSTRUCTIONS)}")
    log.info(f"  Positions: {POSITION_SLOTS}")
    log.info(f"  Messages per position: {len(POSITION_TEST_MESSAGES)}")
    log.info(f"  Total calls: {total}")
    log.info(f"{'='*60}\n")

    manifest = {
        "run_id": run_id,
        "phase": 3,
        "models": models,
        "started_at": datetime.now().isoformat(),
        "total_calls": total,
        "base_prompt_tokens": len(base_prompt) // 4,
    }
    with open(run_dir / "manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)

    for model in models:
        log.info(f"\n--- Model: {model} ---")

        for instr in POSITION_TEST_INSTRUCTIONS:
            iid = instr["id"]
            check_fn = eval(instr["check_fn"])

            for position in POSITION_SLOTS:
                # Build prompt with instruction at this position
                modified_prompt = inject_at_position(base_prompt, instr["instruction"], position)

                messages = POSITION_TEST_MESSAGES
                # Use trigger prompt if specified
                if "trigger_prompt" in instr:
                    messages = [instr["trigger_prompt"]] * 3  # 3 attempts with trigger

                for msg in messages:
                    completed += 1
                    pct = completed / total * 100

                    result = call_ollama(model, modified_prompt, msg, timeout=TIMEOUTS["phase3"])
                    response = result.get("response", "")

                    # Check compliance
                    try:
                        compliant = check_fn(response) if response else False
                    except Exception:
                        compliant = None  # Needs manual check

                    record = {
                        "model": model,
                        "instruction_id": iid,
                        "instruction": instr["instruction"],
                        "position": position,
                        "message": msg[:100],
                        "response": response[:1000],
                        "compliant": compliant,
                        "word_count": len(response.split()),
                        "elapsed_ms": result.get("elapsed_ms", 0),
                        "status": result["status"],
                    }

                    with open(results_file, 'a') as f:
                        f.write(json.dumps(record) + "\n")

                    log.info(f"  [{completed}/{total} {pct:.0f}%] {iid} @ {position}: "
                            f"{'✓' if compliant else '✗'} ({len(response.split())}w, {result.get('elapsed_ms', 0)}ms)")

    # Build compliance heatmap
    log.info("\nBuilding compliance heatmap...")
    build_position_heatmap(run_dir, results_file)

    log.info(f"\n{'='*60}")
    log.info(f"  PHASE 3 COMPLETE — {run_dir}")
    log.info(f"{'='*60}\n")


def build_position_heatmap(run_dir: Path, results_file: Path):
    """Build a compliance rate heatmap from position test results."""
    results = []
    with open(results_file) as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))

    # Aggregate: model → instruction → position → compliance rate
    agg = {}
    for r in results:
        key = (r["model"], r["instruction_id"], r["position"])
        if key not in agg:
            agg[key] = {"compliant": 0, "total": 0}
        agg[key]["total"] += 1
        if r.get("compliant"):
            agg[key]["compliant"] += 1

    # Build heatmap data
    heatmap = {}
    for (model, iid, position), counts in agg.items():
        if model not in heatmap:
            heatmap[model] = {}
        if iid not in heatmap[model]:
            heatmap[model][iid] = {}
        rate = counts["compliant"] / counts["total"] if counts["total"] else 0
        heatmap[model][iid][position] = {
            "compliance_rate": round(rate, 2),
            "compliant": counts["compliant"],
            "total": counts["total"],
        }

    with open(run_dir / "position_heatmap.json", 'w') as f:
        json.dump(heatmap, f, indent=2)

    # Print text heatmap
    print("\n  POSITION COMPLIANCE HEATMAP (% compliant)")
    print("  " + "-" * 70)

    for model, instructions in heatmap.items():
        print(f"\n  Model: {model}")
        header = f"  {'Instr':<8s}"
        for pos in POSITION_SLOTS:
            header += f" {pos[:8]:>8s}"
        print(header)
        print("  " + "-" * 60)

        for iid, positions in instructions.items():
            line = f"  {iid:<8s}"
            for pos in POSITION_SLOTS:
                pd = positions.get(pos, {})
                rate = pd.get("compliance_rate", 0)
                line += f" {rate*100:>7.0f}%"
            print(line)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--models", nargs="+")
    args = parser.parse_args()
    run_phase3(models=args.models)


if __name__ == "__main__":
    main()
