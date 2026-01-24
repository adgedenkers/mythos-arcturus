#!/bin/bash
# Nuke all sales intake data - reset to clean state

echo "🔥 NUKING SALES DATA..."
echo ""

# Confirm
read -p "This will delete ALL items_for_sale, item_images, and intake files. Continue? [y/N] " confirm
if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo "📊 Clearing database tables..."
sudo -u postgres psql -d mythos -c "TRUNCATE item_images, items_for_sale CASCADE;"

echo ""
echo "📁 Clearing intake folders..."
rm -rf /opt/mythos/intake/pending/*
rm -rf /opt/mythos/intake/processed/*
rm -rf /opt/mythos/intake/failed/*

echo ""
echo "🖼️ Clearing asset images..."
rm -rf /opt/mythos/assets/images/*

echo ""
echo "✅ Done. Sales data reset to clean state."
echo ""

# Show counts to confirm
echo "📊 Current counts:"
sudo -u postgres psql -d mythos -c "SELECT 'items_for_sale' as table_name, COUNT(*) FROM items_for_sale UNION SELECT 'item_images', COUNT(*) FROM item_images;"
