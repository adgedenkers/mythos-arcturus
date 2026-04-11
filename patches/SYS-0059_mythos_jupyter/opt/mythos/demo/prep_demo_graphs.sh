#!/bin/bash
# prep_demo_graphs.sh — Pre-demo state setup for the Tony Miller (M7) demo
#
# This script is IDEMPOTENT. You can run it as many times as you want.
# It brings the two demo Neo4j containers to a known-good state:
#
#   demo-live     (bolt://localhost:7688) — EMPTY, ready for live crawl in Section 1
#   demo-complete (bolt://localhost:7689) — PRE-POPULATED with strapi AutoDoc2 graph
#
# Run this:
#   - The night before the demo (full clean setup + rehearsal)
#   - An hour before the demo (sanity check — should be a no-op on demo-complete
#     if nothing has changed, and will always re-empty demo-live)
#
# Requires:
#   - Both demo Neo4j containers running (docker ps | grep demo)
#   - /opt/mythos/.env.demo-live and /opt/mythos/.env.demo-complete present
#   - autodoc2 CLI installed at /opt/mythos/bin/autodoc2
#   - Internet connection for the strapi clone

set -e
set -o pipefail

# ─── Configuration ───────────────────────────────────────────────────────────

STRAPI_REPO_URL="https://github.com/strapi/strapi.git"
STRAPI_TAG="v5.9.0"          # pinned for reproducibility
STRAPI_DIR="/opt/mythos/demo/repos/strapi"

DEMO_LIVE_NAME="demo-live"
DEMO_LIVE_PASS="demo-live-password"
DEMO_LIVE_PORT="7688"

DEMO_COMPLETE_NAME="demo-complete"
DEMO_COMPLETE_PASS="demo-complete-password"
DEMO_COMPLETE_PORT="7689"

ENV_LIVE="/opt/mythos/.env.demo-live"
ENV_COMPLETE="/opt/mythos/.env.demo-complete"

AUTODOC2="/opt/mythos/bin/autodoc2"

# ─── Helpers ─────────────────────────────────────────────────────────────────

BOLD="$(tput bold 2>/dev/null || echo)"
DIM="$(tput dim 2>/dev/null || echo)"
RED="$(tput setaf 1 2>/dev/null || echo)"
GREEN="$(tput setaf 2 2>/dev/null || echo)"
YELLOW="$(tput setaf 3 2>/dev/null || echo)"
BLUE="$(tput setaf 4 2>/dev/null || echo)"
RESET="$(tput sgr0 2>/dev/null || echo)"

step() { echo ""; echo "${BOLD}${BLUE}▶ $*${RESET}"; }
ok()   { echo "  ${GREEN}✓${RESET} $*"; }
warn() { echo "  ${YELLOW}⚠${RESET} $*"; }
err()  { echo "  ${RED}✗${RESET} $*" >&2; }
die()  { err "$*"; exit 1; }

cypher_live() {
    docker exec "$DEMO_LIVE_NAME" cypher-shell \
        -u neo4j -p "$DEMO_LIVE_PASS" "$1" 2>&1 | \
        grep -v "WARNING" || true
}

cypher_complete() {
    docker exec "$DEMO_COMPLETE_NAME" cypher-shell \
        -u neo4j -p "$DEMO_COMPLETE_PASS" "$1" 2>&1 | \
        grep -v "WARNING" || true
}

count_nodes_live() {
    cypher_live "MATCH (n) RETURN count(n) AS c;" | \
        awk '/^[0-9]+$/ {print; exit}'
}

count_nodes_complete() {
    cypher_complete "MATCH (n) RETURN count(n) AS c;" | \
        awk '/^[0-9]+$/ {print; exit}'
}

# ─── Pre-flight ──────────────────────────────────────────────────────────────

step "Pre-flight checks"

[ -x "$AUTODOC2" ] || die "autodoc2 CLI not found at $AUTODOC2"
ok "autodoc2 CLI present"

[ -f "$ENV_LIVE" ] || die "$ENV_LIVE not found — run setup_demo_graphs.sh first"
[ -f "$ENV_COMPLETE" ] || die "$ENV_COMPLETE not found — run setup_demo_graphs.sh first"
ok "demo env files present"

docker ps --format '{{.Names}}' | grep -q "^${DEMO_LIVE_NAME}$" \
    || die "$DEMO_LIVE_NAME container is not running"
