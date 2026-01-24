#!/usr/bin/env python3
"""
Read helper to resolve image paths for clothing/shoes.

Resolution order:
1) asset_rel_path -> /opt/mythos/assets/<asset_rel_path>
2) batch_name + filename -> batch images directory
"""
import os
from pathlib import Path
import psycopg2

MYTHOS_DB = os.environ.get("MYTHOS_DB", "mythos")
ASSETS_ROOT = Path("/opt/mythos/assets")
SALES_ROOT = Path("/opt/mythos/sales_ingestion")
SHOE_ROOT = Path("/opt/mythos/shoe_ingestion")

def _conn():
    return psycopg2.connect(dbname=MYTHOS_DB)

def resolve_clothing_images(item_id: str):
    q = """
    SELECT filename, original_filename, view_type, batch_name, asset_rel_path
    FROM clothing_images
    WHERE item_id = %s
    ORDER BY id ASC
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(q, (item_id,))
            rows = cur.fetchall()
    finally:
        conn.close()

    out = []
    for filename, original_filename, view_type, batch_name, asset_rel_path in rows:
        resolved = None
        if asset_rel_path:
            resolved = str(ASSETS_ROOT / asset_rel_path)
        elif batch_name:
            resolved = str(SALES_ROOT / batch_name / "images" / filename)
        out.append({
            "filename": filename,
            "original_filename": original_filename,
            "view_type": view_type,
            "batch_name": batch_name,
            "asset_rel_path": asset_rel_path,
            "resolved_path": resolved
        })
    return out

def resolve_shoe_images(item_id: str):
    # Assumes shoe_images has item_id column as in your earlier schema
    q = """
    SELECT filename, original_filename, view_type, batch_name, asset_rel_path
    FROM shoe_images
    WHERE item_id = %s
    ORDER BY id ASC
    """
    conn = _conn()
    try:
        with conn.cursor() as cur:
            cur.execute(q, (item_id,))
            rows = cur.fetchall()
    finally:
        conn.close()

    out = []
    for filename, original_filename, view_type, batch_name, asset_rel_path in rows:
        resolved = None
        if asset_rel_path:
            resolved = str(ASSETS_ROOT / asset_rel_path)
        elif batch_name:
            resolved = str(SHOE_ROOT / batch_name / "images" / filename)
        out.append({
            "filename": filename,
            "original_filename": original_filename,
            "view_type": view_type,
            "batch_name": batch_name,
            "asset_rel_path": asset_rel_path,
            "resolved_path": resolved
        })
    return out
