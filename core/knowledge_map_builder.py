#!/usr/bin/env python3
"""
Knowledge Map Builder
=====================
Rebuilds the dynamic sections of KNOWLEDGE_MAP.md from the database.
Preserves manually-written static sections (People, Locations, Notes).

Triggered by:
- Redis stream message (from pg_notify listener)
- Direct call: python3 knowledge_map_builder.py
- On startup of the listener service

The static header and footer are maintained in a template.
Dynamic sections (bills, accounts, routines) are generated from DB.
"""

import os
import logging
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')

logger = logging.getLogger(__name__)

KNOWLEDGE_MAP_PATH = '/opt/mythos/docs/KNOWLEDGE_MAP.md'


def _get_conn():
    return psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', '/var/run/postgresql'),
        database=os.getenv('POSTGRES_DB', 'mythos'),
        user=os.getenv('POSTGRES_USER', 'postgres'),
        password=os.getenv('POSTGRES_PASSWORD', ''),
        port=os.getenv('POSTGRES_PORT', '5432'),
        cursor_factory=RealDictCursor,
    )


def _build_accounts_section(cur) -> str:
    """Generate accounts section from DB."""
    cur.execute("""
        SELECT account_name, abbreviation, account_type
        FROM accounts
        WHERE is_active = true
        ORDER BY 
            CASE account_type 
                WHEN 'checking' THEN 1 WHEN 'savings' THEN 2 
                WHEN 'credit' THEN 3 WHEN 'loan' THEN 4 
            END, account_name
    """)
    accounts = cur.fetchall()

    lines = ["## Financial Accounts",
             "| Abbreviation | Account Name | Type |",
             "|-------------|-------------|------|"]
    for a in accounts:
        lines.append(f"| {a['abbreviation']} | {a['account_name']} | {a['account_type']} |")

    return "\n".join(lines)


def _build_bills_section(cur) -> str:
    """Generate bills section from DB."""
    cur.execute("""
        SELECT merchant_name, expected_amount, expected_day, 
               category_primary, is_active
        FROM recurring_bills
        WHERE is_active = true
        ORDER BY expected_day NULLS LAST, merchant_name
    """)
    bills = cur.fetchall()

    lines = ["## Bills & Utilities",
             "| Merchant | Expected Amount | Due Day | Category |",
             "|----------|----------------|---------|----------|"]
    for b in bills:
        amt = f"${float(b['expected_amount']):,.0f}" if b['expected_amount'] else "varies"
        day = f"Day {b['expected_day']}" if b['expected_day'] else "as-needed"
        cat = b.get('category_primary', '') or ''
        lines.append(f"| {b['merchant_name']} | {amt} | {day} | {cat} |")

    return "\n".join(lines)


def _build_routines_section(cur) -> str:
    """Generate routines section from DB."""
    cur.execute("""
        SELECT title, frequency, domain, day_of_week, day_of_month
        FROM routines
        WHERE is_active = true
        ORDER BY frequency, sort_order
    """)
    routines = cur.fetchall()

    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    lines = ["## Active Routines",
             "| Routine | Frequency | Domain |",
             "|---------|-----------|--------|"]
    for r in routines:
        freq = r['frequency']
        if freq == 'weekly' and r['day_of_week'] is not None:
            freq = f"weekly ({day_names[r['day_of_week']]})"
        elif freq == 'monthly' and r['day_of_month']:
            freq = f"monthly (day {r['day_of_month']})"
        lines.append(f"| {r['title']} | {freq} | {r['domain']} |")

    return "\n".join(lines)


# Static sections that don't come from the DB
STATIC_HEADER = """# Mythos Knowledge Map
# ====================
# This file is AUTO-GENERATED from the database.
# Static sections (People, Locations, Notes, Data Routing) are preserved.
# Dynamic sections (Accounts, Bills, Routines) are rebuilt on DB changes.
# Last rebuilt: {timestamp}

## People
- **Adge** (also: Ka'tuar'el, Adriaan, me, I) → the user speaking
- **Rebecca** (also: Seraphe, Becky, Lou, she, wife, partner) → wife/partner
- **Fitz** (also: son, kid, boy, little man) → son
"""

