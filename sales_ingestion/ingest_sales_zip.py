#!/usr/bin/env python3
"""
Sales ingestion runner with:
- DB logging + idempotency (from your pipeline)
- JSON clothing ingestion (preferred)
- SQL fallback ingestion (legacy/shoes)
- Asset store integration (new): central dedupe + batch provenance
"""

import os
import json
import subprocess
import logging
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values

from pathlib import Path as _Path
import sys as _sys
_sys.path.append("/opt/mythos/assets")
from asset_store import ensure_asset

LOG_PATH = "/var/log/mythos_patch_monitor.log"
DB_NAME = os.environ.get("MYTHOS_DB", "mythos")






logger = logging.getLogger("MythosSalesIngestor")

# ------------------------------------------------------------
# DB helpers
# ------------------------------------------------------------

def get_conn():
    return psycopg2.connect(dbname=DB_NAME)

def upsert_log(cur, batch_name, artifact_type, status, extract_dir, error=None):
    cur.execute(
        """
        INSERT INTO sales_ingestion_log
            (batch_name, artifact_type, status, extract_dir, error)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (batch_name, artifact_type)
        DO UPDATE SET
            status = EXCLUDED.status,
            error = EXCLUDED.error,
            updated_at = now()
        """,
        (batch_name, artifact_type, status, extract_dir, error),
    )

def get_log_status(cur, batch_name, artifact_type):
    cur.execute(
        """
        SELECT status FROM sales_ingestion_log
        WHERE batch_name = %s AND artifact_type = %s
        """,
        (batch_name, artifact_type),
    )
    row = cur.fetchone()
    return row[0] if row else None

def upsert_media_asset(cur, sha256, file_ext, rel_path, byte_size):
    cur.execute("""
      INSERT INTO media_assets (sha256, file_ext, rel_path, byte_size)
      VALUES (%s, %s, %s, %s)
      ON CONFLICT (sha256) DO NOTHING
    """, (sha256, file_ext, rel_path, byte_size))

# ------------------------------------------------------------
# Ingestion logic
# ------------------------------------------------------------

def run_psql_file(sql_file: Path):
    logger.info(f"Executing SQL file: {sql_file}")
    subprocess.run(
        ["psql", DB_NAME, "-v", "ON_ERROR_STOP=1", "-f", str(sql_file)],
        check=True,
    )

def ingest_items_json(cur, json_path: Path, extract_dir: Path, batch_name: str):
    logger.info(f"Ingesting clothing JSON: {json_path} (batch={batch_name})")

    with open(json_path, "r") as f:
        items = json.load(f)

    images_dir = extract_dir / "images"

    for item in items:
        # Insert item row (idempotent)
        cur.execute(
            """
            INSERT INTO clothing_items (
                id, brand, garment_type, gender_category,
                size_label, standardized_size, condition,
                country_of_manufacture,
                original_retail_price, estimated_resale_price,
                care_instructions, confidence_score,
                inferred_fields, notes
            )
            VALUES (
                %(id)s, %(brand)s, %(garment_type)s, %(gender_category)s,
                %(size_label)s, %(standardized_size)s, %(condition)s,
                %(country_of_manufacture)s,
                %(original_retail_price)s, %(estimated_resale_price)s,
                %(care_instructions)s, %(confidence_score)s,
                %(inferred_fields)s, %(notes)s
            )
            ON CONFLICT (id) DO NOTHING
            """,
            item,
        )

        insert_simple(cur, "clothing_colors", "color", item["id"], item.get("colors", []))
        insert_simple(cur, "clothing_materials", "material", item["id"], item.get("materials", []))
        insert_images_with_assets(cur, item["id"], item.get("images", []), images_dir, batch_name)

def insert_simple(cur, table, column, item_id, values):
    if values:
        execute_values(
            cur,
            f"INSERT INTO {table} (item_id, {column}) VALUES %s",
            [(item_id, v) for v in values],
        )

def insert_shoe_images_with_assets(cur, item_id, images, images_dir: Path, batch_name: str):
    if len(images) != 3:
        raise ValueError("Shoes must have exactly 3 images")

    if not any(img["view_type"] == "box" for img in images):
        raise ValueError("Shoes must include a box image")

    rows = []
    for img in images:
        filename = img["filename"]
        img_path = images_dir / filename

        if not img_path.exists():
            raise FileNotFoundError(str(img_path))

        asset = ensure_asset(img_path)
        upsert_media_asset(
            cur,
            asset["sha256"],
            asset["file_ext"],
            asset["rel_path"],
            asset["byte_size"]
        )

        rows.append((
            item_id,
            filename,
            img.get("original_filename"),
            img.get("view_type"),
            batch_name,
            asset["sha256"],
            asset["rel_path"],
        ))

    execute_values(
        cur,
        """
        INSERT INTO shoe_images
            (item_id, filename, original_filename, view_type, batch_name, asset_sha256, asset_rel_path)
        VALUES %s
        """,
        rows,
    )


