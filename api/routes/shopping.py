#!/usr/bin/env python3
"""
Mythos Shopping API Routes
/opt/mythos/api/routes/shopping.py

Endpoints:
    # Stores
    GET    /api/shopping/stores          - List stores
    POST   /api/shopping/stores          - Create store
    PATCH  /api/shopping/stores/{id}     - Update store
    DELETE /api/shopping/stores/{id}     - Delete store

    # Items
    GET    /api/shopping/items           - List items
    POST   /api/shopping/items           - Create item
    PATCH  /api/shopping/items/{id}      - Update item
    DELETE /api/shopping/items/{id}      - Delete item
    POST   /api/shopping/items/{id}/store - Associate item with store

    # Lists
    GET    /api/shopping/lists           - List shopping lists
    POST   /api/shopping/lists           - Create list
    PATCH  /api/shopping/lists/{id}      - Update list
    DELETE /api/shopping/lists/{id}      - Delete list
    POST   /api/shopping/lists/{id}/add  - Add item to list
    POST   /api/shopping/lists/{id}/done - Mark item done
    GET    /api/shopping/lists/{id}/items - Get list items

    # The Killer Feature
    GET    /api/shopping/at/{store}      - Items grouped by dept for a store

    # Stats
    GET    /api/shopping/stats           - Summary stats
"""
import os
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

router = APIRouter(prefix="/api/shopping", tags=["shopping"])


def get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
    )


# ── Models ──────────────────────────────────────────

class StoreCreate(BaseModel):
    name: str
    category: str = "grocery"
    address: str = ""
    city: str = ""
    state: str = ""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: str = ""

class StoreUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    notes: Optional[str] = None

class ItemCreate(BaseModel):
    name: str
    department: str = ""
    default_quantity: float = 1
    default_unit: str = "each"
    notes: str = ""

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    default_quantity: Optional[float] = None
    default_unit: Optional[str] = None
    notes: Optional[str] = None
    usual_price: Optional[float] = None

class ListCreate(BaseModel):
    name: str
    description: str = ""

class ListItemAdd(BaseModel):
    item_name: str
    quantity: Optional[float] = None
    unit: Optional[str] = None
    priority: str = "normal"
    notes: str = ""
    store_name: Optional[str] = None

class ItemStoreAssoc(BaseModel):
    store_name: str
    aisle: str = ""
    department_override: str = ""
    usual_price: Optional[float] = None


# ── Stats ───────────────────────────────────────────

@router.get("/stats")
async def shopping_stats():
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT
                (SELECT count(*) FROM stores WHERE is_active) AS stores,
                (SELECT count(*) FROM shopping_items WHERE is_active) AS items,
                (SELECT count(*) FROM shopping_lists WHERE is_active) AS lists,
                (SELECT count(*) FROM shopping_list_items WHERE NOT completed) AS pending_items,
                (SELECT count(*) FROM shopping_list_items WHERE completed) AS completed_items
        """)
        return cur.fetchone()
    finally:
        conn.close()


# ── Stores ──────────────────────────────────────────

@router.get("/stores")
async def list_stores(search: Optional[str] = None, category: Optional[str] = None):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        where = ["is_active = TRUE"]
        params = []
        if search:
            where.append("(LOWER(name) LIKE LOWER(%s) OR LOWER(address) LIKE LOWER(%s))")
            params.extend([f"%{search}%", f"%{search}%"])
        if category:
            where.append("category = %s")
            params.append(category)
        cur.execute(f"""
            SELECT id, name, category, address, city, state,
                   latitude, longitude, notes, visit_frequency, last_visited
            FROM stores WHERE {' AND '.join(where)}
            ORDER BY visit_frequency DESC, name
        """, params)
        return {"stores": cur.fetchall(), "count": cur.rowcount}
    finally:
        conn.close()

@router.post("/stores", status_code=201)
async def create_store(body: StoreCreate):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            INSERT INTO stores (name, category, address, city, state, latitude, longitude, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id, name, category
        """, (body.name, body.category, body.address, body.city, body.state,
              body.latitude, body.longitude, body.notes))
        conn.commit()
        return cur.fetchone()
    finally:
        conn.close()

