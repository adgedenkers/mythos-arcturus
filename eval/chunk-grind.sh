#!/bin/bash
# chunk-grind — Run the multi-pass grinder on a build plan
# Usage:
#   chunk-grind voice_memo_search                    # Default model
#   chunk-grind voice_memo_search qwen3-coder:30b    # Specific model
#   chunk-grind voice_memo_search llama3.3:70b 10    # Model + max retries

set -e
PYTHON="/opt/mythos/.venv/bin/python3"
GRINDER="/opt/mythos/eval/ollama_grinder.py"
EVAL_DIR="/opt/mythos/eval"

PLAN="${1:?Usage: chunk-grind <plan_id> [model] [max_retries]}"
MODEL="${2:-qwen3-coder:30b}"
MAX_RETRIES="${3:-5}"

# Find the build plan
PLAN_FILE="$EVAL_DIR/challenges/$PLAN/build_plan.json"
if [ ! -f "$PLAN_FILE" ]; then
    echo "Build plan not found: $PLAN_FILE"
    echo ""
    echo "Available plans:"
    find "$EVAL_DIR/challenges" -name "build_plan.json" -type f 2>/dev/null | while read f; do
        DIR=$(dirname "$f")
        echo "  $(basename "$DIR")"
    done
    exit 1
fi

echo ""
echo "╔══════════════════════════════════════════════╗"
echo "║         CHUNK GRINDER — Build Run            ║"
echo "╠══════════════════════════════════════════════╣"
echo "║  Plan:      $PLAN"
echo "║  Model:     $MODEL"
echo "║  Retries:   $MAX_RETRIES"
echo "╚══════════════════════════════════════════════╝"
echo ""

$PYTHON "$GRINDER" \
    --plan "$PLAN_FILE" \
    --model "$MODEL" \
    --max-retries "$MAX_RETRIES" \
    --verbose
