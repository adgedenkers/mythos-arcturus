"""
Module: integrity/file_scanner.py
Biological System: iris-immune (Immune System — self-knowledge)
Subsystem: mythos-integrity (v0.1.0)
Purpose: Walk /opt/mythos/ tree, compute SHA-256 hashes, MERGE File and
         Directory nodes into Neo4j. Detect orphan files (on disk but not
         in graph) and ghost nodes (in graph but not on disk).
Introduced: Patch 0171
Last Modified: Patch 0171

Dependencies:
  - neo4j (graph database)
  - hashlib (SHA-256 hashing)

Part of: Integrity Scanner
"""

import os
import hashlib
import logging
from datetime import datetime
from pathlib import Path

from integrity.graph import get_driver, run_write, run_query

logger = logging.getLogger("mythos.integrity.file_scanner")

# Directories to skip during scan
SKIP_DIRS = {
    ".git", "__pycache__", ".venv", "node_modules",
    ".mypy_cache", ".pytest_cache", "venv", ".tox",
    "patches",  # patches dir is huge and managed separately
    "data",     # binary data (redis dumps, etc.) — not code
}

# Specific files to skip (permission issues, binary blobs, etc.)
SKIP_FILES = {
    "dump.rdb",
}

# File extensions to skip (binary blobs, media, etc.)
SKIP_EXTENSIONS = {
    ".pyc", ".pyo", ".so", ".o", ".a",
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".ico", ".svg",
    ".mp3", ".mp4", ".wav", ".m4a", ".ogg", ".flac",
    ".zip", ".tar", ".gz", ".bz2", ".xz", ".7z",
    ".whl", ".egg",
    ".ttf", ".otf", ".woff", ".woff2",
    ".sqlite", ".db",
}

MYTHOS_ROOT = os.getenv("MYTHOS_ROOT", "/opt/mythos")


def compute_sha256(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, PermissionError) as e:
        logger.warning(f"Cannot hash {filepath}: {e}")
        return ""


def should_skip_dir(dirname: str) -> bool:
    """Check if a directory should be skipped."""
    return dirname in SKIP_DIRS or dirname.startswith(".")


def should_skip_file(filename: str) -> bool:
    """Check if a file should be skipped based on extension or name."""
    if filename in SKIP_FILES:
        return True
    _, ext = os.path.splitext(filename)
    return ext.lower() in SKIP_EXTENSIONS


def scan_files(root: str = None, driver=None) -> dict:
    """
    Walk the Mythos directory tree and MERGE File/Directory nodes into Neo4j.

    Returns:
        dict with scan statistics: files_scanned, dirs_scanned,
        files_new, files_updated, files_unchanged, files_missing
    """
    root = root or MYTHOS_ROOT
    own_driver = driver is None
    if own_driver:
        driver = get_driver()

    scan_start = datetime.now().isoformat()
    stats = {
        "files_scanned": 0,
        "dirs_scanned": 0,
        "files_new": 0,
        "files_updated": 0,
        "files_unchanged": 0,
        "files_missing": 0,
        "scan_start": scan_start,
        "errors": [],
    }

    disk_paths = set()

    try:
        for dirpath, dirnames, filenames in os.walk(root):
            # Filter out skip dirs in-place (prevents os.walk from descending)
            dirnames[:] = [d for d in dirnames if not should_skip_dir(d)]

            rel_dir = os.path.relpath(dirpath, root)
            abs_dir = os.path.abspath(dirpath)

            # MERGE directory node
            _merge_directory(driver, abs_dir, rel_dir, scan_start)
            stats["dirs_scanned"] += 1

            # Create parent relationship
            parent_dir = os.path.dirname(abs_dir)
            if parent_dir != abs_dir and parent_dir.startswith(root):
                _link_directory_parent(driver, abs_dir, parent_dir)

            for filename in filenames:
                if should_skip_file(filename):
                    continue

                filepath = os.path.join(dirpath, filename)
                abs_path = os.path.abspath(filepath)
                disk_paths.add(abs_path)

                try:
                    stat = os.stat(filepath)
                    file_hash = compute_sha256(filepath)
                    _, ext = os.path.splitext(filename)

                    result = _merge_file(
                        driver,
                        path=abs_path,
                        filename=filename,
                        extension=ext.lower(),
                        directory=abs_dir,
                        sha256=file_hash,
                        size_bytes=stat.st_size,
                        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        scan_timestamp=scan_start,
                    )

                    stats["files_scanned"] += 1
                    if result == "new":
                        stats["files_new"] += 1
                    elif result == "updated":
                        stats["files_updated"] += 1
                    else:
                        stats["files_unchanged"] += 1

                except (OSError, PermissionError) as e:
                    logger.warning(f"Cannot scan {filepath}: {e}")
                    stats["errors"].append(str(e))

        # Mark files that are in graph but not on disk as "missing"
        stats["files_missing"] = _mark_missing_files(driver, disk_paths, scan_start, root)

    finally:
        if own_driver:
            driver.close()

    stats["scan_end"] = datetime.now().isoformat()
    return stats


