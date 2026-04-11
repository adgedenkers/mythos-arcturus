"""
Module: integrity/service_scanner.py
Biological System: iris-immune (Immune System — self-knowledge)
Subsystem: mythos-integrity (v0.2.0)
Purpose: Scan systemd mythos-* services, check health, and MERGE
         Service nodes into Neo4j. Links services to their entry
         point files when identifiable.
Introduced: Patch 0172
Last Modified: Patch 0172

Dependencies:
  - systemctl (systemd)
  - neo4j (graph database)

Part of: Integrity Scanner
"""

import os
import re
import logging
import subprocess
from datetime import datetime

from integrity.graph import get_driver, run_write, run_query

logger = logging.getLogger("mythos.integrity.service_scanner")

MYTHOS_ROOT = os.getenv("MYTHOS_ROOT", "/opt/mythos")


def run_cmd(cmd, default=""):
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=15
        )
        return result.stdout.strip() if result.returncode == 0 else default
    except Exception:
        return default


def scan_services(driver=None) -> dict:
    """
    Scan all mythos-* systemd services and MERGE IntegrityService nodes.
    Links to entry point IntegrityFile nodes where possible.

    Returns:
        dict with stats: services_found, healthy, unhealthy, linked_to_files
    """
    own_driver = driver is None
    if own_driver:
        driver = get_driver()

    scan_timestamp = datetime.now().isoformat()
    stats = {
        "services_found": 0,
        "healthy": 0,
        "unhealthy": 0,
        "linked_to_files": 0,
        "scan_start": scan_timestamp,
    }

    try:
        # Get all mythos service unit files
        unit_files = _find_unit_files()

        for unit_name, unit_path in unit_files:
            service_info = _parse_unit_file(unit_name, unit_path)
            service_info["scan_timestamp"] = scan_timestamp

            # Check live status
            is_active = run_cmd(f"systemctl is-active {unit_name}") == "active"
            sub_state = run_cmd(f"systemctl show {unit_name} --property=SubState --value")
            service_info["is_active"] = is_active
            service_info["sub_state"] = sub_state

            # Get recent journal errors (last 5 lines if unhealthy)
            if not is_active:
                recent_errors = run_cmd(
                    f"journalctl -u {unit_name} --no-pager -n 5 --priority=err -q"
                )
                service_info["recent_errors"] = recent_errors[:500] if recent_errors else ""

            # MERGE into Neo4j
            _merge_service(driver, service_info)
            stats["services_found"] += 1

            if is_active:
                stats["healthy"] += 1
            else:
                stats["unhealthy"] += 1

            # Try to link to entry point file
            if service_info.get("exec_start_path"):
                linked = _link_to_entry_point(driver, unit_name, service_info["exec_start_path"])
                if linked:
                    stats["linked_to_files"] += 1

    finally:
        if own_driver:
            driver.close()

    stats["scan_end"] = datetime.now().isoformat()
    return stats


def _find_unit_files() -> list:
    """Find all mythos-* service unit files."""
    units = []

    # Check standard systemd locations
    for search_dir in ["/etc/systemd/system", "/lib/systemd/system"]:
        if not os.path.isdir(search_dir):
            continue
        for filename in os.listdir(search_dir):
            if filename.startswith("mythos-") and filename.endswith(".service"):
                units.append((filename, os.path.join(search_dir, filename)))

    return units


def _parse_unit_file(unit_name: str, unit_path: str) -> dict:
    """Parse a systemd unit file for key fields."""
    info = {
        "unit_name": unit_name,
        "service_name": unit_name.replace(".service", ""),
        "unit_path": unit_path,
        "description": "",
        "exec_start": "",
        "exec_start_path": "",
        "working_directory": "",
        "user": "",
        "environment_file": "",
        "restart_policy": "",
        "after": "",
    }

    try:
        with open(unit_path, "r") as f:
            content = f.read()

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("Description="):
                info["description"] = line.split("=", 1)[1]
            elif line.startswith("ExecStart="):
                info["exec_start"] = line.split("=", 1)[1]
                # Extract the Python script path if present
                exec_val = info["exec_start"]
                py_match = re.search(r'(/opt/mythos/\S+\.py)', exec_val)
                if py_match:
                    info["exec_start_path"] = py_match.group(1)
            elif line.startswith("WorkingDirectory="):
                info["working_directory"] = line.split("=", 1)[1]
            elif line.startswith("User="):
                info["user"] = line.split("=", 1)[1]
            elif line.startswith("EnvironmentFile="):
                info["environment_file"] = line.split("=", 1)[1]
            elif line.startswith("Restart="):
                info["restart_policy"] = line.split("=", 1)[1]
            elif line.startswith("After="):
                info["after"] = line.split("=", 1)[1]

    except (OSError, PermissionError) as e:
        logger.warning(f"Cannot read {unit_path}: {e}")

    return info


def _merge_service(driver, info: dict):
    """MERGE an IntegrityService node."""
    cypher = """
    MERGE (s:IntegrityService {name: $name})
    SET s.unit_name = $unit_name,
        s.unit_path = $unit_path,
        s.description = $description,
        s.exec_start = $exec_start,
        s.exec_start_path = $exec_start_path,
        s.working_directory = $working_directory,
        s.user = $user,
        s.restart_policy = $restart_policy,
        s.is_active = $is_active,
        s.sub_state = $sub_state,
        s.last_health_check = $scan_timestamp
    """
    run_write(driver, cypher,
              name=info["service_name"],
              unit_name=info["unit_name"],
              unit_path=info["unit_path"],
              description=info["description"],
              exec_start=info["exec_start"],
              exec_start_path=info.get("exec_start_path", ""),
              working_directory=info["working_directory"],
              user=info["user"],
              restart_policy=info["restart_policy"],
              is_active=info["is_active"],
              sub_state=info.get("sub_state", ""),
              scan_timestamp=info["scan_timestamp"])

    # Store recent errors if unhealthy
    if not info["is_active"] and info.get("recent_errors"):
        err_cypher = """
        MATCH (s:IntegrityService {name: $name})
        SET s.recent_errors = $errors
        """
        run_write(driver, err_cypher, name=info["service_name"],
                  errors=info["recent_errors"])


def _link_to_entry_point(driver, unit_name: str, exec_path: str) -> bool:
    """Link a service to its entry point IntegrityFile node."""
    # Check if the file exists in the graph
    check = run_query(
        driver,
        "MATCH (f:IntegrityFile {path: $path}) RETURN f.path",
        path=exec_path
    )
    if not check:
        return False

    service_name = unit_name.replace(".service", "")
    cypher = """
    MATCH (s:IntegrityService {name: $sname})
    MATCH (f:IntegrityFile {path: $fpath})
    MERGE (s)-[:ENTRY_POINT]->(f)
    """
    run_write(driver, cypher, sname=service_name, fpath=exec_path)
    return True
