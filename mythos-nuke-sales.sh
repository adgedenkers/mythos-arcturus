#!/bin/bash
# ============================================================================
# MYTHOS SALES SYSTEM - NUCLEAR RESET
# Removes ALL sales-related tables, data, files, and starts fresh
# ============================================================================

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

DB_NAME="mythos"
DB_USER="postgres"

print_header() {
    echo ""
    echo -e "${CYAN}============================================================================${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${CYAN}============================================================================${NC}"
    echo ""
}

print_warning() {
    echo -e "${YELLOW}⚠ WARNING: $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# ============================================================================
# CONFIRMATION
# ============================================================================

print_header "MYTHOS SALES SYSTEM - NUCLEAR RESET"

echo -e "${RED}THIS WILL PERMANENTLY DELETE:${NC}"
echo ""
echo "  DATABASE TABLES:"
echo "    - clothing_items"
echo "    - clothing_colors"
echo "    - clothing_materials"
echo "    - clothing_images"
echo "    - shoes_forsale"
echo "    - shoe_colors"
echo "    - shoe_materials"
echo "    - shoe_images"
echo "    - sales"
echo "    - sales_ingestion_log"
echo "    - media_assets"
echo ""
echo "  FILE SYSTEM:"
echo "    - /opt/mythos/assets/images/*"
echo "    - /opt/mythos/sales_ingestion/sales-db-ingestion-*"
echo "    - /opt/mythos/shoe_ingestion/shoe-db-ingestion-*"
echo "    - /opt/mythos/sales_ingestion/archive/*"
echo "    - /opt/mythos/shoe_ingestion/archive/*"
echo ""
print_warning "THIS CANNOT BE UNDONE!"
echo ""

read -p "Type 'NUKE IT' to confirm: " confirm
if [[ "$confirm" != "NUKE IT" ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
read -p "Are you ABSOLUTELY sure? Type 'YES' to proceed: " confirm2
if [[ "$confirm2" != "YES" ]]; then
    echo "Aborted."
    exit 0
fi

# ============================================================================
# DROP DATABASE TABLES
# ============================================================================

print_header "DROPPING DATABASE TABLES"

psql -U $DB_USER -d $DB_NAME << 'EOF'

-- Drop dependent tables first (foreign keys)
DROP TABLE IF EXISTS clothing_colors CASCADE;
DROP TABLE IF EXISTS clothing_materials CASCADE;
DROP TABLE IF EXISTS clothing_images CASCADE;
DROP TABLE IF EXISTS shoe_colors CASCADE;
DROP TABLE IF EXISTS shoe_materials CASCADE;
DROP TABLE IF EXISTS shoe_images CASCADE;

-- Drop main item tables
DROP TABLE IF EXISTS clothing_items CASCADE;
DROP TABLE IF EXISTS shoes_forsale CASCADE;

-- Drop sales tracking
DROP TABLE IF EXISTS sales CASCADE;
DROP TABLE IF EXISTS sales_ingestion_log CASCADE;

-- Drop asset tracking
DROP TABLE IF EXISTS media_assets CASCADE;

-- Drop sequences
DROP SEQUENCE IF EXISTS clothing_images_id_seq CASCADE;
DROP SEQUENCE IF EXISTS shoe_images_id_seq CASCADE;
DROP SEQUENCE IF EXISTS sales_sale_id_seq CASCADE;

-- Drop views
DROP VIEW IF EXISTS available_items CASCADE;
DROP VIEW IF EXISTS listed_items CASCADE;
DROP VIEW IF EXISTS sales_detail CASCADE;
DROP VIEW IF EXISTS revenue_summary CASCADE;
DROP VIEW IF EXISTS recent_photos CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS next_sale_id() CASCADE;
DROP FUNCTION IF EXISTS search_photos_by_tag(TEXT) CASCADE;

EOF

print_success "Database tables dropped"

# ============================================================================
# REMOVE FILE SYSTEM CONTENT
# ============================================================================

print_header "REMOVING FILE SYSTEM CONTENT"

# Asset images
if [ -d "/opt/mythos/assets/images" ]; then
    rm -rf /opt/mythos/assets/images/*
    print_success "Cleared /opt/mythos/assets/images/"
fi

# Sales ingestion batches
rm -rf /opt/mythos/sales_ingestion/sales-db-ingestion-*
print_success "Removed sales ingestion batches"

# Shoe ingestion batches
rm -rf /opt/mythos/shoe_ingestion/shoe-db-ingestion-*
print_success "Removed shoe ingestion batches"

# Archives
rm -rf /opt/mythos/sales_ingestion/archive/*
rm -rf /opt/mythos/shoe_ingestion/archive/*
print_success "Cleared archives"

# ============================================================================
# CREATE FRESH SCHEMA
# ============================================================================

print_header "CREATING FRESH SCHEMA"

psql -U $DB_USER -d $DB_NAME << 'EOF'

-- ============================================================================
-- ITEMS FOR SALE - Unified approach with item_type discriminator
-- ============================================================================

CREATE TABLE items_for_sale (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_type TEXT NOT NULL,  -- 'clothing', 'shoes', 'other'
    
    -- Common fields
    brand TEXT,
    model TEXT,  -- Style name, model number, etc.
    title TEXT,  -- Generated listing title
    description TEXT,  -- Generated listing description
    
    -- Categorization
    category TEXT NOT NULL,  -- 'jeans', 'sneakers', 'boots', 'shirt', etc.
    gender_category TEXT NOT NULL CHECK (gender_category IN ('mens', 'womens', 'unisex', 'kids')),
    
    -- Sizing (flexible for different item types)
    size_label TEXT,  -- As written: "16 Regular", "11", "XL"
    size_numeric NUMERIC(5,1),  -- Normalized: 16, 11, etc.
    size_width TEXT,  -- For shoes: 'narrow', 'medium', 'wide'
    
    -- Condition & Pricing
    condition TEXT NOT NULL CHECK (condition IN (
        'new_with_tags', 'new_without_tags', 'like_new', 
        'gently_used', 'used', 'well_worn'
    )),
    estimated_price NUMERIC(10,2),
    listed_price NUMERIC(10,2),
    
    -- Item details (JSON for flexibility)
    colors TEXT[],
    materials TEXT[],
    features JSONB,  -- Waterproof, heel height, closure type, etc.
    
    -- Provenance
    country_of_manufacture TEXT,
    original_retail_price NUMERIC(10,2),
    care_instructions TEXT,
    
    -- AI extraction metadata
    confidence_score NUMERIC(3,2),
    inferred_fields TEXT[],
    extraction_notes TEXT,
    
    -- Status tracking
    status TEXT DEFAULT 'available' CHECK (status IN (
        'pending',      -- Waiting for AI analysis
        'available',    -- Ready to list
        'listed',       -- Posted to marketplace
        'reserved',     -- Someone interested
        'sold',         -- Sale complete
        'donated',      -- Given away
        'removed'       -- Removed from inventory
    )),
    
    -- Sale linking
    sale_id INTEGER,
    bundle_id UUID,  -- For grouping items in bundles
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    listed_date TIMESTAMP,
    sold_date TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_items_status ON items_for_sale(status);
CREATE INDEX idx_items_type ON items_for_sale(item_type);
CREATE INDEX idx_items_category ON items_for_sale(category);
CREATE INDEX idx_items_sale_id ON items_for_sale(sale_id);
CREATE INDEX idx_items_bundle_id ON items_for_sale(bundle_id);

-- ============================================================================
-- ITEM IMAGES
-- ============================================================================

CREATE TABLE item_images (
    id SERIAL PRIMARY KEY,
    item_id UUID REFERENCES items_for_sale(id) ON DELETE CASCADE,
    
    -- File info
    filename TEXT NOT NULL,  -- Standardized name: item-NNNNNN.jpeg
    original_filename TEXT,  -- Original from phone/camera
    
    -- View classification
    view_type TEXT,  -- 'front', 'back', 'label', 'tag', 'box', 'detail'
    is_primary BOOLEAN DEFAULT FALSE,  -- Main listing photo
    
    -- Asset store integration
    asset_sha256 TEXT,
    asset_rel_path TEXT,
    
    -- Telegram integration
    telegram_file_id TEXT,
    telegram_file_unique_id TEXT,
    
    -- Metadata
    width INTEGER,
    height INTEGER,
    file_size_bytes INTEGER,
    
    -- Batch tracking
    batch_name TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_item_images_item ON item_images(item_id);
CREATE INDEX idx_item_images_sha256 ON item_images(asset_sha256);

-- ============================================================================
-- SALES / LISTINGS
-- ============================================================================

CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    
    -- Listing info
    platform TEXT NOT NULL,  -- 'facebook_marketplace', 'craigslist', 'ebay', etc.
    marketplace_title TEXT,
    marketplace_description TEXT,
    marketplace_listing_url TEXT,
    marketplace_id TEXT,  -- Platform's listing ID
    
    -- Pricing
    asking_price NUMERIC(10,2),
    final_price NUMERIC(10,2),
    shipping_cost NUMERIC(10,2) DEFAULT 0,
    
    -- Buyer info
    buyer_name TEXT,
    buyer_contact TEXT,
    
    -- Status
    payment_method TEXT,  -- 'cash', 'venmo', 'paypal', etc.
    payment_status TEXT DEFAULT 'pending' CHECK (payment_status IN ('pending', 'paid', 'refunded')),
    shipping_status TEXT DEFAULT 'not_applicable' CHECK (shipping_status IN (
        'not_applicable', 'pending', 'shipped', 'delivered'
    )),
    
    -- Pickup details
    pickup_location TEXT DEFAULT 'Magro''s Restaurant & Pizzeria, 104 East Main Street, Norwich NY',
    pickup_contact TEXT DEFAULT 'Hannah',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    listed_at TIMESTAMP,
    sold_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sales_platform ON sales(platform);
CREATE INDEX idx_sales_payment ON sales(payment_status);

-- ============================================================================
-- BUNDLES (for grouping items)
-- ============================================================================

CREATE TABLE bundles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT,  -- "4 Old Navy Jeans Bundle"
    description TEXT,
    bundle_price NUMERIC(10,2),
    item_count INTEGER,
    status TEXT DEFAULT 'available',
    sale_id INTEGER REFERENCES sales(sale_id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- MEDIA ASSETS (deduplication store)
-- ============================================================================

CREATE TABLE media_assets (
    sha256 TEXT PRIMARY KEY,
    file_ext TEXT,
    rel_path TEXT NOT NULL,
    byte_size INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- INGESTION LOG (idempotency tracking)
-- ============================================================================

CREATE TABLE sales_ingestion_log (
    id SERIAL PRIMARY KEY,
    batch_name TEXT NOT NULL,
    artifact_type TEXT NOT NULL,  -- 'clothing', 'shoes', 'telegram'
    status TEXT NOT NULL,  -- 'processing', 'success', 'failed'
    extract_dir TEXT,
    error TEXT,
    items_created INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(batch_name, artifact_type)
);

-- ============================================================================
-- PENDING INTAKE (telegram photo collection)
-- ============================================================================

CREATE TABLE pending_intake (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_user_id BIGINT NOT NULL,
    telegram_chat_id BIGINT NOT NULL,
    
    -- Photo collection
    photo_count INTEGER DEFAULT 0,
    photos JSONB DEFAULT '[]'::jsonb,  -- Array of {file_id, file_unique_id, local_path}
    
    -- Status
    status TEXT DEFAULT 'collecting' CHECK (status IN (
        'collecting',   -- Waiting for more photos
        'ready',        -- Has 3 photos, ready for analysis
        'analyzing',    -- AI processing
        'complete',     -- Item created
        'failed'        -- Error occurred
    )),
    
    -- Result
    item_id UUID REFERENCES items_for_sale(id),
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_pending_user ON pending_intake(telegram_user_id, status);

-- ============================================================================
-- VIEWS
-- ============================================================================

-- Available items ready to list
CREATE VIEW available_items AS
SELECT 
    i.id,
    i.item_type,
    i.brand,
    i.model,
    i.category,
    i.gender_category,
    i.size_label,
    i.condition,
    i.estimated_price,
    i.colors,
    i.materials,
    i.status,
    COUNT(img.id) as image_count
FROM items_for_sale i
LEFT JOIN item_images img ON i.id = img.item_id
WHERE i.status = 'available'
GROUP BY i.id
ORDER BY i.created_at DESC;

-- Items currently listed
CREATE VIEW listed_items AS
SELECT 
    i.*,
    s.platform,
    s.marketplace_listing_url,
    s.asking_price,
    s.listed_at
FROM items_for_sale i
JOIN sales s ON i.sale_id = s.sale_id
WHERE i.status = 'listed';

-- Sales summary
CREATE VIEW sales_summary AS
SELECT 
    s.platform,
    COUNT(*) as total_listings,
    COUNT(CASE WHEN s.payment_status = 'paid' THEN 1 END) as completed_sales,
    SUM(CASE WHEN s.payment_status = 'paid' THEN s.final_price ELSE 0 END) as total_revenue
FROM sales s
GROUP BY s.platform;

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Get next image number
CREATE OR REPLACE FUNCTION next_image_number() RETURNS INTEGER AS $$
DECLARE
    max_num INTEGER;
BEGIN
    SELECT COALESCE(MAX(
        CASE 
            WHEN filename ~ '^item-[0-9]+\.jpeg$' 
            THEN CAST(SUBSTRING(filename FROM 'item-([0-9]+)\.jpeg') AS INTEGER)
            ELSE 0
        END
    ), 0) INTO max_num
    FROM item_images;
    
    RETURN max_num + 1;
END;
$$ LANGUAGE plpgsql;

EOF

print_success "Fresh schema created"

# ============================================================================
# CREATE DIRECTORIES
# ============================================================================

print_header "CREATING DIRECTORIES"

mkdir -p /opt/mythos/assets/images
mkdir -p /opt/mythos/sales_ingestion/archive
mkdir -p /opt/mythos/shoe_ingestion/archive
mkdir -p /opt/mythos/intake/pending
mkdir -p /opt/mythos/intake/processed

print_success "Directories created"

# ============================================================================
# DONE
# ============================================================================

print_header "NUCLEAR RESET COMPLETE"

echo "Fresh schema ready with:"
echo "  - items_for_sale (unified table for all item types)"
echo "  - item_images (with asset store integration)"
echo "  - sales (marketplace listings)"
echo "  - bundles (for grouping items)"
echo "  - pending_intake (telegram photo collection)"
echo "  - media_assets (deduplication)"
echo ""
echo "Ready for Telegram intake integration."
echo ""
