"""
Export and inventory handlers - FB Marketplace optimized
"""

import os
import logging
from datetime import datetime
from pathlib import Path

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
        lines.append(f"\n━━━━━━━━━━━━━━━━━━━━━━━━")
        lines.append(f"💰 Total value: ${total_value:.0f}")
        lines.append(f"\nUse /export to generate listings.")
        
        await update.message.reply_text("\n".join(lines))
        
    except Exception as e:
        logger.error(f"Error fetching inventory: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def export_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate FB Marketplace listings with copy-friendly code blocks"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            SELECT 
                i.id, i.brand, i.model, i.title, i.description,
                i.category, i.gender_category, i.size_label,
                i.condition, i.estimated_price, i.colors,
                i.materials, i.features
            FROM items_for_sale i
            WHERE i.status = 'available'
            ORDER BY i.created_at DESC
        """)
        
        items = cur.fetchall()
        
        if not items:
            await update.message.reply_text(
                "📤 **No items to export**\n\n"
                "All items are either listed or sold.\n"
                "Use /mode sell to add more items."
            )
            conn.close()
            return
        
        await update.message.reply_text(f"📤 Generating {len(items)} listing(s)...\n\nEach field is in a code block - tap to copy!")
        
        for item in items:
            (item_id, brand, model, title, description,
             category, gender, size, condition, price, colors,
             materials, features) = item
            
            # Get images for this item
            cur.execute("""
                SELECT asset_rel_path 
                FROM item_images 
                WHERE item_id = %s 
                ORDER BY is_primary DESC
            """, (item_id,))
            images = cur.fetchall()
            image_paths = [f"/opt/mythos/assets/{img[0]}" for img in images] if images else []
            
            # Map condition for FB
            condition_map = {
                "new_with_tags": "New",
                "new_without_tags": "New",
                "like_new": "Like New",
                "gently_used": "Good",
                "used": "Good",
                "well_worn": "Fair"
            }
            fb_condition = condition_map.get(condition, "Good")
            
            # Map category for FB
            fb_category = _get_fb_category(category, gender)
            
            # Build title if not set
            brand_str = brand or "Brand"
            if not title:
                title = f"{brand_str} {category.title() if category else 'Item'}"
                if size:
                    title += f" Size {size}"
            
            # Build description with pickup info
            full_description = description or f"{brand_str} {category or 'item'} in {fb_condition.lower()} condition."
            full_description += "\n\n📍 Pickup: Magro's Restaurant & Pizzeria, 104 East Main Street, Norwich NY"
            full_description += "\n💵 Cash preferred"
            
            # Build the listing message with code blocks
            listing = f"""━━━━━━━━━━━━━━━━━━━━━━━━
📦 **{brand_str} {category or 'Item'}**
━━━━━━━━━━━━━━━━━━━━━━━━

**Title** (tap to copy):
```
{title}
```

**Price**:
```
{price:.0f}
```

**Condition**:
```
{fb_condition}
```

**Category**:
```
{fb_category}
```

**Brand**:
```
{brand_str}
```

**Description**:
```
{full_description}
```

**Photos**: {len(image_paths)} available
"""
            # Add image paths
            if image_paths:
                listing += "```\n" + "\n".join(image_paths) + "\n```\n"
            
            listing += f"""
━━━━━━━━━━━━━━━━━━━━━━━━
`/listed {str(item_id)[:8]}` after posting
"""
            
            await update.message.reply_text(listing, parse_mode='Markdown')
        
        conn.close()
        
        await update.message.reply_text(
            f"✅ **{len(items)} listing(s) ready**\n\n"
            "Tap any code block to copy.\n"
            "Run `/listed <id>` after posting each item."
        )
        
    except Exception as e:
        logger.error(f"Error generating export: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Error: {e}")


def _get_fb_category(category: str, gender: str) -> str:
    """Map item category to FB Marketplace category string"""
    
    # Base category mapping
    category_map = {
        "sneakers": "Clothing & Shoes > Shoes",
        "shoes": "Clothing & Shoes > Shoes",
        "boots": "Clothing & Shoes > Shoes",
        "heels": "Clothing & Shoes > Shoes",
        "sandals": "Clothing & Shoes > Shoes",
        "flats": "Clothing & Shoes > Shoes",
        "jeans": "Clothing & Shoes",
        "pants": "Clothing & Shoes",
        "shorts": "Clothing & Shoes",
        "shirt": "Clothing & Shoes",
        "blouse": "Clothing & Shoes",
        "top": "Clothing & Shoes",
        "dress": "Clothing & Shoes",
        "skirt": "Clothing & Shoes",
        "jacket": "Clothing & Shoes",
        "coat": "Clothing & Shoes",
        "sweater": "Clothing & Shoes",
        "hoodie": "Clothing & Shoes",
        "activewear": "Clothing & Shoes",
        "athletic": "Clothing & Shoes",
    }
    
    base = category_map.get(category.lower() if category else "", "Clothing & Shoes")
    
    # Add gender context
    if gender == "mens":
        return f"{base} > Men's Clothing" if "Shoes" not in base else base
    elif gender == "womens":
        return f"{base} > Women's Clothing" if "Shoes" not in base else base
    elif gender == "kids":
        return f"{base} > Kids' Clothing" if "Shoes" not in base else f"{base} > Kids"
    
    return base


async def listed_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark an item as listed on marketplace"""
    try:
        args = context.args
        if not args:
            await update.message.reply_text(
                "Usage: `/listed <item_id>`\n\n"
                "Example: `/listed 6615ca89`"
            )
            return
        
        item_id_prefix = args[0]
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Find item by prefix
        cur.execute("""
            UPDATE items_for_sale 
            SET status = 'listed', listed_date = NOW(), updated_at = NOW()
            WHERE id::text LIKE %s AND status = 'available'
            RETURNING id, brand, category
        """, (f"{item_id_prefix}%",))
        
        result = cur.fetchone()
        conn.commit()
        conn.close()
        
        if result:
            item_id, brand, category = result
            await update.message.reply_text(
                f"✅ **Marked as Listed**\n\n"
                f"{brand or 'Item'} {category or ''}\n"
                f"ID: `{item_id}`"
            )
        else:
            await update.message.reply_text(
                f"❌ No available item found starting with `{item_id_prefix}`"
            )
            
    except Exception as e:
        logger.error(f"Error marking listed: {e}")
        await update.message.reply_text(f"❌ Error: {e}")


async def sold_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mark an item as sold"""
    try:
        args = context.args
        if not args:
            await update.message.reply_text(
                "Usage: `/sold <item_id>`\n\n"
                "Example: `/sold 6615ca89`"
            )
            return
        
        item_id_prefix = args[0]
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Find item by prefix
        cur.execute("""
            UPDATE items_for_sale 
            SET status = 'sold', sold_date = NOW(), updated_at = NOW()
            WHERE id::text LIKE %s AND status IN ('available', 'listed')
            RETURNING id, brand, category, estimated_price
        """, (f"{item_id_prefix}%",))
        
        result = cur.fetchone()
        conn.commit()
        conn.close()
        
        if result:
            item_id, brand, category, price = result
            await update.message.reply_text(
                f"🎉 **SOLD!**\n\n"
                f"{brand or 'Item'} {category or ''}\n"
                f"💰 ${price:.0f}\n"
                f"ID: `{item_id}`"
            )
        else:
            await update.message.reply_text(
                f"❌ No available/listed item found starting with `{item_id_prefix}`"
            )
            
    except Exception as e:
        logger.error(f"Error marking sold: {e}")
        await update.message.reply_text(f"❌ Error: {e}")
