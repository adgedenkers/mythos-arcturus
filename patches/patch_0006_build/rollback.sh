#!/bin/bash
# Rollback Script for Patch 0006
# Removes LLM diagnostics interface

set -e

echo "=========================================="
echo "Rolling Back Patch 0006: LLM Diagnostics"
echo "=========================================="
echo ""

# Load environment
if [ -f ~/.arcturus_development_env.sh ]; then
    source ~/.arcturus_development_env.sh
fi

# Remove CLI symlinks
echo "Removing CLI commands..."
sudo rm -f /usr/local/bin/mythos-ask
sudo rm -f /usr/local/bin/mythos-chat
echo "✓ CLI commands removed"

# Remove installation directory
echo ""
read -p "Remove /opt/mythos/llm_diagnostics directory? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo rm -rf /opt/mythos/llm_diagnostics
    echo "✓ Directory removed"
fi

# Ask about conversation logs
echo ""
read -p "Remove conversation logs from Neo4j? (y/N) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -n "$NEO4J_URI" ] && [ -n "$NEO4J_USER" ] && [ -n "$NEO4J_PASSWORD" ]; then
        cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" << 'CYPHER'
MATCH (c:Conversation) DETACH DELETE c;
RETURN "Conversations removed" AS status;
CYPHER
        echo "✓ Conversations removed"
    fi
fi

# Revert Git changes
if [ -n "$ARCTURUS_GIT_DIR" ] && [ -d "$ARCTURUS_GIT_DIR/.git" ]; then
    echo ""
    echo "Reverting Git changes..."
    cd "$ARCTURUS_GIT_DIR"
    
    git revert HEAD --no-edit 2>/dev/null || true
    
    python3 << 'PYTHON'
import json
try:
    with open('.patch_state.json', 'r') as f:
        state = json.load(f)
    
    state['patches'] = [p for p in state['patches'] if p['number'] != 6]
    state['current_patch'] = 5
    
    with open('.patch_state.json', 'w') as f:
        json.dump(state, f, indent=2)
    
    print("✓ Patch state updated")
except Exception as e:
    print(f"Warning: Could not update patch state: {e}")
PYTHON
    
    git add .patch_state.json 2>/dev/null || true
    git commit -m "Rollback: Removed Patch 0006 (LLM Diagnostics)" 2>/dev/null || true
    
    echo "✓ Git changes reverted"
fi

echo ""
echo "=========================================="
echo "Rollback Complete"
echo "=========================================="
echo ""
echo "Note: Ollama and the llama3.2:3b model were not removed."
echo "To remove them manually:"
echo "  sudo systemctl stop ollama"
echo "  sudo systemctl disable ollama"
echo "  ollama rm llama3.2:3b"
echo ""
