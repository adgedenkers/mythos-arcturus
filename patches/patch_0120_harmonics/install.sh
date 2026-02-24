#!/bin/bash
set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
MYTHOS="/opt/mythos"
VENV="$MYTHOS/.venv/bin/python3"

echo "═══════════════════════════════════════════"
echo "  Patch 0120: Harmonic Analysis System"
echo "═══════════════════════════════════════════"

# ─── Install harmonics package ───
echo "[1/4] Installing harmonics package..."
mkdir -p "$MYTHOS/harmonics"
cp "$PATCH_DIR/opt/mythos/harmonics/__init__.py" "$MYTHOS/harmonics/"
cp "$PATCH_DIR/opt/mythos/harmonics/engine.py" "$MYTHOS/harmonics/"
echo "  ✓ Harmonics engine installed"

# ─── Run schema ───
echo "[2/4] Running schema migration..."
sudo -u postgres psql -d mythos -f "$PATCH_DIR/opt/mythos/harmonics/schema.sql"
echo "  ✓ Tables created and seed data migrated"

# ─── Populate harmonics for existing dates ───
echo "[3/4] Populating harmonics for existing person_dates..."
cd "$MYTHOS"
$VENV -c "
import sys
sys.path.insert(0, '$MYTHOS')
from harmonics.engine import populate_all_harmonics
results = populate_all_harmonics()
for k, v in results.items():
    print(f'  {k}: {v} values')
print('  ✓ All harmonics populated')
"

# ─── Run initial resonance: everyone vs Seraphe ───
echo "[4/4] Computing initial resonance with Seraphe..."
cd "$MYTHOS"
$VENV -c "
import sys
sys.path.insert(0, '$MYTHOS')
from harmonics.engine import compute_resonance_pair, resonance_summary, get_db_connection
import json

conn = get_db_connection()
cur = conn.cursor()

# Get all people except Seraphe (id=2)
cur.execute('SELECT id, display_text FROM people WHERE id != 2')
people = cur.fetchall()

for pid, name in people:
    count = compute_resonance_pair(2, pid, conn)
    print(f'  Seraphe ↔ {name}: {count} matches')

# Also Ka ↔ Fitz
count = compute_resonance_pair(1, 3, conn)
print(f'  Ka ↔ Fitz: {count} matches')

# Print summary for Ka ↔ Seraphe
summary = resonance_summary(2, 1, conn)
print()
print(f'  === {summary[\"person_a\"]} ↔ {summary[\"person_b\"]} ===')
print(f'  Total matches: {summary[\"total_matches\"]}')
for mtype, cnt in summary['by_type'].items():
    print(f'    {mtype}: {cnt}')

conn.close()
print()
print('  ✓ Initial resonance computed')
"

echo ""
echo "═══════════════════════════════════════════"
echo "  Patch 0120 complete!"
echo ""
echo "  Tables created:"
echo "    • person_dates (significant dates per person)"
echo "    • harmonic_values (full decomposition per number)"
echo "    • harmonic_resonance (match records between people)"
echo ""
echo "  CLI usage:"
echo "    cd /opt/mythos"
echo "    .venv/bin/python3 harmonics/engine.py populate"
echo "    .venv/bin/python3 harmonics/engine.py resonate 1 2"
echo "    .venv/bin/python3 harmonics/engine.py seraphe 1"
echo "    .venv/bin/python3 harmonics/engine.py summary 1 2"
echo "═══════════════════════════════════════════"
