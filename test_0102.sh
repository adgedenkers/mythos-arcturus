#!/bin/bash
# Patch 0102 Verification Script
# Run on Arcturus after installing the patch
# Usage: bash test_0102.sh [--live]
#   --live flag runs actual 32b model analysis (takes ~30s)

set -e
PASS=0
FAIL=0
WARN=0

pass() { echo "  ✅ $1"; ((PASS++)); }
fail() { echo "  ❌ $1"; ((FAIL++)); }
warn() { echo "  ⚠️  $1"; ((WARN++)); }

echo "🧠 Patch 0102: Backlog Intelligence — Verification"
echo "===================================================="

# --- Schema Checks ---
echo ""
echo "📊 Schema Checks"

# idea_backlog new columns
for col in priority_order depends_on blocked_by phase estimated_effort category source last_analyzed analyst_notes; do
    if sudo -u postgres psql -d mythos -tAc "SELECT column_name FROM information_schema.columns WHERE table_name='idea_backlog' AND column_name='$col';" | grep -q "$col"; then
        pass "idea_backlog.$col exists"
    else
        fail "idea_backlog.$col MISSING"
    fi
done

# backlog_analysis table
if sudo -u postgres psql -d mythos -tAc "SELECT tablename FROM pg_tables WHERE tablename='backlog_analysis';" | grep -q "backlog_analysis"; then
    pass "backlog_analysis table exists"
else
    fail "backlog_analysis table MISSING"
fi

# Check backlog_analysis columns
for col in trigger_type summary transfer_recommendations predictions_made predictions_correct model_used; do
    if sudo -u postgres psql -d mythos -tAc "SELECT column_name FROM information_schema.columns WHERE table_name='backlog_analysis' AND column_name='$col';" | grep -q "$col"; then
        pass "backlog_analysis.$col exists"
    else
        fail "backlog_analysis.$col MISSING"
    fi
done

# Indexes
for idx in idx_backlog_priority idx_analysis_created idx_analysis_trigger; do
    if sudo -u postgres psql -d mythos -tAc "SELECT indexname FROM pg_indexes WHERE indexname='$idx';" | grep -q "$idx"; then
        pass "Index $idx exists"
    else
        fail "Index $idx MISSING"
    fi
done

# --- Data Checks ---
echo ""
echo "📦 Data Checks"

# Backlog items seeded
BACKLOG_COUNT=$(sudo -u postgres psql -d mythos -tAc "SELECT COUNT(*) FROM idea_backlog WHERE priority_order IS NOT NULL;")
BACKLOG_COUNT=$(echo "$BACKLOG_COUNT" | tr -d ' ')
if [ "$BACKLOG_COUNT" -ge 20 ]; then
    pass "Backlog items with priority: $BACKLOG_COUNT"
else
    warn "Only $BACKLOG_COUNT backlog items have priority_order set (expected 20+)"
fi

# Check priority ordering is sane
DUPES=$(sudo -u postgres psql -d mythos -tAc "SELECT COUNT(*) FROM (SELECT priority_order, COUNT(*) c FROM idea_backlog WHERE priority_order IS NOT NULL AND status != 'done' GROUP BY priority_order HAVING COUNT(*) > 1) x;")
DUPES=$(echo "$DUPES" | tr -d ' ')
if [ "$DUPES" -eq 0 ]; then
    pass "No duplicate priority_order values"
else
    warn "$DUPES priority_order values have duplicates (may be OK if old items overlap with seeded)"
fi

# Doc items
DOC_COUNT=$(sudo -u postgres psql -d mythos -tAc "SELECT COUNT(*) FROM idea_backlog WHERE category='docs' AND priority_order >= 100;")
DOC_COUNT=$(echo "$DOC_COUNT" | tr -d ' ')
if [ "$DOC_COUNT" -ge 9 ]; then
    pass "Documentation backlog items: $DOC_COUNT"
else
    warn "Only $DOC_COUNT doc items (expected 9)"
fi

# --- File Checks ---
echo ""
echo "📁 File Checks"

for f in /opt/mythos/core/backlog_analyst.py /opt/mythos/core/morning_briefing.py /opt/mythos/telegram_bot/handlers/analyst_handler.py; do
    if [ -f "$f" ]; then
        pass "$(basename $f) installed"
    else
        fail "$f MISSING"
    fi
done

# TODO.md updated
if grep -q "Backlog Intelligence" /opt/mythos/docs/TODO.md 2>/dev/null; then
    pass "TODO.md updated (contains 'Backlog Intelligence')"
else
    fail "TODO.md not updated or missing"
fi

# --- Import Checks ---
echo ""
echo "🐍 Import Checks"

# Test that backlog_analyst imports cleanly
if /opt/mythos/.venv/bin/python3 -c "from core.backlog_analyst import BacklogAnalyst; print('OK')" 2>/dev/null; then
    pass "backlog_analyst imports successfully"
