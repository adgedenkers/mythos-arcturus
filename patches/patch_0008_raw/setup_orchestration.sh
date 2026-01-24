#!/bin/bash
#
# Mythos Orchestration System - Master Setup Script
# 
# This script sets up the complete orchestration infrastructure:
# 1. Qdrant (Vector Database)
# 2. Redis (Task Queue / Pub-Sub)
# 3. TimescaleDB extension in PostgreSQL
# 4. Worker processes for extraction
# 5. Orchestrator API updates
#
# Usage: ./setup_orchestration.sh [step]
#   ./setup_orchestration.sh          # Run all steps
#   ./setup_orchestration.sh 1        # Run only step 1 (Qdrant)
#   ./setup_orchestration.sh 2        # Run only step 2 (Redis)
#   ./setup_orchestration.sh 3        # Run only step 3 (TimescaleDB)
#   ./setup_orchestration.sh 4        # Run only step 4 (Workers)
#   ./setup_orchestration.sh 5        # Run only step 5 (Orchestrator)
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
MYTHOS_BASE="/opt/mythos"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Logging
LOG_FILE="${MYTHOS_BASE}/logs/orchestration_setup_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "${MYTHOS_BASE}/logs"

log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_FILE"
}

header() {
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}  $1${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# Check prerequisites
check_prerequisites() {
    header "Checking Prerequisites"
    
    local missing=()
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        missing+=("docker")
    else
        log "✓ Docker installed: $(docker --version)"
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        missing+=("docker-compose")
    else
        log "✓ Docker Compose available"
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        missing+=("python3")
    else
        log "✓ Python3 installed: $(python3 --version)"
    fi
    
    # Check pip
    if ! command -v pip3 &> /dev/null; then
        missing+=("pip3")
    else
        log "✓ pip3 available"
    fi
    
    # Check PostgreSQL client
    if ! command -v psql &> /dev/null; then
        warn "psql not found - some database operations may fail"
    else
        log "✓ PostgreSQL client available"
    fi
    
    # Check Mythos base directory
    if [ ! -d "$MYTHOS_BASE" ]; then
        error "Mythos base directory not found: $MYTHOS_BASE"
        exit 1
    else
        log "✓ Mythos directory exists: $MYTHOS_BASE"
    fi
    
    # Check .env file
    if [ ! -f "$MYTHOS_BASE/.env" ]; then
        warn ".env file not found - will need manual configuration"
    else
        log "✓ .env file exists"
    fi
    
    if [ ${#missing[@]} -ne 0 ]; then
        error "Missing prerequisites: ${missing[*]}"
        echo "Please install missing dependencies and try again."
        exit 1
    fi
    
    log "All prerequisites satisfied!"
}

# Step 1: Setup Qdrant
setup_qdrant() {
    header "Step 1: Setting Up Qdrant (Vector Database)"
    
    # Check if Qdrant is already running
    if docker ps | grep -q qdrant; then
        log "Qdrant container already running"
        docker ps | grep qdrant
        return 0
    fi
    
    # Check if container exists but stopped
    if docker ps -a | grep -q mythos-qdrant; then
        log "Starting existing Qdrant container..."
        docker start mythos-qdrant
    else
        log "Creating Qdrant container..."
        
        # Create data directory
        mkdir -p "${MYTHOS_BASE}/data/qdrant"
        
        # Run Qdrant
        docker run -d \
            --name mythos-qdrant \
            -p 6333:6333 \
            -p 6334:6334 \
            -v "${MYTHOS_BASE}/data/qdrant:/qdrant/storage" \
            --restart unless-stopped \
            qdrant/qdrant:latest
        
        log "Waiting for Qdrant to start..."
        sleep 5
    fi
    
    # Verify Qdrant is running
    if curl -s http://localhost:6333/healthz | grep -q "passed"; then
        log "✓ Qdrant is healthy and running on port 6333"
    else
        error "Qdrant health check failed"
        return 1
    fi
    
    # Initialize collections
    log "Initializing Qdrant collections..."
    python3 "${SCRIPT_DIR}/step1_qdrant_setup.py"
    
    log "✓ Step 1 Complete: Qdrant is ready"
}

# Step 2: Setup Redis
setup_redis() {
    header "Step 2: Setting Up Redis (Task Queue)"
    
    # Check if Redis is already running
    if docker ps | grep -q redis; then
        log "Redis container already running"
        docker ps | grep redis
        return 0
    fi
    
    # Check if container exists but stopped
    if docker ps -a | grep -q mythos-redis; then
        log "Starting existing Redis container..."
        docker start mythos-redis
    else
        log "Creating Redis container..."
        
        # Create data directory
        mkdir -p "${MYTHOS_BASE}/data/redis"
        
        # Run Redis
        docker run -d \
            --name mythos-redis \
            -p 6379:6379 \
            -v "${MYTHOS_BASE}/data/redis:/data" \
            --restart unless-stopped \
            redis:7-alpine redis-server --appendonly yes
        
        log "Waiting for Redis to start..."
        sleep 3
    fi
    
    # Verify Redis is running
    if redis-cli ping 2>/dev/null | grep -q "PONG"; then
        log "✓ Redis is healthy and running on port 6379"
    elif docker exec mythos-redis redis-cli ping | grep -q "PONG"; then
        log "✓ Redis is healthy and running on port 6379 (via docker)"
    else
        error "Redis health check failed"
        return 1
    fi
    
    # Initialize streams
    log "Initializing Redis streams..."
    python3 "${SCRIPT_DIR}/step2_redis_setup.py"
    
    log "✓ Step 2 Complete: Redis is ready"
}

# Step 3: Setup TimescaleDB
setup_timescaledb() {
    header "Step 3: Setting Up TimescaleDB Extension"
    
    # Load environment variables
    if [ -f "$MYTHOS_BASE/.env" ]; then
        source "$MYTHOS_BASE/.env"
    fi
    
    # Default values if not in .env
    POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
    POSTGRES_DB="${POSTGRES_DB:-mythos}"
    POSTGRES_USER="${POSTGRES_USER:-postgres}"
    
    log "Connecting to PostgreSQL at ${POSTGRES_HOST}/${POSTGRES_DB}..."
    
    # Run TimescaleDB setup script
    python3 "${SCRIPT_DIR}/step3_timescaledb_setup.py"
    
    log "✓ Step 3 Complete: TimescaleDB is configured"
}

# Step 4: Setup Workers
setup_workers() {
    header "Step 4: Setting Up Worker Processes"
    
    # Create workers directory
    mkdir -p "${MYTHOS_BASE}/workers"
    
    # Copy worker files
    log "Installing worker modules..."
#     cp "${SCRIPT_DIR}/workers/"*.py "${MYTHOS_BASE}/workers/"
    
    # Install Python dependencies
    log "Installing Python dependencies..."
    if [ -f "${MYTHOS_BASE}/.venv/bin/activate" ]; then
        source "${MYTHOS_BASE}/.venv/bin/activate"
    fi
    
    pip install --break-system-packages \
        redis \
        qdrant-client \
        sentence-transformers \
        Pillow \
        aiohttp \
        2>&1 | tee -a "$LOG_FILE"
    
    # Create systemd service files for workers
    log "Creating systemd service files..."
    python3 "${SCRIPT_DIR}/step4_worker_setup.py"
    
    log "✓ Step 4 Complete: Workers are installed"
    echo ""
    echo "To start workers manually:"
    echo "  cd ${MYTHOS_BASE}/workers"
    echo "  python3 worker.py grid"
    echo "  python3 worker.py embedding"
    echo "  python3 worker.py vision"
    echo ""
    echo "Or enable systemd services:"
    echo "  sudo systemctl enable mythos-worker-grid"
    echo "  sudo systemctl start mythos-worker-grid"
}

# Step 5: Update Orchestrator
setup_orchestrator() {
    header "Step 5: Updating Orchestrator API"
    
    # Backup existing API
    if [ -f "${MYTHOS_BASE}/api/main.py" ]; then
        cp "${MYTHOS_BASE}/api/main.py" "${MYTHOS_BASE}/api/main.py.backup.$(date +%Y%m%d_%H%M%S)"
        log "Backed up existing main.py"
    fi
    
    # Copy orchestrator modules
    log "Installing orchestrator modules..."
#     cp "${SCRIPT_DIR}/orchestrator/"*.py "${MYTHOS_BASE}/api/"
    
    # Run integration script
    log "Integrating orchestrator with existing API..."
    python3 "${SCRIPT_DIR}/step5_orchestrator_setup.py"
    
    # Restart API if running as service
    if systemctl is-active --quiet mythos-api; then
        log "Restarting Mythos API service..."
        sudo systemctl restart mythos-api
        sleep 3
        
        if systemctl is-active --quiet mythos-api; then
            log "✓ API restarted successfully"
        else
            error "API failed to restart - check logs with: journalctl -u mythos-api"
            return 1
        fi
    else
        warn "Mythos API service not running - restart manually when ready"
    fi
    
    log "✓ Step 5 Complete: Orchestrator is updated"
}

# Verify complete installation
verify_installation() {
    header "Verifying Installation"
    
    local all_good=true
    
    # Check Qdrant
    if curl -s http://localhost:6333/healthz | grep -q "passed"; then
        log "✓ Qdrant: Running"
    else
        error "✗ Qdrant: Not responding"
        all_good=false
    fi
    
    # Check Redis
    if docker exec mythos-redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
        log "✓ Redis: Running"
    else
        error "✗ Redis: Not responding"
        all_good=false
    fi
    
    # Check TimescaleDB
    if python3 -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv('${MYTHOS_BASE}/.env')
conn = psycopg2.connect(
    host=os.getenv('POSTGRES_HOST', 'localhost'),
    database=os.getenv('POSTGRES_DB', 'mythos'),
    user=os.getenv('POSTGRES_USER', 'postgres'),
    password=os.getenv('POSTGRES_PASSWORD', '')
)
cur = conn.cursor()
cur.execute(\"SELECT extname FROM pg_extension WHERE extname = 'timescaledb'\")
result = cur.fetchone()
exit(0 if result else 1)
" 2>/dev/null; then
        log "✓ TimescaleDB: Installed"
    else
        error "✗ TimescaleDB: Not installed or not accessible"
        all_good=false
    fi
    
    # Check worker files
    if [ -f "${MYTHOS_BASE}/workers/worker.py" ]; then
        log "✓ Workers: Installed"
    else
        error "✗ Workers: Not installed"
        all_good=false
    fi
    
    # Check orchestrator files
    if [ -f "${MYTHOS_BASE}/api/orchestrator.py" ]; then
        log "✓ Orchestrator: Installed"
    else
        error "✗ Orchestrator: Not installed"
        all_good=false
    fi
    
    echo ""
    if $all_good; then
        echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}  ✓ All components installed successfully!${NC}"
        echo -e "${GREEN}════════════════════════════════════════════════════════════${NC}"
    else
        echo -e "${RED}════════════════════════════════════════════════════════════${NC}"
        echo -e "${RED}  ⚠️  Some components failed - check logs above${NC}"
        echo -e "${RED}════════════════════════════════════════════════════════════${NC}"
    fi
}

# Main execution
main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║     Mythos Orchestration System - Setup Script             ║${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    local step="${1:-all}"
    
    check_prerequisites
    
    case "$step" in
        1|qdrant)
            setup_qdrant
            ;;
        2|redis)
            setup_redis
            ;;
        3|timescale|timescaledb)
            setup_timescaledb
            ;;
        4|workers)
            setup_workers
            ;;
        5|orchestrator)
            setup_orchestrator
            ;;
        all)
            setup_qdrant
            setup_redis
            setup_timescaledb
            setup_workers
            setup_orchestrator
            verify_installation
            ;;
        verify)
            verify_installation
            ;;
        *)
            echo "Usage: $0 [step]"
            echo "  step: 1|2|3|4|5|all|verify"
            echo ""
            echo "Steps:"
            echo "  1 - Setup Qdrant (Vector Database)"
            echo "  2 - Setup Redis (Task Queue)"
            echo "  3 - Setup TimescaleDB (Time-series)"
            echo "  4 - Setup Workers (Extraction processors)"
            echo "  5 - Setup Orchestrator (API updates)"
            echo "  all - Run all steps"
            echo "  verify - Verify installation"
            exit 1
            ;;
    esac
    
    echo ""
    log "Setup complete! Log saved to: $LOG_FILE"
}

main "$@"
