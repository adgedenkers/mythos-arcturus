#!/bin/bash
# Patch 0081: Complete Astrology System
# Installation script

set -e

PATCH_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MYTHOS_ROOT="/opt/mythos"
EPHE_DIR="$MYTHOS_ROOT/ephemeris"

echo "=================================="
echo "Patch 0081: Astrology System"
echo "=================================="
echo ""

# Check if running as correct user
if [ "$EUID" -eq 0 ]; then
   echo "❌ Do not run as root. Run as adge user."
   exit 1
fi

# Backup existing files
echo "📦 Creating backups..."
if [ -d "$MYTHOS_ROOT/astrology" ]; then
    sudo cp -r "$MYTHOS_ROOT/astrology" "$MYTHOS_ROOT/astrology.backup.$(date +%Y%m%d_%H%M%S)" || true
fi

# Copy files
echo "📂 Copying files..."
sudo cp -r "$PATCH_DIR/opt/mythos/"* "$MYTHOS_ROOT/"

# Set permissions
echo "🔐 Setting permissions..."
sudo chown -R adge:adge "$MYTHOS_ROOT/astrology"
sudo chmod +x "$MYTHOS_ROOT/astrology/calculator.py"

# Download Swiss Ephemeris files if not present
if [ ! -d "$EPHE_DIR" ]; then
    echo "📥 Downloading Swiss Ephemeris files..."
    
    sudo mkdir -p "$EPHE_DIR"
    cd "$EPHE_DIR"
    
    # Download essential ephemeris files from Astrodienst
    echo "   Downloading planetary files..."
    sudo wget -q https://www.astro.com/ftp/swisseph/ephe/seas_18.se1 || echo "   Warning: Could not download seas_18.se1"
    sudo wget -q https://www.astro.com/ftp/swisseph/ephe/semo_18.se1 || echo "   Warning: Could not download semo_18.se1"
    sudo wget -q https://www.astro.com/ftp/swisseph/ephe/sepl_18.se1 || echo "   Warning: Could not download sepl_18.se1"
    
    # Download asteroid files
    echo "   Downloading asteroid files..."
    sudo wget -q https://www.astro.com/ftp/swisseph/ephe/ast0/se00001.se1 || echo "   Warning: Could not download Ceres"
    sudo wget -q https://www.astro.com/ftp/swisseph/ephe/ast0/se00002.se1 || echo "   Warning: Could not download Pallas"
    sudo wget -q https://www.astro.com/ftp/swisseph/ephe/ast0/se00003.se1 || echo "   Warning: Could not download Juno"
    sudo wget -q https://www.astro.com/ftp/swisseph/ephe/ast0/se00004.se1 || echo "   Warning: Could not download Vesta"
    
    sudo chown -R adge:adge "$EPHE_DIR"
    
    echo "   ✅ Ephemeris files downloaded to $EPHE_DIR"
else
    echo "✅ Ephemeris files already exist at $EPHE_DIR"
fi

# Update .env with ephemeris path
if ! grep -q "SWISSEPH_PATH" "$MYTHOS_ROOT/.env"; then
    echo "" | sudo tee -a "$MYTHOS_ROOT/.env" > /dev/null
    echo "# Swiss Ephemeris" | sudo tee -a "$MYTHOS_ROOT/.env" > /dev/null
    echo "SWISSEPH_PATH=$EPHE_DIR" | sudo tee -a "$MYTHOS_ROOT/.env" > /dev/null
    echo "✅ Added SWISSEPH_PATH to .env"
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
source "$MYTHOS_ROOT/.venv/bin/activate"
pip install --quiet pyswisseph || pip install --break-system-packages pyswisseph

# Create database schema
echo "🗄️  Creating database schema..."
sudo -u postgres psql -d mythos -f "$MYTHOS_ROOT/astrology/schema.sql" > /dev/null 2>&1

# Calculate charts for existing people
echo "🌟 Calculating natal charts..."
python3 "$MYTHOS_ROOT/astrology/calculator.py" --batch-all

# Register handlers in bot
echo "🤖 Registering Telegram handlers..."
HANDLER_REG="$MYTHOS_ROOT/telegram_bot/mythos_bot.py"

if ! grep -q "astrology_handler" "$HANDLER_REG"; then
    # Add import
    sudo sed -i '/^from handlers import/a from handlers import astrology_handler' "$HANDLER_REG"
    
    # Add registration call
    sudo sed -i '/finance_handler.register_handlers/a \    astrology_handler.register_handlers(application)' "$HANDLER_REG"
    
    echo "   ✅ Handler registered"
fi

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart mythos-bot.service
sudo systemctl restart mythos-api.service

# Wait for services to come up
sleep 2

# Verify
echo ""
echo "✅ Installation complete!"
echo ""
echo "📊 Chart Summary:"
CHART_COUNT=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM astro_charts")
PLACEMENT_COUNT=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM astro_placements")
ASPECT_COUNT=$(sudo -u postgres psql -d mythos -t -c "SELECT COUNT(*) FROM astro_aspects")

echo "   Charts: $CHART_COUNT"
echo "   Placements: $PLACEMENT_COUNT"
echo "   Aspects: $ASPECT_COUNT"
echo ""
echo "🎯 Available Commands:"
echo "   /chart <n>              - Show natal chart"
echo "   /chart <name1> <name2>  - Compare charts"
echo "   /planets <n>            - Planet positions only"
echo "   /houses <n>             - House cusps only"
echo "   /aspects <n>            - Natal aspects only"
echo "   /group_planets <p> <s>  - Find all with planet in sign"
echo ""
echo "📖 Example Usage:"
echo "   /chart Ka"
echo "   /chart Ka Seraphe"
echo "   /group_planets Mars Aries"
echo ""
echo "✨ Astrology system ready!"