else
    # Try with path
    if cd /opt/mythos && /opt/mythos/.venv/bin/python3 -c "from core.backlog_analyst import BacklogAnalyst; print('OK')" 2>/dev/null; then
        pass "backlog_analyst imports successfully (from /opt/mythos)"
    else
        fail "backlog_analyst import failed"
    fi
fi

if cd /opt/mythos && /opt/mythos/.venv/bin/python3 -c "from core.morning_briefing import MorningBriefing; print('OK')" 2>/dev/null; then
    pass "morning_briefing imports successfully"
else
    fail "morning_briefing import failed"
fi

if cd /opt/mythos && /opt/mythos/.venv/bin/python3 -c "from telegram_bot.handlers.analyst_handler import cmd_briefing, cmd_priorities, cmd_transfers; print('OK')" 2>/dev/null; then
    pass "analyst_handler imports successfully"
else
    fail "analyst_handler import failed"
fi

# --- Service Checks ---
echo ""
echo "🔧 Service Checks"

for svc in mythos-bot mythos-api mythos-patch-monitor mythos-knowledge-map; do
    if systemctl is-active --quiet "$svc.service"; then
        pass "$svc.service is active"
    else
        warn "$svc.service is not active"
    fi
done

# --- Ollama Model Check ---
echo ""
echo "🤖 Model Check"

if curl -s http://localhost:11434/api/tags | grep -q "qwen2.5:32b"; then
    pass "qwen2.5:32b model available"
else
    fail "qwen2.5:32b model NOT available — analyst needs this model"
fi

# --- Live Test (optional) ---
if [ "$1" = "--live" ]; then
    echo ""
    echo "🧠 Live Analysis Test (running 32b model...)"
    echo "   This will take ~30 seconds..."
    
    cd /opt/mythos
    RESULT=$(/opt/mythos/.venv/bin/python3 -c "
import asyncio, json, sys
sys.path.insert(0, '/opt/mythos')
from core.backlog_analyst import BacklogAnalyst

async def test():
    a = BacklogAnalyst()
    r = await a.run_analysis('on_demand')
    a.close()
    return r

r = asyncio.run(test())
print('BRIEFING:', r.get('briefing', 'NONE')[:200])
print('PRIORITIES:', len(r.get('priorities_today', [])))
print('URGENT:', len(r.get('urgent_flags', [])))
print('TRANSFERS:', len(r.get('transfer_recommendations', [])))
print('ANALYSIS_ID:', r.get('analysis_id', 'NONE'))
print('PARSE_ERROR:', r.get('_parse_error', False))
" 2>&1)
    
    echo "$RESULT"
    
    if echo "$RESULT" | grep -q "ANALYSIS_ID: [0-9]"; then
        pass "Live analysis completed and saved to DB"
    else
        fail "Live analysis did not produce an analysis ID"
    fi
    
    if echo "$RESULT" | grep -q "PARSE_ERROR: False"; then
        pass "Model output parsed as valid JSON"
    elif echo "$RESULT" | grep -q "PARSE_ERROR: True"; then
        warn "Model output failed JSON parse (check raw_model_response in backlog_analysis)"
    fi
    
    # Verify it's in the DB
    ANALYSIS_COUNT=$(sudo -u postgres psql -d mythos -tAc "SELECT COUNT(*) FROM backlog_analysis;")
    ANALYSIS_COUNT=$(echo "$ANALYSIS_COUNT" | tr -d ' ')
    echo ""
    echo "   📊 Total analyses in DB: $ANALYSIS_COUNT"
else
    echo ""
    echo "💡 Run with --live to test actual 32b model analysis:"
    echo "   bash test_0102.sh --live"
fi

# --- Wiring Check ---
echo ""
echo "🔌 Wiring Check"

if grep -q "analyst_handler" /opt/mythos/telegram_bot/mythos_bot.py 2>/dev/null; then
    pass "analyst_handler wired in mythos_bot.py"
else
    warn "analyst_handler NOT YET wired in mythos_bot.py — see install output for instructions"
fi

if grep -q "morning_briefing\|MorningBriefing" /opt/mythos/telegram_bot/mythos_bot.py 2>/dev/null; then
    pass "MorningBriefing wired in mythos_bot.py"
else
    warn "MorningBriefing NOT YET wired in mythos_bot.py — see install output for instructions"
fi

# --- Summary ---
echo ""
echo "======================================================"
echo "Results: ✅ $PASS passed | ❌ $FAIL failed | ⚠️  $WARN warnings"
echo "======================================================"

if [ "$FAIL" -gt 0 ]; then
    echo "⚠️  Some checks failed — review above"
    exit 1
elif [ "$WARN" -gt 0 ]; then
    echo "📋 Mostly good — review warnings above"
    exit 0
else
    echo "🎉 All checks passed!"
    exit 0
fi
