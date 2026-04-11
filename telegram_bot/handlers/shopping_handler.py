#!/usr/bin/env python3
"""
Mythos Shopping Telegram Handler
/opt/mythos/telegram_bot/handlers/shopping_handler.py

Commands:
    /shop                              - Show usage + stats
    /shop add <item> [--store X]       - Add item to Master List
    /shop add <item> --list <name>     - Add to specific list
    /shop list [name]                  - Show list items
    /shop lists                        - Show all lists
    /shop at <store>                   - KILLER FEATURE: items at store by dept
    /shop done <item>                  - Mark item completed
    /shop store add <name> | <category> | <address>  - Add a store
    /shop stores                       - List stores
    /shop search <keyword>             - Search items
    /shop newlist <name>               - Create new list
"""
import os
import logging
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')
log = logging.getLogger(__name__)


def get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'localhost'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
    )


def _get_master_list_id(cur):
    """Get or create Master List."""
    cur.execute("SELECT id FROM shopping_lists WHERE name = 'Master List' AND is_active LIMIT 1")
    row = cur.fetchone()
    if row:
        return row['id'] if isinstance(row, dict) else row[0]
    cur.execute(
        "INSERT INTO shopping_lists (name, description, source) VALUES ('Master List', 'Default list', 'system') RETURNING id"
    )
    return cur.fetchone()[0]


def handle_shop(text: str) -> str:
    """Handle /shop command. Returns response string."""
    if not text or not text.strip():
        return _show_usage()

    parts = text.strip()
    cmd = parts.split()[0].lower()
    rest = parts[len(cmd):].strip()

    if cmd == 'add':
        return _add_item(rest)
    elif cmd == 'at':
        return _at_store(rest)
    elif cmd == 'done':
        return _done_item(rest)
    elif cmd == 'list':
        return _show_list(rest)
    elif cmd == 'lists':
        return _show_lists()
    elif cmd == 'stores':
        return _show_stores()
    elif cmd == 'store':
        return _store_command(rest)
    elif cmd == 'search':
        return _search_items(rest)
    elif cmd == 'newlist':
        return _new_list(rest)
    elif cmd == 'stats':
        return _show_stats()
    else:
        # Treat bare text as "add"
        return _add_item(parts)


def _show_usage() -> str:
    stats = _show_stats()
    return (
        "🛒 Shopping Lists\n\n"
        "Usage:\n"
        "  /shop add <item>           — add to Master List\n"
        "  /shop add <item> --store X — add + associate with store\n"
        "  /shop at <store>           — items at a store by dept\n"
        "  /shop done <item>          — mark completed\n"
        "  /shop list [name]          — show list items\n"
        "  /shop lists                — all lists\n"
        "  /shop stores               — all stores\n"
        "  /shop store add <name> | <category> | <address>\n"
        "  /shop newlist <name>       — create list\n"
        "  /shop search <keyword>     — search items\n\n"
        f"{stats}"
    )


