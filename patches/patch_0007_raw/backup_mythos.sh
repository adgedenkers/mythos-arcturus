#!/bin/bash
#
# Mythos Complete System Backup
# Creates full backup of all Mythos infrastructure
#
# Backs up:
# - All Python code (API, bot, assistants, tools)
# - Configuration files (.env, configs)
# - Database schemas (PostgreSQL + Neo4j exports)
# - Patches and deployment scripts
# - System service files
# - Media storage (optional, can be large)
#
# Stores in: ~/mythos-backups/full-backup__YYYYMMDD_HHMMSS.zip

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
BACKUP_BASE_DIR="$HOME/mythos-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="full-backup__${TIMESTAMP}"
BACKUP_DIR="${BACKUP_BASE_DIR}/${BACKUP_NAME}"
BACKUP_ZIP="${BACKUP_BASE_DIR}/${BACKUP_NAME}.zip"

# Mythos locations
MYTHOS_ROOT="/opt/mythos"
MEDIA_DIR="/opt/mythos/media"
ENV_FILE="/opt/mythos/.env"

# Database config
DB_NAME="mythos"
DB_USER="postgres"

# Options
INCLUDE_MEDIA=false
INCLUDE_DB_DATA=false
VERBOSE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --with-media)
            INCLUDE_MEDIA=true
            shift
            ;;
        --with-db-data)
            INCLUDE_DB_DATA=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "Mythos Complete System Backup"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --with-media      Include media files (can be very large)"
            echo "  --with-db-data    Include full database data dump (not just schema)"
            echo "  -v, --verbose     Show detailed progress"
            echo "  -h, --help        Show this help message"
            echo ""
            echo "Default behavior:"
            echo "  - Backs up all code, configs, schemas"
            echo "  - Excludes media files (they're large)"
            echo "  - Exports only database schema (not data)"
            echo ""
            echo "Output: ~/mythos-backups/full-backup__YYYYMMDD_HHMMSS.zip"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Run with --help for usage"
            exit 1
            ;;
    esac
done

# Helper functions
log() {
    echo -e "$1"
}

log_step() {
    log "\n${CYAN}▶ $1${NC}"
}

log_success() {
    log "${GREEN}✓ $1${NC}"
}

log_warning() {
    log "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    log "${RED}❌ $1${NC}"
}

log_verbose() {
    if [ "$VERBOSE" = true ]; then
        log "  $1"
    fi
}

