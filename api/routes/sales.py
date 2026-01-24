"""
Sales item management API routes
"""

from fastapi import APIRouter, HTTPException, Header
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os

router = APIRouter(prefix="/items/sale", tags=["sales"])

# Database connection
def get_db():
    return psycopg2.connect(
        dbname=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        host=os.getenv('POSTGRES_HOST', 'localhost')
    )

# Models
class ItemUpdate(BaseModel):
    title: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    size_label: Optional[str] = None
    condition: Optional[str] = None
    estimated_price: Optional[float] = None
    description: Optional[str] = None
    status: Optional[str] = None
    listing_platform: Optional[str] = None
    actual_sale_price: Optional[float] = None

@router.get("")
async def get_items(status: str = "available"):
    """Get all items for sale by status"""
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT 
                    i.*,
                    COUNT(img.id) as photo_count
                FROM items_for_sale i
                LEFT JOIN item_images img ON img.item_id = i.id
                WHERE i.status = %s
                GROUP BY i.id
                ORDER BY i.created_at DESC
            """, (status,))
            items = cur.fetchall()
        conn.close()
        
        # Convert datetime and UUID objects to strings
        for item in items:
            for key, value in item.items():
                if isinstance(value, datetime):
                    item[key] = value.isoformat()
                elif hasattr(value, 'hex'):  # UUID
                    item[key] = str(value)
        
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{item_id}")
async def get_item(item_id: str):
    """Get single item details"""
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM items_for_sale WHERE id = %s", (item_id,))
            item = cur.fetchone()
        conn.close()
        
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Convert datetime and UUID objects
        for key, value in item.items():
            if isinstance(value, datetime):
                item[key] = value.isoformat()
            elif hasattr(value, 'hex'):
                item[key] = str(value)
        
        return {"item": item}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{item_id}")
async def update_item(item_id: str, updates: ItemUpdate):
    """Update item fields"""
    try:
        conn = get_db()
        
        # Build UPDATE query
        update_dict = updates.dict(exclude_unset=True)
        if not update_dict:
            raise HTTPException(status_code=400, detail="No updates provided")
        
        set_clauses = []
        values = []
        for key, value in update_dict.items():
            set_clauses.append(f"{key} = %s")
            values.append(value)
        
        values.append(item_id)
        
        with conn.cursor() as cur:
            cur.execute(f"""
                UPDATE items_for_sale 
                SET {', '.join(set_clauses)}
                WHERE id = %s
            """, values)
            conn.commit()
        conn.close()
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{item_id}")
async def delete_item(item_id: str):
    """Delete an item"""
    try:
        conn = get_db()
        with conn.cursor() as cur:
            cur.execute("DELETE FROM items_for_sale WHERE id = %s", (item_id,))
            conn.commit()
        conn.close()
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{item_id}/photos")
async def get_item_photos(item_id: str):
    """Get photos for an item"""
    try:
        conn = get_db()
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT * FROM item_images 
                WHERE item_id = %s 
                ORDER BY is_primary DESC, id ASC
            """, (item_id,))
            photos = cur.fetchall()
        conn.close()
        
        # Convert datetime and UUID objects
        for photo in photos:
            for key, value in photo.items():
                if isinstance(value, datetime):
                    photo[key] = value.isoformat()
                elif hasattr(value, 'hex'):
                    photo[key] = str(value)
        
        return {"photos": photos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
