#!/usr/bin/env bash
#
# layer_walk.sh — Incrementally add layers and watch the response change
# ========================================================================
# Tests the same prompt(s) across profiles from naked → full_stack,
# optionally for two models side by side.
#
# Usage:
#   ./layer_walk.sh --test ego_inflation --suite sovereignty --mode sovereign
#   ./layer_walk.sh --test soul_code_synthesis --suite sovereignty --mode sovereign --models "qwen2.5:32b iris-thinking-v2"
#   ./layer_walk.sh --suite sovereignty --mode sovereign  # all tests in suite
#
set -euo pipefail

BENCH="/opt/mythos/.venv/bin/python3 /opt/mythos/tools/prompt_lab/bench.py"
RESULTS_DIR="/opt/mythos/tools/prompt_lab/results"

# Layer progression — each profile adds one more layer
PROFILES=(
    "naked"
    "identity_only"
    "identity_personality"
    "identity_personality_voice"
    "full_no_life"
    "full_stack"
)

# Defaults
TEST=""
SUITE="sovereignty"
MODE="sovereign"
PERSONALITY="sovereign"
MODELS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --test) TEST="$2"; shift 2 ;;
        --suite) SUITE="$2"; shift 2 ;;
        --mode) MODE="$2"; shift 2 ;;
        --personality) PERSONALITY="$2"; shift 2 ;;
        --models) MODELS="$2"; shift 2 ;;
        *) echo "Unknown arg: $1"; exit 1 ;;
    esac
done

if [[ -z "$MODELS" ]]; then
    MODELS="qwen2.5:32b"
fi

# Build the bench test arg
BENCH_TEST_ARG=""
if [[ -n "$TEST" ]]; then
    BENCH_TEST_ARG="--test $TEST --suite $SUITE"
else
    BENCH_TEST_ARG="--suite $SUITE"
fi

echo "============================================"
echo "  Layer Walk"
echo "============================================"
echo "  Test:        ${TEST:-"(full suite: $SUITE)"}"
echo "  Suite:       $SUITE"
echo "  Mode:        $MODE"
echo "  Personality: $PERSONALITY"
echo "  Models:      $MODELS"
echo "  Profiles:    ${PROFILES[*]}"
echo "============================================"
echo ""

# Collect all run files for summary
declare -A RUN_MAP  # key = "model|profile" → filepath

for MODEL in $MODELS; do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "  MODEL: $MODEL"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    for PROFILE in "${PROFILES[@]}"; do
        echo ""
        echo "  ── Profile: $PROFILE ──"

        # For naked/identity_only, mode and personality don't apply
        # but bench.py handles missing mode files gracefully
        $BENCH \
            --profile "$PROFILE" \
            --mode "$MODE" \
            --personality "$PERSONALITY" \
            --model "$MODEL" \
            $BENCH_TEST_ARG \
            --save

        LATEST=$(ls -t "$RESULTS_DIR"/run_*.json 2>/dev/null | head -1)
        if [[ -n "$LATEST" ]]; then
            RUN_MAP["${MODEL}|${PROFILE}"]="$LATEST"
        fi
    done
done

# Summary table
echo ""
echo ""
echo "============================================"
echo "  LAYER WALK SUMMARY"
echo "============================================"
echo ""

for MODEL in $MODELS; do
    echo "Model: $MODEL"
    printf "  %-35s %8s %8s %8s\n" "Profile" "Score" "Words" "Time"
    printf "  %s\n" "$(printf '─%.0s' {1..65})"

    for PROFILE in "${PROFILES[@]}"; do
        KEY="${MODEL}|${PROFILE}"
        RF="${RUN_MAP[$KEY]:-}"
        if [[ -n "$RF" && -f "$RF" ]]; then
            python3 -c "
import json
with open('$RF') as f:
    data = json.load(f)
results = data.get('results', [])
scores = [r.get('score',{}).get('score',0) for r in results]
words = [r.get('score',{}).get('word_count',0) for r in results]
times = [r.get('elapsed_seconds',0) for r in results]
avg_s = sum(scores)/len(scores) if scores else 0
avg_w = sum(words)/len(words) if words else 0
avg_t = sum(times)/len(times) if times else 0
print(f'  {\"$PROFILE\":<35} {avg_s:>7.1f} {avg_w:>7.0f}w {avg_t:>7.1f}s')
"
        else
            printf "  %-35s %8s\n" "$PROFILE" "(no data)"
        fi
    done
    echo ""
done

echo "Run files saved in: $RESULTS_DIR"