docker ps --format '{{.Names}}' | grep -q "^${DEMO_COMPLETE_NAME}$" \
    || die "$DEMO_COMPLETE_NAME container is not running"
ok "both demo containers running"

# Connectivity test — if cypher-shell auth is broken, fail loudly NOW, not later.
cypher_live "RETURN 1;" | grep -q "^1$" \
    || die "cannot talk to $DEMO_LIVE_NAME — password wrong?"
cypher_complete "RETURN 1;" | grep -q "^1$" \
    || die "cannot talk to $DEMO_COMPLETE_NAME — password wrong?"
ok "both containers reachable with credentials"

# ─── Step 1: Clone or update strapi at pinned tag ────────────────────────────

step "Strapi source at $STRAPI_DIR (pinned to $STRAPI_TAG)"

mkdir -p "$(dirname "$STRAPI_DIR")"

if [ -d "$STRAPI_DIR/.git" ]; then
    cd "$STRAPI_DIR"
    CURRENT_SHA=$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    # Fetch the specific tag so we can check it out
    git fetch --quiet --depth 1 origin "refs/tags/${STRAPI_TAG}:refs/tags/${STRAPI_TAG}" 2>/dev/null || {
        warn "could not fetch tag $STRAPI_TAG — using existing checkout"
    }
    # Checkout the tag if we're not already on it
    TARGET_SHA=$(git rev-list -n 1 "$STRAPI_TAG" 2>/dev/null || echo "")
    if [ -n "$TARGET_SHA" ] && [ "$CURRENT_SHA" != "$TARGET_SHA" ]; then
        git checkout --quiet "$STRAPI_TAG"
        ok "checked out $STRAPI_TAG (was $CURRENT_SHA)"
    else
        ok "already at $STRAPI_TAG"
    fi
    cd - > /dev/null
else
    echo "  cloning $STRAPI_REPO_URL (shallow, tag $STRAPI_TAG)..."
    # Shallow clone of just the tag. Uses --branch to target the tag directly,
    # which with --depth 1 means we download only the commit we care about.
    git clone --quiet --depth 1 --branch "$STRAPI_TAG" "$STRAPI_REPO_URL" "$STRAPI_DIR" \
        || die "strapi clone failed"
    ok "cloned to $STRAPI_DIR"
fi

# Log the exact SHA we ended up at — this is the reproducibility anchor
RESOLVED_SHA=$(cd "$STRAPI_DIR" && git rev-parse HEAD)
RESOLVED_FILES=$(cd "$STRAPI_DIR" && git ls-files | wc -l)
ok "resolved SHA: ${DIM}${RESOLVED_SHA}${RESET}"
ok "tracked files: $RESOLVED_FILES"

# ─── Step 2: Wipe demo-live ──────────────────────────────────────────────────

step "Wiping demo-live (port $DEMO_LIVE_PORT)"

BEFORE_LIVE=$(count_nodes_live || echo "?")
echo "  nodes before wipe: $BEFORE_LIVE"

# Delete all nodes + relationships in chunks to avoid heap blowout on large graphs.
# The CALL {...} IN TRANSACTIONS syntax is Neo4j 5+.
cypher_live "MATCH (n) CALL (n) { DETACH DELETE n } IN TRANSACTIONS OF 10000 ROWS;" > /dev/null

# Drop all constraints so AutoDoc2's setup_constraints() on next crawl starts clean.
CONSTRAINT_NAMES=$(cypher_live "SHOW CONSTRAINTS YIELD name RETURN name;" | \
    grep -v "^name$" | grep -v "^$" | tr -d '"')
if [ -n "$CONSTRAINT_NAMES" ]; then
    while IFS= read -r cname; do
        [ -n "$cname" ] && cypher_live "DROP CONSTRAINT \`$cname\`;" > /dev/null
    done <<< "$CONSTRAINT_NAMES"
    ok "dropped $(echo "$CONSTRAINT_NAMES" | wc -l) constraint(s)"
fi

AFTER_LIVE=$(count_nodes_live || echo "?")
if [ "$AFTER_LIVE" = "0" ]; then
    ok "demo-live is empty (0 nodes)"
else
    die "demo-live wipe failed — still $AFTER_LIVE nodes"
fi

# ─── Step 3: Wipe demo-complete ──────────────────────────────────────────────

