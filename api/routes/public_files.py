"""
Public File Server - directory listing API
Provides JSON directory listings for the Command Center file browser.
The actual file serving is handled by FastAPI StaticFiles mount.
"""
from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import Optional
import os
import time

router = APIRouter(prefix="/api/public", tags=["public"])

PUBLIC_ROOT = Path("/opt/mythos/public")


@router.get("/ls")
async def list_directory(path: str = ""):
    """List files and directories under /opt/mythos/public/"""
    target = (PUBLIC_ROOT / path)

    # Security: prevent traversal outside public root
    if not str(target.resolve()).startswith("/opt/mythos"):
        raise HTTPException(status_code=403, detail="Access denied")

    if not target.exists():
        raise HTTPException(status_code=404, detail="Path not found")

    if not target.is_dir():
        raise HTTPException(status_code=400, detail="Not a directory")

    items = []
    for entry in sorted(target.iterdir()):
        stat = entry.stat()
        rel = str(entry.relative_to(PUBLIC_ROOT))
        item = {
            "name": entry.name,
            "path": rel,
            "type": "dir" if entry.is_dir() else "file",
            "size": stat.st_size if entry.is_file() else None,
            "modified": stat.st_mtime,
        }
        if entry.is_file():
            ext = entry.suffix.lower()
            item["url"] = f"/public/{rel}"
            item["ext"] = ext
        items.append(item)

    return {
        "path": path or "/",
        "items": items,
        "count": len(items),
    }


@router.get("/tree")
async def file_tree(depth: int = 2):
    """Return a shallow tree of the public directory"""
    def walk(p, d):
        if d <= 0:
            return []
        result = []
        if not p.is_dir():
            return result
        for entry in sorted(p.iterdir()):
            rel = str(entry.relative_to(PUBLIC_ROOT))
            node = {"name": entry.name, "path": rel}
            if entry.is_dir():
                node["type"] = "dir"
                node["children"] = walk(entry, d - 1)
            else:
                node["type"] = "file"
                node["url"] = f"/public/{rel}"
                node["ext"] = entry.suffix.lower()
                node["size"] = entry.stat().st_size
            result.append(node)
        return result

    return {"tree": walk(PUBLIC_ROOT, depth)}
