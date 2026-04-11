#!/bin/bash
# stream_status.sh — Run at session start to see what's happening across all streams
# Usage: bash /opt/mythos/docs/stream_status.sh [STREAM_PREFIX]
# Example: bash /opt/mythos/docs/stream_status.sh NEU

D=~/diag.txt; > "$D"

echo "=== STREAMS STATUS ===" >> "$D"
cat /opt/mythos/docs/STREAMS.md >> "$D" 2>&1

echo -e "\n\n=== TODO.md (Active Work) ===" >> "$D"
cat /opt/mythos/docs/TODO.md >> "$D" 2>&1

echo -e "\n\n=== RECENT PATCHES (last 20 git tags) ===" >> "$D"
cd /opt/mythos && git tag --sort=-creatordate | head -20 >> "$D" 2>&1

echo -e "\n\n=== RECENT COMMITS (last 10) ===" >> "$D"
cd /opt/mythos && git log --oneline -10 >> "$D" 2>&1

# If a stream prefix was provided, show stream-specific info
if [ -n "$1" ]; then
    STREAM="$1"
    echo -e "\n\n=== STREAM-SPECIFIC: $STREAM ===" >> "$D"

    echo -e "\n--- Recent $STREAM patches ---" >> "$D"
    cd /opt/mythos && git tag --sort=-creatordate | grep -i "^${STREAM}" | head -10 >> "$D" 2>&1

    echo -e "\n--- Recent $STREAM commits ---" >> "$D"
    cd /opt/mythos && git log --oneline -10 --all --grep="$STREAM" >> "$D" 2>&1

    echo -e "\n--- $STREAM files changed in last 5 commits ---" >> "$D"
    cd /opt/mythos && git log --oneline --name-only -5 --all --grep="$STREAM" >> "$D" 2>&1
fi

echo -e "\n\n=== DISK / SERVICES ===" >> "$D"
systemctl is-active mythos-bot.service >> "$D" 2>&1
echo -n " mythos-bot | " >> "$D"
systemctl is-active mythos-patch-monitor.service >> "$D" 2>&1
echo " mythos-patch-monitor" >> "$D"

cat "$D" | xclip -selection clipboard && echo "✓ Copied to clipboard — paste into Claude session"
