#!/usr/bin/env python3
"""
Mythos Downloads Monitor Service

Watches ~/Downloads for known artifact zip files and routes them to
appropriate handlers.

Supported artifacts:
- patch_####_*.zip              → Mythos patch ingestion
- sales-db-ingestion-####.zip   → Sales database ingestion
"""

import os
import re
import shutil
import zipfile
import time
import logging
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

ARTIFACT_PATTERNS = {
    "patch": re.compile(r"^patch_\d{4}_.*\.zip$"),
    "sales_ingestion": re.compile(r"^sales-db-ingestion-\d{4}\.zip$"),
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
    # Sales ingestion handling (new)
    # --------------------------------------------------------

    def process_sales_ingestion(self, zip_path):
        name = zip_path.name
        if name in self.processing:
            return

        try:
            self.processing.add(name)

            if not self._is_valid_zip(zip_path):
                logger.error(f"Invalid sales ingestion zip: {name}")
                return

            SALES_DIR.mkdir(parents=True, exist_ok=True)
            SALES_ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

            dest = SALES_DIR / name
            shutil.copy2(zip_path, dest)

            extract_dir = SALES_DIR / name.replace(".zip", "")
            extract_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(dest, "r") as z:
                z.extractall(extract_dir)

            shutil.move(dest, SALES_ARCHIVE_DIR / name)
            zip_path.unlink()

            logger.info(f"✓ Sales ingestion staged: {name}")

        except Exception as e:
            logger.error(f"Sales ingestion error {name}: {e}", exc_info=True)
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
    logger.info("Mythos Downloads Monitor Service stopped")


if __name__ == "__main__":
    main()
