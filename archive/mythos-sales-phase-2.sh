#!/bin/bash
# ============================================================================
# PHASE 2: TELEGRAM INTEGRATION
# Adds sell mode to Telegram bot with photo collection and vision analysis
# ============================================================================

set -e

PHASE="2"
PHASE_NAME="Telegram Integration"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/mythos/_backups/phase_${PHASE}_${TIMESTAMP}"
LOG_FILE="/var/log/mythos_phase_${PHASE}.log"

# Configuration
MYTHOS_BASE="/opt/mythos"
VENV_PYTHON="/opt/mythos/.venv/bin/python3"
SERVICE_USER="adge"
BOT_FILE="$MYTHOS_BASE/telegram_bot/mythos_bot.py"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${CYAN}[$(date '+%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"; }
success() { echo -e "${GREEN}✓${NC} $1" | tee -a "$LOG_FILE"; }
warn() { echo -e "${YELLOW}⚠${NC} $1" | tee -a "$LOG_FILE"; }
error() { echo -e "${RED}✗${NC} $1" | tee -a "$LOG_FILE"; exit 1; }

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================

preflight_checks() {
    log "Running pre-flight checks..."
    
    # Check vision module exists
    if [ ! -f "$MYTHOS_BASE/vision/core.py" ]; then
        error "Vision module not found. Run Phase 1 first."
    fi
    success "Vision module found"
    
    # Check bot file exists
    if [ ! -f "$BOT_FILE" ]; then
        error "Telegram bot not found at $BOT_FILE"
    fi
    success "Telegram bot found"
    
    # Check database has new schema
    if ! sudo -u postgres psql -d mythos -c "SELECT 1 FROM items_for_sale LIMIT 1" > /dev/null 2>&1; then
        error "New schema not found. Run nuclear reset first."
    fi
    success "Database schema ready"
    
    # Check venv
    if [ ! -f "$VENV_PYTHON" ]; then
        error "Python venv not found"
    fi
    success "Python venv found"
    
    success "Pre-flight checks passed"
}

# ============================================================================
# BACKUP
# ============================================================================

create_backup() {
    log "Creating backup at $BACKUP_DIR..."
    mkdir -p "$BACKUP_DIR"
    
    # Backup the bot file
    cp "$BOT_FILE" "$BACKUP_DIR/mythos_bot.py.bak"
    
    # Record manifest
    cat > "$BACKUP_DIR/manifest.txt" << EOF
Phase $PHASE Backup - $TIMESTAMP
==============================
Files backed up:
- mythos_bot.py

To rollback: $0 rollback
EOF
    
    success "Backup created"
}

# ============================================================================
# CREATE HANDLERS MODULE
# ============================================================================

create_handlers() {
    log "Creating sell mode handlers..."
    
    mkdir -p "$MYTHOS_BASE/telegram_bot/handlers"
    
    # -------------------------------------------------------------------------
    # handlers/__init__.py
    # -------------------------------------------------------------------------
    cat > "$MYTHOS_BASE/telegram_bot/handlers/__init__.py" << 'PYEOF'
"""
Telegram bot handlers for various modes
"""

from .sell_mode import (
    enter_sell_mode,
    handle_sell_photos,
    sell_done_command,
    sell_status_command,
    sell_undo_command,
    is_sell_mode
)

from .export_handler import (
    export_command,
    inventory_command
)

__all__ = [
    'enter_sell_mode',
    'handle_sell_photos',
    'sell_done_command',
    'sell_status_command',
    'sell_undo_command',
    'is_sell_mode',
    'export_command',
    'inventory_command'
]
PYEOF

    # -------------------------------------------------------------------------
    # handlers/sell_mode.py
    # -------------------------------------------------------------------------
    cat > "$MYTHOS_BASE/telegram_bot/handlers/sell_mode.py" << 'PYEOF'
"""
Sell mode handler for Telegram bot

Flow:
1. User enters /mode sell
2. User sends 3 photos (in one message or multiple)
3. Vision module analyzes photos
4. Item created in database
5. User notified with summary
"""

import os
import sys
import uuid
import logging
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

import psycopg2
from psycopg2.extras import Json
from telegram import Update
from telegram.ext import ContextTypes

# Add mythos to path
sys.path.insert(0, '/opt/mythos')

from vision import analyze_image
from vision.prompts import sales
from vision.config import get_config

logger = logging.getLogger(__name__)

# Intake storage path
INTAKE_PATH = Path("/opt/mythos/intake/pending")
ASSETS_PATH = Path("/opt/mythos/assets/images")


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        host=os.getenv('POSTGRES_HOST', 'localhost')
    )


def is_sell_mode(session: dict) -> bool:
    """Check if user is in sell mode"""
    return session.get("current_mode") == "sell"


async def enter_sell_mode(update: Update, session: dict):
    """Initialize sell mode for user"""
    session["current_mode"] = "sell"
    session["sell_session"] = {
        "active": True,
        "items_added": [],
        "current_photos": [],  # Buffer for photos until we have 3
        "started_at": datetime.now().isoformat()
    }
    
    await update.message.reply_text(
        "📦 **Sell Mode Active**\n\n"
        "Send 3 photos per item (in one message or separate).\n"
        "I'll analyze and add to inventory.\n\n"
        "**Commands:**\n"
        "  /done   - Exit sell mode\n"
        "  /status - Show items added\n"
        "  /undo   - Remove last item\n\n"
        "Send photos to begin!"
    )


async def handle_sell_photos(update: Update, context: ContextTypes.DEFAULT_TYPE, session: dict):
    """
    Handle photos in sell mode.
    Collects photos until we have 3, then processes.
    """
    telegram_id = update.effective_user.id
    sell_session = session.get("sell_session", {})
    
    if not sell_session.get("active"):
        await update.message.reply_text("❌ Sell mode not active. Use /mode sell")
        return
    
    # Get all photos from this message (Telegram sends multiple resolutions)
    # We take the largest of each unique photo
    message_photos = update.message.photo
    
    if not message_photos:
        await update.message.reply_text("No photos detected in message.")
        return
    
    # Get highest resolution (last in list)
    photo = message_photos[-1]
    
    # Check if this is part of a media group (multiple photos in one message)
    media_group_id = update.message.media_group_id
    
    # Download and store photo
    try:
        file = await context.bot.get_file(photo.file_id)
        
        # Create temp directory for this intake
        if not sell_session.get("current_intake_id"):
            intake_id = str(uuid.uuid4())
            sell_session["current_intake_id"] = intake_id
            intake_dir = INTAKE_PATH / intake_id
            intake_dir.mkdir(parents=True, exist_ok=True)
            sell_session["intake_dir"] = str(intake_dir)
        else:
            intake_id = sell_session["current_intake_id"]
            intake_dir = Path(sell_session["intake_dir"])
        
        # Download photo
        photo_num = len(sell_session["current_photos"]) + 1
        photo_filename = f"photo_{photo_num}.jpg"
        photo_path = intake_dir / photo_filename
        
        await file.download_to_drive(str(photo_path))
        
        # Add to buffer
        sell_session["current_photos"].append({
            "path": str(photo_path),
            "filename": photo_filename,
            "telegram_file_id": photo.file_id,
            "telegram_file_unique_id": photo.file_unique_id,
            "width": photo.width,
            "height": photo.height,
            "received_at": datetime.now().isoformat()
        })
        
        current_count = len(sell_session["current_photos"])
        
        logger.info(f"Photo {current_count}/3 received for intake {intake_id}")
        
        # If we have 3 photos, process the item
        if current_count >= 3:
            await update.message.reply_text("📸 3 photos received. Analyzing...")
            
            # Process in background to not block
            asyncio.create_task(
                process_item(update, context, session, telegram_id)
            )
        else:
            # Acknowledge receipt
            remaining = 3 - current_count
            await update.message.reply_text(
                f"📸 Photo {current_count}/3 received.\n"
                f"Send {remaining} more photo{'s' if remaining > 1 else ''}."
            )
            
    except Exception as e:
        logger.error(f"Error handling sell photo: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error saving photo: {e}")


async def process_item(update: Update, context: ContextTypes.DEFAULT_TYPE, session: dict, telegram_id: int):
    """Process 3 photos through vision and create item"""
    sell_session = session.get("sell_session", {})
    photos = sell_session.get("current_photos", [])
    intake_id = sell_session.get("current_intake_id")
    
    if len(photos) < 3:
        await update.message.reply_text("❌ Not enough photos to process")
        return
    
    try:
        # Get photo paths
        photo_paths = [p["path"] for p in photos[:3]]
        
        # Analyze with vision
        logger.info(f"Analyzing {len(photo_paths)} photos with vision model...")
        
        result = analyze_image(
            photo_paths,
            prompt=sales.ITEM_ANALYSIS,
            response_format="json"
        )
        
        # Check for parse errors
        if result.get("parse_error"):
            logger.error(f"Vision parse error: {result.get('raw_response', '')[:500]}")
            await update.message.reply_text(
                "⚠️ Couldn't parse item details. Please try again with clearer photos.\n"
                f"Raw response saved for review."
            )
            # Reset for next item
            _reset_current_item(sell_session)
            return
        
        # Create item in database
        item_id = await create_item_from_analysis(result, photos, telegram_id)
        
        if item_id:
            # Add to session items
            sell_session["items_added"].append({
                "id": str(item_id),
                "brand": result.get("brand", "Unknown"),
                "category": result.get("category", "item"),
                "size": result.get("size_label", ""),
                "price": result.get("estimated_price", 0),
                "title": result.get("title", "")
            })
            
            # Format response
            brand = result.get("brand") or "Unknown Brand"
            category = result.get("category", "item")
            size = result.get("size_label", "")
            price = result.get("estimated_price", 0)
            condition = result.get("condition", "").replace("_", " ")
            colors = ", ".join(result.get("colors", [])) or "N/A"
            
            response = (
                f"✅ **Item Added**\n\n"
                f"**{brand} {category.title()}**\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📏 Size: {size}\n"
                f"✨ Condition: {condition.title()}\n"
                f"🎨 Colors: {colors}\n"
                f"💰 Est. Price: ${price:.0f}\n\n"
                f"📷 3 photos stored\n\n"
                f"Send more items or /done to finish."
            )
            
            await update.message.reply_text(response)
            
            # Move photos to processed
            _move_to_processed(intake_id)
        else:
            await update.message.reply_text("❌ Failed to create item. Check logs.")
        
        # Reset for next item
        _reset_current_item(sell_session)
        
    except TimeoutError:
        await update.message.reply_text(
            "⏱️ Analysis timed out. The vision model might be busy.\n"
            "Please try again in a moment."
        )
        _reset_current_item(sell_session)
        
    except Exception as e:
        logger.error(f"Error processing item: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error processing item: {e}")
        _reset_current_item(sell_session)


async def create_item_from_analysis(analysis: dict, photos: list, telegram_id: int) -> Optional[uuid.UUID]:
    """Create item_for_sale record from vision analysis"""
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        item_id = uuid.uuid4()
        
        # Insert item
        cur.execute("""
            INSERT INTO items_for_sale (
                id, item_type, brand, model, title, description,
                category, gender_category,
                size_label, size_numeric, size_width,
                condition, estimated_price,
                colors, materials, features,
                country_of_manufacture, care_instructions,
                confidence_score, inferred_fields, extraction_notes,
                status, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                %s, %s,
                %s, %s, %s,
                'available', NOW()
            )
        """, (
            item_id,
            analysis.get("item_type", "other"),
            analysis.get("brand"),
            analysis.get("model"),
            analysis.get("title"),
            analysis.get("description"),
            analysis.get("category", "other"),
            analysis.get("gender_category", "unisex"),
            analysis.get("size_label"),
            analysis.get("size_numeric"),
            analysis.get("size_width"),
            analysis.get("condition", "used"),
            analysis.get("estimated_price"),
            analysis.get("colors", []),
            analysis.get("materials", []),
            Json(analysis.get("features", {})),
            analysis.get("country_of_manufacture"),
            analysis.get("care_instructions"),
            analysis.get("confidence_score", 0.0),
            analysis.get("inferred_fields", []),
            analysis.get("extraction_notes"),
        ))
        
        # Insert images
        for i, photo in enumerate(photos[:3]):
            # Determine view type based on position
            view_types = ["front", "label", "detail"]
            view_type = view_types[i] if i < len(view_types) else "detail"
            
            # Generate standardized filename
            # Get next image number
            cur.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM item_images")
            next_num = cur.fetchone()[0]
            std_filename = f"item-{next_num:06d}.jpeg"
            
            # Copy to assets with SHA256 naming
            photo_path = Path(photo["path"])
            if photo_path.exists():
                import hashlib
                import shutil
                
                # Calculate SHA256
                with open(photo_path, "rb") as f:
                    sha256 = hashlib.sha256(f.read()).hexdigest()
                
                # Create asset path
                shard = sha256[:2]
                asset_dir = ASSETS_PATH / shard
                asset_dir.mkdir(parents=True, exist_ok=True)
                asset_path = asset_dir / f"{sha256}.jpeg"
                
                # Copy if not exists
                if not asset_path.exists():
                    shutil.copy2(photo_path, asset_path)
                
                rel_path = f"images/{shard}/{sha256}.jpeg"
                
                # Insert image record
                cur.execute("""
                    INSERT INTO item_images (
                        item_id, filename, original_filename, view_type,
                        is_primary, asset_sha256, asset_rel_path,
                        telegram_file_id, telegram_file_unique_id,
                        width, height, created_at
                    ) VALUES (
                        %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s,
                        %s, %s, NOW()
                    )
                """, (
                    item_id,
                    std_filename,
                    photo.get("filename"),
                    view_type,
                    i == 0,  # First photo is primary
                    sha256,
                    rel_path,
                    photo.get("telegram_file_id"),
                    photo.get("telegram_file_unique_id"),
                    photo.get("width"),
                    photo.get("height"),
                ))
        
        conn.commit()
        logger.info(f"Created item {item_id} with 3 images")
        return item_id
        
    except Exception as e:
        logger.error(f"Database error creating item: {e}", exc_info=True)
        if conn:
            conn.rollback()
        return None
    finally:
        if conn:
            conn.close()


def _reset_current_item(sell_session: dict):
    """Reset the current item buffer for next item"""
    sell_session["current_photos"] = []
    sell_session["current_intake_id"] = None
    sell_session["intake_dir"] = None


def _move_to_processed(intake_id: str):
    """Move intake folder to processed"""
    try:
        import shutil
        src = INTAKE_PATH / intake_id
        dst = Path("/opt/mythos/intake/processed") / intake_id
        if src.exists():
            shutil.move(str(src), str(dst))
    except Exception as e:
        logger.error(f"Error moving to processed: {e}")


async def sell_done_command(update: Update, context: ContextTypes.DEFAULT_TYPE, session: dict):
    """Handle /done command - exit sell mode"""
    sell_session = session.get("sell_session", {})
    items = sell_session.get("items_added", [])
    
    # Calculate totals
    total_items = len(items)
    total_value = sum(item.get("price", 0) for item in items)
    
    # Build summary
    if total_items > 0:
        item_lines = []
        for i, item in enumerate(items, 1):
            item_lines.append(
                f"{i}. {item.get('brand', 'Unknown')} {item.get('category', 'item')} "
                f"- ${item.get('price', 0):.0f}"
            )
        
        summary = (
            f"📋 **Sell Session Complete**\n\n"
            f"Items added: {total_items}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            + "\n".join(item_lines) +
            f"\n━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 Total estimated: ${total_value:.0f}\n\n"
            f"Use /export to generate marketplace listings."
        )
    else:
        summary = (
            "📋 **Sell Session Complete**\n\n"
            "No items added.\n\n"
            "Use /mode sell to start again."
        )
    
    # Reset session
    session["current_mode"] = "chat"
    session["sell_session"] = None
    
    await update.message.reply_text(summary)


async def sell_status_command(update: Update, context: ContextTypes.DEFAULT_TYPE, session: dict):
    """Handle /status command in sell mode"""
    sell_session = session.get("sell_session", {})
    
    if not sell_session.get("active"):
        await update.message.reply_text("Not in sell mode.")
        return
    
    items = sell_session.get("items_added", [])
    current_photos = len(sell_session.get("current_photos", []))
    
    if items:
        item_lines = [f"• {item.get('brand', '')} {item.get('category', '')} - ${item.get('price', 0):.0f}" 
                     for item in items]
        items_text = "\n".join(item_lines)
    else:
        items_text = "None yet"
    
    status = (
        f"📊 **Sell Session Status**\n\n"
        f"Items added: {len(items)}\n"
        f"Current item: {current_photos}/3 photos\n\n"
        f"**Items:**\n{items_text}"
    )
    
    await update.message.reply_text(status)


async def sell_undo_command(update: Update, context: ContextTypes.DEFAULT_TYPE, session: dict):
    """Handle /undo command - remove last item"""
    sell_session = session.get("sell_session", {})
    
    if not sell_session.get("active"):
        await update.message.reply_text("Not in sell mode.")
        return
    
    items = sell_session.get("items_added", [])
    
    if not items:
        await update.message.reply_text("No items to undo.")
        return
    
    # Get last item
    last_item = items.pop()
    item_id = last_item.get("id")
    
    # Delete from database
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Delete images first (cascade should handle this, but being explicit)
        cur.execute("DELETE FROM item_images WHERE item_id = %s", (item_id,))
        cur.execute("DELETE FROM items_for_sale WHERE id = %s", (item_id,))
        
        conn.commit()
        conn.close()
        
        await update.message.reply_text(
            f"↩️ Removed: {last_item.get('brand', '')} {last_item.get('category', '')}\n\n"
            f"Items remaining: {len(items)}"
        )
        
    except Exception as e:
        logger.error(f"Error undoing item: {e}")
        await update.message.reply_text(f"❌ Error removing item: {e}")
PYEOF

    # -------------------------------------------------------------------------
    # handlers/export_handler.py
    # -------------------------------------------------------------------------
    cat > "$MYTHOS_BASE/telegram_bot/handlers/export_handler.py" << 'PYEOF'
"""
Export and inventory handlers
"""

import os
import sys
import logging
from typing import Optional

import psycopg2
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        host=os.getenv('POSTGRES_HOST', 'localhost')
    )


async def inventory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show inventory of available items"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                i.id, i.item_type, i.brand, i.category, 
                i.size_label, i.condition, i.estimated_price,
                i.status, COUNT(img.id) as photo_count
            FROM items_for_sale i
            LEFT JOIN item_images img ON i.id = img.item_id
            WHERE i.status IN ('available', 'listed')
            GROUP BY i.id
            ORDER BY i.created_at DESC
            LIMIT 20
        """)
        
        items = cur.fetchall()
        conn.close()
        
        if not items:
            await update.message.reply_text(
                "📦 **Inventory Empty**\n\n"
                "No items for sale. Use /mode sell to add items."
            )
            return
        
        # Group by status
        available = [i for i in items if i[7] == 'available']
        listed = [i for i in items if i[7] == 'listed']
        
        lines = ["📦 **Inventory**\n"]
        
        if available:
            lines.append(f"\n**Available ({len(available)}):**")
            for item in available:
                item_id, item_type, brand, category, size, condition, price, status, photos = item
                brand_str = brand or "Unknown"
                lines.append(f"• {brand_str} {category} ({size}) - ${price:.0f}")
        
        if listed:
            lines.append(f"\n**Listed ({len(listed)}):**")
            for item in listed:
                item_id, item_type, brand, category, size, condition, price, status, photos = item
                brand_str = brand or "Unknown"
                lines.append(f"• {brand_str} {category} ({size}) - ${price:.0f}")
        
        total_value = sum(i[6] or 0 for i in items)
        lines.append(f"\n━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"💰 Total value: ${total_value:.0f}")
        lines.append(f"\nUse /export to generate listings.")
        
        await update.message.reply_text("\n".join(lines))
        
    except Exception as e:
        logger.error(f"Error fetching inventory: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate marketplace listings for available items"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                i.id, i.brand, i.model, i.title, i.description,
                i.category, i.gender_category, i.size_label,
                i.condition, i.estimated_price, i.colors
            FROM items_for_sale i
            WHERE i.status = 'available'
            ORDER BY i.created_at DESC
        """)
        
        items = cur.fetchall()
        conn.close()
        
        if not items:
            await update.message.reply_text(
                "📤 **No items to export**\n\n"
                "All items are either listed or sold.\n"
                "Use /mode sell to add more items."
            )
            return
        
        # Generate listings
        await update.message.reply_text(f"📤 Generating {len(items)} listing(s)...")
        
        for item in items:
            (item_id, brand, model, title, description,
             category, gender, size, condition, price, colors) = item
            
            # Map condition for marketplace
            condition_map = {
                "new_with_tags": "New",
                "new_without_tags": "New",
                "like_new": "Used - Like New",
                "gently_used": "Used - Good",
                "used": "Used - Good",
                "well_worn": "Used - Fair"
            }
            fb_condition = condition_map.get(condition, "Used - Good")
            
            # Build listing
            brand_str = brand or "Brand"
            listing = (
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"**FACEBOOK MARKETPLACE**\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"**Title:**\n{title or f'{brand_str} {category} {size}'}\n\n"
                f"**Price:** ${price:.0f}\n\n"
                f"**Condition:** {fb_condition}\n\n"
                f"**Description:**\n{description or 'No description'}\n\n"
                f"**Pickup:** Magro's Restaurant & Pizzeria, 104 East Main Street, Norwich NY - Ask for Hannah\n\n"
                f"**Payment:** Cash only\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"Item ID: {str(item_id)[:8]}...\n"
                f"After posting, run:\n"
                f"`/listed {str(item_id)[:8]}`"
            )
            
            await update.message.reply_text(listing)
        
        await update.message.reply_text(
            f"✅ {len(items)} listing(s) generated.\n\n"
            "Copy/paste to Facebook Marketplace.\n"
            "Use /listed <id> after posting to track."
        )
        
    except Exception as e:
        logger.error(f"Error generating export: {e}")
        await update.message.reply_text(f"❌ Error: {e}")
