"""
Module: integrity/table_scanner.py
Biological System: iris-immune (Immune System — self-knowledge)
Subsystem: mythos-integrity (v0.1.0)
Purpose: Introspect PostgreSQL mythos database — catalog tables, columns,
         foreign keys, and row counts as Neo4j nodes and relationships.
Introduced: Patch 0171
Last Modified: Patch 0171

Dependencies:
  - psycopg2 (PostgreSQL adapter)
  - neo4j (graph database)

Part of: Integrity Scanner
"""

import os
import logging
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor

from integrity.graph import get_driver, run_write, run_query

logger = logging.getLogger("mythos.integrity.table_scanner")


def get_pg_connection():
    """Get a PostgreSQL connection to the mythos database."""
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "mythos"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", ""),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )


def scan_tables(driver=None) -> dict:
    """
    Introspect PostgreSQL and MERGE Table, Column nodes into Neo4j.
    Also creates HAS_COLUMN and REFERENCES relationships.

    Returns:
        dict with scan stats: tables_found, columns_found, fk_relationships
    """
    own_driver = driver is None
    if own_driver:
        driver = get_driver()

    scan_timestamp = datetime.now().isoformat()
    stats = {
        "tables_found": 0,
        "columns_found": 0,
        "fk_relationships": 0,
        "scan_start": scan_timestamp,
    }

    try:
        conn = get_pg_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        # Get all tables in public schema
        cur.execute("""
            SELECT table_name, table_type
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """)
        tables = cur.fetchall()

        for table in tables:
            table_name = table["table_name"]
            full_name = f"mythos.public.{table_name}"

            # Get row count
            try:
                cur.execute(f'SELECT count(*) AS cnt FROM "{table_name}"')
                row_count = cur.fetchone()["cnt"]
            except Exception:
                row_count = -1

            # MERGE table node
            _merge_table(driver, full_name, table_name, row_count, scan_timestamp)
            stats["tables_found"] += 1

            # Get columns
            cur.execute("""
                SELECT column_name, data_type, is_nullable,
                       column_default, character_maximum_length,
                       ordinal_position
                FROM information_schema.columns
                WHERE table_schema = 'public' AND table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            columns = cur.fetchall()

            for col in columns:
                _merge_column(driver, full_name, table_name, col, scan_timestamp)
                stats["columns_found"] += 1

        # Get foreign key relationships
        cur.execute("""
            SELECT
                tc.table_name AS source_table,
                kcu.column_name AS source_column,
                ccu.table_name AS target_table,
                ccu.column_name AS target_column,
                tc.constraint_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
                ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
                ON tc.constraint_name = ccu.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
              AND tc.table_schema = 'public'
        """)
        fks = cur.fetchall()

        for fk in fks:
            _merge_fk_relationship(driver, fk, scan_timestamp)
            stats["fk_relationships"] += 1

        cur.close()
        conn.close()

    except psycopg2.Error as e:
        logger.error(f"PostgreSQL error: {e}")
        stats["error"] = str(e)

    finally:
        if own_driver:
            driver.close()

    stats["scan_end"] = datetime.now().isoformat()
    return stats


def _merge_table(driver, full_name: str, table_name: str,
                 row_count: int, scan_timestamp: str):
    """MERGE a table node."""
    cypher = """
    MERGE (t:IntegrityTable {full_name: $full_name})
    SET t.name = $table_name,
        t.database = 'mythos',
        t.schema = 'public',
        t.row_count = $row_count,
        t.last_scanned = $scan_timestamp
    """
    run_write(driver, cypher, full_name=full_name, table_name=table_name,
              row_count=row_count, scan_timestamp=scan_timestamp)

    # Also create/link Database node
    db_cypher = """
    MERGE (db:IntegrityDatabase {name: 'mythos'})
    SET db.type = 'postgresql', db.host = 'localhost', db.port = 5432
    WITH db
    MATCH (t:IntegrityTable {full_name: $full_name})
    MERGE (db)-[:HAS_TABLE]->(t)
    """
    run_write(driver, db_cypher, full_name=full_name)


def _merge_column(driver, table_full_name: str, table_name: str,
                  col: dict, scan_timestamp: str):
    """MERGE a column node and link to its table."""
    uid = f"{table_full_name}.{col['column_name']}"

    cypher = """
    MERGE (c:IntegrityColumn {uid: $uid})
    SET c.name = $name,
        c.data_type = $data_type,
        c.is_nullable = $is_nullable,
        c.column_default = $column_default,
        c.max_length = $max_length,
        c.ordinal_position = $ordinal_position,
        c.last_scanned = $scan_timestamp
    """
    run_write(driver, cypher, uid=uid, name=col["column_name"],
              data_type=col["data_type"],
              is_nullable=col["is_nullable"] == "YES",
              column_default=col.get("column_default"),
              max_length=col.get("character_maximum_length"),
              ordinal_position=col["ordinal_position"],
              scan_timestamp=scan_timestamp)

    # Link column to table
    link_cypher = """
    MATCH (t:IntegrityTable {full_name: $table_full_name})
    MATCH (c:IntegrityColumn {uid: $uid})
    MERGE (t)-[:HAS_COLUMN]->(c)
    """
    run_write(driver, link_cypher, table_full_name=table_full_name, uid=uid)


def _merge_fk_relationship(driver, fk: dict, scan_timestamp: str):
    """Create a REFERENCES relationship between tables for a foreign key."""
    source_full = f"mythos.public.{fk['source_table']}"
    target_full = f"mythos.public.{fk['target_table']}"

    cypher = """
    MATCH (src:IntegrityTable {full_name: $source})
    MATCH (tgt:IntegrityTable {full_name: $target})
    MERGE (src)-[r:REFERENCES {constraint_name: $constraint}]->(tgt)
    SET r.source_column = $src_col,
        r.target_column = $tgt_col,
        r.last_scanned = $scan_timestamp
    """
    run_write(driver, cypher, source=source_full, target=target_full,
              constraint=fk["constraint_name"],
              src_col=fk["source_column"], tgt_col=fk["target_column"],
              scan_timestamp=scan_timestamp)
