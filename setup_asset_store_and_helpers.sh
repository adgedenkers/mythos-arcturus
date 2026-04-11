#!/usr/bin/env bash
set -euo pipefail

echo "============================================================"
echo "Mythos: Asset Store + Read Helper Setup"
echo "============================================================"

MYTHOS_ROOT="/opt/mythos"
VENV_PY="${MYTHOS_ROOT}/.venv/bin/python"
VENV_PIP="${MYTHOS_ROOT}/.venv/bin/pip"

SALES_DIR="${MYTHOS_ROOT}/sales_ingestion"
SHOE_DIR="${MYTHOS_ROOT}/shoe_ingestion"
ASSETS_DIR="${MYTHOS_ROOT}/assets"
ASSET_IMAGES_DIR="${ASSETS_DIR}/images"

INGESTOR="${SALES_DIR}/ingest_sales_zip.py"
MONITOR_SERVICE="/etc/systemd/system/mythos-patch-monitor.service"
LOG="/var/log/mythos_patch_monitor.log"

: "${MYTHOS_DB:=mythos}"

BACKUP_DIR="${MYTHOS_ROOT}/_upgrade_backups/asset_store_$(date +%Y%m%d_%H%M%S)"
mkdir -p "${BACKUP_DIR}"

echo "[1/8] Preflight..."
test -x "${VENV_PY}" || { echo "❌ Missing venv python: ${VENV_PY}"; exit 1; }
command -v psql >/dev/null || { echo "❌ psql not found"; exit 1; }

echo "[2/8] Backing up current files to ${BACKUP_DIR} ..."
if [[ -f "${INGESTOR}" ]]; then
  cp -a "${INGESTOR}" "${BACKUP_DIR}/ingest_sales_zip.py.bak"
fi

echo "[3/8] Ensuring directories..."
mkdir -p "${ASSET_IMAGES_DIR}"
mkdir -p "${ASSETS_DIR}/bin"
mkdir -p "${SALES_DIR}"
mkdir -p "${SHOE_DIR}"

echo "[4/8] Ensuring Python deps..."
"${VENV_PIP}" install -q --upgrade pip >/dev/null
# psycopg2 is required for DB inserts & helper queries
"${VENV_PIP}" install -q psycopg2-binary >/dev/null

echo "[5/8] Creating DB structures (assets + columns)..."
psql "${MYTHOS_DB}" <<'SQL'
-- Ensure pgcrypto for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Central asset registry
CREATE TABLE IF NOT EXISTS media_assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sha256 TEXT NOT NULL UNIQUE,
    file_ext TEXT,
    rel_path TEXT NOT NULL,
    byte_size BIGINT,
    created_at TIMESTAMP DEFAULT now()
);

-- Clothing images: add batch + asset columns if not present
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema='public' AND table_name='clothing_images'
  ) THEN
    IF NOT EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_schema='public' AND table_name='clothing_images' AND column_name='batch_name'
    ) THEN
      ALTER TABLE clothing_images ADD COLUMN batch_name TEXT;
    END IF;

    IF NOT EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_schema='public' AND table_name='clothing_images' AND column_name='asset_sha256'
    ) THEN
      ALTER TABLE clothing_images ADD COLUMN asset_sha256 TEXT;
    END IF;

    IF NOT EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_schema='public' AND table_name='clothing_images' AND column_name='asset_rel_path'
    ) THEN
      ALTER TABLE clothing_images ADD COLUMN asset_rel_path TEXT;
    END IF;
  END IF;
END $$;

-- Shoe images: add batch + asset columns if shoe_images exists
DO $$
BEGIN
  IF EXISTS (
    SELECT 1 FROM information_schema.tables
    WHERE table_schema='public' AND table_name='shoe_images'
  ) THEN
    IF NOT EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_schema='public' AND table_name='shoe_images' AND column_name='batch_name'
    ) THEN
      ALTER TABLE shoe_images ADD COLUMN batch_name TEXT;
    END IF;

    IF NOT EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_schema='public' AND table_name='shoe_images' AND column_name='asset_sha256'
    ) THEN
      ALTER TABLE shoe_images ADD COLUMN asset_sha256 TEXT;
    END IF;

    IF NOT EXISTS (
      SELECT 1 FROM information_schema.columns
      WHERE table_schema='public' AND table_name='shoe_images' AND column_name='asset_rel_path'
    ) THEN
      ALTER TABLE shoe_images ADD COLUMN asset_rel_path TEXT;
    END IF;
  END IF;
