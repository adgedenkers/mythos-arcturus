"""
Facebook Marketplace export generator

Creates a markdown listing page with copy-friendly code blocks
for each field, making it dead simple to copy/paste into FB.
"""

import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
import psycopg2

logger = logging.getLogger(__name__)

# FB Marketplace category mapping
FB_CATEGORY_MAP = {
    "sneakers": "Clothing & Shoes > Shoes",
    "shoes": "Clothing & Shoes > Shoes",
    "boots": "Clothing & Shoes > Shoes",
    "heels": "Clothing & Shoes > Shoes",
    "sandals": "Clothing & Shoes > Shoes",
    "jeans": "Clothing & Shoes > Women's Clothing" ,  # or Men's based on gender
    "pants": "Clothing & Shoes > Women's Clothing",
    "shorts": "Clothing & Shoes > Women's Clothing",
    "shirt": "Clothing & Shoes > Women's Clothing",
    "blouse": "Clothing & Shoes > Women's Clothing",
    "dress": "Clothing & Shoes > Women's Clothing",
    "jacket": "Clothing & Shoes > Women's Clothing",
    "coat": "Clothing & Shoes > Women's Clothing",
    "sweater": "Clothing & Shoes > Women's Clothing",
    "other": "Clothing & Shoes > Women's Clothing",
}

def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        host=os.getenv('POSTGRES_HOST', 'localhost')
    )


def get_fb_category(category: str, gender: str) -> str:
    """Map item category to FB Marketplace category"""
    base_category = FB_CATEGORY_MAP.get(category.lower(), "Clothing & Shoes")
    
    # Adjust for gender
    if gender == "mens":
        base_category = base_category.replace("Women's", "Men's")
    elif gender == "kids":
        base_category = base_category.replace("Women's Clothing", "Kids' Clothing")
    
    return base_category


def generate_fb_listing(item: dict, images: list) -> str:
    """Generate markdown listing for a single item"""
    
    # Build title
    title = item.get('title') or f"{item.get('brand', 'Unknown')} {item.get('category', 'Item')}"
    
    # Get price
    price = item.get('estimated_price') or 0
    
    # Get FB category
    fb_category = get_fb_category(
        item.get('category', 'other'),
        item.get('gender_category', 'unisex')
    )
    
    # Build condition for FB (they use different terms)
    condition_map = {
        'new_with_tags': 'New',
        'new_without_tags': 'New',
        'like_new': 'Like New',
        'gently_used': 'Good',
        'used': 'Good',
        'well_worn': 'Fair',
    }
    fb_condition = condition_map.get(item.get('condition', 'like_new'), 'Good')
    
    # Build description
    description = item.get('description', '')
    
    # Add size info if not in description
    size_label = item.get('size_label', '')
    if size_label and size_label.lower() not in description.lower():
        description += f"\n\nSize: {size_label}"
    
    # Add pickup info
    description += "\n\n📍 Pickup: Magro's Restaurant & Pizzeria, 104 East Main Street, Norwich NY"
    description += "\n💵 Cash preferred"
    
    # Build image paths
    image_section = ""
    if images:
        image_section = "\n### Photos\n"
        for img in images:
            image_section += f"- `{img.get('asset_rel_path', img.get('filename', 'unknown'))}`\n"
        image_section += f"\nFull path: `/opt/mythos/assets/{images[0].get('asset_rel_path', '')}`\n"
    
    # Build the listing markdown
    listing = f"""
---

## {title}

**Item ID:** `{item.get('id')}`

### Title
```
{title}
```

### Price
```
${price:.0f}
```

### Category
```
{fb_category}
```

### Condition
```
{fb_condition}
```

### Description
```
{description}
```

### Brand
```
{item.get('brand') or 'Unbranded'}
```
{image_section}
"""
    
    return listing


def generate_export_page(items: list = None, status: str = 'available') -> tuple[str, Path]:
    """
    Generate full export page for FB Marketplace listings
    
    Returns:
        Tuple of (markdown_content, output_path)
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get items
        if items:
            # Specific items by ID
            placeholders = ','.join(['%s'] * len(items))
            cur.execute(f"""
                SELECT * FROM items_for_sale 
                WHERE id IN ({placeholders})
                ORDER BY created_at DESC
            """, items)
        else:
            # All items with given status
            cur.execute("""
                SELECT * FROM items_for_sale 
                WHERE status = %s
                ORDER BY created_at DESC
            """, (status,))
        
        columns = [desc[0] for desc in cur.description]
        rows = cur.fetchall()
        
        if not rows:
            return "# No Items to Export\n\nNo available items found.", None
        
        # Build header
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        markdown = f"""# Facebook Marketplace Listings

**Generated:** {timestamp}  
**Items:** {len(rows)}  
**Status:** {status}

---

## Quick Reference

| Brand | Category | Size | Price |
|-------|----------|------|-------|
"""
        
        # Add quick reference table
        items_data = []
        for row in rows:
            item = dict(zip(columns, row))
            items_data.append(item)
            markdown += f"| {item.get('brand', 'Unknown')} | {item.get('category', '')} | {item.get('size_label', '')} | ${item.get('estimated_price', 0):.0f} |\n"
        
        markdown += "\n---\n\n# Listings\n"
        
        # Generate each listing
        for item in items_data:
            # Get images for this item
            cur.execute("""
                SELECT filename, view_type, asset_rel_path, is_primary
                FROM item_images 
                WHERE item_id = %s
                ORDER BY is_primary DESC, view_type
            """, (item['id'],))
            
            img_columns = [desc[0] for desc in cur.description]
            img_rows = cur.fetchall()
            images = [dict(zip(img_columns, img)) for img in img_rows]
            
            markdown += generate_fb_listing(item, images)
        
        # Write to file
        export_dir = Path("/opt/mythos/exports")
        export_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"fb_listings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        output_path = export_dir / filename
        
        with open(output_path, 'w') as f:
            f.write(markdown)
        
        logger.info(f"Generated FB export: {output_path}")
        
        return markdown, output_path
        
    except Exception as e:
        logger.error(f"Export error: {e}", exc_info=True)
        return f"# Export Error\n\n{e}", None
    finally:
        if conn:
            conn.close()


async def export_command(update, context, session: dict):
    """Handle /export command from Telegram"""
    from telegram import Update
    from telegram.ext import ContextTypes
    
    await update.message.reply_text("📤 Generating Facebook Marketplace listings...")
    
    try:
        markdown, output_path = generate_export_page()
        
        if output_path:
            # Send the file
            with open(output_path, 'rb') as f:
                await update.message.reply_document(
                    document=f,
                    filename=output_path.name,
                    caption=f"✅ Export complete!\n\n{len(markdown)} characters\nFile: `{output_path}`"
                )
        else:
            await update.message.reply_text(markdown[:4000])  # Telegram message limit
            
    except Exception as e:
        logger.error(f"Export command error: {e}", exc_info=True)
        await update.message.reply_text(f"❌ Export failed: {e}")
