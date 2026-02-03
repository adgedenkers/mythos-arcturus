#!/bin/bash
# Patch 0057: Perception Layer Foundation
#
# Creates the foundation tables for Iris's consciousness Layer 1:
#   - perception_log: Raw intake of everything
#   - idea_inbox: Auto-captured lists from conversations
#   - idea_backlog: Curated ideas worth keeping
#
# This is where consciousness begins - nothing enters Iris's awareness
# without passing through perception_log first.

set -e

PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
PATCH_NUM="0057"

echo "=== Patch ${PATCH_NUM}: Perception Layer Foundation ==="

# ============================================================
# 1. RUN MIGRATION
# ============================================================
echo "Running migration..."

sudo -u postgres psql -d mythos -f "$PATCH_DIR/opt/mythos/migrations/migration_0057_perception_layer.sql"

echo "  ✓ Migration complete"

# ============================================================
# 2. COPY MIGRATION TO MYTHOS
# ============================================================
echo "Copying migration file..."
mkdir -p /opt/mythos/migrations
cp "$PATCH_DIR/opt/mythos/migrations/migration_0057_perception_layer.sql" /opt/mythos/migrations/

echo "  ✓ Migration file copied"

# ============================================================
# 3. VERIFY TABLES
# ============================================================
echo ""
echo "=== Verification ==="

# Check perception_log
if sudo -u postgres psql -d mythos -c "\d perception_log" &>/dev/null; then
    ROW_COUNT=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM perception_log")
    echo "  ✓ perception_log exists (${ROW_COUNT// /} rows)"
else
    echo "  ✗ perception_log NOT CREATED"
fi

# Check idea_inbox
if sudo -u postgres psql -d mythos -c "\d idea_inbox" &>/dev/null; then
    ROW_COUNT=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM idea_inbox")
    echo "  ✓ idea_inbox exists (${ROW_COUNT// /} rows)"
else
    echo "  ✗ idea_inbox NOT CREATED"
fi

# Check idea_backlog
if sudo -u postgres psql -d mythos -c "\d idea_backlog" &>/dev/null; then
    ROW_COUNT=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM idea_backlog")
    echo "  ✓ idea_backlog exists (${ROW_COUNT// /} rows)"
else
    echo "  ✗ idea_backlog NOT CREATED"
fi

# Check views
echo ""
echo "Views:"
for view in v_inbox_pending v_backlog_open v_perception_recent; do
    if sudo -u postgres psql -d mythos -c "\d $view" &>/dev/null; then
        echo "  ✓ $view"
    else
        echo "  ✗ $view NOT CREATED"
    fi
done

# ============================================================
# 4. VERIFY ONE-LINER
# ============================================================
echo ""
echo "Verify one-liner:"
echo '  sudo -u postgres psql -d mythos -tc "SELECT COUNT(*) FROM information_schema.tables WHERE table_name IN ('\''perception_log'\'', '\''idea_inbox'\'', '\''idea_backlog'\'')" | grep -q 3 && echo "✓ 0057 OK" || echo "✗ 0057 FAIL"'

# ============================================================
# 5. SUMMARY
# ============================================================
echo ""
echo "=== Patch ${PATCH_NUM} Complete ==="
echo ""
echo "Created tables:"
echo "  - perception_log    (Layer 1 - raw intake of everything)"
echo "  - idea_inbox        (auto-captured lists from conversations)"
echo "  - idea_backlog      (curated ideas worth keeping)"
echo ""
echo "Created views:"
echo "  - v_inbox_pending   (ideas awaiting review)"
echo "  - v_backlog_open    (open items by priority)"
echo "  - v_perception_recent (last 24 hours)"
echo ""
echo "Next: Wire Telegram conversations into perception_log"
echo ""
