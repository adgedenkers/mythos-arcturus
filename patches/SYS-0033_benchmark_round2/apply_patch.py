"""
SYS-0033: Benchmark Round 2
- Deploys bench_config_round2.json
- Deploys run_benchmark_round2.sh — wrapper that sets config and kicks off the runner
- Deploys deepseek_solo.sh — single-model run for deepseek-r1:32b when ready
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=33,
    description='benchmark round 2 - 9 model run config and launcher',
    patch_type='MINOR',
)
patch.begin()

PATCH_DIR = Path(__file__).parent
BENCH_DIR = Path('/opt/mythos/orchestrator/benchmark')

# ── 1. Deploy round 2 config ──────────────────────────────────────────────────

patch.deploy_file(
    str(PATCH_DIR / 'opt/mythos/orchestrator/benchmark/bench_config_round2.json'),
    str(BENCH_DIR / 'bench_config_round2.json'),
)
print("  ✓ bench_config_round2.json deployed")

# ── 2. Write run_benchmark_round2.sh ─────────────────────────────────────────

run_script = BENCH_DIR / 'run_benchmark_round2.sh'
run_script.write_text(
    '#!/bin/bash\n'
    '# Round 2 benchmark — 9 models, all 43 tasks\n'
    '# Usage: ./run_benchmark_round2.sh\n'
    'set -e\n'
    'cd /opt/mythos/orchestrator/benchmark\n'
    'echo ""\n'
    'echo "══════════════════════════════════════════════════"\n'
    'echo "  Mythos Model Benchmark — Round 2"\n'
    'echo "  Models: qwen3:30b-a3b, qwen2.5:32b, command-r:35b,"\n'
    'echo "          mistral-small:24b, gemma2:27b, nous-hermes2,"\n'
    'echo "          phi4:14b, qwen3:14b, yi:34b-chat"\n'
    'echo "  Tasks:  43 across 6 categories"\n'
    'echo "══════════════════════════════════════════════════"\n'
    'echo ""\n'
    '/opt/mythos/.venv/bin/python3 run_benchmark.py --config bench_config_round2.json "$@"\n'
)
run_script.chmod(0o755)
print("  ✓ run_benchmark_round2.sh written")

# ── 3. Write deepseek_solo.sh ─────────────────────────────────────────────────

deepseek_script = BENCH_DIR / 'run_deepseek_solo.sh'
deepseek_script.write_text(
    '#!/bin/bash\n'
    '# DeepSeek-R1:32b solo benchmark run\n'
    '# Run this once the model finishes downloading\n'
    '# Usage: ./run_deepseek_solo.sh\n'
    'set -e\n'
    'cd /opt/mythos/orchestrator/benchmark\n'
    '\n'
    '# Check model is available\n'
    'if ! ollama list | grep -q "deepseek-r1:32b"; then\n'
    '    echo "❌ deepseek-r1:32b not yet available — still downloading?"\n'
    '    echo "   Check with: ollama list"\n'
    '    exit 1\n'
    'fi\n'
    '\n'
    'echo ""\n'
    'echo "══════════════════════════════════════════════════"\n'
    'echo "  DeepSeek-R1:32b Solo Benchmark"\n'
    'echo "  43 tasks — comparing against Round 2 results"\n'
    'echo "══════════════════════════════════════════════════"\n'
    'echo ""\n'
    '\n'
    '# Write a single-model config on the fly\n'
    '/opt/mythos/.venv/bin/python3 -c "\n'
    'import json, pathlib\n'
    'cfg = json.loads(pathlib.Path(\"bench_config_round2.json\").read_text())\n'
    'cfg[\"models\"] = [\"deepseek-r1:32b\"]\n'
    'cfg[\"run_id_prefix\"] = \"deepseek_solo\"\n'
    'cfg[\"notes\"] = \"DeepSeek-R1:32b solo run for comparison against Round 2\"\n'
    'pathlib.Path(\"bench_config_deepseek.json\").write_text(json.dumps(cfg, indent=2))\n'
    'print(\"Config written\")\n'
    '"\n'
    '\n'
    '/opt/mythos/.venv/bin/python3 run_benchmark.py --config bench_config_deepseek.json "$@"\n'
)
deepseek_script.chmod(0o755)
print("  ✓ run_deepseek_solo.sh written")

# ── 4. Verify run_benchmark.py accepts --config flag ─────────────────────────

runner = BENCH_DIR / 'run_benchmark.py'
runner_text = runner.read_text()

if '--config' not in runner_text:
    # Runner doesn't support --config flag yet — patch it in
    # Find the argparse section
    old_argparse = 'parser = argparse.ArgumentParser'
    if old_argparse in runner_text:
        # Add config argument after parser creation
        old_add_arg = 'parser.add_argument('
        # Find first add_argument and prepend config arg before it
        insert_point = runner_text.index(old_add_arg)
        config_arg = (
            "parser.add_argument('--config', type=str, default='bench_config.json',\n"
            "                    help='Path to benchmark config JSON')\n    "
        )
        runner_text = runner_text[:insert_point] + config_arg + runner_text[insert_point:]
        runner.write_text(runner_text)
        print("  ✓ Patched run_benchmark.py to accept --config flag")
    else:
        print("  ⚠ Could not patch --config flag — check run_benchmark.py manually")
        print("    Run with: python3 run_benchmark.py  (then edit bench_config.json first)")
else:
    print("  ✓ run_benchmark.py already accepts --config flag")

# ── Done ──────────────────────────────────────────────────────────────────────

patch.finish()

print()
print("╔══════════════════════════════════════════════════╗")
print("║  SYS-0033: Benchmark Round 2 ready.             ║")
print("║                                                  ║")
print("║  To run:                                         ║")
print("║    cd /opt/mythos/orchestrator/benchmark         ║")
print("║    ./run_benchmark_round2.sh                     ║")
print("║                                                  ║")
print("║  DeepSeek solo (when download done):             ║")
print("║    ./run_deepseek_solo.sh                        ║")
print("╚══════════════════════════════════════════════════╝")