def ingest_shoes_json(cur, json_path: Path, extract_dir: Path, batch_name: str):
    logger.info(f"Ingesting shoes JSON: {json_path} (batch={batch_name})")

    with open(json_path, "r") as f:
        items = json.load(f)

    images_dir = extract_dir / "images"

    for item in items:
        # Insert shoe item (idempotent)
        cur.execute(
            """
            INSERT INTO shoes_forsale (
                id,
                brand,
                model,
                gender_category,
                size_label,
                standardized_size,
                condition,
                original_retail_price,
                estimated_resale_price,
                confidence_score,
                inferred_fields,
                notes
            )
            VALUES (
                %(id)s,
                %(brand)s,
                %(model)s,
                %(gender_category)s,
                %(size_label)s,
                %(standardized_size)s,
                %(condition)s,
                %(original_retail_price)s,
                %(estimated_resale_price)s,
                %(confidence_score)s,
                %(inferred_fields)s,
                %(notes)s
            )
            ON CONFLICT (id) DO NOTHING
            """,
            item,
        )

        insert_shoe_images_with_assets(
            cur,
            item["id"],
            item["images"],
            images_dir,
            batch_name
        )
def ingest_shoes_json(cur, json_path: Path, extract_dir: Path, batch_name: str):
    logger.info(f"Ingesting shoes JSON: {json_path} (batch={batch_name})")

    with open(json_path, "r") as f:
        items = json.load(f)

    images_dir = extract_dir / "images"

    for item in items:
        # Insert shoe item (idempotent)
        cur.execute(
            """
            INSERT INTO shoes_forsale (
                id,
                brand,
                model,
                gender_category,
                size_label,
                standardized_size,
                condition,
                original_retail_price,
                estimated_resale_price,
                confidence_score,
                inferred_fields,
                notes
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (id) DO NOTHING
            """,
            (
                item["id"],
                item["brand"],
                item.get("model"),
                item["gender_category"],
                item["size_label"],
                item["standardized_size"],
                item["condition"],
                item.get("original_retail_price"),
                item.get("estimated_resale_price"),
                item.get("confidence_score", 0.0),
                item.get("inferred_fields", []),
                item.get("notes"),
            ),
        )


        insert_shoe_images_with_assets(
            cur,
            item["id"],
            item["images"],
            images_dir,
            batch_name
        )


def insert_images_with_assets(cur, item_id, images, images_dir: Path, batch_name: str):
    if not images:
        return

    rows = []
    for img in images:
        filename = img["filename"]
        img_path = images_dir / filename

        asset_sha = None
        asset_rel = None

        # Assetize if file exists; if not, we still store the row (and can backfill later)
        if img_path.exists():
            asset = ensure_asset(img_path)
            upsert_media_asset(cur, asset["sha256"], asset["file_ext"], asset["rel_path"], asset["byte_size"])
            asset_sha = asset["sha256"]
            asset_rel = asset["rel_path"]

        rows.append((
            item_id,
            filename,
            img.get("original_filename"),
            img.get("view_type"),
            batch_name,
            asset_sha,
            asset_rel,
        ))

    execute_values(
        cur,
        """
        INSERT INTO clothing_images
            (item_id, filename, original_filename, view_type, batch_name, asset_sha256, asset_rel_path)
        VALUES %s
        """,
        rows,
    )

# ------------------------------------------------------------
# Entry point
# ------------------------------------------------------------

def main():
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--type", required=True, choices=["sales", "shoes"])
    ap.add_argument("--extract-dir", required=True)
    args = ap.parse_args()

    extract_dir = Path(args.extract_dir)
    batch_name = extract_dir.name
    artifact_type = args.type

    conn = get_conn()
    conn.autocommit = False

    try:
        with conn.cursor() as cur:
            status = get_log_status(cur, batch_name, artifact_type)

            if status == "success":
                logger.info(f"Skipping already-successful batch: {batch_name}")
                return

            if status == "processing":
                logger.warning(f"Batch already processing, skipping: {batch_name}")
                return

            upsert_log(cur, batch_name, artifact_type, "processing", str(extract_dir))
            conn.commit()

            items_json = extract_dir / "items.json"
            sql_files = list(extract_dir.glob("*.sql"))

            if artifact_type == "sales" and items_json.exists():
                ingest_items_json(cur, items_json, extract_dir, batch_name)

            elif artifact_type == "shoes":
                shoes_json = extract_dir / "shoes.json"
                if shoes_json.exists():
                    ingest_shoes_json(cur, shoes_json, extract_dir, batch_name)
                elif sql_files:
                    logger.warning(
                        f"Shoe batch {batch_name} using legacy SQL ingestion "
                        f"(JSON preferred going forward)"
                    )
                    run_psql_file(sql_files[0])
                else:
                    raise RuntimeError("No shoes.json or SQL found")

            elif sql_files:
                run_psql_file(sql_files[0])


            upsert_log(cur, batch_name, artifact_type, "success", str(extract_dir))
            conn.commit()
            logger.info(f"✓ Ingestion success: {batch_name}")

    except Exception as e:
        conn.rollback()
        with conn.cursor() as cur:
            upsert_log(cur, batch_name, artifact_type, "failed", str(extract_dir), error=str(e))
            conn.commit()
        logger.exception(f"✗ Ingestion failed: {batch_name}")
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    main()