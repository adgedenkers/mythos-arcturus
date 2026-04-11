#!/bin/bash
# ============================================================================
# MYTHOS SALES SYSTEM RESET SCRIPT
# Clears non-finalized inventory and restores archived import packages
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
CLOTHING_ARCHIVE="/opt/mythos/sales_ingestion/archive"
SHOE_ARCHIVE="/opt/mythos/shoe_ingestion/archive"
ASSET_IMAGES="/opt/mythos/assets/images"
RESTORE_TARGET="$HOME/Documents"
DB_NAME="mythos"
DB_USER="postgres"

# ============================================================================
# FUNCTIONS
# ============================================================================

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

print_info() {
    echo -e "  $1"
}

confirm_action() {
    local prompt="$1"
    local response
    echo ""
    echo -e "${YELLOW}$prompt${NC}"
    read -p "Type 'yes' to confirm: " response
    if [[ "$response" != "yes" ]]; then
        echo "Aborted."
        exit 0
    fi
}

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================

print_header "MYTHOS SALES SYSTEM RESET"

echo "This script will:"
echo "  1. Remove non-finalized inventory from the database"
echo "  2. Remove associated images from the asset repository"
echo "  3. Restore archived import packages to ~/Documents"
echo ""
print_warning "Finalized/completed sales will NOT be affected."
echo ""

# ============================================================================
# INITIAL CONFIRMATION
# ============================================================================

confirm_action "Do you want to proceed with the reset?"

# ============================================================================
# SELECT WHAT TO CLEAR
# ============================================================================

print_header "SELECT ITEMS TO CLEAR"

echo "What would you like to clear?"
echo ""
echo "  1) Clothing only"
echo "  2) Shoes only"
echo "  3) Both clothing and shoes"
echo "  4) Cancel"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        CLEAR_CLOTHING=true
        CLEAR_SHOES=false
        echo ""
        print_info "Selected: Clothing only"
        ;;
    2)
        CLEAR_CLOTHING=false
        CLEAR_SHOES=true
        echo ""
        print_info "Selected: Shoes only"
        ;;
    3)
        CLEAR_CLOTHING=true
        CLEAR_SHOES=true
        echo ""
        print_info "Selected: Both clothing and shoes"
        ;;
    4|*)
        echo "Cancelled."
        exit 0
        ;;
esac

# ============================================================================
# SHOW WHAT WILL BE AFFECTED
# ============================================================================

print_header "ANALYZING CURRENT STATE"

