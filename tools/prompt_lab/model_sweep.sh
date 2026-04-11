#!/usr/bin/env bash
#
# model_sweep.sh — Run the same suite across multiple models
# ============================================================
# Tests a bunch of models against a bunch of things.
# Saves each run, then prints a comparison table at the end.
#
# Usage:
#   ./model_sweep.sh --suite sovereignty --mode sovereign --personality sovereign
#   ./model_sweep.sh --suite calibration --models "qwen2.5:32b gemma3:27b phi4:14b"
#   ./model_sweep.sh --suite sovereignty --mode sovereign --personality sovereign --models "iris-thinking-v2 qwen2.5:32b gemma2:27b"
#
set -euo pipefail

BENCH="/opt/mythos/.venv/bin/python3 /opt/mythos/tools/prompt_lab/bench.py"
RESULTS_DIR="/opt/mythos/tools/prompt_lab/results"

# Defaults
SUITE="sovereignty"
MODE="sovereign"
PERSONALITY="sovereign"
PROFILE="full_no_life"
MODELS=""

# Parse args
while [[ $# -gt 0 ]]; do
    case $1 in
        --suite) SUITE="$2"; shift 2 ;;
        --mode) MODE="$2"; shift 2 ;;
        --personality) PERSONALITY="$2"; shift 2 ;;
        --profile) PROFILE="$2"; shift 2 ;;
        --models) MODELS="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

# Default model list if not specified
if [[ -z "$MODELS" ]]; then
    MODELS="iris-thinking-v2 qwen2.5:32b gemma3:27b mistral-small:24b phi4:14b"
fi

echo "============================================"
echo "  Model Sweep"
echo "============================================"
echo "  Suite:       $SUITE"
echo "  Mode:        $MODE"
echo "  Personality: $PERSONALITY"
echo "  Profile:     $PROFILE"
echo "  Models:      $MODELS"
echo "============================================"
echo ""

RUN_FILES=()

for MODEL in $MODELS; do
    echo ""
    echo "━━━ Testing: $MODEL ━━━"
    $BENCH \
        --profile "$PROFILE" \
        --mode "$MODE" \
        --personality "$PERSONALITY" \
        --model "$MODEL" \
        --suite "$SUITE" \
        --save

    # Capture the most recent result file
    LATEST=$(ls -t "$RESULTS_DIR"/run_*.json 2>/dev/null | head -1)
    if [[ -n "$LATEST" ]]; then
        RUN_FILES+=("$LATEST")
    fi
    echo ""
done

# Print comparison table
echo ""
echo "============================================"
echo "  SWEEP SUMMARY"
echo "============================================"
echo ""

# Header
printf "%-30s" "Model"

# Get test IDs from first run
if [[ ${#RUN_FILES[@]} -gt 0 ]]; then
    TEST_IDS=$(python3 -c "
import json
with open('${RUN_FILES[0]}') as f:
    data = json.load(f)
for r in data.get('results', []):
    print(r.get('test_id', '?'))
")
    for TID in $TEST_IDS; do
        printf "%15s" "$TID"
    done
    printf "%10s\n" "AVG"
    printf "%s\n" "$(printf '─%.0s' {1..150})"

    # Each model row
    for RF in "${RUN_FILES[@]}"; do
        python3 -c "
import json
with open('$RF') as f:
    data = json.load(f)
model = data.get('model', '?')
results = data.get('results', [])
scores = []
line = f'{model:<30}'
for r in results:
    s = r.get('score', {}).get('score', 0)
    scores.append(s)
    line += f'{s:>15}'
avg = sum(scores) / len(scores) if scores else 0
line += f'{avg:>10.1f}'
print(line)
"
    done
fi

echo ""
echo "Run files saved in: $RESULTS_DIR"
echo "Diff any two: bench --diff <file_a> <file_b>"