def _show_stats() -> str:
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT
                (SELECT count(*) FROM stores WHERE is_active) AS stores,
                (SELECT count(*) FROM shopping_items WHERE is_active) AS items,
                (SELECT count(*) FROM shopping_lists WHERE is_active) AS lists,
                (SELECT count(*) FROM shopping_list_items WHERE NOT completed) AS pending
        """)
        r = cur.fetchone()
        return f"📊 {r['stores']} stores · {r['items']} items · {r['lists']} lists · {r['pending']} pending"
    except Exception as e:
        return f"❌ {e}"
    finally:
        conn.close()


def _add_item(text: str) -> str:
    """Add item to a list. Supports --store and --list flags."""
    if not text:
        return "🛒 Usage: /shop add <item> [--store X] [--list Y]"

    # Parse flags
    store_name = None
    list_name = None
    item_text = text

    if '--store' in text:
        parts = text.split('--store')
        item_text = parts[0].strip()
        store_rest = parts[1].strip()
        # Store name might be followed by --list
        if '--list' in store_rest:
            sp = store_rest.split('--list')
            store_name = sp[0].strip()
            list_name = sp[1].strip()
        else:
            store_name = store_rest

    if '--list' in item_text:
        parts = item_text.split('--list')
        item_text = parts[0].strip()
        list_name = parts[1].strip()

    if not item_text:
        return "🛒 Item name required."

    # Parse quantity: "2 gallons milk" → qty=2, unit=gallon, name=milk
    # Simple: just use the whole thing as name for now
    item_name = item_text

    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Find or create item
        cur.execute("SELECT id, name FROM shopping_items WHERE LOWER(name) = LOWER(%s) AND is_active", (item_name,))
        item = cur.fetchone()
        if not item:
            cur.execute(
                "INSERT INTO shopping_items (name) VALUES (%s) RETURNING id, name",
                (item_name,)
            )
            item = cur.fetchone()

        # Find list
        if list_name:
            cur.execute("SELECT id, name FROM shopping_lists WHERE LOWER(name) LIKE LOWER(%s) AND is_active LIMIT 1",
                         (f"%{list_name}%",))
            lst = cur.fetchone()
            if not lst:
                return f"❌ List '{list_name}' not found. Create with /shop newlist {list_name}"
            list_id = lst['id']
            list_display = lst['name']
        else:
            list_id = _get_master_list_id(cur)
            list_display = "Master List"

        # Add to list
        cur.execute("""
            INSERT INTO shopping_list_items (list_id, item_id, added_by)
            VALUES (%s, %s, 'telegram')
            ON CONFLICT (list_id, item_id) DO UPDATE SET completed = FALSE, completed_at = NULL
        """, (list_id, item['id']))

        # Associate with store if specified
        store_info = ""
        if store_name:
            cur.execute("SELECT id, name FROM stores WHERE LOWER(name) LIKE LOWER(%s) AND is_active LIMIT 1",
                         (f"%{store_name}%",))
            store = cur.fetchone()
            if store:
                cur.execute("""
                    INSERT INTO item_stores (item_id, store_id) VALUES (%s, %s)
                    ON CONFLICT (item_id, store_id) DO NOTHING
                """, (item['id'], store['id']))
                store_info = f" → {store['name']}"
            else:
                store_info = f" (store '{store_name}' not found)"

        conn.commit()
        return f"✅ Added: {item['name']} [{list_display}]{store_info}"
    except Exception as e:
        log.error(f"Error adding shopping item: {e}")
        conn.rollback()
        return f"❌ {e}"
    finally:
        conn.close()


def _at_store(store_name: str) -> str:
    """THE KILLER FEATURE: Show items at a specific store, grouped by department."""
    if not store_name:
        return "🛒 Usage: /shop at <store name>"

    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Find store
        cur.execute("SELECT id, name, category FROM stores WHERE LOWER(name) LIKE LOWER(%s) AND is_active LIMIT 1",
                     (f"%{store_name}%",))
        store = cur.fetchone()
        if not store:
            # Show available stores
            cur.execute("SELECT name FROM stores WHERE is_active ORDER BY visit_frequency DESC")
            stores = [r['name'] for r in cur.fetchall()]
            if stores:
                return f"❌ Store '{store_name}' not found.\n\nAvailable:\n" + "\n".join(f"  • {s}" for s in stores)
            return f"❌ No stores yet. Add one with /shop store add <name> | <category>"

        # Get all pending items associated with this store
        cur.execute("""
            SELECT i.name,
                   COALESCE(ist.department_override, i.department, 'General') AS department,
                   COALESCE(li.quantity, i.default_quantity, 1) AS quantity,
                   COALESCE(li.unit_override, i.default_unit, 'each') AS unit,
                   li.priority, li.notes,
                   ist.aisle
            FROM shopping_list_items li
            JOIN shopping_items i ON i.id = li.item_id
            JOIN shopping_lists l ON l.id = li.list_id AND l.is_active = TRUE
            JOIN item_stores ist ON ist.item_id = i.id AND ist.store_id = %s
            WHERE NOT li.completed AND i.is_active = TRUE
            ORDER BY department, li.priority DESC, i.name
        """, (store['id'],))
        items = cur.fetchall()

        # Also get unassociated pending items
        cur.execute("""
            SELECT i.name,
                   COALESCE(i.department, 'Uncategorized') AS department,
                   COALESCE(li.quantity, i.default_quantity, 1) AS quantity,
                   COALESCE(li.unit_override, i.default_unit, 'each') AS unit,
                   li.priority, li.notes,
                   NULL AS aisle
            FROM shopping_list_items li
            JOIN shopping_items i ON i.id = li.item_id
            JOIN shopping_lists l ON l.id = li.list_id AND l.is_active = TRUE
            WHERE NOT li.completed AND i.is_active = TRUE
              AND i.id NOT IN (SELECT item_id FROM item_stores)
            ORDER BY department, i.name
        """)
        unassigned = cur.fetchall()

        all_items = items + unassigned
        if not all_items:
            return f"🛒 {store['name']} — nothing to buy! 🎉"

        # Group by department
        depts = {}
        for item in all_items:
            dept = item['department']
            if dept not in depts:
                depts[dept] = []
            depts[dept].append(item)

        # Format output
        lines = [f"🛒 Shopping at {store['name']} ({len(all_items)} items)\n"]
        for dept in sorted(depts.keys()):
            lines.append(f"\n{dept.upper()}")
            for item in depts[dept]:
                qty = item['quantity']
                unit = item['unit']
                qty_str = f" ({qty} {unit})" if qty and qty != 1 else ""
                priority_icon = "🔴" if item['priority'] == 'urgent' else "🟡" if item['priority'] == 'high' else "☐"
                aisle_str = f" [aisle {item['aisle']}]" if item['aisle'] else ""
                lines.append(f"  {priority_icon} {item['name']}{qty_str}{aisle_str}")

        # Update visit stats
        cur.execute("UPDATE stores SET visit_frequency = visit_frequency + 1, last_visited = NOW() WHERE id = %s",
                     (store['id'],))
        conn.commit()

        return '\n'.join(lines)
    except Exception as e:
        log.error(f"Error showing store items: {e}")
        return f"❌ {e}"
    finally:
        conn.close()


def _done_item(item_name: str) -> str:
    """Mark an item as completed across all active lists."""
    if not item_name:
        return "🛒 Usage: /shop done <item name>"

    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("""
            UPDATE shopping_list_items li SET completed = TRUE, completed_at = NOW()
            FROM shopping_items i, shopping_lists l
            WHERE li.item_id = i.id AND li.list_id = l.id
              AND LOWER(i.name) LIKE LOWER(%s) AND l.is_active = TRUE AND NOT li.completed
        """, (f"%{item_name}%",))
        count = cur.rowcount
        if count == 0:
            return f"❌ No pending item matching '{item_name}'"
        # Update purchase stats
        cur.execute("""
            UPDATE shopping_items SET last_purchased = NOW(), purchase_count = purchase_count + 1
            WHERE LOWER(name) LIKE LOWER(%s) AND is_active
        """, (f"%{item_name}%",))
        conn.commit()
        return f"✅ Done: {item_name} ({count} list{'s' if count > 1 else ''})"
    except Exception as e:
        log.error(f"Error marking done: {e}")
        conn.rollback()
        return f"❌ {e}"
    finally:
        conn.close()


def _show_list(name: str = None) -> str:
    """Show items in a list (default: Master List)."""
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if name:
            cur.execute("SELECT id, name FROM shopping_lists WHERE LOWER(name) LIKE LOWER(%s) AND is_active LIMIT 1",
                         (f"%{name}%",))
        else:
            cur.execute("SELECT id, name FROM shopping_lists WHERE name = 'Master List' AND is_active LIMIT 1")
        lst = cur.fetchone()
        if not lst:
            return "❌ List not found." if name else "❌ Master List not found. Run /shop add to create it."

        cur.execute("""
            SELECT i.name, i.department,
                   COALESCE(li.quantity, i.default_quantity, 1) AS qty,
                   COALESCE(li.unit_override, i.default_unit, '') AS unit,
                   li.priority, li.completed
            FROM shopping_list_items li
            JOIN shopping_items i ON i.id = li.item_id
            WHERE li.list_id = %s
            ORDER BY li.completed, li.priority DESC, i.department, i.name
        """, (lst['id'],))
        items = cur.fetchall()
        if not items:
            return f"🛒 {lst['name']} — empty!\n\nUse /shop add <item> to add items."

        pending = [i for i in items if not i['completed']]
        done = [i for i in items if i['completed']]

        lines = [f"🛒 {lst['name']} ({len(pending)} pending, {len(done)} done)\n"]
        for item in pending:
            qty_str = f" ({item['qty']} {item['unit']})" if item['unit'] else ""
            p = "🔴" if item['priority'] == 'urgent' else "🟡" if item['priority'] == 'high' else "☐"
            lines.append(f"  {p} {item['name']}{qty_str}")
        if done:
            lines.append(f"\n  ─ completed ({len(done)}) ─")
            for item in done[:5]:
                lines.append(f"  ✓ {item['name']}")
            if len(done) > 5:
                lines.append(f"  ... and {len(done) - 5} more")

        return '\n'.join(lines)
    except Exception as e:
        return f"❌ {e}"
    finally:
        conn.close()


def _show_lists() -> str:
    """Show all shopping lists."""
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT l.name, l.status,
                   (SELECT count(*) FROM shopping_list_items li WHERE li.list_id = l.id AND NOT li.completed) AS pending
            FROM shopping_lists l WHERE l.is_active ORDER BY l.created_at DESC
        """)
        rows = cur.fetchall()
        if not rows:
            return "🛒 No lists yet. Create with /shop newlist <name>"
        lines = ["🛒 Shopping Lists\n"]
        for r in rows:
            lines.append(f"  • {r['name']} ({r['pending']} pending)")
        return '\n'.join(lines)
    except Exception as e:
        return f"❌ {e}"
    finally:
        conn.close()