END $$;
SQL

echo "[6/8] Writing asset store module + read helper..."

cat > "${ASSETS_DIR}/asset_store.py" <<'PY'
#!/usr/bin/env python3
import hashlib
import os
import shutil
from pathlib import Path

ASSETS_ROOT = Path("/opt/mythos/assets")
IMAGES_ROOT = ASSETS_ROOT / "images"

def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()

def ensure_asset(image_path: Path) -> dict:
    """
    Copy image into central asset store if not already present.
    Returns: {sha256, rel_path, byte_size, file_ext}
    """
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(str(image_path))

    sha = sha256_file(image_path)
    ext = image_path.suffix.lower().lstrip(".") or None
    shard = sha[:2]
    out_dir = IMAGES_ROOT / shard
    out_dir.mkdir(parents=True, exist_ok=True)

    out_name = f"{sha}.{ext}" if ext else sha
    out_path = out_dir / out_name

    if not out_path.exists():
        # copy2 preserves mtime; fine for provenance
        shutil.copy2(image_path, out_path)

    rel_path = str(out_path.relative_to(ASSETS_ROOT))
    byte_size = out_path.stat().st_size
    return {"sha256": sha, "rel_path": rel_path, "byte_size": byte_size, "file_ext": ext}
PY
chmod +x "${ASSETS_DIR}/asset_store.py"

cat > "${ASSETS_DIR}/read_helper.py" <<'PY'
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
PY
chmod +x "${ASSETS_DIR}/read_helper.py"

cat > "${ASSETS_DIR}/bin/backfill_assets_for_batch.py" <<'PY'
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
PY
chmod +x "${ASSETS_DIR}/bin/backfill_assets_for_batch.py"

echo "[7/8] Updating ingestor to assetize clothing images at ingest-time..."

cat > "${INGESTOR}" <<'PY'
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

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
)
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
            elif sql_files:
                # NOTE: For shoes, SQL remains canonical; assetization will come once shoes are JSON-ingested.
                run_psql_file(sql_files[0])
            else:
                raise RuntimeError("No ingestible artifact found (items.json or *.sql)")

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
PY
chmod +x "${INGESTOR}"

echo "[8/8] Restarting monitor service..."
# Ensure MYTHOS_DB env is set in the service if not already.
if ! grep -q 'Environment="MYTHOS_DB=' "${MONITOR_SERVICE}"; then
  echo "Adding MYTHOS_DB=${MYTHOS_DB} to ${MONITOR_SERVICE} ..."
  sudo bash -c "awk '
    {print}
    \$0 ~ /^Environment=\"PYTHONUNBUFFERED=1\"/ {
      print \"Environment=\\\"MYTHOS_DB=${MYTHOS_DB}\\\"\"
    }
  ' ${MONITOR_SERVICE} > ${MONITOR_SERVICE}.tmp && mv ${MONITOR_SERVICE}.tmp ${MONITOR_SERVICE}"
fi

sudo systemctl daemon-reload
sudo systemctl restart mythos-patch-monitor.service

echo ""
echo "============================================================"
echo "✅ Asset store + helper installed."
echo "Backups: ${BACKUP_DIR}"
echo ""
echo "Asset store root:"
echo "  ${ASSETS_DIR}"
echo ""
echo "Try tailing logs:"
echo "  tail -f ${LOG}"
echo ""
echo "Try resolving clothing item images (example):"
echo "  ${VENV_PY} -c \"import os; os.environ['MYTHOS_DB']='${MYTHOS_DB}'; from pathlib import Path; import sys; sys.path.append('/opt/mythos/assets'); import read_helper; print(read_helper.resolve_clothing_images('<UUID>'))\""
echo ""
echo "Backfill legacy batch assets (optional):"
echo "  MYTHOS_DB=${MYTHOS_DB} ${VENV_PY} /opt/mythos/assets/bin/backfill_assets_for_batch.py --batch-dir /opt/mythos/sales_ingestion/sales-db-ingestion-0001"
echo "============================================================"
