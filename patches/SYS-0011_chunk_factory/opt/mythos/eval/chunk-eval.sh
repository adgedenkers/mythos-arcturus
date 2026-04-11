#!/bin/bash
# chunk-eval — Convenience wrapper for the Ollama chunk builder eval harness
# Usage:
#   chunk-eval people_lookup                    # Run with default model
#   chunk-eval people_lookup qwen3-coder:30b    # Specify model
#   chunk-eval people_lookup llama3.3:70b 10    # Specify model + max iterations
#   chunk-eval --list                           # List available challenges
#   chunk-eval --models                         # List available models
#   chunk-eval --compare people_lookup          # Compare all model results for a challenge

set -e

EVAL_DIR="/opt/mythos/eval"
PYTHON="/opt/mythos/.venv/bin/python3"
BUILDER="$EVAL_DIR/ollama_builder.py"

if [ "$1" == "--list" ]; then
    $PYTHON "$BUILDER" --list-challenges
    exit 0
fi

if [ "$1" == "--models" ]; then
    $PYTHON "$BUILDER" --list-models
    exit 0
fi

if [ "$1" == "--compare" ]; then
    CHALLENGE="${2:?Usage: chunk-eval --compare <challenge_id>}"
    RESULTS_DIR="$EVAL_DIR/results/$CHALLENGE"
    if [ ! -d "$RESULTS_DIR" ]; then
        echo "No results found for challenge: $CHALLENGE"
        exit 1
    fi
    echo ""
    echo "=== Results for challenge: $CHALLENGE ==="
    echo ""
    for report in $(find "$RESULTS_DIR" -name "report.json" -type f | sort); do
        MODEL=$(python3 -c "import json; print(json.load(open('$report'))['model'])")
        SCORE=$(python3 -c "import json; print(json.load(open('$report'))['best_composite_score'])")
        PASS=$(python3 -c "import json; print('PASS' if json.load(open('$report'))['final_pass'] else 'FAIL')")
        ITERS=$(python3 -c "import json; print(json.load(open('$report'))['iterations_used'])")
        TIMESTAMP=$(basename "$(dirname "$report")")
        printf "  %-25s  Score: %.1f%%  %s  Iters: %s  (%s)\n" "$MODEL" "$(echo "$SCORE * 100" | bc)" "$PASS" "$ITERS" "$TIMESTAMP"
    done
    echo ""
    exit 0
fi

# Default: run a challenge
CHALLENGE="${1:?Usage: chunk-eval <challenge_id> [model] [max_iterations]}"
MODEL="${2:-qwen3-coder:30b}"
MAX_ITER="${3:-5}"

SPEC="$EVAL_DIR/challenges/$CHALLENGE/challenge_spec.json"
if [ ! -f "$SPEC" ]; then
    echo "Challenge not found: $SPEC"
    echo "Available challenges:"
    $PYTHON "$BUILDER" --list-challenges
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║         CHUNK FACTORY — Eval Run             ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  Challenge: $CHALLENGE"
echo "║  Model:     $MODEL"
echo "║  Max iter:  $MAX_ITER"
echo "╚══════════════════════════════════════════════╝"
echo ""

$PYTHON "$BUILDER" \
    --challenge "$SPEC" \
    --model "$MODEL" \
    --max-iterations "$MAX_ITER" \
    --verbose
