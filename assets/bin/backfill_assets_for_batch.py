#!/usr/bin/env python3
"""
Backfill asset fields for a single clothing batch directory that contains items.json + images/.

This is for legacy ingestions where clothing_images rows exist but asset columns are empty.
Matches rows by (item_id, filename) and sets:
- batch_name
- asset_sha256
- asset_rel_path
Also upserts media_assets.
"""
import sys
sys.path.append("/opt/mythos/assets")

import os, json
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values

from asset_store import ensure_asset

MYTHOS_DB = os.environ.get("MYTHOS_DB", "mythos")
ASSETS_ROOT = Path("/opt/mythos/assets")

def conn():
    return psycopg2.connect(dbname=MYTHOS_DB)

def upsert_media_asset(cur, sha256, file_ext, rel_path, byte_size):
    cur.execute("""
      INSERT INTO media_assets (sha256, file_ext, rel_path, byte_size)
      VALUES (%s, %s, %s, %s)
      ON CONFLICT (sha256) DO NOTHING
    """, (sha256, file_ext, rel_path, byte_size))

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch-dir", required=True, help="e.g. /opt/mythos/sales_ingestion/sales-db-ingestion-0001")
    args = ap.parse_args()

    batch_dir = Path(args.batch_dir)
    batch_name = batch_dir.name
    items_json = batch_dir / "items.json"
    images_dir = batch_dir / "images"

    if not items_json.exists():
        raise FileNotFoundError(str(items_json))
    if not images_dir.exists():
        raise FileNotFoundError(str(images_dir))

    items = json.loads(items_json.read_text())

    c = conn()
    c.autocommit = False
    try:
        with c.cursor() as cur:
            for item in items:
                item_id = item["id"]
                for img in item.get("images", []):
                    filename = img["filename"]
                    img_path = images_dir / filename
                    if not img_path.exists():
                        # Some batches may not include images/ but nested; keep honest
                        continue

                    asset = ensure_asset(img_path)
                    upsert_media_asset(cur, asset["sha256"], asset["file_ext"], asset["rel_path"], asset["byte_size"])

                    cur.execute("""
                      UPDATE clothing_images
                      SET batch_name = %s,
                          asset_sha256 = %s,
                          asset_rel_path = %s
                      WHERE item_id = %s AND filename = %s
                    """, (batch_name, asset["sha256"], asset["rel_path"], item_id, filename))

        c.commit()
        print(f"✓ Backfill complete for {batch_name}")
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()

if __name__ == "__main__":
    main()
