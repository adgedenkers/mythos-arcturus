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
import psycopg2.extras
psycopg2.extras.register_uuid()
from psycopg2.extras import Json
from telegram import Update
from telegram.ext import ContextTypes

# Add mythos to path
sys.path.insert(0, '/opt/mythos')

from vision import analyze_image
from vision.prompts import sales
from vision.config import get_config

logger = logging.getLogger(__name__)

# === Value normalizers for DB constraints ===

GENDER_MAP = {
    "mens": "mens", "men": "mens", "male": "mens", "m": "mens",
    "womens": "womens", "women": "womens", "female": "womens", "w": "womens", "ladies": "womens",
    "unisex": "unisex", "neutral": "unisex",
    "kids": "kids", "children": "kids", "boys": "kids", "girls": "kids", "youth": "kids",
}

CONDITION_MAP = {
    "new_with_tags": "new_with_tags", "new with tags": "new_with_tags", "nwt": "new_with_tags",
    "new_without_tags": "new_without_tags", "new without tags": "new_without_tags", "nwot": "new_without_tags",
    "like_new": "like_new", "like new": "like_new", "excellent": "like_new",
    "gently_used": "gently_used", "gently used": "gently_used", "good": "gently_used",
    "used": "used", "fair": "used",
    "well_worn": "well_worn", "well worn": "well_worn", "poor": "well_worn",
}

def normalize_gender(value: str) -> str:
    """Normalize gender_category to valid DB value"""
    if not value:
        return "unisex"
    return GENDER_MAP.get(value.lower().strip(), "unisex")

def normalize_condition(value: str) -> str:
    """Normalize condition to valid DB value"""
    if not value:
        return "like_new"
    return CONDITION_MAP.get(value.lower().strip(), "like_new")

