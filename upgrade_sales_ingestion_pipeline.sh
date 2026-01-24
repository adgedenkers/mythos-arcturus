#!/usr/bin/env bash
set -euo pipefail

echo "============================================================"
echo "UPGRADE: Mythos downloads monitor + Sales/Shoe ingestion"
echo "============================================================"

# ---- Settings ----
MYTHOS_ROOT="/opt/mythos"
VENV_PY="${MYTHOS_ROOT}/.venv/bin/python"
MONITOR_PY="${MYTHOS_ROOT}/mythos_patch_monitor.py"
INGESTOR_PY="${MYTHOS_ROOT}/sales_ingestion/ingest_sales_zip.py"
BACKUP_DIR="${MYTHOS_ROOT}/_upgrade_backups/$(date +%Y%m%d_%H%M%S)"

SALES_DIR="${MYTHOS_ROOT}/sales_ingestion"
SHOE_DIR="${MYTHOS_ROOT}/shoe_ingestion"

# Default DB to 'mythos' (matches how you already run psql mythos)
: "${MYTHOS_DB:=mythos}"

# ---- Preflight ----
echo "[1/7] Preflight checks..."
if [[ ! -x "${VENV_PY}" ]]; then
  echo "❌ Missing venv python: ${VENV_PY}"
  exit 1
fi
if [[ ! -f "${MONITOR_PY}" ]]; then
  echo "❌ Missing monitor script: ${MONITOR_PY}"
  exit 1
fi
if ! command -v psql >/dev/null 2>&1; then
  echo "❌ psql not found in PATH"
  exit 1
fi

# ---- Backups ----
echo "[2/7] Backing up current files to ${BACKUP_DIR} ..."
mkdir -p "${BACKUP_DIR}"
cp -a "${MONITOR_PY}" "${BACKUP_DIR}/mythos_patch_monitor.py.bak"
cp -a /etc/systemd/system/mythos-patch-monitor.service "${BACKUP_DIR}/mythos-patch-monitor.service.bak" || true

# ---- Ensure directories ----
echo "[3/7] Ensuring ingestion directories exist..."
mkdir -p "${SALES_DIR}/archive"
mkdir -p "${SHOE_DIR}/archive"

# ---- Install ingestor ----
echo "[4/7] Installing ingestion runner: ${INGESTOR_PY} ..."
cat > "${INGESTOR_PY}" <<'PY'
#!/usr/bin/env python3
"""
Sales/Shoe ingestion runner.

Called by mythos_patch_monitor after staging + extracting zips.

Behavior:
- If an extracted folder contains *.sql (items.sql / shoes.sql), execute it via psql against MYTHOS_DB.
- If SQL is missing, log and leave staged (no destructive behavior).

This intentionally uses the psql CLI (already present) rather than assuming a Python DB driver exists in the venv.
"""

import os
import subprocess
import logging
from pathlib import Path

LOG_PATH = "/var/log/mythos_patch_monitor.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_PATH), logging.StreamHandler()],
)
logger = logging.getLogger("MythosSalesIngestor")

def run_psql_file(sql_file: Path, dbname: str) -> None:
    logger.info(f"Executing SQL file against db '{dbname}': {sql_file}")
    # Use ON_ERROR_STOP so partial failures halt; your SQL can manage transactions if needed.
    cmd = ["psql", dbname, "-v", "ON_ERROR_STOP=1", "-f", str(sql_file)]
    subprocess.run(cmd, check=True)

def find_sql(extract_dir: Path) -> Path | None:
    # Prefer items.sql, then shoes.sql, then any single *.sql
    preferred = ["items.sql", "shoes.sql"]
    for name in preferred:
        p = extract_dir / name
        if p.exists() and p.is_file():
            return p
    sql_files = sorted(extract_dir.glob("*.sql"))
    if len(sql_files) == 1:
        return sql_files[0]
    if len(sql_files) > 1:
        # If multiple, pick the most likely by name
        for cand in sql_files:
            if "item" in cand.name.lower():
                return cand
        return sql_files[0]
    return None

def ingest_extracted_dir(extract_dir: Path, artifact_type: str) -> None:
    dbname = os.environ.get("MYTHOS_DB", "mythos")

    if not extract_dir.exists():
        raise FileNotFoundError(f"Extract dir does not exist: {extract_dir}")

    sql_file = find_sql(extract_dir)
    if not sql_file:
        logger.warning(
            f"No SQL file found in {extract_dir}. "
            f"Artifact staged only (type={artifact_type})."
        )
        return

    try:
        run_psql_file(sql_file, dbname)
        logger.info(f"✓ Ingestion complete for: {extract_dir.name} (type={artifact_type})")
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ SQL ingestion failed for {extract_dir.name}: {e}", exc_info=True)
        raise

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--type", required=True, choices=["sales", "shoes"])
    ap.add_argument("--extract-dir", required=True)
    args = ap.parse_args()

    ingest_extracted_dir(Path(args.extract_dir), args.type)

