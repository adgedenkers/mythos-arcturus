#!/bin/bash
# DeepSeek-R1:32b solo benchmark run
# Run this once the model finishes downloading
# Usage: ./run_deepseek_solo.sh
set -e
cd /opt/mythos/orchestrator/benchmark

# Check model is available
if ! ollama list | grep -q "deepseek-r1:32b"; then
    echo "❌ deepseek-r1:32b not yet available — still downloading?"
    echo "   Check with: ollama list"
    exit 1
fi

echo ""
echo "══════════════════════════════════════════════════"
echo "  DeepSeek-R1:32b Solo Benchmark"
echo "  43 tasks — comparing against Round 2 results"
echo "══════════════════════════════════════════════════"
echo ""

# Write a single-model config on the fly
/opt/mythos/.venv/bin/python3 -c "
import json, pathlib
cfg = json.loads(pathlib.Path("bench_config_round2.json").read_text())
cfg["models"] = ["deepseek-r1:32b"]
cfg["run_id_prefix"] = "deepseek_solo"
cfg["notes"] = "DeepSeek-R1:32b solo run for comparison against Round 2"
pathlib.Path("bench_config_deepseek.json").write_text(json.dumps(cfg, indent=2))
print("Config written")
"

/opt/mythos/.venv/bin/python3 run_benchmark.py --config bench_config_deepseek.json "$@"