def sanitize_analysis(analysis: dict) -> dict:
    """Sanitize all vision output to match DB constraints"""
    analysis["gender_category"] = normalize_gender(analysis.get("gender_category", ""))
    analysis["condition"] = normalize_condition(analysis.get("condition", ""))
    return analysis


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
    
    # Handle both regular photos and documents (HEIC, etc)
    if update.message.photo:
        # Regular photo - Telegram provides multiple resolutions
        message_photos = update.message.photo
        
        # Debug: log all available photo sizes
        for i, p in enumerate(message_photos):
            logger.info(f"Photo option {i}: {p.width}x{p.height}, size={p.file_size}")
        
        # Get highest resolution (last in list)
        photo = message_photos[-1]
        file_id = photo.file_id
        file_unique_id = photo.file_unique_id
        width = photo.width
        height = photo.height
        is_document = False
        
    elif update.message.document:
        # Document (HEIC, full-res JPEG, etc)
        document = update.message.document
        
        # Check if it's an image
        if not document.mime_type or not document.mime_type.startswith('image/'):
            await update.message.reply_text("📷 Please send image files only.")
            return
        
        logger.info(f"Received document: {document.file_name}, {document.file_size:,} bytes, {document.mime_type}")
        
        file_id = document.file_id
        file_unique_id = document.file_unique_id
        width = 0  # Will get from actual file
        height = 0
        is_document = True
        
    else:
        await update.message.reply_text("No photos detected in message.")
        return
    
    # Check if this is part of a media group (multiple photos in one message)
    media_group_id = update.message.media_group_id
    
    # Download and store photo/document
    try:
        file = await context.bot.get_file(file_id)
        
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
        
        # Download photo/document
        photo_num = len(sell_session["current_photos"]) + 1
        
        if is_document:
            # Get extension from document filename
            ext = document.file_name.split('.')[-1].lower() if '.' in document.file_name else 'jpg'
            photo_filename = f"photo_{photo_num}.{ext}"
        else:
            photo_filename = f"photo_{photo_num}.jpg"
        
        photo_path = intake_dir / photo_filename
        
        await file.download_to_drive(str(photo_path))
        
        # Convert HEIC to JPEG if needed
        if is_document and ext in ['heic', 'heif']:
            try:
                from PIL import Image
                import pillow_heif
                
                # Register HEIF opener
                pillow_heif.register_heif_opener()
                
                # Convert to JPEG
                with Image.open(photo_path) as img:
                    if img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')
                    
                    jpeg_path = intake_dir / f"photo_{photo_num}.jpg"
                    img.save(jpeg_path, 'JPEG', quality=95)
                    
                    # Update path
                    photo_path = jpeg_path
                    photo_filename = f"photo_{photo_num}.jpg"
                    width, height = img.size
                    
                    logger.info(f"Converted HEIC to JPEG: {width}x{height}")
                    
            except Exception as e:
                logger.error(f"Error converting HEIC: {e}")
                await update.message.reply_text(f"⚠️ Error converting HEIC image. Try sending as JPEG.")
                return
        
        # Get dimensions if not already set
        if width == 0 or height == 0:
            try:
                from PIL import Image
                with Image.open(photo_path) as img:
                    width, height = img.size
            except Exception as e:
                logger.warning(f"Couldn't get image dimensions: {e}")
        
        # Add to buffer
        sell_session["current_photos"].append({
            "path": str(photo_path),
            "filename": photo_filename,
            "telegram_file_id": file_id,
            "telegram_file_unique_id": file_unique_id,
            "width": width,
            "height": height,
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
        
        # Sanitize vision output to match DB constraints
        analysis = sanitize_analysis(analysis)
        
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
            analysis.get("gender_category"),
            analysis.get("size_label"),
            analysis.get("size_numeric"),
            analysis.get("size_width"),
            "like_new",  # Default - override manually for NWT or gently_used
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


async def handle_sell_document(update: Update, context: ContextTypes.DEFAULT_TYPE, session: dict):
    """
    Handle documents (uncompressed photos) in sell mode.
    Same flow as photos but preserves full resolution.
    """
    telegram_id = update.effective_user.id
    sell_session = session.get("sell_session", {})
    
    if not sell_session.get("active"):
        # Not in sell mode, ignore
        return
    
    document = update.message.document
    
    # Only accept image documents
    if not document.mime_type or not document.mime_type.startswith('image/'):
        await update.message.reply_text("📷 Please send image files only (in sell mode).")
        return
    
    logger.info(f"Received full-res document: {document.file_name}, {document.file_size:,} bytes")
    
    # Same handling as photos from here
    try:
        file = await context.bot.get_file(document.file_id)
        
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
        
        # Download document (full resolution)
        photo_num = len(sell_session["current_photos"]) + 1
        ext = document.file_name.split('.')[-1] if '.' in document.file_name else 'jpg'
        photo_filename = f"photo_{photo_num}.{ext}"
        photo_path = intake_dir / photo_filename
        
        await file.download_to_drive(str(photo_path))
        
        # Get actual dimensions from file
        try:
            from PIL import Image
            with Image.open(photo_path) as img:
                width, height = img.size
        except:
            width, height = 0, 0
        
        # Add to buffer
        sell_session["current_photos"].append({
            "path": str(photo_path),
            "filename": photo_filename,
            "telegram_file_id": document.file_id,
            "telegram_file_unique_id": document.file_unique_id,
            "width": width,
            "height": height,
            "received_at": datetime.now().isoformat()
        })
        
        current_count = len(sell_session["current_photos"])
        
        logger.info(f"Document photo {current_count}/3 received ({width}x{height}, {document.file_size:,} bytes)")
        
        # If we have 3 photos, process the item
        if current_count >= 3:
            await update.message.reply_text("📸 3 photos received. Analyzing...")
            
            # Process in background
            asyncio.create_task(
                process_item(update, context, session, telegram_id)
            )
        else:
            # Acknowledge receipt
            remaining = 3 - current_count
            await update.message.reply_text(
                f"📸 Photo {current_count}/3 received (full resolution: {width}x{height}).\n"
                f"Send {remaining} more photo{'s' if remaining > 1 else ''}."
            )
            
    except Exception as e:
        logger.error(f"Error handling document: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error saving photo: {e}")
