#!/usr/bin/env python3
"""
Iris Systems API
/opt/mythos/api/routes/iris_systems.py

Serves iris_systems.json and allows status updates.
GET  /api/iris/systems          → full systems data
GET  /api/iris/systems/summary  → status counts
POST /api/iris/systems/update   → update a system's status
"""
import json
from pathlib import Path
from datetime import date
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

router = APIRouter(prefix="/api/iris", tags=["iris-systems"])

SYSTEMS_FILE = Path("/opt/mythos/docs/iris_systems.json")


def load_systems():
    """Load the systems JSON file"""
    if not SYSTEMS_FILE.exists():
        raise HTTPException(status_code=404, detail="iris_systems.json not found")
    return json.loads(SYSTEMS_FILE.read_text())


def save_systems(data):
    """Save updated systems data back to JSON file"""
    data["last_updated"] = str(date.today())
    SYSTEMS_FILE.write_text(json.dumps(data, indent=2))


@router.get("/systems")
async def get_systems():
    """Return full iris systems data"""
    return JSONResponse(content=load_systems())


@router.get("/systems/summary")
async def get_systems_summary():
    """Return status counts and category summary"""
    data = load_systems()
    
    status_counts = {"live": 0, "partial": 0, "stub": 0, "designed": 0, "planned": 0}
    category_summary = []
    total = 0
    
    for cat in data.get("categories", []):
        cat_counts = {"live": 0, "partial": 0, "stub": 0, "designed": 0, "planned": 0}
        for sys in cat.get("systems", []):
            st = sys.get("status", "planned")
            status_counts[st] = status_counts.get(st, 0) + 1
            cat_counts[st] = cat_counts.get(st, 0) + 1
            total += 1
        category_summary.append({
            "id": cat["id"],
            "title": cat["title"],
            "icon": cat["icon"],
            "total": len(cat["systems"]),
            "counts": {k: v for k, v in cat_counts.items() if v > 0},
        })
    
    return JSONResponse(content={
        "total_systems": total,
        "status_counts": status_counts,
        "categories": category_summary,
        "last_updated": data.get("last_updated"),
        "version": data.get("version"),
    })


class StatusUpdate(BaseModel):
    system_id: str
    new_status: str
    note: str = ""


@router.post("/systems/update")
async def update_system_status(update: StatusUpdate):
    """Update a system's status"""
    valid_statuses = ["live", "partial", "stub", "designed", "planned"]
    if update.new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    
    data = load_systems()
    found = False
    
    for cat in data.get("categories", []):
        for sys in cat.get("systems", []):
            if sys.get("id") == update.system_id:
                old_status = sys["status"]
                sys["status"] = update.new_status
                if update.note:
                    sys["detail"] = update.note + " | " + sys.get("detail", "")
                found = True
                break
        if found:
            break
    
    if not found:
        raise HTTPException(status_code=404, detail=f"System '{update.system_id}' not found")
    
    save_systems(data)
    
    return JSONResponse(content={
        "success": True,
        "system_id": update.system_id,
        "old_status": old_status,
        "new_status": update.new_status,
    })