STATIC_ROUTING = """
## Data Routing
| Domain | Target | Action |
|--------|--------|--------|
| Bill payment | `bill_overrides` table | INSERT/UPDATE with is_paid=true |
| Money spent / purchase | `life_events` table | Log event, amount, merchant |
| Appointment / event | `calendar_events` table | INSERT new event |
| Task completed | `idea_backlog` table | UPDATE status='done' |
| New task / to-do | `idea_backlog` table | INSERT new task |
| Routine done | `routine_completions` table | UPDATE status='done' |
| Mood / emotional state | `life_events` table | Log with domain='mood' |
| Health update | `life_events` table | Log with domain='health' |
| Fitz/Rebecca update | `life_events` table | Log with person field |
| Financial observation | `life_events` table | Log with domain='finance' |
"""

STATIC_FOOTER = """
## Locations (common)
- Home: Oxford, NY
- VA office: work
- Price Chopper: grocery store
- Tractor Supply: farm/hardware store
- Walmart: general shopping
- Norwich: nearby town (pharmacy, doctor, etc.)

## Notes
- All financial amounts are in USD
- Rebecca handles some bill payments herself (LLBean, TSC logins are hers)
- NBT account is estate money (Jennie Joy Ryan) — temporary, not regular spending
- DVA/Advantage FCU is pass-through only for OneMain loan — excluded from reports
- Propane (Blueox) is as-needed, not monthly
"""


def rebuild_knowledge_map() -> str:
    """
    Rebuild the knowledge map from database + static sections.
    Returns the full document text.
    """
    conn = _get_conn()
    cur = conn.cursor()

    try:
        accounts = _build_accounts_section(cur)
        bills = _build_bills_section(cur)
        routines = _build_routines_section(cur)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        document = STATIC_HEADER.format(timestamp=timestamp)
        document += "\n" + accounts
        document += "\n\n" + bills
        document += "\n\n" + routines
        document += "\n" + STATIC_ROUTING
        document += STATIC_FOOTER

        # Write to disk
        with open(KNOWLEDGE_MAP_PATH, 'w') as f:
            f.write(document)

        logger.info(f"Knowledge map rebuilt at {timestamp}")
        return document

    finally:
        cur.close()
        conn.close()


def listen_and_rebuild():
    """
    Listen for pg_notify signals and rebuild on changes.
    Runs as a long-lived service.
    """
    import select
    import redis as redis_lib

    conn = _get_conn()
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("LISTEN knowledge_map_rebuild;")

    # Also push to Redis so other services know
    try:
        r = redis_lib.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        redis_available = True
    except Exception:
        redis_available = False
        logger.warning("Redis not available for rebuild notifications")

    logger.info("Knowledge map listener started, waiting for changes...")
    print("🗺️  Knowledge map listener active. Waiting for DB changes...")

    # Initial build on startup
    rebuild_knowledge_map()
    print("✓ Initial build complete")

    while True:
        if select.select([conn], [], [], 60) == ([], [], []):
            continue  # Timeout, loop again

        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            print(f"📢 Change detected: {notify.payload}")
            logger.info(f"Rebuild triggered: {notify.payload}")

            rebuild_knowledge_map()
            print("✓ Knowledge map rebuilt")

            # Signal Redis
            if redis_available:
                try:
                    r.publish('mythos:knowledge_map:rebuilt', notify.payload)
                except Exception as e:
                    logger.warning(f"Redis publish failed: {e}")


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'listen':
        listen_and_rebuild()
    else:
        doc = rebuild_knowledge_map()
        print(f"✓ Knowledge map rebuilt ({len(doc)} chars)")
        print(f"  Written to {KNOWLEDGE_MAP_PATH}")
