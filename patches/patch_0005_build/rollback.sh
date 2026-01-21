#!/bin/bash
# Rollback Script for Patch 0005
# Removes graph logging system and reverts changes

set -e

echo "=========================================="
echo "Rolling Back Patch 0005: Graph Logging"
echo "=========================================="
echo ""

# Load environment
if [ -f ~/.arcturus_development_env.sh ]; then
    source ~/.arcturus_development_env.sh
else
    echo "Warning: Arcturus environment not found"
fi

# Stop services
echo "Stopping services..."
systemctl --user stop arcturus-monitor.service 2>/dev/null || true
systemctl --user stop arcturus-cleanup.timer 2>/dev/null || true
systemctl --user stop arcturus-cleanup.service 2>/dev/null || true

# Disable services
echo "Disabling services..."
systemctl --user disable arcturus-monitor.service 2>/dev/null || true
systemctl --user disable arcturus-cleanup.timer 2>/dev/null || true

# Remove systemd files
echo "Removing systemd service files..."
rm -f ~/.config/systemd/user/arcturus-monitor.service
rm -f ~/.config/systemd/user/arcturus-cleanup.service
rm -f ~/.config/systemd/user/arcturus-cleanup.timer

# Reload systemd
systemctl --user daemon-reload

# Ask about removing installation directory
echo ""
read -p "Remove /opt/mythos/graph_logging directory? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing installation directory..."
    sudo rm -rf /opt/mythos/graph_logging
    echo "✓ Directory removed"
else
    echo "Keeping installation directory (you can remove manually later)"
fi

# Ask about removing Neo4j data
echo ""
read -p "Remove graph events from Neo4j? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing graph events..."
    
    if [ -n "$NEO4J_URI" ] && [ -n "$NEO4J_USER" ] && [ -n "$NEO4J_PASSWORD" ]; then
        cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" << 'CYPHER'
// Remove all Event, Process, Service, Metric nodes
MATCH (e:Event) DETACH DELETE e;
MATCH (p:Process) DETACH DELETE p;
MATCH (s:Service) DETACH DELETE s;
MATCH (m:Metric) DETACH DELETE m;

// Drop indexes
DROP INDEX event_timestamp IF EXISTS;
DROP INDEX event_type IF EXISTS;
DROP INDEX event_id IF EXISTS;
DROP INDEX process_pid IF EXISTS;
DROP INDEX service_name IF EXISTS;
DROP INDEX metric_timestamp IF EXISTS;

// Update System node
MATCH (sys:System {name: 'localhost'})
SET sys.monitoring_enabled = false,
    sys.monitoring_removed = datetime();

RETURN "Graph events removed" AS status;
CYPHER
        echo "✓ Graph events removed"
    else
        echo "Warning: Neo4j credentials not found, skipping graph cleanup"
        echo "You can manually remove events later with:"
        echo "  MATCH (e:Event) DETACH DELETE e;"
    fi
else
    echo "Keeping graph events (you can remove manually later)"
fi

# Revert Git changes if in arcturus repo
if [ -n "$ARCTURUS_GIT_DIR" ] && [ -d "$ARCTURUS_GIT_DIR/.git" ]; then
    echo ""
    echo "Reverting Git changes..."
    cd "$ARCTURUS_GIT_DIR"
    
    # Revert the patch commit
    git revert HEAD --no-edit 2>/dev/null || true
    
    # Update patch state
    python3 << 'PYTHON'
import json
try:
    with open('.patch_state.json', 'r') as f:
        state = json.load(f)
    
    # Remove patch 5 from state
    state['patches'] = [p for p in state['patches'] if p['number'] != 5]
    state['current_patch'] = max([p['number'] for p in state['patches']], default=0)
    
    with open('.patch_state.json', 'w') as f:
        json.dump(state, f, indent=2)
    
    print("✓ Patch state updated")
except Exception as e:
    print(f"Warning: Could not update patch state: {e}")
PYTHON
    
    git add .patch_state.json 2>/dev/null || true
    git commit -m "Rollback: Removed Patch 0005 (Graph Logging)" 2>/dev/null || true
    
    echo "✓ Git changes reverted"
fi

echo ""
echo "=========================================="
echo "Rollback Complete"
echo "=========================================="
echo ""
echo "Patch 0005 has been rolled back."
echo "System restored to pre-patch state."
echo ""
echo "If you want to reinstall later, run:"
echo "  pa 5"
echo ""