def _show_stores() -> str:
    """Show all stores."""
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT name, category, city, state, visit_frequency
            FROM stores WHERE is_active ORDER BY visit_frequency DESC, name
        """)
        rows = cur.fetchall()
        if not rows:
            return "🏪 No stores yet. Add with /shop store add <name> | <category>"
        lines = ["🏪 Stores\n"]
        for r in rows:
            loc = f" — {r['city']}, {r['state']}" if r['city'] else ""
            visits = f" ({r['visit_frequency']} visits)" if r['visit_frequency'] else ""
            lines.append(f"  • {r['name']} [{r['category']}]{loc}{visits}")
        return '\n'.join(lines)
    except Exception as e:
        return f"❌ {e}"
    finally:
        conn.close()


def _store_command(text: str) -> str:
    """Handle /shop store add ... """
    if not text or not text.strip().lower().startswith('add'):
        return "🏪 Usage: /shop store add <name> | <category> | <address>"
    rest = text.strip()[3:].strip()
    parts = [p.strip() for p in rest.split('|')]
    if not parts or not parts[0]:
        return "🏪 Store name required."
    name = parts[0]
    category = parts[1] if len(parts) > 1 else "grocery"
    address = parts[2] if len(parts) > 2 else ""

    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO stores (name, category, address) VALUES (%s, %s, %s) RETURNING id",
            (name, category, address)
        )
        conn.commit()
        return f"✅ Added store: {name} [{category}]"
    except Exception as e:
        conn.rollback()
        return f"❌ {e}"
    finally:
        conn.close()


def _search_items(query: str) -> str:
    """Search items."""
    if not query:
        return "🛒 Usage: /shop search <keyword>"
    conn = get_conn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("""
            SELECT name, department, purchase_count, last_purchased
            FROM shopping_items WHERE LOWER(name) LIKE LOWER(%s) AND is_active
            ORDER BY purchase_count DESC, name LIMIT 15
        """, (f"%{query}%",))
        rows = cur.fetchall()
        if not rows:
            return f"❌ No items matching '{query}'"
        lines = [f"🔍 Items matching '{query}' ({len(rows)})\n"]
        for r in rows:
            dept = f" [{r['department']}]" if r['department'] else ""
            bought = f" (bought {r['purchase_count']}x)" if r['purchase_count'] else ""
            lines.append(f"  • {r['name']}{dept}{bought}")
        return '\n'.join(lines)
    except Exception as e:
        return f"❌ {e}"
    finally:
        conn.close()


def _new_list(name: str) -> str:
    """Create a new shopping list."""
    if not name:
        return "🛒 Usage: /shop newlist <name>"
    conn = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO shopping_lists (name, source) VALUES (%s, 'telegram') RETURNING id",
            (name,)
        )
        conn.commit()
        return f"✅ Created list: {name}"
    except Exception as e:
        conn.rollback()
        return f"❌ {e}"
    finally:
        conn.close()