@router.patch("/stores/{store_id}")
async def update_store(store_id: str, body: StoreUpdate):
    conn = get_conn()
    try:
        cur = conn.cursor()
        updates = body.dict(exclude_unset=True, exclude_none=True)
        if not updates:
            raise HTTPException(400, "No fields to update")
        sets = [f"{k} = %s" for k in updates]
        sets.append("updated_at = NOW()")
        vals = list(updates.values()) + [store_id]
        cur.execute(f"UPDATE stores SET {', '.join(sets)} WHERE id = %s", vals)
        conn.commit()
        return {"status": "updated", "store_id": store_id}
    finally:
        conn.close()

@router.delete("/stores/{store_id}")
async def delete_store(store_id: str):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE stores SET is_active = FALSE, updated_at = NOW() WHERE id = %s", (store_id,))
        conn.commit()
        return {"status": "deactivated", "store_id": store_id}
    finally:
        conn.close()


# ── Items ───────────────────────────────────────────

@router.get("/items")
async def list_items(
    search: Optional[str] = None,
    department: Optional[str] = None,
    limit: int = Query(200, ge=1, le=500),
):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        where = ["is_active = TRUE"]
        params = []
        if search:
            where.append("LOWER(name) LIKE LOWER(%s)")
            params.append(f"%{search}%")
        if department:
            where.append("department = %s")
            params.append(department)
        params.append(limit)
        cur.execute(f"""
            SELECT i.id, i.name, i.department, i.default_quantity, i.default_unit,
                   i.notes, i.usual_price, i.last_purchased, i.purchase_count,
                   (SELECT array_agg(s.name) FROM item_stores ist
                    JOIN stores s ON s.id = ist.store_id WHERE ist.item_id = i.id) AS stores
            FROM shopping_items i WHERE {' AND '.join(where)}
            ORDER BY i.name
            LIMIT %s
        """, params)
        return {"items": cur.fetchall(), "count": cur.rowcount}
    finally:
        conn.close()

@router.post("/items", status_code=201)
async def create_item(body: ItemCreate):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Check if item already exists by name (case-insensitive)
        cur.execute("SELECT id, name FROM shopping_items WHERE LOWER(name) = LOWER(%s) AND is_active", (body.name,))
        existing = cur.fetchone()
        if existing:
            return {"status": "exists", "item": existing}
        cur.execute("""
            INSERT INTO shopping_items (name, department, default_quantity, default_unit, notes)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, name, department
        """, (body.name, body.department, body.default_quantity, body.default_unit, body.notes))
        conn.commit()
        return cur.fetchone()
    finally:
        conn.close()

@router.patch("/items/{item_id}")
async def update_item(item_id: str, body: ItemUpdate):
    conn = get_conn()
    try:
        cur = conn.cursor()
        updates = body.dict(exclude_unset=True, exclude_none=True)
        if not updates:
            raise HTTPException(400, "No fields to update")
        sets = [f"{k} = %s" for k in updates]
        sets.append("updated_at = NOW()")
        vals = list(updates.values()) + [item_id]
        cur.execute(f"UPDATE shopping_items SET {', '.join(sets)} WHERE id = %s", vals)
        conn.commit()
        return {"status": "updated", "item_id": item_id}
    finally:
        conn.close()

@router.delete("/items/{item_id}")
async def delete_item(item_id: str):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE shopping_items SET is_active = FALSE, updated_at = NOW() WHERE id = %s", (item_id,))
        conn.commit()
        return {"status": "deactivated", "item_id": item_id}
    finally:
        conn.close()

@router.post("/items/{item_id}/store")
async def associate_item_store(item_id: str, body: ItemStoreAssoc):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Find store by name
        cur.execute("SELECT id, name FROM stores WHERE LOWER(name) LIKE LOWER(%s) AND is_active LIMIT 1",
                     (f"%{body.store_name}%",))
        store = cur.fetchone()
        if not store:
            raise HTTPException(404, f"Store '{body.store_name}' not found")
        cur.execute("""
            INSERT INTO item_stores (item_id, store_id, aisle, department_override, usual_price)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (item_id, store_id) DO UPDATE SET
                aisle = EXCLUDED.aisle, department_override = EXCLUDED.department_override,
                usual_price = EXCLUDED.usual_price
            RETURNING id
        """, (item_id, store['id'], body.aisle, body.department_override, body.usual_price))
        conn.commit()
        return {"status": "associated", "store": store['name']}
    finally:
        conn.close()