if __name__ == "__main__":
    main()
PY
chmod +x "${INGESTOR_PY}"

# ---- Upgrade monitor script ----
echo "[5/7] Upgrading ${MONITOR_PY} (adds DB ingestion + shoe support)..."

cat > "${MONITOR_PY}" <<'PY'
#!/usr/bin/env python3
"""
Mythos Downloads Monitor Service

Watches ~/Downloads for known artifact zip files and routes them to
appropriate handlers.

Supported artifacts:
- patch_####_*.zip              → Mythos patch ingestion (existing)
- sales-db-ingestion-####.zip   → Sales DB ingestion (stage + extract + run SQL)
- shoe-db-ingestion-####.zip    → Shoe DB ingestion (stage + extract + run SQL)

Notes:
- Uses /opt/mythos/.venv python
- Executes SQL via the psql CLI through a dedicated runner script:
  /opt/mythos/sales_ingestion/ingest_sales_zip.py
"""

import os
import re
import shutil
import zipfile
import time
import logging
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

WATCH_DIR = Path.home() / "Downloads"

PATCH_DIR = Path("/opt/mythos/patches")
PATCH_ARCHIVE_DIR = PATCH_DIR / "archive"

SALES_DIR = Path("/opt/mythos/sales_ingestion")
SALES_ARCHIVE_DIR = SALES_DIR / "archive"

SHOE_DIR = Path("/opt/mythos/shoe_ingestion")
SHOE_ARCHIVE_DIR = SHOE_DIR / "archive"

INGESTOR = Path("/opt/mythos/sales_ingestion/ingest_sales_zip.py")
VENV_PY = Path("/opt/mythos/.venv/bin/python")

ARTIFACT_PATTERNS = {
    "patch": re.compile(r"^patch_\d{4}_.*\.zip$"),
    "sales_ingestion": re.compile(r"^sales-db-ingestion-\d{4}\.zip$"),
    "shoe_ingestion": re.compile(r"^shoe-db-ingestion-\d{4}\.zip$"),
}

# ------------------------------------------------------------
# Logging
# ------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/var/log/mythos_patch_monitor.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("MythosDownloadsMonitor")

# ------------------------------------------------------------
# Handler
# ------------------------------------------------------------