PYEOF

    success "Handler modules created"
}

# ============================================================================
# PATCH BOT FILE
# ============================================================================

patch_bot() {
    log "Patching Telegram bot..."
    
    # Create patched version
    cat > "$MYTHOS_BASE/telegram_bot/mythos_bot_patched.py" << 'PYEOF'
#!/usr/bin/env python3
"""
Mythos Telegram Bot - WITH SELL MODE
Updated to include item selling via photo analysis
"""

import os
import logging
import uuid
from datetime import datetime
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv('/opt/mythos/.env')

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import sell mode handlers
from handlers import (
    enter_sell_mode,
    handle_sell_photos,
    sell_done_command,
    sell_status_command,
    sell_undo_command,
    is_sell_mode,
    export_command,
    inventory_command
)

# Configuration
API_URL = "https://mythos-api.denkers.co"
API_KEY = os.getenv('API_KEY_TELEGRAM_BOT')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
MEDIA_BASE_PATH = "/opt/mythos/media"

# In-memory session store
SESSIONS = {}

def get_or_create_session(telegram_id):
    """Get or create session for this Telegram user"""
    if telegram_id not in SESSIONS:
        try:
            response = requests.get(
                f"{API_URL}/user/{telegram_id}",
                headers={"X-API-Key": API_KEY}
            )
            
            if response.status_code == 200:
                user = response.json()
                SESSIONS[telegram_id] = {
                    "user": user,
                    "current_mode": "db",
                    "current_model": "auto",
                    "conversation_id": None,
                    "last_activity": datetime.now(),
                    "sell_session": None  # Added for sell mode
                }
            else:
                return None
        
        except Exception as e:
            logger.error(f"Error fetching user: {e}")
            return None
    
    SESSIONS[telegram_id]["last_activity"] = datetime.now()
    return SESSIONS[telegram_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text(
            "❌ You are not registered in the Mythos system.\n\n"
            f"Your Telegram ID: {telegram_id}\n\n"
            "Please contact Ka to register your account."
        )
        return
    
    user = session["user"]
    
    await update.message.reply_text(
        f"🔮 Welcome to the Mythos System, {user['soul_name']}!\n\n"
        f"Current mode: {session['current_mode']}\n\n"
        "Available commands:\n"
        "/mode - Switch modes\n"
        "/convo - Start a tracked conversation\n"
        "/photos - View recent photos\n"
        "/inventory - View items for sale\n"
        "/export - Generate marketplace listings\n"
        "/help - Show help\n"
        "/status - Show current status\n\n"
        "Just send a message or photo to interact."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
🔮 Mythos System Commands

📋 Modes:
  /mode db        - Database Manager
  /mode seraphe   - Seraphe's Cosmology Assistant
  /mode genealogy - Genealogy Assistant
  /mode chat      - Natural conversation
  /mode sell      - Sell items (photo analysis)

📦 Selling:
  /mode sell  - Enter sell mode
  /done       - Exit sell mode
  /status     - Items in current session
  /undo       - Remove last item
  /inventory  - View all items for sale
  /export     - Generate marketplace listings

💬 Conversation:
  /convo      - Start tracked conversation
  /endconvo   - End tracked conversation

🤖 AI Models:
  /model auto - Smart routing
  /model fast - Quick responses
  /model deep - Best quality

📸 Media:
  /photos     - View recent photos

ℹ️ Info:
  /status - Show current mode/user
  /help   - Show this message

💡 Selling Flow:
  1. /mode sell
  2. Send 3 photos per item
  3. Wait for analysis
  4. Repeat or /done
  5. /export for listings
"""
    await update.message.reply_text(help_text)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    # Check if in sell mode
    if is_sell_mode(session):
        await sell_status_command(update, context, session)
        return
    
    user = session["user"]
    
    convo_status = "None"
    if session.get("conversation_id"):
        convo_status = f"Active ({session['conversation_id'][:8]}...)"
    
    status_text = f"""
📊 Current Status

👤 User: {user['soul_name']} (@{user['username']})
🔮 Soul: {user['soul_name']}
🔧 Mode: {session['current_mode']}
🤖 Model: {session['current_model']}
💬 Conversation: {convo_status}

Use /help to see available commands.
"""
    await update.message.reply_text(status_text)


async def mode_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /mode command to switch modes"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    if context.args:
        new_mode = context.args[0].lower()
        
        valid_modes = ["db", "seraphe", "genealogy", "chat", "sell"]
        
        if new_mode in valid_modes:
            # Handle sell mode specially
            if new_mode == "sell":
                await enter_sell_mode(update, session)
                return
            
            # Exit sell mode if switching away
            if is_sell_mode(session):
                session["sell_session"] = None
            
            session["current_mode"] = new_mode
            
            mode_descriptions = {
                "db": "Database Manager - Query souls, persons, and lineages",
                "seraphe": "Seraphe's Cosmology Assistant - Spiritual guidance and symbolism",
                "genealogy": "Genealogy Assistant - Trace bloodlines and ancestors",
                "chat": "Natural conversation - General purpose assistant"
            }
            
            await update.message.reply_text(
                f"✅ Switched to {new_mode} mode\n\n"
                f"📝 {mode_descriptions[new_mode]}"
            )
        else:
            await update.message.reply_text(
                f"❌ Unknown mode: {new_mode}\n\n"
                "Available modes: db, seraphe, genealogy, chat, sell"
            )
    else:
        current = session.get("current_mode", "db")
        await update.message.reply_text(
            f"Current mode: **{current}**\n\n"
            "Available modes:\n"
            "  /mode db        - Database Manager\n"
            "  /mode seraphe   - Seraphe's Cosmology\n"
            "  /mode genealogy - Genealogy Research\n"
            "  /mode chat      - Natural conversation\n"
            "  /mode sell      - Sell items (photo analysis)"
        )


async def done_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /done command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found.")
        return
    
    if is_sell_mode(session):
        await sell_done_command(update, context, session)
    else:
        await update.message.reply_text("Nothing to finish. Not in sell mode.")


async def undo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /undo command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found.")
        return
    
    if is_sell_mode(session):
        await sell_undo_command(update, context, session)
    else:
        await update.message.reply_text("Nothing to undo. Not in sell mode.")


async def convo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /convo command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start to begin.")
        return
    
    if session.get("conversation_id"):
        await update.message.reply_text(
            f"⚠️ Already in conversation mode\n"
            f"Current: {session['conversation_id'][:8]}...\n\n"
            "Use /endconvo to end first."
        )
        return
    
    conversation_id = str(uuid.uuid4())
    session["conversation_id"] = conversation_id
    
    try:
        response = requests.post(
            f"{API_URL}/conversation/start",
            headers={"X-API-Key": API_KEY},
            json={
                "user_id": str(telegram_id),
                "conversation_id": conversation_id,
                "title": f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            await update.message.reply_text(
                f"🗣️ Conversation started\n"
                f"ID: {conversation_id[:8]}...\n\n"
                "All messages will be tracked.\n"
                "Use /endconvo when finished."
            )
        else:
            await update.message.reply_text(
                f"⚠️ Local conversation started\n"
                f"ID: {conversation_id[:8]}...\n"
                "(API notification failed)"
            )
    except Exception as e:
        logger.error(f"Error starting conversation: {e}")
        await update.message.reply_text(
            f"⚠️ Conversation started locally\n"
            f"ID: {conversation_id[:8]}..."
        )


async def endconvo_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /endconvo command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found.")
        return
    
    if not session.get("conversation_id"):
        await update.message.reply_text("No active conversation.")
        return
    
    conversation_id = session["conversation_id"]
    session["conversation_id"] = None
    
    try:
        requests.post(
            f"{API_URL}/conversation/end",
            headers={"X-API-Key": API_KEY},
            json={
                "user_id": str(telegram_id),
                "conversation_id": conversation_id
            },
            timeout=10
        )
    except:
        pass
    
    await update.message.reply_text(
        f"✅ Conversation ended\n"
        f"ID: {conversation_id[:8]}..."
    )


async def model_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /model command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found.")
        return
    
    if context.args:
        new_model = context.args[0].lower()
        
        if new_model in ["auto", "fast", "deep"]:
            session["current_model"] = new_model
            
            descriptions = {
                "auto": "Automatic (smart routing)",
                "fast": "Qwen 32B (fast, ~10s)",
                "deep": "DeepSeek 236B (best, ~60s)"
            }
            
            await update.message.reply_text(
                f"✅ Model: {new_model}\n{descriptions[new_model]}"
            )
        else:
            await update.message.reply_text(
                f"❌ Unknown model: {new_model}\n"
                "Available: auto, fast, deep"
            )
    else:
        current = session.get("current_model", "auto")
        await update.message.reply_text(
            f"Current model: {current}\n\n"
            "/model auto - Smart routing\n"
            "/model fast - Quick (Qwen 32B)\n"
            "/model deep - Best (DeepSeek 236B)"
        )


async def photos_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /photos command"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found.")
        return
    
    try:
        response = requests.get(
            f"{API_URL}/media/recent/{telegram_id}",
            headers={"X-API-Key": API_KEY},
            params={"limit": 10},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            photos = data.get('photos', [])
            
            if not photos:
                await update.message.reply_text("No photos yet.")
                return
            
            lines = [f"📸 Recent Photos ({len(photos)})\n"]
            for i, photo in enumerate(photos, 1):
                processed = "✅" if photo.get('processed') else "⏳"
                lines.append(f"{i}. {processed} {photo.get('filename', 'unknown')}")
            
            await update.message.reply_text("\n".join(lines))
        else:
            await update.message.reply_text("❌ Failed to get photos.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def inventory_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper for inventory command"""
    await inventory_command(update, context)


async def export_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Wrapper for export command"""
    await export_command(update, context)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle photo messages - routes to sell mode or general handling"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Not registered. Use /start")
        return
    
    # Route to sell mode if active
    if is_sell_mode(session):
        await handle_sell_photos(update, context, session)
        return
    
    # Otherwise, standard photo handling
    photo = update.message.photo[-1]
    caption = update.message.caption or ""
    user_uuid = session['user']['uuid']
    conversation_id = session.get('conversation_id')
    
    try:
        file = await context.bot.get_file(photo.file_id)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        user_prefix = user_uuid[:8]
        filename = f"{timestamp}_{photo.file_unique_id[:16]}.jpg"
        
        storage_dir = os.path.join(MEDIA_BASE_PATH, user_prefix)
        os.makedirs(storage_dir, exist_ok=True)
        
        storage_path = os.path.join(storage_dir, filename)
        await file.download_to_drive(storage_path)
        
        file_size = os.path.getsize(storage_path)
        
        response = requests.post(
            f"{API_URL}/media/upload",
            headers={"X-API-Key": API_KEY},
            json={
                "user_id": str(telegram_id),
                "conversation_id": conversation_id,
                "filename": filename,
                "file_path": storage_path,
                "file_size": file_size,
                "width": photo.width,
                "height": photo.height,
                "telegram_file_id": photo.file_id,
                "telegram_file_unique_id": photo.file_unique_id,
                "caption": caption,
                "mime_type": "image/jpeg"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            await update.message.reply_text(
                f"📸 Photo received\n"
                f"🆔 {data['media_id'][:8]}...\n"
                f"💾 {file_size // 1024}KB"
            )
        else:
            await update.message.reply_text("⚠️ Photo saved locally.")
            
    except Exception as e:
        logger.error(f"Photo error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    telegram_id = update.effective_user.id
    session = get_or_create_session(telegram_id)
    
    if not session:
        await update.message.reply_text("❌ Session not found. Use /start")
        return
    
    # In sell mode, text is ignored (photos only)
    if is_sell_mode(session):
        await update.message.reply_text(
            "📦 In sell mode - send photos only.\n"
            "Use /done to exit or /status to check progress."
        )
        return
    
    user_message = update.message.text
    user = session["user"]
    mode = session["current_mode"]
    model = session["current_model"]
    conversation_id = session.get("conversation_id")
    
    await update.message.chat.send_action("typing")
    
    try:
        response = requests.post(
            f"{API_URL}/message",
            headers={"X-API-Key": API_KEY},
            json={
                "user_id": str(telegram_id),
                "message": user_message,
                "mode": mode,
                "model_preference": model,
                "conversation_id": conversation_id
            },
            timeout=120
        )
        
        if response.status_code == 200:
            data = response.json()
            bot_response = data["response"]
            
            if len(bot_response) > 4000:
                chunks = [bot_response[i:i+4000] for i in range(0, len(bot_response), 4000)]
                for chunk in chunks:
                    await update.message.reply_text(chunk)
            else:
                await update.message.reply_text(bot_response)
        else:
            await update.message.reply_text(f"❌ API Error: {response.status_code}")
    
    except requests.Timeout:
        await update.message.reply_text("⏱️ Request timed out.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Error: {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ An error occurred.")


def main():
    """Start the bot"""
    if not BOT_TOKEN:
        print("❌ TELEGRAM_BOT_TOKEN not found")
        return
    
    if not API_KEY:
        print("❌ API_KEY_TELEGRAM_BOT not found")
        return
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("mode", mode_command))
    application.add_handler(CommandHandler("model", model_command))
    application.add_handler(CommandHandler("convo", convo_command))
    application.add_handler(CommandHandler("endconvo", endconvo_command))
    application.add_handler(CommandHandler("photos", photos_command))
    
    # Sell mode commands
    application.add_handler(CommandHandler("done", done_command))
    application.add_handler(CommandHandler("undo", undo_command))
    application.add_handler(CommandHandler("inventory", inventory_wrapper))
    application.add_handler(CommandHandler("export", export_wrapper))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    print("🤖 Mythos Telegram Bot starting...")
    print("📦 Sell mode enabled")
    print("📸 Photo analysis via Ollama")
    print("   Press Ctrl+C to stop")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
PYEOF

    # Replace original with patched version
    mv "$MYTHOS_BASE/telegram_bot/mythos_bot_patched.py" "$BOT_FILE"
    
    success "Bot patched with sell mode"
}

# ============================================================================
# SET PERMISSIONS
# ============================================================================

set_permissions() {
    log "Setting permissions..."
    
    chown -R "$SERVICE_USER:$SERVICE_USER" "$MYTHOS_BASE/telegram_bot"
    chmod -R 755 "$MYTHOS_BASE/telegram_bot"
    
    success "Permissions set"
}

# ============================================================================
# VALIDATION
# ============================================================================

validate_phase() {
    log "Validating Phase $PHASE..."
    
    ERRORS=0
    
    # Check handlers module
    if ! "$VENV_PYTHON" -c "import sys; sys.path.insert(0, '/opt/mythos/telegram_bot'); from handlers import is_sell_mode" 2>/dev/null; then
        error "Failed to import handlers"
        ERRORS=$((ERRORS + 1))
    else
        success "Handlers module imports correctly"
    fi
    
    # Syntax check bot
    if ! "$VENV_PYTHON" -m py_compile "$BOT_FILE" 2>/dev/null; then
        error "Bot has syntax errors"
        ERRORS=$((ERRORS + 1))
    else
        success "Bot syntax OK"
    fi
    
    # Check vision integration
    if ! "$VENV_PYTHON" -c "
import sys
sys.path.insert(0, '/opt/mythos')
sys.path.insert(0, '/opt/mythos/telegram_bot')
from handlers.sell_mode import analyze_image
print('OK')
" 2>/dev/null; then
        error "Vision not accessible from handlers"
        ERRORS=$((ERRORS + 1))
    else
        success "Vision integration OK"
    fi
    
    if [ $ERRORS -gt 0 ]; then
        error "Validation failed with $ERRORS errors"
    fi
    
    success "Validation complete"
}

# ============================================================================
# RESTART BOT
# ============================================================================

restart_bot() {
    log "Restarting Telegram bot..."
    
    if systemctl is-active --quiet mythos-telegram-bot; then
        systemctl restart mythos-telegram-bot
        sleep 2
        if systemctl is-active --quiet mythos-telegram-bot; then
            success "Bot restarted successfully"
        else
            error "Bot failed to restart. Check: journalctl -u mythos-telegram-bot"
        fi
    else
        warn "Bot service not running. Start with: systemctl start mythos-telegram-bot"
    fi
}

# ============================================================================
# ROLLBACK
# ============================================================================

rollback() {
    warn "Rolling back Phase $PHASE..."
    
    LATEST_BACKUP=$(ls -td /opt/mythos/_backups/phase_${PHASE}_* 2>/dev/null | head -1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        error "No backup found for Phase $PHASE"
    fi
    
    log "Using backup: $LATEST_BACKUP"
    
    # Restore bot
    if [ -f "$LATEST_BACKUP/mythos_bot.py.bak" ]; then
        cp "$LATEST_BACKUP/mythos_bot.py.bak" "$BOT_FILE"
        success "Restored bot"
    fi
    
    # Remove handlers
    rm -rf "$MYTHOS_BASE/telegram_bot/handlers"
    success "Removed handlers"
    
    # Restart bot
    systemctl restart mythos-telegram-bot 2>/dev/null || true
    
    success "Rollback complete"
}

# ============================================================================
# MAIN
# ============================================================================

main() {
    echo ""
    echo -e "${CYAN}============================================================================${NC}"
    echo -e "${CYAN}PHASE $PHASE: $PHASE_NAME${NC}"
    echo -e "${CYAN}============================================================================${NC}"
    echo ""
    
    case "${1:-install}" in
        install)
            preflight_checks
            create_backup
            create_handlers
            patch_bot
            set_permissions
            validate_phase
            restart_bot
            
            echo ""
            success "Phase $PHASE complete!"
            echo ""
            echo "The Telegram bot now supports sell mode."
            echo ""
            echo "Usage:"
            echo "  /mode sell     - Enter sell mode"
            echo "  [send 3 photos] - Add item"
            echo "  /done          - Exit sell mode"
            echo "  /inventory     - View items"
            echo "  /export        - Generate listings"
            echo ""
            echo "Next steps:"
            echo "  1. Test: Send /mode sell to your bot"
            echo "  2. If issues: $0 rollback"
            ;;
        rollback)
            rollback
            ;;
        validate)
            validate_phase
            ;;
        *)
            echo "Usage: $0 [install|rollback|validate]"
            exit 1
            ;;
    esac
}

main "$@"
