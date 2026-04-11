#!/bin/bash
# Round 2 benchmark — 9 models, all 43 tasks
# Usage: ./run_benchmark_round2.sh
set -e
cd /opt/mythos/orchestrator/benchmark
echo ""
echo "══════════════════════════════════════════════════"
echo "  Mythos Model Benchmark — Round 2"
echo "  Models: qwen3:30b-a3b, qwen2.5:32b, command-r:35b,"
echo "          mistral-small:24b, gemma2:27b, nous-hermes2,"
echo "          phi4:14b, qwen3:14b, yi:34b-chat"
echo "  Tasks:  43 across 6 categories"
echo "══════════════════════════════════════════════════"
echo ""
/opt/mythos/.venv/bin/python3 run_benchmark.py --config bench_config_round2.json "$@"