step "Wiping demo-complete (port $DEMO_COMPLETE_PORT)"

BEFORE_COMPLETE=$(count_nodes_complete || echo "?")
echo "  nodes before wipe: $BEFORE_COMPLETE"

cypher_complete "MATCH (n) CALL (n) { DETACH DELETE n } IN TRANSACTIONS OF 10000 ROWS;" > /dev/null

CONSTRAINT_NAMES=$(cypher_complete "SHOW CONSTRAINTS YIELD name RETURN name;" | \
    grep -v "^name$" | grep -v "^$" | tr -d '"')
if [ -n "$CONSTRAINT_NAMES" ]; then
    while IFS= read -r cname; do
        [ -n "$cname" ] && cypher_complete "DROP CONSTRAINT \`$cname\`;" > /dev/null
    done <<< "$CONSTRAINT_NAMES"
    ok "dropped $(echo "$CONSTRAINT_NAMES" | wc -l) constraint(s)"
fi

AFTER_COMPLETE=$(count_nodes_complete || echo "?")
if [ "$AFTER_COMPLETE" = "0" ]; then
    ok "demo-complete is empty (0 nodes)"
else
    die "demo-complete wipe failed — still $AFTER_COMPLETE nodes"
fi

# ─── Step 4: Crawl strapi into demo-complete ─────────────────────────────────

step "Crawling strapi into demo-complete"
echo "  target:    $STRAPI_DIR"
echo "  neo4j:     bolt://localhost:$DEMO_COMPLETE_PORT"
echo "  llm:       disabled (--skip-llm — faster, no Iris summaries needed for backup)"
echo ""

START_TS=$(date +%s)
"$AUTODOC2" "$STRAPI_DIR" \
    --env-file "$ENV_COMPLETE" \
    --skip-llm \
    --verbose 2>&1 | while IFS= read -r line; do
        # Indent autodoc2's output under our step
        echo "    $line"
    done
END_TS=$(date +%s)
ELAPSED=$((END_TS - START_TS))
ok "crawl complete in ${ELAPSED}s"

# ─── Step 5: Verify demo-complete contents ───────────────────────────────────

step "Verifying demo-complete graph state"

CRAWL_INFO=$(cypher_complete "MATCH (c:AutodocCrawl) RETURN c.crawl_id, c.target, c.file_count, c.status;" 2>&1 | grep -v "^c\." | grep -v "^$" || true)

if [ -z "$CRAWL_INFO" ]; then
    die "no AutodocCrawl node in demo-complete after crawl — something went wrong"
fi

echo "  AutodocCrawl: $CRAWL_INFO"

TOTAL_NODES=$(count_nodes_complete)
ok "demo-complete total nodes: $TOTAL_NODES"

# Sanity floor: strapi should produce thousands of nodes. If we got under 1000,
# something is wrong — AutoDoc2 probably skipped most files.
if [ "$TOTAL_NODES" -lt 1000 ]; then
    die "demo-complete has only $TOTAL_NODES nodes — expected thousands. Crawl may have failed."
fi

# ─── Step 6: Verify demo-live is still empty ─────────────────────────────────

step "Verifying demo-live is still empty"

FINAL_LIVE=$(count_nodes_live)
if [ "$FINAL_LIVE" = "0" ]; then
    ok "demo-live: 0 nodes (ready for live crawl in Section 1 of the notebook)"
else
    die "demo-live has $FINAL_LIVE nodes — should be 0"
fi

# ─── Summary ─────────────────────────────────────────────────────────────────

echo ""
echo "${BOLD}${GREEN}════════════════════════════════════════════════════════════${RESET}"
echo "${BOLD}${GREEN}  DEMO GRAPHS READY${RESET}"
echo "${BOLD}${GREEN}════════════════════════════════════════════════════════════${RESET}"
echo ""
echo "  strapi pinned:    $STRAPI_TAG"
echo "  strapi SHA:       $RESOLVED_SHA"
echo "  strapi path:      $STRAPI_DIR"
echo "  strapi files:     $RESOLVED_FILES"
echo ""
echo "  demo-live   :7688 — empty, awaiting live crawl"
echo "  demo-complete :7689 — $TOTAL_NODES nodes, backup ready"
echo ""
echo "${DIM}  Next: open the notebook and rehearse Section 1 against demo-live.${RESET}"
echo ""