def _merge_directory(driver, abs_path: str, rel_path: str, scan_timestamp: str):
    """MERGE a directory node."""
    cypher = """
    MERGE (d:IntegrityDirectory {path: $path})
    SET d.rel_path = $rel_path,
        d.last_scanned = $scan_timestamp
    """
    run_write(driver, cypher, path=abs_path, rel_path=rel_path,
              scan_timestamp=scan_timestamp)


def _link_directory_parent(driver, child_path: str, parent_path: str):
    """Create CHILD_OF relationship between directories."""
    cypher = """
    MATCH (child:IntegrityDirectory {path: $child_path})
    MATCH (parent:IntegrityDirectory {path: $parent_path})
    MERGE (child)-[:CHILD_OF]->(parent)
    """
    run_write(driver, cypher, child_path=child_path, parent_path=parent_path)


def _merge_file(driver, path: str, filename: str, extension: str,
                directory: str, sha256: str, size_bytes: int,
                last_modified: str, scan_timestamp: str) -> str:
    """
    MERGE a file node. Returns 'new', 'updated', or 'unchanged'.
    """
    # Check if file exists and if hash changed
    cypher_check = """
    MATCH (f:IntegrityFile {path: $path})
    RETURN f.sha256 AS old_hash, f.status AS old_status
    """
    existing = run_query(driver, cypher_check, path=path)

    if not existing:
        # New file
        cypher = """
        CREATE (f:IntegrityFile {
            path: $path,
            filename: $filename,
            extension: $extension,
            directory: $directory,
            sha256: $sha256,
            size_bytes: $size_bytes,
            last_modified: $last_modified,
            last_scanned: $scan_timestamp,
            status: 'active'
        })
        """
        run_write(driver, cypher, path=path, filename=filename,
                  extension=extension, directory=directory, sha256=sha256,
                  size_bytes=size_bytes, last_modified=last_modified,
                  scan_timestamp=scan_timestamp)

        # Link to directory
        _link_file_to_directory(driver, path, directory)
        return "new"

    old_hash = existing[0].get("old_hash", "")

    if old_hash != sha256:
        # File changed
        cypher = """
        MATCH (f:IntegrityFile {path: $path})
        SET f.sha256 = $sha256,
            f.size_bytes = $size_bytes,
            f.last_modified = $last_modified,
            f.last_scanned = $scan_timestamp,
            f.previous_hash = f.sha256,
            f.hash_changed = true,
            f.status = 'active'
        """
        run_write(driver, cypher, path=path, sha256=sha256,
                  size_bytes=size_bytes, last_modified=last_modified,
                  scan_timestamp=scan_timestamp)
        return "updated"

    else:
        # Unchanged — just update scan timestamp
        cypher = """
        MATCH (f:IntegrityFile {path: $path})
        SET f.last_scanned = $scan_timestamp,
            f.hash_changed = false,
            f.status = 'active'
        """
        run_write(driver, cypher, path=path, scan_timestamp=scan_timestamp)
        return "unchanged"


def _link_file_to_directory(driver, file_path: str, dir_path: str):
    """Create IN_DIRECTORY relationship."""
    cypher = """
    MATCH (f:IntegrityFile {path: $file_path})
    MATCH (d:IntegrityDirectory {path: $dir_path})
    MERGE (f)-[:IN_DIRECTORY]->(d)
    """
    run_write(driver, cypher, file_path=file_path, dir_path=dir_path)


def _mark_missing_files(driver, disk_paths: set, scan_timestamp: str, root: str) -> int:
    """
    Find IntegrityFile nodes whose path starts with root but weren't found
    on disk. Mark them as 'missing'. Returns count of missing files.
    """
    cypher = """
    MATCH (f:IntegrityFile)
    WHERE f.path STARTS WITH $root
      AND f.last_scanned < $scan_timestamp
      AND f.status = 'active'
    SET f.status = 'missing'
    RETURN count(f) AS missing_count
    """
    result = run_query(driver, cypher, root=root, scan_timestamp=scan_timestamp)
    return result[0]["missing_count"] if result else 0
