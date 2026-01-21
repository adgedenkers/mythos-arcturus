#!/bin/bash
# Patch 0005 Installation Script
# AI-Native Graph Event Logging System
# Created: 2025-01-14
# By: Ka_tuar_el via Claude

set -e  # Exit on any error

# Track installation state
CURRENT_STEP="initialization"
ERROR_MESSAGE=""
INSTALL_LOG="/tmp/patch_0005_install_$(date +%s).log"

# Redirect all output to log file as well
exec > >(tee -a "$INSTALL_LOG") 2>&1

echo "=========================================="
echo "Patch 0005: AI-Native Graph Logging"
echo "=========================================="
echo ""
echo "Installation log: $INSTALL_LOG"
echo ""

# Error handler - runs on any error
rollback_on_error() {
    exit_code=$1
    
    if [ $exit_code -ne 0 ]; then
        echo ""
        echo "=========================================="
        echo "ERROR DETECTED - ROLLING BACK"
        echo "=========================================="
        echo ""
        
        # Generate detailed error report
        ERROR_REPORT="/tmp/patch_0005_error_$(date +%s).log"
        
        {
            echo "Patch 0005 Installation Failed"
            echo "==============================="
            echo ""
            echo "Exit Code: $exit_code"
            echo "Failed At: $(date -Iseconds)"
            echo "Failed Step: $CURRENT_STEP"
            echo ""
            echo "Error Message:"
            echo "$ERROR_MESSAGE"
            echo ""
            echo "=========================================="
            echo "System State at Failure"
            echo "=========================================="
            echo ""
            echo "Neo4j Status:"
            systemctl status neo4j --no-pager 2>&1 || echo "  Neo4j not running or not accessible"
            echo ""
            echo "PostgreSQL Status:"
            systemctl status postgresql --no-pager 2>&1 || echo "  PostgreSQL not running or not accessible"
            echo ""
            echo "Disk Space:"
            df -h / 2>&1 || echo "  Could not check disk space"
            echo ""
            echo "Python Version:"
            python3 --version 2>&1 || echo "  Python not found"
            echo ""
            echo "Pip Packages:"
            pip list 2>&1 | grep -E "(neo4j|psutil|yaml)" || echo "  Required packages not found"
            echo ""
            echo "Environment Variables:"
            echo "  NEO4J_URI: ${NEO4J_URI:-not set}"
            echo "  NEO4J_USER: ${NEO4J_USER:-not set}"
            echo "  NEO4J_PASSWORD: ${NEO4J_PASSWORD:+[set]}"
            echo "  ARCTURUS_GIT_DIR: ${ARCTURUS_GIT_DIR:-not set}"
            echo ""
            echo "=========================================="
            echo "Installation Progress"
            echo "=========================================="
            echo ""
            echo "Completed steps before failure:"
            echo "  (see install log for details)"
            echo ""
            echo "=========================================="
            echo "Rollback Actions"
            echo "=========================================="
            echo ""
        } > "$ERROR_REPORT"
        
        echo "Detailed error report: $ERROR_REPORT"
        echo ""
        
        # Execute rollback
        if [ -f ./rollback.sh ]; then
            echo "Executing automatic rollback..."
            chmod +x ./rollback.sh
            ./rollback.sh 2>&1 | tee -a "$ERROR_REPORT" || true
        fi
        
        {
            echo ""
            echo "=========================================="
            echo "Recommendations"
            echo "=========================================="
            echo ""
            
            case "$CURRENT_STEP" in
                "pre-flight checks")
                    echo "Pre-flight check failed. Please verify:"
                    echo "  - Neo4j is running: systemctl status neo4j"
                    echo "  - PostgreSQL is running: systemctl status postgresql"
                    echo "  - Environment variables are set in ~/.arcturus_development_env.sh"
                    echo "  - Python 3.11+ is installed: python3 --version"
                    ;;
                "applying Neo4j schema")
                    echo "Neo4j schema application failed. Please verify:"
                    echo "  - Neo4j is accessible: echo 'RETURN 1' | cypher-shell"
                    echo "  - Neo4j credentials are correct"
                    echo "  - No existing conflicting schema"
                    ;;
                "installing Python modules")
                    echo "Python module installation failed. Please verify:"
                    echo "  - /opt/mythos directory is writable"
                    echo "  - Python dependencies can be installed"
                    ;;
                "installing systemd services")
                    echo "Systemd service installation failed. Please verify:"
                    echo "  - ~/.config/systemd/user/ directory exists"
                    echo "  - Systemd user services are enabled"
                    echo "  - You have permission to install user services"
                    ;;
                *)
                    echo "Installation failed at: $CURRENT_STEP"
                    echo "Check the error report for details: $ERROR_REPORT"
                    ;;
            esac
            
            echo ""
            echo "Full installation log: $INSTALL_LOG"
            echo "Full error report: $ERROR_REPORT"
            echo ""
        } >> "$ERROR_REPORT"
        
        cat "$ERROR_REPORT"
        
        echo ""
        echo "Rollback complete. Review error reports for details."
        echo ""
        
        exit $exit_code
    fi
}