class DownloadsHandler(FileSystemEventHandler):

    def __init__(self):
        super().__init__()
        self.processing = set()

    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)
        name = path.name

        artifact_type = self._detect_artifact_type(name)
        if not artifact_type:
            return

        logger.info(f"Detected {artifact_type} artifact: {name}")
        # Give browsers/OS time to finish writing the zip
        time.sleep(2)
        self.process_artifact(artifact_type, path)

    def _detect_artifact_type(self, filename):
        for artifact_type, pattern in ARTIFACT_PATTERNS.items():
            if pattern.match(filename):
                return artifact_type
        return None

    def process_artifact(self, artifact_type, path):
        if artifact_type == "patch":
            self.process_patch(path)
        elif artifact_type == "sales_ingestion":
            self.process_sales_ingestion(path)
        elif artifact_type == "shoe_ingestion":
            self.process_shoe_ingestion(path)

    # --------------------------------------------------------
    # Patch handling (existing behavior)
    # --------------------------------------------------------

    def process_patch(self, zip_path):
        name = zip_path.name
        if name in self.processing:
            return

        try:
            self.processing.add(name)

            if not self._is_valid_zip(zip_path):
                logger.error(f"Invalid patch zip: {name}")
                return

            PATCH_DIR.mkdir(parents=True, exist_ok=True)
            PATCH_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

            dest = PATCH_DIR / name
            shutil.copy2(zip_path, dest)

            with zipfile.ZipFile(dest, "r") as z:
                z.extractall(PATCH_DIR)

            shutil.move(dest, PATCH_ARCHIVE_DIR / name)
            zip_path.unlink()

            logger.info(f"✓ Patch processed: {name}")

        except Exception as e:
            logger.error(f"Patch error {name}: {e}", exc_info=True)
        finally:
            self.processing.discard(name)

    # --------------------------------------------------------
    # Sales ingestion handling
    # --------------------------------------------------------

    def process_sales_ingestion(self, zip_path):
        self._process_ingestion_zip(
            zip_path=zip_path,
            root_dir=SALES_DIR,
            archive_dir=SALES_ARCHIVE_DIR,
            ingestor_type="sales"
        )

    # --------------------------------------------------------
    # Shoe ingestion handling
    # --------------------------------------------------------

    def process_shoe_ingestion(self, zip_path):
        self._process_ingestion_zip(
            zip_path=zip_path,
            root_dir=SHOE_DIR,
            archive_dir=SHOE_ARCHIVE_DIR,
            ingestor_type="shoes"
        )

    # --------------------------------------------------------
    # Shared ingestion flow
    # --------------------------------------------------------

    def _process_ingestion_zip(self, zip_path: Path, root_dir: Path, archive_dir: Path, ingestor_type: str):
        name = zip_path.name
        if name in self.processing:
            return

        try:
            self.processing.add(name)

            if not self._is_valid_zip(zip_path):
                logger.error(f"Invalid {ingestor_type} ingestion zip: {name}")
                return

            root_dir.mkdir(parents=True, exist_ok=True)
            archive_dir.mkdir(parents=True, exist_ok=True)

            dest = root_dir / name
            shutil.copy2(zip_path, dest)

            extract_dir = root_dir / name.replace(".zip", "")
            extract_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(dest, "r") as z:
                z.extractall(extract_dir)

            # Archive the staged zip and remove the original download
            shutil.move(dest, archive_dir / name)
            zip_path.unlink()

            logger.info(f"✓ {ingestor_type} ingestion staged: {name} -> {extract_dir}")

            # Now run DB ingestion (SQL execution) via ingestor
            if not INGESTOR.exists():
                logger.error(f"Ingestor missing: {INGESTOR}. Staged only.")
                return
            if not VENV_PY.exists():
                logger.error(f"Venv python missing: {VENV_PY}. Staged only.")
                return

            env = os.environ.copy()
            # Default to mythos; allow override in service Environment or shell env
            env.setdefault("MYTHOS_DB", "mythos")

            cmd = [str(VENV_PY), str(INGESTOR), "--type", ingestor_type, "--extract-dir", str(extract_dir)]
            logger.info(f"Running ingestor: {' '.join(cmd)} (MYTHOS_DB={env.get('MYTHOS_DB')})")
            subprocess.run(cmd, check=True, env=env)

        except subprocess.CalledProcessError as e:
            logger.error(f"{ingestor_type} ingestion failed for {name}: {e}", exc_info=True)
        except Exception as e:
            logger.error(f"{ingestor_type} ingestion error {name}: {e}", exc_info=True)
        finally:
            self.processing.discard(name)

    # --------------------------------------------------------

    def _is_valid_zip(self, path):
        try:
            with zipfile.ZipFile(path, "r") as z:
                return z.testzip() is None
        except Exception:
            return False


# ------------------------------------------------------------
# Main loop
# ------------------------------------------------------------

def main():
    logger.info("=" * 60)
    logger.info("Mythos Downloads Monitor Service Starting")
    logger.info(f"Watching: {WATCH_DIR}")

    for k, v in ARTIFACT_PATTERNS.items():
        logger.info(f"Artifact type '{k}': {v.pattern}")

    logger.info("=" * 60)

    handler = DownloadsHandler()
    observer = Observer()
    observer.schedule(handler, str(WATCH_DIR), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()
PY
chmod +x "${MONITOR_PY}"

# ---- Systemd: add MYTHOS_DB env (optional but nice) ----
echo "[6/7] Updating systemd service env (adds MYTHOS_DB=${MYTHOS_DB})..."
# Keep your service structure, just ensure MYTHOS_DB is available.
# If it's already present, we won't duplicate.
if ! grep -q 'Environment="MYTHOS_DB=' /etc/systemd/system/mythos-patch-monitor.service; then
  sudo bash -c "awk '
    {print}
    \$0 ~ /^Environment=\"PYTHONUNBUFFERED=1\"/ {
      print \"Environment=\\\"MYTHOS_DB=${MYTHOS_DB}\\\"\"
    }
  ' /etc/systemd/system/mythos-patch-monitor.service > /etc/systemd/system/mythos-patch-monitor.service.tmp && mv /etc/systemd/system/mythos-patch-monitor.service.tmp /etc/systemd/system/mythos-patch-monitor.service"
else
  echo "Service already defines MYTHOS_DB; leaving as-is."
fi

# ---- Restart service ----
echo "[7/7] Reloading systemd + restarting mythos-patch-monitor..."
sudo systemctl daemon-reload
sudo systemctl restart mythos-patch-monitor.service

echo ""
echo "============================================================"
echo "✅ Upgrade complete."
echo "Backups stored at: ${BACKUP_DIR}"
echo "Service restarted: mythos-patch-monitor.service"
echo ""
echo "Tip: watch logs with:"
echo "  tail -f /var/log/mythos_patch_monitor.log"
echo "============================================================"