# ── Lists ───────────────────────────────────────────

@router.get("/lists")
async def list_lists(include_completed: bool = False):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        where = "is_active = TRUE" if not include_completed else "TRUE"
        cur.execute(f"""
            SELECT l.id, l.name, l.description, l.status, l.created_at,
                   (SELECT count(*) FROM shopping_list_items li WHERE li.list_id = l.id AND NOT li.completed) AS pending,
                   (SELECT count(*) FROM shopping_list_items li WHERE li.list_id = l.id AND li.completed) AS done
            FROM shopping_lists l WHERE {where}
            ORDER BY l.created_at DESC
        """)
        return {"lists": cur.fetchall()}
    finally:
        conn.close()

@router.post("/lists", status_code=201)
async def create_list(body: ListCreate):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            INSERT INTO shopping_lists (name, description)
            VALUES (%s, %s) RETURNING id, name
        """, (body.name, body.description))
        conn.commit()
        return cur.fetchone()
    finally:
        conn.close()

@router.get("/lists/{list_id}/items")
async def get_list_items(list_id: str, show_done: bool = False):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        where = "NOT li.completed" if not show_done else "TRUE"
        cur.execute(f"""
            SELECT li.id AS list_item_id, i.id AS item_id, i.name, i.department,
                   COALESCE(li.quantity, i.default_quantity) AS quantity,
                   COALESCE(li.unit_override, i.default_unit) AS unit,
                   li.priority, li.notes, li.completed, li.completed_at,
                   (SELECT array_agg(s.name) FROM item_stores ist
                    JOIN stores s ON s.id = ist.store_id WHERE ist.item_id = i.id) AS available_stores
            FROM shopping_list_items li
            JOIN shopping_items i ON i.id = li.item_id
            WHERE li.list_id = %s AND {where}
            ORDER BY li.priority DESC, i.department, i.name
        """, (list_id,))
        return {"items": cur.fetchall()}
    finally:
        conn.close()

@router.post("/lists/{list_id}/add", status_code=201)
async def add_item_to_list(list_id: str, body: ListItemAdd):
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Find or create the item
        cur.execute("SELECT id, name FROM shopping_items WHERE LOWER(name) = LOWER(%s) AND is_active", (body.item_name,))
        item = cur.fetchone()
        if not item:
            cur.execute("""
                INSERT INTO shopping_items (name, default_quantity, default_unit, notes)
                VALUES (%s, %s, %s, %s) RETURNING id, name
            """, (body.item_name, body.quantity or 1, body.unit or 'each', body.notes))
            item = cur.fetchone()

        # Add to list
        cur.execute("""
            INSERT INTO shopping_list_items (list_id, item_id, quantity, unit_override, priority, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (list_id, item_id) DO UPDATE SET
                quantity = EXCLUDED.quantity, priority = EXCLUDED.priority,
                completed = FALSE, completed_at = NULL
            RETURNING id
        """, (list_id, item['id'], body.quantity, body.unit, body.priority, body.notes))

        # If store specified, create association
        if body.store_name:
            cur.execute("SELECT id FROM stores WHERE LOWER(name) LIKE LOWER(%s) AND is_active LIMIT 1",
                         (f"%{body.store_name}%",))
            store = cur.fetchone()
            if store:
                cur.execute("""
                    INSERT INTO item_stores (item_id, store_id) VALUES (%s, %s)
                    ON CONFLICT (item_id, store_id) DO NOTHING
                """, (item['id'], store['id']))

        conn.commit()
        return {"status": "added", "item": item['name'], "list_id": list_id}
    finally:
        conn.close()

@router.post("/lists/{list_id}/done")
async def mark_done(list_id: str, item_name: str):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE shopping_list_items li SET completed = TRUE, completed_at = NOW()
            FROM shopping_items i
            WHERE li.item_id = i.id AND li.list_id = %s AND LOWER(i.name) = LOWER(%s)
            RETURNING li.id
        """, (list_id, item_name))
        if cur.rowcount == 0:
            raise HTTPException(404, f"Item '{item_name}' not found in list")
        # Update item stats
        cur.execute("""
            UPDATE shopping_items SET last_purchased = NOW(), purchase_count = purchase_count + 1
            WHERE LOWER(name) = LOWER(%s)
        """, (item_name,))
        conn.commit()
        return {"status": "done", "item": item_name}
    finally:
        conn.close()