# Register error handler
trap 'rollback_on_error $?' EXIT

# ==========================================
# Step 1: Load Environment
# ==========================================
CURRENT_STEP="loading environment"

if [ -f ~/.arcturus_development_env.sh ]; then
    source ~/.arcturus_development_env.sh
    echo "✓ Environment loaded"
else
    ERROR_MESSAGE="Arcturus environment file not found: ~/.arcturus_development_env.sh"
    echo "Error: $ERROR_MESSAGE"
    exit 1
fi

# ==========================================
# Step 2: Pre-flight Checks
# ==========================================
CURRENT_STEP="pre-flight checks"
echo ""
echo "Running pre-flight checks..."

# Required environment variables
REQUIRED_VARS=("NEO4J_URI" "NEO4J_USER" "NEO4J_PASSWORD" "ARCTURUS_GIT_DIR")
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        ERROR_MESSAGE="Required environment variable not set: $var"
        echo "Error: $ERROR_MESSAGE"
        exit 1
    fi
done
echo "✓ Environment variables set"

# Check Neo4j is running
if ! systemctl is-active neo4j >/dev/null 2>&1; then
    ERROR_MESSAGE="Neo4j is not running. Start it with: sudo systemctl start neo4j"
    echo "Error: $ERROR_MESSAGE"
    exit 1
fi
echo "✓ Neo4j is running"

# Test Neo4j connection
if ! echo "RETURN 1" | cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" >/dev/null 2>&1; then
    ERROR_MESSAGE="Cannot connect to Neo4j. Check credentials and URI."
    echo "Error: $ERROR_MESSAGE"
    exit 1
fi
echo "✓ Neo4j connection successful"

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 11 ]); then
    ERROR_MESSAGE="Python 3.11+ required, found: $PYTHON_VERSION"
    echo "Error: $ERROR_MESSAGE"
    exit 1
fi
echo "✓ Python $PYTHON_VERSION"

# Check disk space (need at least 1GB free)
AVAILABLE_KB=$(df /opt | tail -1 | awk '{print $4}')
if [ "$AVAILABLE_KB" -lt 1048576 ]; then  # 1GB in KB
    ERROR_MESSAGE="Insufficient disk space in /opt (need at least 1GB free)"
    echo "Error: $ERROR_MESSAGE"
    exit 1
fi
echo "✓ Sufficient disk space"

# Check if systemd user directory exists
if [ ! -d ~/.config/systemd/user ]; then
    mkdir -p ~/.config/systemd/user
    echo "✓ Created systemd user directory"
else
    echo "✓ Systemd user directory exists"
fi

echo "✓ All pre-flight checks passed"

# ==========================================
# Step 3: Create Directories
# ==========================================
CURRENT_STEP="creating directories"
echo ""
echo "Creating installation directories..."

sudo mkdir -p /opt/mythos/graph_logging/{src,config,logs,scripts}
sudo chown -R $USER:$USER /opt/mythos/graph_logging
echo "✓ Directories created"

# ==========================================
# Step 4: Apply Neo4j Schema
# ==========================================
CURRENT_STEP="applying Neo4j schema"
echo ""
echo "Applying Neo4j schema..."

if ! cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" < files/schema/neo4j_schema.cypher; then
    ERROR_MESSAGE="Failed to apply Neo4j schema. Check Neo4j logs for details."
    exit 1
