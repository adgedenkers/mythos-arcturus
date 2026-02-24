#!/bin/bash
# layer_test.sh — Run a message through every profile and collect results
# Usage: ./layer_test.sh "hey whats up"
#        ./layer_test.sh  (uses default greeting)

set -e

BENCH="/opt/mythos/.venv/bin/python3 /opt/mythos/tools/prompt_lab/bench.py"
MSG="${1:-hey whats up}"
OUT=$(mktemp /tmp/bench_results_XXXX.txt)

PROFILES=(
    naked
    identity_only
    identity_personality
    identity_personality_voice
    full_no_life
    full_stack
)

echo "=== LAYER ISOLATION TEST ===" > "$OUT"
echo "Message: $MSG" >> "$OUT"
echo "Model: qwen2.5:32b" >> "$OUT"
echo "Date: $(date)" >> "$OUT"
echo "Profiles: ${#PROFILES[@]}" >> "$OUT"

for i in "${!PROFILES[@]}"; do
    p="${PROFILES[$i]}"
    n=$((i + 1))
    echo -n "[$n/${#PROFILES[@]}] $p..."
    echo "" >> "$OUT"
    echo "================================================================" >> "$OUT"
    echo "PROFILE: $p ($n/${#PROFILES[@]})" >> "$OUT"
    echo "================================================================" >> "$OUT"
    $BENCH --profile "$p" -m "$MSG" >> "$OUT" 2>&1
    echo " done"
done

echo "" >> "$OUT"
echo "================================================================" >> "$OUT"
echo "END OF LAYER ISOLATION TEST" >> "$OUT"
echo "================================================================" >> "$OUT"

cat "$OUT" | xclip -selection clipboard
echo ""
echo "✓ All ${#PROFILES[@]} profiles complete"
echo "✓ Results copied to clipboard"
echo "✓ Also saved: $OUT"
