"""
Grocery API Routes — /api/grocery/*
Serves both the Command Center React frontend and the Telegram skill.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Optional

router = APIRouter(prefix="/api/grocery", tags=["grocery"])

# Import the aisle guesser from the skill
import sys
sys.path.insert(0, '/opt/mythos/skills/data')
from grocery_skill import _guess_aisle


def _get_conn():
    return psycopg2.connect(
        dbname='mythos', user='adge', host='localhost',
        cursor_factory=RealDictCursor
    )


def _get_active_list_id(conn, telegram_user_id: int = 0) -> int:
    cur = conn.cursor()
    cur.execute(
        "SELECT id FROM grocery_lists WHERE telegram_user_id = %s AND is_active = TRUE ORDER BY created_at DESC LIMIT 1",
        (telegram_user_id,)
    )
    row = cur.fetchone()
    if row:
        return row['id']
    cur.execute(
        "INSERT INTO grocery_lists (name, telegram_user_id) VALUES ('Shopping List', %s) RETURNING id",
        (telegram_user_id,)
    )
    conn.commit()
    return cur.fetchone()['id']


class AddItemsRequest(BaseModel):
    items: str  # comma-separated
    telegram_user_id: int = 0


class CheckRequest(BaseModel):
    checked: bool


@router.get("/list")
async def get_list(telegram_user_id: int = 0):
    conn = _get_conn()
    try:
        list_id = _get_active_list_id(conn, telegram_user_id)
        cur = conn.cursor()

        cur.execute("SELECT * FROM grocery_aisles ORDER BY sort_order")
        aisles = cur.fetchall()

        cur.execute("""
            SELECT gi.id, gi.name, gi.quantity, gi.checked, gi.notes,
                   ga.name AS aisle_name, ga.icon AS aisle_icon, ga.sort_order AS aisle_sort
            FROM grocery_items gi
            JOIN grocery_aisles ga ON gi.aisle_id = ga.id
            WHERE gi.list_id = %s
            ORDER BY ga.sort_order, gi.name
        """, (list_id,))
        items = cur.fetchall()

        return {"items": items, "aisles": aisles, "list_id": list_id}
    finally:
        conn.close()


@router.post("/add")
async def add_items(req: AddItemsRequest):
    import re
    conn = _get_conn()
    try:
        list_id = _get_active_list_id(conn, req.telegram_user_id)
        cur = conn.cursor()
        items_raw = [i.strip() for i in req.items.split(',') if i.strip()]
        added = []

        for raw in items_raw:
            qty = '1'
            name = raw
            m = re.match(r'^(\d+)\s*[xX]?\s+(.+)$', raw)
            if m:
                qty = m.group(1)
                name = m.group(2)

            aisle_name = _guess_aisle(name)
            cur.execute("SELECT id FROM grocery_aisles WHERE name = %s", (aisle_name,))
            aisle_row = cur.fetchone()
            aisle_id = aisle_row['id'] if aisle_row else None

            cur.execute(
                "INSERT INTO grocery_items (list_id, aisle_id, name, quantity) VALUES (%s, %s, %s, %s) RETURNING id",
                (list_id, aisle_id, name.strip(), qty)
            )
            row = cur.fetchone()
            added.append({"id": row['id'], "name": name.strip(), "qty": qty, "aisle": aisle_name})

        conn.commit()
        return {"added": added}
    finally:
        conn.close()


@router.post("/check/{item_id}")
async def check_item(item_id: int, req: CheckRequest):
    conn = _get_conn()
    try:
        cur = conn.cursor()
        if req.checked:
            cur.execute(
                "UPDATE grocery_items SET checked = TRUE, checked_at = NOW() WHERE id = %s", (item_id,)
            )
        else:
            cur.execute(
                "UPDATE grocery_items SET checked = FALSE, checked_at = NULL WHERE id = %s", (item_id,)
            )
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


@router.delete("/remove/{item_id}")
async def remove_item(item_id: int):
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM grocery_items WHERE id = %s RETURNING name", (item_id,))
        row = cur.fetchone()
        conn.commit()
        if not row:
            raise HTTPException(status_code=404, detail="Item not found")
        return {"removed": row['name']}
    finally:
        conn.close()


@router.post("/clear")
async def clear_checked(telegram_user_id: int = 0):
    conn = _get_conn()
    try:
        list_id = _get_active_list_id(conn, telegram_user_id)
        cur = conn.cursor()
        cur.execute(
            "DELETE FROM grocery_items WHERE list_id = %s AND checked = TRUE", (list_id,)
        )
        conn.commit()
        return {"ok": True, "cleared": cur.rowcount}
    finally:
        conn.close()


@router.post("/reset")
async def reset_list(telegram_user_id: int = 0):
    conn = _get_conn()
    try:
        list_id = _get_active_list_id(conn, telegram_user_id)
        cur = conn.cursor()
        cur.execute(
            "UPDATE grocery_lists SET is_active = FALSE, completed_at = NOW() WHERE id = %s", (list_id,)
        )
        cur.execute(
            "INSERT INTO grocery_lists (name, telegram_user_id) VALUES ('Shopping List', %s) RETURNING id",
            (telegram_user_id,)
        )
        conn.commit()
        return {"ok": True, "new_list_id": cur.fetchone()['id']}
    finally:
        conn.close()
