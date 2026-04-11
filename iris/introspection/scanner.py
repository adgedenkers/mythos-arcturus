"""
Scanner - wraps existing integrity file_scanner (patch 0171)
and groups results by component.
"""

import os
import hashlib
import logging
from pathlib import Path
from datetime import datetime, timezone

logger = logging.getLogger("iris.introspection.scanner")

# Component detection: maps directory prefixes to component names
COMPONENT_MAP = {
    "telegram_bot": "telegram_bot",
    "finance": "finance",
    "iris": "iris",
    "skills": "skills",
    "patches": "patches",
    "docs": "docs",
    "command_center": "command_center",
    "genealogy": "genealogy",
    "people": "people",
    "astrology": "astrology",
    "integrity": "integrity",
    "voice": "voice",
    "bin": "bin",
}

SCAN_EXTENSIONS = {
    ".py", ".sql", ".sh", ".yaml", ".yml", ".json", ".md",
    ".toml", ".cfg", ".ini", ".js", ".jsx", ".ts", ".tsx",
    ".html", ".css", ".service",
}

SKIP_DIRS = {
    "__pycache__", ".git", "node_modules", ".venv", "venv",
    ".mypy_cache", ".pytest_cache", "eggs", "*.egg-info",
}


def detect_component(file_path: str, base_path: str = "/opt/mythos") -> str:
    """Determine which component a file belongs to based on its path."""
    rel = os.path.relpath(file_path, base_path)
    parts = Path(rel).parts
    if parts:
        first_dir = parts[0]
        if first_dir in COMPONENT_MAP:
            return COMPONENT_MAP[first_dir]
    return "root"


def file_hash(file_path: str) -> str:
    """SHA-256 content hash for change detection and dedup."""
    h = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
    except (OSError, PermissionError):
        return ""
    return h.hexdigest()


def scan_file(file_path: str, base_path: str = "/opt/mythos") -> dict:
    """Scan a single file and return its metadata dict."""
    stat = os.stat(file_path)
    ext = Path(file_path).suffix
    line_count = 0
    try:
        with open(file_path, "r", errors="replace") as f:
            line_count = sum(1 for _ in f)
    except (OSError, PermissionError):
        pass

    return {
        "file_path": file_path,
        "component": detect_component(file_path, base_path),
        "file_type": ext.lstrip(".") if ext else "unknown",
        "size_bytes": stat.st_size,
        "line_count": line_count,
        "last_modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "content_hash": file_hash(file_path),
    }


def scan_directory(
    base_path: str = "/opt/mythos",
    target_path: str = None,
) -> list[dict]:
    """
    Walk the codebase and return metadata for every scannable file.
    Calls the existing integrity file_scanner first if available,
    then supplements with our own walk.
    """
    scan_root = target_path or base_path
    results = []
    existing_paths = set()

    # Try to use existing integrity scanner from patch 0171
    try:
        from integrity.file_scanner import scan_files as integrity_scan
        logger.info("Using existing integrity file_scanner")
        integrity_results = integrity_scan(scan_root)
        for item in integrity_results:
            # Handle both formats: list of strings or list of dicts
            if isinstance(item, str):
                fp = item
            elif isinstance(item, dict):
                fp = item.get("path") or item.get("file_path", "")
            else:
                continue
            if fp and fp not in existing_paths:
                existing_paths.add(fp)
                meta = scan_file(fp, base_path)
                if isinstance(item, dict):
                    if "functions" in item:
                        meta["functions"] = item["functions"]
                    if "classes" in item:
                        meta["classes"] = item["classes"]
                    if "imports" in item:
                        meta["imports"] = item["imports"]
                results.append(meta)

        # for item in integrity_results:
        #     fp = item.get("path") or item.get("file_path", "")
        #     if fp and fp not in existing_paths:
        #         existing_paths.add(fp)
        #         # Merge integrity data with our format
        #         meta = scan_file(fp, base_path)
        #         # Carry over any extra fields from integrity scanner
        #         if "functions" in item:
        #             meta["functions"] = item["functions"]
        #         if "classes" in item:
        #             meta["classes"] = item["classes"]
        #         if "imports" in item:
        #             meta["imports"] = item["imports"]
        #         results.append(meta)
    except ImportError:
        logger.warning("Integrity file_scanner not importable, using standalone walk")
    except Exception as e:
        logger.warning(f"Integrity scanner error: {e}, falling back to standalone walk")

    # Walk for anything the integrity scanner missed
    for root, dirs, filenames in os.walk(scan_root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for fname in filenames:
            fpath = os.path.join(root, fname)
            if fpath in existing_paths:
                continue
            ext = Path(fname).suffix
            if ext not in SCAN_EXTENSIONS:
                continue
            try:
                results.append(scan_file(fpath, base_path))
                existing_paths.add(fpath)
            except Exception as e:
                logger.warning(f"Error scanning {fpath}: {e}")

    logger.info(f"Scanned {len(results)} files from {scan_root}")
    return results


def group_by_component(file_list: list[dict]) -> dict[str, list[dict]]:
    """Group scanned files by their component."""
    groups = {}
    for f in file_list:
        comp = f.get("component", "root")
        groups.setdefault(comp, []).append(f)
    return groups
