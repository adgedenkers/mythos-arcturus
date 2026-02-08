#!/usr/bin/env python3
"""
Mythos API - System Status Routes
/opt/mythos/api/routes/system.py

Provides live system health data for the dashboard.
"""
import os
import subprocess
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/system", tags=["system"])

SERVICES = [
    {"unit": "mythos-api.service", "name": "Mythos API", "description": "FastAPI gateway"},
    {"unit": "mythos-bot.service", "name": "Telegram Bot", "description": "Telegram interface"},
    {"unit": "mythos-patch-monitor.service", "name": "Patch Monitor", "description": "Auto-deploy patches"},
    {"unit": "postgresql.service", "name": "PostgreSQL", "description": "Relational database"},
    {"unit": "neo4j.service", "name": "Neo4j", "description": "Graph database"},
    {"unit": "cloudflared.service", "name": "Cloudflare Tunnel", "description": "External access"},
]


def run_cmd(cmd, timeout=5):
    """Run a shell command and return stdout"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip()
    except:
        return ""


def check_service(unit):
    """Check if a systemd service is active"""
    result = run_cmd(f"systemctl is-active {unit}")
    return result == "active"


def get_uptime():
    """Get system uptime"""
    raw = run_cmd("uptime -p")
    return raw.replace("up ", "") if raw else "unknown"


def get_cpu():
    """Get CPU info"""
    try:
        cores = os.cpu_count() or 0
        load = run_cmd("cat /proc/loadavg")
        parts = load.split()
        load_1m = parts[0] if parts else "?"
        # CPU usage via /proc/stat snapshot
        percent = run_cmd("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
        return {"cores": cores, "load_1m": load_1m, "percent": round(float(percent or 0))}
    except:
        return {"cores": os.cpu_count(), "load_1m": "?", "percent": 0}


def get_memory():
    """Get memory usage"""
    try:
        raw = run_cmd("free -b | grep Mem")
        parts = raw.split()
        total = int(parts[1])
        used = int(parts[2])
        pct = round(used / total * 100) if total > 0 else 0
        return {
            "total_gb": f"{total/1073741824:.1f}",
            "used_gb": f"{used/1073741824:.1f}",
            "percent": pct,
        }
    except:
        return {"total_gb": "?", "used_gb": "?", "percent": 0}


def get_disk():
    """Get disk usage for /"""
    try:
        raw = run_cmd("df -B1 / | tail -1")
        parts = raw.split()
        total = int(parts[1])
        used = int(parts[2])
        pct = round(used / total * 100) if total > 0 else 0
        return {
            "total_gb": f"{total/1073741824:.0f}",
            "used_gb": f"{used/1073741824:.0f}",
            "percent": pct,
        }
    except:
        return {"total_gb": "?", "used_gb": "?", "percent": 0}


def get_gpu():
    """Get GPU info via nvidia-smi"""
    try:
        name = run_cmd("nvidia-smi --query-gpu=gpu_name --format=csv,noheader,nounits 2>/dev/null")
        if name:
            mem = run_cmd("nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits 2>/dev/null")
            return {"name": name, "memory": mem.replace(", ", " / ") + " MiB" if mem else "?"}
    except:
        pass
    return None


def get_databases():
    """Check database connectivity"""
    dbs = []
    
    # PostgreSQL
    pg_ok = run_cmd("sudo -u postgres psql -d mythos -c 'SELECT 1' 2>/dev/null")
    pg_tables = run_cmd("sudo -u postgres psql -d mythos -t -c \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'\" 2>/dev/null").strip()
    dbs.append({
        "name": "PostgreSQL (mythos)",
        "connected": "1" in pg_ok,
        "details": f"{pg_tables} tables" if pg_tables else "",
    })
    
    # Neo4j
    neo_ok = run_cmd("curl -s -o /dev/null -w '%{http_code}' http://localhost:7474 2>/dev/null")
    dbs.append({
        "name": "Neo4j",
        "connected": neo_ok == "200",
        "details": "Bolt: 7687 · HTTP: 7474",
    })
    
    return dbs


def get_patches():
    """Get recent patches from git tags"""
    try:
        raw = run_cmd("cd /opt/mythos && git log --oneline -15 -- patches/")
        patches = []
        for line in raw.split('\n'):
            if line.strip():
                parts = line.strip().split(' ', 1)
                patches.append({
                    "name": parts[1] if len(parts) > 1 else parts[0],
                    "hash": parts[0],
                    "status": "applied",
                })
        return patches
    except:
        return []


def get_last_patch():
    """Get name of most recent patch"""
    patches_dir = Path('/opt/mythos/patches')
    if patches_dir.exists():
        dirs = sorted([d for d in patches_dir.iterdir() if d.is_dir() and d.name.startswith('patch_')], reverse=True)
        if dirs:
            return dirs[0].name.replace('patch_', '').replace('_', ' ')[:20]
    return "—"


@router.get("/status")
async def system_status():
    """Full system status"""
    services = []
    services_up = 0
    
    for svc in SERVICES:
        active = check_service(svc['unit'])
        if active:
            services_up += 1
        services.append({
            "name": svc['name'],
            "unit": svc['unit'],
            "description": svc['description'],
            "active": active,
        })
    
    return JSONResponse(content={
        "hostname": run_cmd("hostname") or "arcturus",
        "uptime": get_uptime(),
        "services": services,
        "services_up": services_up,
        "services_total": len(services),
        "cpu": get_cpu(),
        "memory": get_memory(),
        "disk": get_disk(),
        "gpu": get_gpu(),
        "databases": get_databases(),
        "patches": get_patches(),
        "last_patch": get_last_patch(),
        "timestamp": datetime.now().isoformat(),
    })
