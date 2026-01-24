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
