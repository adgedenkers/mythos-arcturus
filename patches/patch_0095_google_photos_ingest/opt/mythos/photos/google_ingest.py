#!/usr/bin/env python3
"""
Google Photos Takeout Ingestion Pipeline
Patch 0095 - Mythos Photo System

Usage:
    python3 google_ingest.py --zips /path/to/takeout/zips
    python3 google_ingest.py --zips /path/to/takeout/zips --dry-run
    python3 google_ingest.py --already-extracted  # if you already unzipped manually

What this does:
    1. Extracts all Takeout zip files
    2. Reads Google's JSON sidecar files to recover real timestamps
    3. Writes correct timestamps back into EXIF data
    4. Deduplicates against existing Immich library
    5. Copies clean files to Immich import watch folder
"""

import os
import sys
import json
import shutil
import hashlib
import zipfile
import argparse
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# ── Configuration ─────────────────────────────────────────────────────────────
EXTRACT_DIR   = Path("/opt/photos/import/google/extracted")
STAGING_DIR   = Path("/opt/photos/import/google/staging")
IMPORT_DIR    = Path("/opt/photos/import/google/ready")   # Immich watches this
LIBRARY_DIR   = Path("/opt/photos/library")
LOG_FILE      = Path("/opt/photos/import/google/ingest.log")

SUPPORTED_EXTENSIONS = {
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".heif",
    ".mp4", ".mov", ".avi", ".mkv", ".m4v", ".3gp"
}

# ── Logging ───────────────────────────────────────────────────────────────────
def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] [{level}] {msg}"
    print(line)
    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

# ── Hashing for deduplication ─────────────────────────────────────────────────
def file_hash(path, chunk_size=65536):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()

def build_library_hash_set():
    """Build a set of SHA256 hashes of all files already in the Immich library."""
    log("Building hash index of existing library (this may take a moment)...")
    hashes = set()
    count = 0
    for p in LIBRARY_DIR.rglob("*"):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS:
            try:
                hashes.add(file_hash(p))
                count += 1
            except Exception as e:
                log(f"Could not hash {p}: {e}", "WARN")
    log(f"Library index built: {count} existing files hashed")
    return hashes

# ── Zip extraction ────────────────────────────────────────────────────────────
def extract_zips(zip_dir: Path):
    zips = list(zip_dir.glob("*.zip"))
    if not zips:
        log(f"No zip files found in {zip_dir}", "WARN")
        return

    log(f"Found {len(zips)} zip file(s) to extract")
    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)

    for z in sorted(zips):
        log(f"Extracting {z.name}...")
        try:
            with zipfile.ZipFile(z, "r") as zf:
                zf.extractall(EXTRACT_DIR)
            log(f"  ✓ {z.name} extracted")
        except Exception as e:
            log(f"  ✗ Failed to extract {z.name}: {e}", "ERROR")

# ── JSON sidecar parsing ──────────────────────────────────────────────────────
def find_sidecar(photo_path: Path) -> Path | None:
    """
    Google creates JSON sidecars with naming patterns like:
      photo.jpg.json
      photo.json
      photo(1).jpg.json  (for duplicates)
    """
    candidates = [
        photo_path.parent / (photo_path.name + ".json"),
        photo_path.parent / (photo_path.stem + ".json"),
        photo_path.parent / (photo_path.stem + ".jpg.json"),
    ]
    for c in candidates:
        if c.exists():
            return c
    return None

def get_timestamp_from_sidecar(sidecar_path: Path) -> datetime | None:
    try:
        with open(sidecar_path) as f:
            data = json.load(f)

        # Google stores epoch seconds as a string in photoTakenTime
        if "photoTakenTime" in data:
            ts = int(data["photoTakenTime"]["timestamp"])
            return datetime.fromtimestamp(ts, tz=timezone.utc)

        if "creationTime" in data:
            ts = int(data["creationTime"]["timestamp"])
            return datetime.fromtimestamp(ts, tz=timezone.utc)

    except Exception as e:
        log(f"  Could not parse sidecar {sidecar_path}: {e}", "WARN")
    return None

# ── EXIF timestamp correction ─────────────────────────────────────────────────
def fix_exif_timestamp(photo_path: Path, dt: datetime, dry_run=False):
    """Use exiftool to write the correct timestamp into EXIF."""
    ts_str = dt.strftime("%Y:%m:%d %H:%M:%S")
    cmd = [
        "exiftool",
        "-overwrite_original",
        f"-DateTimeOriginal={ts_str}",
        f"-CreateDate={ts_str}",
        f"-ModifyDate={ts_str}",
        str(photo_path)
    ]
    if dry_run:
        return True
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        log(f"  exiftool failed on {photo_path.name}: {e}", "WARN")
        return False