# Count items that will be affected
if [ "$CLEAR_CLOTHING" = true ]; then
    CLOTHING_UNSOLD=$(psql -U $DB_USER -d $DB_NAME -t -c "
        SELECT COUNT(*) FROM clothing_items 
        WHERE status NOT IN ('sold') 
        OR status IS NULL
        OR sale_id IS NULL
        OR sale_id NOT IN (SELECT sale_id FROM sales WHERE payment_status = 'paid');
    " 2>/dev/null | tr -d ' ')
    
    CLOTHING_SOLD=$(psql -U $DB_USER -d $DB_NAME -t -c "
        SELECT COUNT(*) FROM clothing_items 
        WHERE status = 'sold' 
        AND sale_id IN (SELECT sale_id FROM sales WHERE payment_status = 'paid');
    " 2>/dev/null | tr -d ' ')
    
    CLOTHING_IMAGES=$(psql -U $DB_USER -d $DB_NAME -t -c "
        SELECT COUNT(*) FROM clothing_images ci
        JOIN clothing_items c ON ci.item_id = c.id
        WHERE c.status NOT IN ('sold')
        OR c.status IS NULL
        OR c.sale_id IS NULL
        OR c.sale_id NOT IN (SELECT sale_id FROM sales WHERE payment_status = 'paid');
    " 2>/dev/null | tr -d ' ')
    
    CLOTHING_ARCHIVES=$(find "$CLOTHING_ARCHIVE" -maxdepth 1 -name "*.zip" 2>/dev/null | wc -l)
    
    echo "CLOTHING:"
    print_info "  Items to REMOVE (unsold/not-finalized): $CLOTHING_UNSOLD"
    print_info "  Items to KEEP (sold/finalized): $CLOTHING_SOLD"
    print_info "  Images to remove: $CLOTHING_IMAGES"
    print_info "  Archives to restore: $CLOTHING_ARCHIVES"
    echo ""
fi

if [ "$CLEAR_SHOES" = true ]; then
    SHOES_UNSOLD=$(psql -U $DB_USER -d $DB_NAME -t -c "
        SELECT COUNT(*) FROM shoes_forsale 
        WHERE status NOT IN ('sold') 
        OR status IS NULL
        OR sale_id IS NULL
        OR sale_id NOT IN (SELECT sale_id FROM sales WHERE payment_status = 'paid');
    " 2>/dev/null | tr -d ' ')
    
    SHOES_SOLD=$(psql -U $DB_USER -d $DB_NAME -t -c "
        SELECT COUNT(*) FROM shoes_forsale 
        WHERE status = 'sold' 
        AND sale_id IN (SELECT sale_id FROM sales WHERE payment_status = 'paid');
    " 2>/dev/null | tr -d ' ')
    
    SHOE_IMAGES=$(psql -U $DB_USER -d $DB_NAME -t -c "
        SELECT COUNT(*) FROM shoe_images si
        JOIN shoes_forsale s ON si.shoe_id = s.id
        WHERE s.status NOT IN ('sold')
        OR s.status IS NULL
        OR s.sale_id IS NULL
        OR s.sale_id NOT IN (SELECT sale_id FROM sales WHERE payment_status = 'paid');
    " 2>/dev/null | tr -d ' ')
    
    SHOE_ARCHIVES=$(find "$SHOE_ARCHIVE" -maxdepth 1 -name "*.zip" 2>/dev/null | wc -l)
    
    echo "SHOES:"
    print_info "  Items to REMOVE (unsold/not-finalized): $SHOES_UNSOLD"
    print_info "  Items to KEEP (sold/finalized): $SHOES_SOLD"
    print_info "  Images to remove: $SHOE_IMAGES"
    print_info "  Archives to restore: $SHOE_ARCHIVES"
    echo ""
fi

# Count pending sales to remove
PENDING_SALES=$(psql -U $DB_USER -d $DB_NAME -t -c "
    SELECT COUNT(*) FROM sales WHERE payment_status != 'paid';
" 2>/dev/null | tr -d ' ')

echo "SALES:"
print_info "  Pending sales to REMOVE: $PENDING_SALES"
print_info "  Paid/finalized sales: PROTECTED"
echo ""

# ============================================================================
# FINAL CONFIRMATION
# ============================================================================

print_warning "This action cannot be undone!"
confirm_action "Are you absolutely sure you want to proceed?"

# ============================================================================
# BEGIN RESET PROCESS
# ============================================================================

print_header "EXECUTING RESET"

# ----------------------------------------------------------------------------
# STEP 1: Collect asset paths to delete before removing DB records
# ----------------------------------------------------------------------------

print_info "Step 1: Collecting asset paths to delete..."

ASSETS_TO_DELETE=""

if [ "$CLEAR_CLOTHING" = true ]; then
    CLOTHING_ASSETS=$(psql -U $DB_USER -d $DB_NAME -t -c "
        SELECT ci.asset_rel_path FROM clothing_images ci
        JOIN clothing_items c ON ci.item_id = c.id
        WHERE ci.asset_rel_path IS NOT NULL
        AND (c.status NOT IN ('sold')
             OR c.status IS NULL
             OR c.sale_id IS NULL
             OR c.sale_id NOT IN (SELECT sale_id FROM sales WHERE payment_status = 'paid'));
    " 2>/dev/null | tr -d ' ')
    ASSETS_TO_DELETE="$ASSETS_TO_DELETE $CLOTHING_ASSETS"
fi

if [ "$CLEAR_SHOES" = true ]; then
    SHOE_ASSETS=$(psql -U $DB_USER -d $DB_NAME -t -c "
        SELECT si.asset_rel_path FROM shoe_images si
        JOIN shoes_forsale s ON si.shoe_id = s.id
        WHERE si.asset_rel_path IS NOT NULL
        AND (s.status NOT IN ('sold')
             OR s.status IS NULL
             OR s.sale_id IS NULL
             OR s.sale_id NOT IN (SELECT sale_id FROM sales WHERE payment_status = 'paid'));
    " 2>/dev/null | tr -d ' ')
    ASSETS_TO_DELETE="$ASSETS_TO_DELETE $SHOE_ASSETS"
fi

print_success "Asset paths collected"

# ----------------------------------------------------------------------------
# STEP 2: Remove database records (in correct order for foreign keys)
# ----------------------------------------------------------------------------

print_info "Step 2: Removing database records..."

if [ "$CLEAR_CLOTHING" = true ]; then
    # Get IDs of clothing items to delete
    psql -U $DB_USER -d $DB_NAME -c "
        -- Delete clothing images for unsold items
        DELETE FROM clothing_images 
        WHERE item_id IN (
            SELECT id FROM clothing_items 
            WHERE status NOT IN ('sold')
            OR status IS NULL
            OR sale_id IS NULL
            OR sale_id NOT IN (SELECT sale_id FROM sales WHERE payment_status = 'paid')
        );
        
        -- Delete clothing colors for unsold items
        DELETE FROM clothing_colors 
        WHERE item_id IN (
            SELECT id FROM clothing_items 
            WHERE status NOT IN ('sold')
            OR status IS NULL
            OR sale_id IS NULL
            OR sale_id NOT IN (SELECT sale_id FROM sales WHERE payment_status = 'paid')
        );
        
        -- Delete clothing materials for unsold items
        DELETE FROM clothing_materials 
        WHERE item_id IN (
            SELECT id FROM clothing_items 
            WHERE status NOT IN ('sold')
            OR status IS NULL
            OR sale_id IS NULL
            OR sale_id NOT IN (SELECT sale_id FROM sales WHERE payment_status = 'paid')
        );
        
        -- Delete the clothing items themselves
        DELETE FROM clothing_items 
        WHERE status NOT IN ('sold')
        OR status IS NULL
        OR sale_id IS NULL
        OR sale_id NOT IN (SELECT sale_id FROM sales WHERE payment_status = 'paid');
    " 2>/dev/null
    
    print_success "Clothing records removed"
fi

if [ "$CLEAR_SHOES" = true ]; then
    psql -U $DB_USER -d $DB_NAME -c "
        -- Delete shoe images for unsold items
        DELETE FROM shoe_images 
        WHERE shoe_id IN (
            SELECT id FROM shoes_forsale 
            WHERE status NOT IN ('sold')
            OR status IS NULL
            OR sale_id IS NULL
            OR sale_id NOT IN (SELECT sale_id FROM sales WHERE payment_status = 'paid')
        );
        
        -- Delete shoe colors for unsold items
        DELETE FROM shoe_colors 
        WHERE shoe_id IN (
            SELECT id FROM shoes_forsale 
            WHERE status NOT IN ('sold')
            OR status IS NULL
            OR sale_id IS NULL
            OR sale_id NOT IN (SELECT sale_id FROM sales WHERE payment_status = 'paid')
        );
        
        -- Delete shoe materials for unsold items
        DELETE FROM shoe_materials 
        WHERE shoe_id IN (
            SELECT id FROM shoes_forsale 
            WHERE status NOT IN ('sold')
            OR status IS NULL
            OR sale_id IS NULL
            OR sale_id NOT IN (SELECT sale_id FROM sales WHERE payment_status = 'paid')
        );
        
        -- Delete the shoes themselves
        DELETE FROM shoes_forsale 
        WHERE status NOT IN ('sold')
        OR status IS NULL
        OR sale_id IS NULL
        OR sale_id NOT IN (SELECT sale_id FROM sales WHERE payment_status = 'paid');
    " 2>/dev/null
    
    print_success "Shoe records removed"
fi

# Delete pending sales (not paid)
psql -U $DB_USER -d $DB_NAME -c "
    DELETE FROM sales WHERE payment_status != 'paid';
" 2>/dev/null

print_success "Pending sales removed"

# ----------------------------------------------------------------------------
# STEP 3: Remove asset files
# ----------------------------------------------------------------------------

print_info "Step 3: Removing asset files..."

ASSETS_REMOVED=0
for asset_path in $ASSETS_TO_DELETE; do
    if [ -n "$asset_path" ]; then
        full_path="$ASSET_IMAGES/../$asset_path"
        if [ -f "$full_path" ]; then
            rm -f "$full_path"
            ((ASSETS_REMOVED++))
        fi
    fi
done

# Clean up empty directories in asset folder
if [ -d "$ASSET_IMAGES" ]; then
    find "$ASSET_IMAGES" -type d -empty -delete 2>/dev/null || true
fi

print_success "Removed $ASSETS_REMOVED asset files"

# ----------------------------------------------------------------------------
# STEP 4: Restore archived import packages
# ----------------------------------------------------------------------------

print_info "Step 4: Restoring archived import packages..."

mkdir -p "$RESTORE_TARGET"

RESTORED_COUNT=0

if [ "$CLEAR_CLOTHING" = true ] && [ -d "$CLOTHING_ARCHIVE" ]; then
    for archive in "$CLOTHING_ARCHIVE"/*.zip; do
        if [ -f "$archive" ]; then
            archive_name=$(basename "$archive")
            cp "$archive" "$RESTORE_TARGET/"
            print_info "  Restored: $archive_name"
            ((RESTORED_COUNT++))
        fi
    done
fi

if [ "$CLEAR_SHOES" = true ] && [ -d "$SHOE_ARCHIVE" ]; then
    for archive in "$SHOE_ARCHIVE"/*.zip; do
        if [ -f "$archive" ]; then
            archive_name=$(basename "$archive")
            cp "$archive" "$RESTORE_TARGET/"
            print_info "  Restored: $archive_name"
            ((RESTORED_COUNT++))
        fi
    done
fi

print_success "Restored $RESTORED_COUNT archive(s) to $RESTORE_TARGET"

# ----------------------------------------------------------------------------
# STEP 5: Reset sequences (optional - keeps IDs clean)
# ----------------------------------------------------------------------------

print_info "Step 5: Resetting sequences..."

if [ "$CLEAR_CLOTHING" = true ]; then
    # Only reset if no sold items remain
    REMAINING=$(psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM clothing_items;" 2>/dev/null | tr -d ' ')
    if [ "$REMAINING" = "0" ]; then
        psql -U $DB_USER -d $DB_NAME -c "
            ALTER SEQUENCE clothing_images_id_seq RESTART WITH 1;
        " 2>/dev/null
        print_success "Clothing image sequence reset"
    else
        print_info "  Clothing sequence not reset (sold items remain)"
    fi
fi

if [ "$CLEAR_SHOES" = true ]; then
    REMAINING=$(psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM shoes_forsale;" 2>/dev/null | tr -d ' ')
    if [ "$REMAINING" = "0" ]; then
        psql -U $DB_USER -d $DB_NAME -c "
            ALTER SEQUENCE shoe_images_id_seq RESTART WITH 1;
        " 2>/dev/null
        print_success "Shoe image sequence reset"
    else
        print_info "  Shoe sequence not reset (sold items remain)"
    fi
fi

# ============================================================================
# SUMMARY
# ============================================================================

print_header "RESET COMPLETE"

echo "Summary:"
if [ "$CLEAR_CLOTHING" = true ]; then
    REMAINING_CLOTHING=$(psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM clothing_items;" 2>/dev/null | tr -d ' ')
    print_info "  Clothing items remaining: $REMAINING_CLOTHING"
fi

if [ "$CLEAR_SHOES" = true ]; then
    REMAINING_SHOES=$(psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM shoes_forsale;" 2>/dev/null | tr -d ' ')
    print_info "  Shoes remaining: $REMAINING_SHOES"
fi

REMAINING_SALES=$(psql -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM sales;" 2>/dev/null | tr -d ' ')
print_info "  Sales remaining (paid/finalized): $REMAINING_SALES"
print_info "  Archives restored to: $RESTORE_TARGET"

echo ""
print_success "Reset complete. You can now re-import the archived packages."
echo ""
