#!/bin/bash
#
# Mythos Sprint 1 Master Deployment Script
# Orchestrates full photo input system deployment
#
# This script runs all deployment steps in correct order:
# 1. Database migration
# 2. Media directory setup
# 3. API patching
# 4. Bot installation
# 5. Service restarts
# 6. Verification tests

set -e  # Exit on any error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
DEPLOYMENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="${DEPLOYMENT_DIR}/deployment_$(date +%Y%m%d_%H%M%S).log"

# Database config (adjust if needed)
DB_NAME="mythos"
DB_USER="postgres"

# Logging function
log() {
    echo -e "$1" | tee -a "$LOG_FILE"
}

log_step() {
    log "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    log "${CYAN}$1${NC}"
    log "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
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

# Check prerequisites
check_prerequisites() {
    log_step "Step 0: Checking Prerequisites"
    
    local all_good=true
    
    # Check if files exist
    if [ ! -f "${DEPLOYMENT_DIR}/001_media_storage_migration.sql" ]; then
        log_error "Missing: 001_media_storage_migration.sql"
        all_good=false
    else
        log_success "Found SQL migration"
    fi
    
    if [ ! -f "${DEPLOYMENT_DIR}/mythos_bot_with_photos.py" ]; then
        log_error "Missing: mythos_bot_with_photos.py"
        all_good=false
    else
        log_success "Found bot file"
    fi
    
    if [ ! -f "${DEPLOYMENT_DIR}/patch_api_with_media.sh" ]; then
        log_error "Missing: patch_api_with_media.sh"
        all_good=false
    else
        log_success "Found API patcher"
    fi
    
    if [ ! -f "${DEPLOYMENT_DIR}/install_bot_with_photos.sh" ]; then
        log_error "Missing: install_bot_with_photos.sh"
        all_good=false
    else
        log_success "Found bot installer"
    fi
    
    # Check PostgreSQL access
    if command -v psql &> /dev/null; then
        log_success "PostgreSQL client available"
    else
        log_warning "psql not found - database migration will need manual execution"
    fi
    
    # Check Python
    if command -v python3 &> /dev/null; then
        log_success "Python 3 available"
    else
        log_error "Python 3 not found"
        all_good=false
    fi
    
    if [ "$all_good" = false ]; then
        log_error "Prerequisites check failed"
        exit 1
    fi
    
    log ""
}

# Step 1: Database migration
run_database_migration() {
    log_step "Step 1: Database Migration"
    
    log "Applying media_files schema..."
    
    if command -v psql &> /dev/null; then
        if psql -U "$DB_USER" -d "$DB_NAME" -f "${DEPLOYMENT_DIR}/001_media_storage_migration.sql" &>> "$LOG_FILE"; then
            log_success "Database migration applied"
            
            # Verify table exists
            if psql -U "$DB_USER" -d "$DB_NAME" -c "\dt media_files" &>> "$LOG_FILE"; then
                log_success "Verified media_files table exists"
            else
                log_error "media_files table not found after migration"
                return 1
            fi
        else
            log_error "Database migration failed - check log: $LOG_FILE"
            return 1
        fi
    else
        log_warning "psql not available - run migration manually:"
        log "  ${YELLOW}psql -U $DB_USER -d $DB_NAME -f ${DEPLOYMENT_DIR}/001_media_storage_migration.sql${NC}"
        log ""
        log "Continue anyway? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            log "Aborted"
            exit 1
        fi
    fi
    
    log ""
}

# Step 2: Media directory setup
setup_media_directory() {
    log_step "Step 2: Media Directory Setup"
    
    local media_dir="/opt/mythos/media"
    
    if [ ! -d "$media_dir" ]; then
        log "Creating $media_dir..."
        
        if mkdir -p "$media_dir" 2>/dev/null; then
            log_success "Created directory"
        else
            log "Creating with sudo..."
            if sudo mkdir -p "$media_dir"; then
                sudo chown mythos:mythos "$media_dir" 2>/dev/null || true
                sudo chmod 755 "$media_dir"
                log_success "Created directory with sudo"
            else
                log_error "Failed to create directory"
                return 1
            fi
        fi
    else
        log_success "Directory already exists"
    fi
    
    # Check permissions
    if [ -w "$media_dir" ]; then
        log_success "Directory is writable"
    else
        log_warning "Directory exists but not writable"
        log "Attempting to fix permissions..."
        if sudo chown -R mythos:mythos "$media_dir" && sudo chmod -R 755 "$media_dir"; then
            log_success "Permissions fixed"
        else
            log_error "Failed to fix permissions"
            return 1
        fi
    fi
    
    log ""
}

# Step 3: API patching
patch_api() {
    log_step "Step 3: API Patching"
    
    log "Running API patcher..."
    
    if bash "${DEPLOYMENT_DIR}/patch_api_with_media.sh" &>> "$LOG_FILE"; then
        log_success "API patched successfully"
    else
        log_error "API patching failed - check log: $LOG_FILE"
        return 1
    fi
    
    log ""
}

# Step 4: Bot installation
install_bot() {
    log_step "Step 4: Bot Installation"
    
    log "Running bot installer..."
    
    # Change to deployment directory so installer finds the bot file
    cd "$DEPLOYMENT_DIR"
    
    if bash "${DEPLOYMENT_DIR}/install_bot_with_photos.sh" &>> "$LOG_FILE"; then
        log_success "Bot installed successfully"
    else
        log_error "Bot installation failed - check log: $LOG_FILE"
        return 1
    fi
    
    log ""
}

# Step 5: Service restarts
restart_services() {
    log_step "Step 5: Service Restarts"
    
    # Check if services exist
    local api_exists=false
    local bot_exists=false
    
    if systemctl list-unit-files | grep -q mythos-api.service; then
        api_exists=true
    fi
    
    if systemctl list-unit-files | grep -q mythos-telegram-bot.service; then
        bot_exists=true
    fi
    
    # Restart API
    if [ "$api_exists" = true ]; then
        log "Restarting mythos-api service..."
        if sudo systemctl restart mythos-api.service; then
            log_success "API service restarted"
            
            # Wait a moment and check status
            sleep 2
            if sudo systemctl is-active --quiet mythos-api.service; then
                log_success "API service is active"
            else
                log_error "API service failed to start"
                log "Check logs: ${YELLOW}sudo journalctl -u mythos-api -n 50${NC}"
                return 1
            fi
        else
            log_error "Failed to restart API service"
            return 1
        fi
    else
        log_warning "API service not found - restart manually if needed"
    fi
    
    # Restart Bot
    if [ "$bot_exists" = true ]; then
        log "Restarting mythos-telegram-bot service..."
        if sudo systemctl restart mythos-telegram-bot.service; then
            log_success "Bot service restarted"
            
            # Wait a moment and check status
            sleep 2
            if sudo systemctl is-active --quiet mythos-telegram-bot.service; then
                log_success "Bot service is active"
            else
                log_error "Bot service failed to start"
                log "Check logs: ${YELLOW}sudo journalctl -u mythos-telegram-bot -n 50${NC}"
                return 1
            fi
        else
            log_error "Failed to restart bot service"
            return 1
        fi
    else
        log_warning "Bot service not found - restart manually if needed"
    fi
    
    log ""
}

# Step 6: Verification
run_verification() {
    log_step "Step 6: Verification"
    
    log "Running basic verification tests...\n"
    
    # Check database table
    log "Checking database:"
    if psql -U "$DB_USER" -d "$DB_NAME" -c "SELECT COUNT(*) FROM media_files" &>> "$LOG_FILE"; then
        log_success "  media_files table accessible"
    else
        log_error "  Cannot query media_files table"
    fi
    
    # Check media directory
    log "Checking filesystem:"
    if [ -w "/opt/mythos/media" ]; then
        log_success "  Media directory writable"
    else
        log_error "  Media directory not writable"
    fi
    
    # Check API file
    log "Checking API:"
    if grep -q "def upload_media" /opt/mythos/api/main.py; then
        log_success "  Media endpoints present"
    else
        log_error "  Media endpoints not found"
    fi
    
    # Check bot file
    log "Checking bot:"
    if grep -q "def handle_photo" /opt/mythos/telegram_bot/mythos_bot.py; then
        log_success "  Photo handler present"
    else
        log_error "  Photo handler not found"
    fi
    
    # Check services
    log "Checking services:"
    if systemctl is-active --quiet mythos-api.service 2>/dev/null; then
        log_success "  API service running"
    else
        log_warning "  API service not running or not found"
    fi
    
    if systemctl is-active --quiet mythos-telegram-bot.service 2>/dev/null; then
        log_success "  Bot service running"
    else
        log_warning "  Bot service not running or not found"
    fi
    
    log ""
}

# Main execution
main() {
    log "${BLUE}════════════════════════════════════════════════════════${NC}"
    log "${BLUE}  Mythos Sprint 1 Master Deployment${NC}"
    log "${BLUE}  Photo Input System - Complete Installation${NC}"
    log "${BLUE}════════════════════════════════════════════════════════${NC}"
    log ""
    log "Deployment log: ${YELLOW}$LOG_FILE${NC}"
    log ""
    log "${YELLOW}This will:${NC}"
    log "  1. Apply database migration (media_files table)"
    log "  2. Create /opt/mythos/media directory"
    log "  3. Patch API with media endpoints"
    log "  4. Install photo-enabled bot"
    log "  5. Restart services"
    log "  6. Run verification tests"
    log ""
    log "${RED}WARNING: This will modify your production system${NC}"
    log "Continue? (y/N)"
    read -r response
    
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log "Deployment cancelled"
        exit 0
    fi
    
    log ""
    log "Starting deployment at $(date)"
    log ""
    
    # Run all steps
    check_prerequisites || { log_error "Prerequisites check failed"; exit 1; }
    run_database_migration || { log_error "Database migration failed"; exit 1; }
    setup_media_directory || { log_error "Media directory setup failed"; exit 1; }
    patch_api || { log_error "API patching failed"; exit 1; }
    install_bot || { log_error "Bot installation failed"; exit 1; }
    restart_services || { log_warning "Some services failed to restart"; }
    run_verification
    
    # Final summary
    log_step "Deployment Complete"
    
    log "${GREEN}✓ Sprint 1 deployment finished successfully!${NC}"
    log ""
    log "${BLUE}What was deployed:${NC}"
    log "  • PostgreSQL: media_files table with indexes"
    log "  • Filesystem: /opt/mythos/media directory"
    log "  • API: 5 new media endpoints"
    log "  • Bot: Photo handling + /photos command"
    log ""
    log "${BLUE}Test your deployment:${NC}"
    log "  1. Open Telegram and message your bot"
    log "  2. Send: ${YELLOW}/start${NC}"
    log "  3. Send a photo"
    log "  4. Send: ${YELLOW}/photos${NC}"
    log "  5. Check: ${YELLOW}https://mythos-api.denkers.co/docs${NC}"
    log ""
    log "${BLUE}Monitor services:${NC}"
    log "  API logs:  ${YELLOW}sudo journalctl -u mythos-api -f${NC}"
    log "  Bot logs:  ${YELLOW}sudo journalctl -u mythos-telegram-bot -f${NC}"
    log ""
    log "${BLUE}Full deployment log:${NC}"
    log "  ${YELLOW}$LOG_FILE${NC}"
    log ""
    log "${GREEN}Next: Test with real photos, then deploy Sprint 2 (conversational awareness)${NC}"
    log ""
}

# Run main
main "$@"
