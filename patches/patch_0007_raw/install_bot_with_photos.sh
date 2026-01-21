#!/bin/bash
#
# Mythos Telegram Bot Photo Handler Installer
# Sprint 1: Replace bot with photo-enabled version
#
# This script:
# 1. Backs up the existing mythos_bot.py
# 2. Copies the new photo-enabled version
# 3. Validates Python syntax
# 4. Optionally restarts the service

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BOT_DIR="/opt/mythos/telegram_bot"
BOT_FILE="${BOT_DIR}/mythos_bot.py"
NEW_BOT_FILE="./mythos_bot_with_photos.py"
BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BOT_FILE}.backup.${BACKUP_TIMESTAMP}"

echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Mythos Telegram Bot Photo Handler Installer${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""

# Check if running as correct user
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Warning: Running as root. Consider running as mythos user.${NC}"
    echo -e "   Press Ctrl+C to cancel, or Enter to continue..."
    read
fi

# Check if bot file exists
if [ ! -f "$BOT_FILE" ]; then
    echo -e "${RED}❌ Error: $BOT_FILE not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found existing bot: $BOT_FILE"

# Check if new bot file exists
if [ ! -f "$NEW_BOT_FILE" ]; then
    echo -e "${RED}❌ Error: $NEW_BOT_FILE not found in current directory${NC}"
    echo -e "   Make sure you're running this from the directory containing:"
    echo -e "   ${YELLOW}mythos_bot_with_photos.py${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Found new bot: $NEW_BOT_FILE"
echo ""

# Show differences summary
echo -e "${BLUE}Changes in new version:${NC}"
echo "  • Added MEDIA_BASE_PATH constant"
echo "  • Added handle_photo() function"
echo "  • Added photos_command() function"
echo "  • Updated help text to mention photos"
echo "  • Updated start message"
echo "  • Registered photo handler in main()"
echo ""

# Create backup
echo -n "Creating backup... "
cp "$BOT_FILE" "$BACKUP_FILE"
echo -e "${GREEN}✓${NC}"
echo -e "  Backup: $BACKUP_FILE"
echo ""

# Validate new bot syntax before installing
echo -e "${BLUE}Validating new bot syntax...${NC}"
echo -n "  Running syntax check... "

if python3 -m py_compile "$NEW_BOT_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo ""
    echo -e "${RED}❌ Syntax error in new bot file!${NC}"
    echo -e "   Fix syntax errors in: ${YELLOW}$NEW_BOT_FILE${NC}"
    echo -e "   Run: ${YELLOW}python3 -m py_compile $NEW_BOT_FILE${NC}"
    exit 1
fi

# Copy new bot
echo -n "Installing new bot... "
cp "$NEW_BOT_FILE" "$BOT_FILE"
echo -e "${GREEN}✓${NC}"
echo ""

# Verify installed bot
echo -n "Verifying installation... "
if python3 -m py_compile "$BOT_FILE" 2>/dev/null; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    echo ""
    echo -e "${RED}❌ Installation verification failed!${NC}"
    echo -e "   Restoring backup..."
    cp "$BACKUP_FILE" "$BOT_FILE"
    echo -e "   ${GREEN}✓${NC} Restored original bot"
    exit 1
fi

echo ""

# Check if service exists
SERVICE_EXISTS=false
if systemctl list-unit-files | grep -q mythos-telegram-bot.service; then
    SERVICE_EXISTS=true
fi

# Ask about restarting service
if [ "$SERVICE_EXISTS" = true ]; then
    echo -e "${BLUE}Bot service detected${NC}"
    echo -e "  Restart mythos-telegram-bot.service now? (y/N)"
    read -r response
    
    if [[ "$response" =~ ^[Yy]$ ]]; then
        echo -n "  Restarting service... "
        
        if sudo systemctl restart mythos-telegram-bot.service 2>/dev/null; then
            echo -e "${GREEN}✓${NC}"
            echo ""
            echo -e "${GREEN}✓ Service restarted successfully${NC}"
            echo ""
            echo -e "  Check status: ${YELLOW}sudo systemctl status mythos-telegram-bot${NC}"
            echo -e "  View logs:    ${YELLOW}sudo journalctl -u mythos-telegram-bot -f${NC}"
        else
            echo -e "${RED}✗${NC}"
            echo ""
            echo -e "${RED}❌ Service restart failed${NC}"
            echo -e "   Check logs: ${YELLOW}sudo journalctl -u mythos-telegram-bot -n 50${NC}"
            echo -e "   The bot file has been updated, but service needs manual restart"
        fi
    else
        echo ""
        echo -e "${YELLOW}⚠️  Service not restarted${NC}"
        echo -e "   Restart manually with: ${YELLOW}sudo systemctl restart mythos-telegram-bot${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  No systemd service detected${NC}"
    echo -e "   If running bot manually, restart with:"
    echo -e "   ${YELLOW}python3 $BOT_FILE${NC}"
fi

echo ""

# Create media directory if it doesn't exist
MEDIA_DIR="/opt/mythos/media"
echo -e "${BLUE}Checking media directory...${NC}"

if [ ! -d "$MEDIA_DIR" ]; then
    echo -n "  Creating $MEDIA_DIR... "
    
    # Try to create without sudo first
    if mkdir -p "$MEDIA_DIR" 2>/dev/null; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${YELLOW}requires sudo${NC}"
        sudo mkdir -p "$MEDIA_DIR"
        sudo chown mythos:mythos "$MEDIA_DIR" 2>/dev/null || true
        sudo chmod 755 "$MEDIA_DIR"
        echo -e "  ${GREEN}✓${NC} Created with sudo"
    fi
else
    echo -e "  ${GREEN}✓${NC} Already exists: $MEDIA_DIR"
fi

# Check permissions
echo -n "  Checking permissions... "
if [ -w "$MEDIA_DIR" ]; then
    echo -e "${GREEN}✓${NC} writable"
else
    echo -e "${YELLOW}not writable${NC}"
    echo ""
    echo -e "${YELLOW}⚠️  Media directory exists but is not writable${NC}"
    echo -e "   Fix with: ${YELLOW}sudo chown -R mythos:mythos $MEDIA_DIR${NC}"
    echo -e "   And:      ${YELLOW}sudo chmod -R 755 $MEDIA_DIR${NC}"
fi

echo ""

# Summary
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Bot Installation Complete${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${BLUE}What changed:${NC}"
echo "  • Bot now handles photo messages"
echo "  • Added /photos command"
echo "  • Photos stored in $MEDIA_DIR"
echo "  • Photo metadata sent to API"
echo ""
echo -e "${BLUE}Backup saved:${NC}"
echo "  $BACKUP_FILE"
echo ""
echo -e "${BLUE}Test the bot:${NC}"
echo "  1. Open Telegram and message your bot"
echo "  2. Send: /start"
echo "  3. Send: /help"
echo "  4. Send a photo"
echo "  5. Send: /photos"
echo ""
echo -e "${BLUE}If bot isn't working:${NC}"
echo "  • Check logs: sudo journalctl -u mythos-telegram-bot -f"
echo "  • Verify .env: /opt/mythos/.env has TELEGRAM_BOT_TOKEN"
echo "  • Restore backup: cp $BACKUP_FILE $BOT_FILE"
echo ""
echo -e "${YELLOW}Note:${NC} The API must also be updated and database migrated."
echo "      See: ${YELLOW}SPRINT_1_DEPLOYMENT.md${NC}"
echo ""
echo -e "${GREEN}Done!${NC}"