@router.patch("/lists/{list_id}")
async def update_list(list_id: str, name: Optional[str] = None, status: Optional[str] = None):
    conn = get_conn()
    try:
        cur = conn.cursor()
        sets = ["updated_at = NOW()"]
        vals = []
        if name:
            sets.append("name = %s"); vals.append(name)
        if status:
            sets.append("status = %s"); vals.append(status)
            if status == "completed":
                sets.append("completed_at = NOW()")
        vals.append(list_id)
        cur.execute(f"UPDATE shopping_lists SET {', '.join(sets)} WHERE id = %s", vals)
        conn.commit()
        return {"status": "updated"}
    finally:
        conn.close()

@router.delete("/lists/{list_id}")
async def delete_list(list_id: str):
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE shopping_lists SET is_active = FALSE, updated_at = NOW() WHERE id = %s", (list_id,))
        conn.commit()
        return {"status": "deactivated"}
    finally:
        conn.close()


# ── THE KILLER FEATURE: Store Context View ──────────

@router.get("/at/{store_name}")
async def items_at_store(store_name: str):
    """Get all pending shopping items available at a specific store, grouped by department."""
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Find the store
        cur.execute("SELECT id, name, category FROM stores WHERE LOWER(name) LIKE LOWER(%s) AND is_active LIMIT 1",
                     (f"%{store_name}%",))
        store = cur.fetchone()
        if not store:
            raise HTTPException(404, f"Store '{store_name}' not found")

        # Get all pending items associated with this store
        cur.execute("""
            SELECT i.id, i.name,
                   COALESCE(ist.department_override, i.department, 'General') AS department,
                   COALESCE(li.quantity, i.default_quantity) AS quantity,
                   COALESCE(li.unit_override, i.default_unit) AS unit,
                   li.priority, li.notes AS list_notes,
                   ist.aisle, ist.usual_price,
                   l.name AS list_name
            FROM shopping_list_items li
            JOIN shopping_items i ON i.id = li.item_id
            JOIN shopping_lists l ON l.id = li.list_id AND l.is_active = TRUE
            JOIN item_stores ist ON ist.item_id = i.id AND ist.store_id = %s
            WHERE NOT li.completed AND i.is_active = TRUE
            ORDER BY department, li.priority DESC, i.name
        """, (store['id'],))
        items = cur.fetchall()

        # Also get items without store association that are on active lists
        # (user might not have categorized them yet)
        cur.execute("""
            SELECT i.id, i.name,
                   COALESCE(i.department, 'Uncategorized') AS department,
                   COALESCE(li.quantity, i.default_quantity) AS quantity,
                   COALESCE(li.unit_override, i.default_unit) AS unit,
                   li.priority, li.notes AS list_notes,
                   NULL AS aisle, NULL AS usual_price,
                   l.name AS list_name
            FROM shopping_list_items li
            JOIN shopping_items i ON i.id = li.item_id
            JOIN shopping_lists l ON l.id = li.list_id AND l.is_active = TRUE
            WHERE NOT li.completed AND i.is_active = TRUE
              AND i.id NOT IN (SELECT item_id FROM item_stores)
            ORDER BY department, li.priority DESC, i.name
        """)
        uncategorized = cur.fetchall()

        # Group by department
        departments = {}
        for item in items + uncategorized:
            dept = item['department']
            if dept not in departments:
                departments[dept] = []
            departments[dept].append(item)

        # Update visit stats
        cur.execute("UPDATE stores SET visit_frequency = visit_frequency + 1, last_visited = NOW() WHERE id = %s",
                     (store['id'],))
        conn.commit()

        return {
            "store": store,
            "departments": departments,
            "total_items": len(items) + len(uncategorized),
            "categorized": len(items),
            "uncategorized": len(uncategorized),
        }
    finally:
        conn.close()