# Start backup
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Mythos Complete System Backup${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""
log "Backup name: ${CYAN}${BACKUP_NAME}${NC}"
log "Timestamp:   ${CYAN}${TIMESTAMP}${NC}"
log "Target:      ${CYAN}${BACKUP_ZIP}${NC}"
echo ""

if [ "$INCLUDE_MEDIA" = true ]; then
    log_warning "Including media files (this will be large)"
fi

if [ "$INCLUDE_DB_DATA" = true ]; then
    log_warning "Including full database data"
fi

echo ""

# Create backup directory
log_step "Creating backup directory"
mkdir -p "${BACKUP_DIR}"
log_success "Created: ${BACKUP_DIR}"

# Create subdirectories
mkdir -p "${BACKUP_DIR}/code"
mkdir -p "${BACKUP_DIR}/config"
mkdir -p "${BACKUP_DIR}/database"
mkdir -p "${BACKUP_DIR}/systemd"
mkdir -p "${BACKUP_DIR}/logs"
mkdir -p "${BACKUP_DIR}/metadata"

# Backup code
log_step "Backing up code files"

if [ -d "$MYTHOS_ROOT" ]; then
    # API
    if [ -d "${MYTHOS_ROOT}/api" ]; then
        log_verbose "Backing up API..."
        cp -r "${MYTHOS_ROOT}/api" "${BACKUP_DIR}/code/"
        log_success "API code backed up"
    fi
    
    # Telegram bot
    if [ -d "${MYTHOS_ROOT}/telegram_bot" ]; then
        log_verbose "Backing up Telegram bot..."
        cp -r "${MYTHOS_ROOT}/telegram_bot" "${BACKUP_DIR}/code/"
        log_success "Telegram bot backed up"
    fi
    
    # Assistants
    if [ -d "${MYTHOS_ROOT}/assistants" ]; then
        log_verbose "Backing up assistants..."
        cp -r "${MYTHOS_ROOT}/assistants" "${BACKUP_DIR}/code/"
        log_success "Assistants backed up"
    fi
    
    # Tools
    if [ -d "${MYTHOS_ROOT}/tools" ]; then
        log_verbose "Backing up tools..."
        cp -r "${MYTHOS_ROOT}/tools" "${BACKUP_DIR}/code/"
        log_success "Tools backed up"
    fi
    
    # Event simulator
    if [ -d "${MYTHOS_ROOT}/event_simulator" ]; then
        log_verbose "Backing up event simulator..."
        cp -r "${MYTHOS_ROOT}/event_simulator" "${BACKUP_DIR}/code/"
        log_success "Event simulator backed up"
    fi
    
    # Finance
    if [ -d "${MYTHOS_ROOT}/finance" ]; then
        log_verbose "Backing up finance modules..."
        cp -r "${MYTHOS_ROOT}/finance" "${BACKUP_DIR}/code/"
        log_success "Finance modules backed up"
    fi
    
    # Graph logging
    if [ -d "${MYTHOS_ROOT}/graph_logging" ]; then
        log_verbose "Backing up graph logging..."
        cp -r "${MYTHOS_ROOT}/graph_logging" "${BACKUP_DIR}/code/"
        log_success "Graph logging backed up"
    fi
    
    # LLM diagnostics
    if [ -d "${MYTHOS_ROOT}/llm_diagnostics" ]; then
        log_verbose "Backing up LLM diagnostics..."
        cp -r "${MYTHOS_ROOT}/llm_diagnostics" "${BACKUP_DIR}/code/"
        log_success "LLM diagnostics backed up"
    fi
    
    # Patches
    if [ -d "${MYTHOS_ROOT}/patches" ]; then
        log_verbose "Backing up patches..."
        cp -r "${MYTHOS_ROOT}/patches" "${BACKUP_DIR}/code/"
        log_success "Patches backed up"
    fi
    
    # Prompts
    if [ -d "${MYTHOS_ROOT}/prompts" ]; then
        log_verbose "Backing up prompts..."
        cp -r "${MYTHOS_ROOT}/prompts" "${BACKUP_DIR}/code/"
        log_success "Prompts backed up"
    fi
    
    # Updates
    if [ -d "${MYTHOS_ROOT}/updates" ]; then
        log_verbose "Backing up update scripts..."
        cp -r "${MYTHOS_ROOT}/updates" "${BACKUP_DIR}/code/"
        log_success "Update scripts backed up"
    fi
    
    # Root-level scripts and files
    log_verbose "Backing up root-level files..."
    for file in "${MYTHOS_ROOT}"/*.py "${MYTHOS_ROOT}"/*.sh "${MYTHOS_ROOT}"/*.sql "${MYTHOS_ROOT}"/*.txt "${MYTHOS_ROOT}"/*.md "${MYTHOS_ROOT}"/*.html; do
        if [ -f "$file" ]; then
            cp "$file" "${BACKUP_DIR}/code/" 2>/dev/null || true
        fi
    done
    log_success "Root-level files backed up"
    
else
    log_error "Mythos root directory not found: $MYTHOS_ROOT"
    log "Continuing with partial backup..."
fi

# Backup configuration files
log_step "Backing up configuration files"

# .env file (sanitized)
if [ -f "$ENV_FILE" ]; then
    log_verbose "Backing up .env (SANITIZED - passwords will be marked)..."
    
    # Create sanitized version
    cat "$ENV_FILE" | sed -E 's/(PASSWORD|SECRET|KEY|TOKEN)=.*/\1=***REDACTED***/g' > "${BACKUP_DIR}/config/.env.sanitized"
    
    # Also keep original with warning
    cp "$ENV_FILE" "${BACKUP_DIR}/config/.env.ORIGINAL_CONTAINS_SECRETS"
    chmod 600 "${BACKUP_DIR}/config/.env.ORIGINAL_CONTAINS_SECRETS"
    
    log_success ".env backed up (sanitized + original)"
    log_warning "Original .env contains secrets - keep backup secure!"
else
    log_warning ".env file not found at $ENV_FILE"
fi

# Config directories
for config_dir in "${MYTHOS_ROOT}/config" "${MYTHOS_ROOT}/*/config"; do
    if [ -d "$config_dir" ]; then
        log_verbose "Backing up config: $config_dir"
        cp -r "$config_dir" "${BACKUP_DIR}/config/" 2>/dev/null || true
    fi
done

if ls "${BACKUP_DIR}/config/"* 1> /dev/null 2>&1; then
    log_success "Configuration files backed up"
else
    log_warning "No configuration files found"
fi

# Backup database schemas
log_step "Backing up database schemas"

# PostgreSQL schema
if command -v pg_dump &> /dev/null; then
    log_verbose "Exporting PostgreSQL schema..."
    
    if [ "$INCLUDE_DB_DATA" = true ]; then
        # Full data dump
        if pg_dump -U "$DB_USER" "$DB_NAME" > "${BACKUP_DIR}/database/postgres_full_dump.sql" 2>/dev/null; then
            log_success "PostgreSQL full dump exported"
        else
            log_warning "PostgreSQL full dump failed (may need sudo or password)"
        fi
    else
        # Schema only
        if pg_dump -U "$DB_USER" --schema-only "$DB_NAME" > "${BACKUP_DIR}/database/postgres_schema.sql" 2>/dev/null; then
            log_success "PostgreSQL schema exported"
        else
            log_warning "PostgreSQL schema export failed (may need sudo or password)"
        fi
    fi
else
    log_warning "pg_dump not found - skipping PostgreSQL backup"
fi

# Neo4j export (if cypher-shell available)
if command -v cypher-shell &> /dev/null; then
    log_verbose "Exporting Neo4j schema..."
    
    # Get constraint and index definitions
    if cypher-shell "SHOW CONSTRAINTS" > "${BACKUP_DIR}/database/neo4j_constraints.txt" 2>/dev/null; then
        log_success "Neo4j constraints exported"
    else
        log_warning "Neo4j constraints export failed"
    fi
    
    if cypher-shell "SHOW INDEXES" > "${BACKUP_DIR}/database/neo4j_indexes.txt" 2>/dev/null; then
        log_success "Neo4j indexes exported"
    else
        log_warning "Neo4j indexes export failed"
    fi
    
    # Export sample of each node type
    cypher-shell "MATCH (n) RETURN DISTINCT labels(n), count(*)" > "${BACKUP_DIR}/database/neo4j_node_counts.txt" 2>/dev/null || true
else
    log_warning "cypher-shell not found - skipping Neo4j backup"
fi

# Backup systemd service files
log_step "Backing up systemd service files"

SYSTEMD_DIR="/etc/systemd/system"
if [ -d "$SYSTEMD_DIR" ]; then
    log_verbose "Looking for Mythos service files..."
    
    for service in mythos-api.service mythos-telegram-bot.service arcturus-monitor.service arcturus-cleanup.service arcturus-cleanup.timer; do
        if [ -f "${SYSTEMD_DIR}/${service}" ]; then
            log_verbose "Backing up: $service"
            sudo cp "${SYSTEMD_DIR}/${service}" "${BACKUP_DIR}/systemd/" 2>/dev/null || cp "${SYSTEMD_DIR}/${service}" "${BACKUP_DIR}/systemd/" 2>/dev/null || true
        fi
    done
    
    if ls "${BACKUP_DIR}/systemd/"*.service 1> /dev/null 2>&1 || ls "${BACKUP_DIR}/systemd/"*.timer 1> /dev/null 2>&1; then
        log_success "Systemd service files backed up"
    else
        log_warning "No systemd service files found"
    fi
else
    log_warning "Systemd directory not found"
fi

# Backup recent logs
log_step "Backing up recent logs"

# Application logs
for log_dir in "${MYTHOS_ROOT}/logs" "${MYTHOS_ROOT}/*/logs"; do
    if [ -d "$log_dir" ]; then
        log_verbose "Backing up logs from: $log_dir"
        cp -r "$log_dir" "${BACKUP_DIR}/logs/" 2>/dev/null || true
    fi
done

# Recent systemd logs
if command -v journalctl &> /dev/null; then
    log_verbose "Exporting recent systemd logs..."
    
    sudo journalctl -u mythos-api --since "7 days ago" > "${BACKUP_DIR}/logs/systemd_mythos-api_7days.log" 2>/dev/null || true
    sudo journalctl -u mythos-telegram-bot --since "7 days ago" > "${BACKUP_DIR}/logs/systemd_mythos-telegram-bot_7days.log" 2>/dev/null || true
fi

if ls "${BACKUP_DIR}/logs/"* 1> /dev/null 2>&1; then
    log_success "Logs backed up"
else
    log_warning "No logs found"
fi

# Backup media (optional)
if [ "$INCLUDE_MEDIA" = true ]; then
    log_step "Backing up media files"
    
    if [ -d "$MEDIA_DIR" ]; then
        log_warning "Media backup can be very large and slow"
        
        # Count files first
        MEDIA_COUNT=$(find "$MEDIA_DIR" -type f 2>/dev/null | wc -l)
        log "Found $MEDIA_COUNT media files"
        
        if [ "$MEDIA_COUNT" -gt 0 ]; then
            log_verbose "Copying media files..."
            mkdir -p "${BACKUP_DIR}/media"
            cp -r "$MEDIA_DIR"/* "${BACKUP_DIR}/media/" 2>/dev/null || true
            log_success "Media files backed up"
        else
            log_warning "No media files found"
        fi
    else
        log_warning "Media directory not found: $MEDIA_DIR"
    fi
else
    log_warning "Skipping media files (use --with-media to include)"
    
    # Create note about media
    echo "Media files were NOT included in this backup." > "${BACKUP_DIR}/media/MEDIA_NOT_INCLUDED.txt"
    echo "Run with --with-media flag to include media files." >> "${BACKUP_DIR}/media/MEDIA_NOT_INCLUDED.txt"
    echo "" >> "${BACKUP_DIR}/media/MEDIA_NOT_INCLUDED.txt"
    echo "Media location: $MEDIA_DIR" >> "${BACKUP_DIR}/media/MEDIA_NOT_INCLUDED.txt"
fi

# Create metadata
log_step "Creating backup metadata"

cat > "${BACKUP_DIR}/metadata/backup_info.txt" << EOF
Mythos System Backup
====================

Backup Name: ${BACKUP_NAME}
Created:     ${TIMESTAMP}
Date:        $(date)
Hostname:    $(hostname)
User:        $(whoami)

Backup Contents:
----------------
Code:        $(du -sh "${BACKUP_DIR}/code" 2>/dev/null | cut -f1)
Config:      $(du -sh "${BACKUP_DIR}/config" 2>/dev/null | cut -f1)
Database:    $(du -sh "${BACKUP_DIR}/database" 2>/dev/null | cut -f1)
Systemd:     $(du -sh "${BACKUP_DIR}/systemd" 2>/dev/null | cut -f1)
Logs:        $(du -sh "${BACKUP_DIR}/logs" 2>/dev/null | cut -f1)
Media:       $(du -sh "${BACKUP_DIR}/media" 2>/dev/null | cut -f1)

Options:
--------
Include Media:    ${INCLUDE_MEDIA}
Include DB Data:  ${INCLUDE_DB_DATA}

System Info:
------------
OS:          $(uname -a)
Python:      $(python3 --version 2>/dev/null || echo "Not found")
PostgreSQL:  $(psql --version 2>/dev/null || echo "Not found")
Neo4j:       $(neo4j version 2>/dev/null || echo "Not found")

Mythos Structure:
-----------------
EOF

# Add directory tree
if command -v tree &> /dev/null; then
    tree -L 2 "$MYTHOS_ROOT" >> "${BACKUP_DIR}/metadata/backup_info.txt" 2>/dev/null || true
else
    find "$MYTHOS_ROOT" -maxdepth 2 -type d >> "${BACKUP_DIR}/metadata/backup_info.txt" 2>/dev/null || true
fi

log_success "Metadata created"

# Create file manifest
log_verbose "Creating file manifest..."
find "${BACKUP_DIR}" -type f > "${BACKUP_DIR}/metadata/file_manifest.txt"
log_success "File manifest created"

# Create checksums
log_verbose "Creating checksums..."
find "${BACKUP_DIR}" -type f -not -path "*/metadata/*" -exec sha256sum {} \; > "${BACKUP_DIR}/metadata/checksums.sha256" 2>/dev/null || true
log_success "Checksums created"

# Calculate total size
log_step "Calculating backup size"
BACKUP_SIZE=$(du -sh "${BACKUP_DIR}" | cut -f1)
log "Total backup size: ${CYAN}${BACKUP_SIZE}${NC}"

# Create zip archive
log_step "Creating ZIP archive"
log_verbose "This may take a while for large backups..."

cd "${BACKUP_BASE_DIR}"
if zip -r -q "${BACKUP_NAME}.zip" "${BACKUP_NAME}"; then
    ZIP_SIZE=$(du -sh "${BACKUP_ZIP}" | cut -f1)
    log_success "ZIP archive created: ${ZIP_SIZE}"
    
    # Remove temporary directory
    log_verbose "Cleaning up temporary directory..."
    rm -rf "${BACKUP_DIR}"
    log_success "Temporary directory removed"
else
    log_error "Failed to create ZIP archive"
    log "Temporary backup directory preserved at: ${BACKUP_DIR}"
    exit 1
fi

# Final summary
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Backup Complete${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
log "${BLUE}Backup Information:${NC}"
log "  Location: ${CYAN}${BACKUP_ZIP}${NC}"
log "  Size:     ${CYAN}${ZIP_SIZE}${NC}"
log "  Created:  ${CYAN}$(date)${NC}"
echo ""
log "${BLUE}What's included:${NC}"
log "  ✓ All Python code (API, bot, assistants, tools)"
log "  ✓ Configuration files (.env sanitized + original)"
log "  ✓ Database schemas (PostgreSQL + Neo4j)"
log "  ✓ System service files"
log "  ✓ Recent logs (last 7 days)"
log "  ✓ Patches and deployment scripts"
if [ "$INCLUDE_MEDIA" = true ]; then
    log "  ✓ Media files"
else
    log "  - Media files (excluded, use --with-media to include)"
fi
if [ "$INCLUDE_DB_DATA" = true ]; then
    log "  ✓ Full database data"
else
    log "  - Full database data (excluded, use --with-db-data to include)"
fi
echo ""
log "${BLUE}Restore procedure:${NC}"
log "  1. Unzip: ${YELLOW}unzip ${BACKUP_ZIP}${NC}"
log "  2. Review: ${YELLOW}cat ${BACKUP_NAME}/metadata/backup_info.txt${NC}"
log "  3. Restore files as needed"
log "  4. Run: ${YELLOW}psql -U postgres -d mythos < ${BACKUP_NAME}/database/postgres_schema.sql${NC}"
echo ""
log "${YELLOW}Security note:${NC}"
log "  Original .env with secrets is included: ${RED}config/.env.ORIGINAL_CONTAINS_SECRETS${NC}"
log "  Keep this backup secure!"
echo ""
log "${GREEN}Done!${NC}"