# ── Main ingestion ────────────────────────────────────────────────────────────
def ingest(zip_dir: Path = None, already_extracted: bool = False, dry_run: bool = False):
    log("=" * 60)
    log("Google Photos Takeout Ingestion Pipeline - Patch 0095")
    log(f"Dry run: {dry_run}")
    log("=" * 60)

    # Check exiftool is available
    if shutil.which("exiftool") is None:
        log("exiftool not found. Install with: sudo apt install exiftool", "ERROR")
        log("Timestamp correction will be skipped — files will still be imported", "WARN")
        has_exiftool = False
    else:
        has_exiftool = True
        log("✓ exiftool found")

    # Step 1: Extract zips
    if not already_extracted and zip_dir:
        extract_zips(zip_dir)
    elif already_extracted:
        log("Skipping extraction — using already-extracted files in " + str(EXTRACT_DIR))

    # Step 2: Build library hash set for deduplication
    existing_hashes = build_library_hash_set()

    # Step 3: Find all photos in extracted dir
    source_dir = EXTRACT_DIR if not already_extracted or EXTRACT_DIR.exists() else zip_dir
    all_photos = [
        p for p in source_dir.rglob("*")
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    log(f"Found {len(all_photos)} media files to process")

    IMPORT_DIR.mkdir(parents=True, exist_ok=True)
    STAGING_DIR.mkdir(parents=True, exist_ok=True)

    stats = {
        "total": len(all_photos),
        "duplicates_skipped": 0,
        "timestamp_fixed": 0,
        "timestamp_skipped": 0,
        "imported": 0,
        "errors": 0,
    }

    for i, photo in enumerate(all_photos, 1):
        if i % 100 == 0:
            log(f"Progress: {i}/{stats['total']} | imported: {stats['imported']} | dupes: {stats['duplicates_skipped']}")

        try:
            # Deduplication check
            h = file_hash(photo)
            if h in existing_hashes:
                stats["duplicates_skipped"] += 1
                continue

            # Find and apply sidecar timestamp
            sidecar = find_sidecar(photo)
            if sidecar and has_exiftool:
                dt = get_timestamp_from_sidecar(sidecar)
                if dt:
                    if not dry_run:
                        # Work on a copy in staging
                        dest_stage = STAGING_DIR / photo.name
                        shutil.copy2(photo, dest_stage)
                        fix_exif_timestamp(dest_stage, dt, dry_run)
                        shutil.move(str(dest_stage), IMPORT_DIR / photo.name)
                    stats["timestamp_fixed"] += 1
                else:
                    if not dry_run:
                        shutil.copy2(photo, IMPORT_DIR / photo.name)
                    stats["timestamp_skipped"] += 1
            else:
                if not dry_run:
                    shutil.copy2(photo, IMPORT_DIR / photo.name)
                stats["timestamp_skipped"] += 1

            existing_hashes.add(h)  # Don't import the same file twice even within this run
            stats["imported"] += 1

        except Exception as e:
            log(f"Error processing {photo.name}: {e}", "ERROR")
            stats["errors"] += 1

    # Summary
    log("=" * 60)
    log("INGESTION COMPLETE")
    log(f"  Total files found:      {stats['total']}")
    log(f"  Imported to Immich:     {stats['imported']}")
    log(f"  Duplicates skipped:     {stats['duplicates_skipped']}")
    log(f"  Timestamps corrected:   {stats['timestamp_fixed']}")
    log(f"  Timestamps not found:   {stats['timestamp_skipped']}")
    log(f"  Errors:                 {stats['errors']}")
    log("=" * 60)

    if not dry_run and stats["imported"] > 0:
        log(f"Files are ready in {IMPORT_DIR}")
        log("Add this folder as an External Library in Immich:")
        log("  Administration → Libraries → Create External Library")
        log(f"  Path: {IMPORT_DIR}")

# ── CLI ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Photos Takeout Ingestion Pipeline")
    parser.add_argument("--zips", type=Path, help="Directory containing Google Takeout zip files")
    parser.add_argument("--already-extracted", action="store_true",
                        help="Skip extraction, process already-extracted files")
    parser.add_argument("--dry-run", action="store_true",
                        help="Analyze only, don't copy any files")
    args = parser.parse_args()

    if not args.zips and not args.already_extracted:
        parser.print_help()
        sys.exit(1)

    ingest(
        zip_dir=args.zips,
        already_extracted=args.already_extracted,
        dry_run=args.dry_run
    )