fi
echo "✓ Neo4j schema applied"

# ==========================================
# Step 5: Install Python Dependencies
# ==========================================
CURRENT_STEP="installing Python dependencies"
echo ""
echo "Installing Python dependencies..."

if ! pip install -r files/requirements.txt --break-system-packages --quiet; then
    ERROR_MESSAGE="Failed to install Python dependencies"
    exit 1
fi
echo "✓ Python dependencies installed"

# ==========================================
# Step 6: Install Python Modules
# ==========================================
CURRENT_STEP="installing Python modules"
echo ""
echo "Installing Python modules..."

cp files/src/*.py /opt/mythos/graph_logging/src/
chmod +x /opt/mythos/graph_logging/src/system_monitor.py
echo "✓ Python modules installed"

# ==========================================
# Step 7: Install Scripts
# ==========================================
CURRENT_STEP="installing scripts"
echo ""
echo "Installing scripts..."

cp files/scripts/*.py /opt/mythos/graph_logging/scripts/
chmod +x /opt/mythos/graph_logging/scripts/*.py
echo "✓ Scripts installed"

# ==========================================
# Step 8: Install Configuration
# ==========================================
CURRENT_STEP="installing configuration"
echo ""
echo "Installing configuration..."

cp files/config/monitoring_config.yaml /opt/mythos/graph_logging/config/
echo "✓ Configuration installed"

# ==========================================
# Step 9: Create Systemd Environment File
# ==========================================
CURRENT_STEP="creating systemd environment file"
echo ""
echo "Creating systemd environment file..."

mkdir -p ~/.config/arcturus

cat > ~/.config/arcturus/systemd.env << EOF
NEO4J_URI=$NEO4J_URI
NEO4J_USER=$NEO4J_USER
NEO4J_PASSWORD=$NEO4J_PASSWORD
ARCTURUS_GIT_DIR=$ARCTURUS_GIT_DIR
EVENT_RETENTION_DAYS=${EVENT_RETENTION_DAYS:-10}
MONITOR_CONFIG=/opt/mythos/graph_logging/config/monitoring_config.yaml
EOF

chmod 600 ~/.config/arcturus/systemd.env
echo "✓ Systemd environment file created"

# ==========================================
# Step 10: Install Systemd Services
# ==========================================
CURRENT_STEP="installing systemd services"
echo ""
echo "Installing systemd services..."

cp files/systemd/*.service ~/.config/systemd/user/
cp files/systemd/*.timer ~/.config/systemd/user/
systemctl --user daemon-reload
echo "✓ Systemd services installed"

# ==========================================
# Step 10: Enable and Start Services
# ==========================================
CURRENT_STEP="enabling and starting services"
echo ""
echo "Enabling services..."

systemctl --user enable arcturus-monitor.service
systemctl --user enable arcturus-cleanup.timer
echo "✓ Services enabled"

echo ""
echo "Starting monitor service..."
systemctl --user start arcturus-monitor.service
echo "✓ Monitor service started"

echo ""
echo "Starting cleanup timer..."
systemctl --user start arcturus-cleanup.timer
echo "✓ Cleanup timer started"

# ==========================================
# Step 11: Verify Installation
# ==========================================
CURRENT_STEP="verifying installation"
echo ""
echo "Verifying installation..."

sleep 5  # Give services time to start

if ! systemctl --user is-active arcturus-monitor.service >/dev/null 2>&1; then
    ERROR_MESSAGE="Monitor service failed to start. Check logs: journalctl --user -u arcturus-monitor -n 50"
    exit 1
fi
echo "✓ Monitor service is active"

if ! systemctl --user is-active arcturus-cleanup.timer >/dev/null 2>&1; then
    ERROR_MESSAGE="Cleanup timer failed to start. Check logs: journalctl --user -u arcturus-cleanup.timer -n 50"
    exit 1
fi
echo "✓ Cleanup timer is active"

# Check if events are being logged
sleep 5
EVENT_COUNT=$(echo "MATCH (e:Event) RETURN count(e) AS count" | \
              cypher-shell -a "$NEO4J_URI" -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" --format plain | \
              tail -1 | awk '{print $1}')

if [ "$EVENT_COUNT" = "0" ]; then
    echo "Warning: No events logged yet (this may be normal if no thresholds exceeded)"
else
    echo "✓ Event logging active ($EVENT_COUNT events)"
fi

# ==========================================
# Step 12: Update Git Repository
# ==========================================
CURRENT_STEP="updating Git repository"
echo ""
echo "Updating Git repository..."

cd "$ARCTURUS_GIT_DIR"

# Update patch state
python3 << 'PYTHON'
import json
from datetime import datetime

with open('.patch_state.json', 'r') as f:
    state = json.load(f)

patch_entry = {
    "number": 5,
    "name": "graph_logging",
    "description": "AI-native event logging system with Neo4j graph storage",
    "applied_at": datetime.utcnow().isoformat() + "Z",
    "applied_by": "Ka_tuar_el",
    "git_commit": "",
    "files_modified": [
        "/opt/mythos/graph_logging/src/system_monitor.py",
        "/opt/mythos/graph_logging/src/event_logger.py",
        "/opt/mythos/graph_logging/src/diagnostics.py",
        "/opt/mythos/graph_logging/config/monitoring_config.yaml",
        "~/.config/systemd/user/arcturus-monitor.service"
    ],
    "rollback_available": True
}

state['patches'].append(patch_entry)
state['current_patch'] = 5

with open('.patch_state.json', 'w') as f:
    json.dump(state, f, indent=2)
PYTHON

# Update deployment history
cat >> deployment/history.md << EOF

## Patch 0005: AI-Native Graph Logging
**Applied:** $(date -Iseconds)  
**By:** Ka_tuar_el

### Changes
- Implemented secondary logging system in Neo4j
- Created system monitoring service (checks every 60 seconds)
- Added daily cleanup service (removes events older than 10 days)
- Monitors: CPU, memory, disk, processes, systemd services
- Enables AI-powered diagnostics and causality analysis

### Files Created
- \`/opt/mythos/graph_logging/\` (complete installation)
- \`~/.config/systemd/user/arcturus-monitor.service\`
- \`~/.config/systemd/user/arcturus-cleanup.service\`
- \`~/.config/systemd/user/arcturus-cleanup.timer\`

### Services Monitored
- neo4j
- postgresql
- mythos_api
- mythos_bot
- Auto-discovers: mythos-*, arcturus-*

EOF

# Commit changes
git add .
git commit -m "Patch 0005: AI-Native Graph Event Logging

- Implemented secondary logging system in Neo4j
- System monitoring service (60 second intervals)
- Daily event cleanup (10 day retention)
- AI diagnostics interface for causality analysis
- Monitors system metrics and service states"

# Update patch state with commit hash
COMMIT_HASH=$(git rev-parse HEAD)
python3 -c "
import json
with open('.patch_state.json', 'r') as f:
    state = json.load(f)
state['patches'][-1]['git_commit'] = '$COMMIT_HASH'
with open('.patch_state.json', 'w') as f:
    json.dump(state, f, indent=2)
"

git add .patch_state.json
git commit --amend --no-edit

echo "✓ Git repository updated"

# ==========================================
# Installation Complete
# ==========================================

echo ""
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Patch 0005 has been successfully applied."
echo ""
echo "Services running:"
echo "  - arcturus-monitor.service (system monitoring)"
echo "  - arcturus-cleanup.timer (daily cleanup at 3 AM)"
echo ""
echo "Configuration:"
echo "  /opt/mythos/graph_logging/config/monitoring_config.yaml"
echo ""
echo "Logs:"
echo "  /opt/mythos/graph_logging/logs/monitor.log"
echo "  /opt/mythos/graph_logging/logs/cleanup.log"
echo ""
echo "Check status:"
echo "  systemctl --user status arcturus-monitor"
echo "  tail -f /opt/mythos/graph_logging/logs/monitor.log"
echo ""
echo "Query events:"
echo "  cypher-shell \"MATCH (e:Event) RETURN e ORDER BY e.timestamp DESC LIMIT 10\""
echo ""
echo "Git commit: $COMMIT_HASH"
echo ""

# Disable error trap (successful installation)
trap - EXIT

exit 0
