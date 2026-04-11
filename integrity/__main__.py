"""
Module: integrity/__main__.py
Biological System: iris-immune (Immune System)
Subsystem: mythos-integrity (v0.1.0)
Purpose: CLI entry point for the integrity scanner.
Introduced: Patch 0171
Last Modified: Patch 0171

Usage:
  cd /opt/mythos
  .venv/bin/python3 -m integrity scan              # full scan
  .venv/bin/python3 -m integrity scan --files       # files only
  .venv/bin/python3 -m integrity scan --funcs       # functions only
  .venv/bin/python3 -m integrity scan --tables      # tables only
  .venv/bin/python3 -m integrity stats              # show graph stats
"""

import argparse
import json
import sys
import time
import logging
from datetime import datetime

from integrity.graph import get_driver, ensure_constraints, run_query


def cmd_scan(args):
    """Run integrity scan."""
    driver = get_driver()

    # Always ensure constraints first
    print("🔧 Ensuring Neo4j constraints...")
    ensure_constraints(driver)

    do_all = not (args.files or args.funcs or args.tables or args.services)
    results = {}

    if do_all or args.files:
        print("\n📁 Scanning files...")
        start = time.time()
        from integrity.file_scanner import scan_files
        file_stats = scan_files(driver=driver)
        elapsed = time.time() - start
        results["files"] = file_stats
        print(f"   Files scanned:  {file_stats['files_scanned']}")
        print(f"   Directories:    {file_stats['dirs_scanned']}")
        print(f"   New:            {file_stats['files_new']}")
        print(f"   Updated:        {file_stats['files_updated']}")
        print(f"   Unchanged:      {file_stats['files_unchanged']}")
        print(f"   Missing:        {file_stats['files_missing']}")
        if file_stats["errors"]:
            print(f"   Errors:         {len(file_stats['errors'])}")
        print(f"   Time:           {elapsed:.1f}s")

    if do_all or args.funcs:
        print("\n🔍 Extracting functions...")
        start = time.time()
        from integrity.function_extractor import extract_functions
        func_stats = extract_functions(driver=driver)
        elapsed = time.time() - start
        results["functions"] = func_stats
        print(f"   Files parsed:   {func_stats['files_parsed']}")
        print(f"   Functions:      {func_stats['functions_found']}")
        print(f"   Imports:        {func_stats['imports_found']}")
        print(f"   Parse errors:   {func_stats['parse_errors']}")
        print(f"   Time:           {elapsed:.1f}s")

    if do_all or args.tables:
        print("\n🗄️  Scanning PostgreSQL tables...")
        start = time.time()
        from integrity.table_scanner import scan_tables
        table_stats = scan_tables(driver=driver)
        elapsed = time.time() - start
        results["tables"] = table_stats
        print(f"   Tables:         {table_stats['tables_found']}")
        print(f"   Columns:        {table_stats['columns_found']}")
        print(f"   Foreign keys:   {table_stats['fk_relationships']}")
        if table_stats.get("error"):
            print(f"   Error:          {table_stats['error']}")
        print(f"   Time:           {elapsed:.1f}s")

    if do_all or args.services:
        print("\n⚙️  Scanning systemd services...")
        start = time.time()
        from integrity.service_scanner import scan_services
        svc_stats = scan_services(driver=driver)
        elapsed = time.time() - start
        results["services"] = svc_stats
        print(f"   Services found: {svc_stats['services_found']}")
        print(f"   Healthy:        {svc_stats['healthy']}")
        print(f"   Unhealthy:      {svc_stats['unhealthy']}")
        print(f"   Linked to files:{svc_stats['linked_to_files']}")
        print(f"   Time:           {elapsed:.1f}s")

    driver.close()

    print("\n✅ Scan complete.")

    # Write results to live directory
    try:
        import os
        live_dir = os.path.join(os.getenv("MYTHOS_ROOT", "/opt/mythos"), "docs", "live")
        os.makedirs(live_dir, exist_ok=True)
        report_path = os.path.join(live_dir, "integrity-scan-latest.json")
        with open(report_path, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"   Report: {report_path}")
    except Exception as e:
        print(f"   ⚠️  Could not write report: {e}")


def cmd_stats(args):
    """Show current graph statistics."""
    driver = get_driver()

    queries = {
        "IntegrityFile (active)": "MATCH (f:IntegrityFile {status: 'active'}) RETURN count(f) AS cnt",
        "IntegrityFile (missing)": "MATCH (f:IntegrityFile {status: 'missing'}) RETURN count(f) AS cnt",
        "IntegrityDirectory": "MATCH (d:IntegrityDirectory) RETURN count(d) AS cnt",
        "IntegrityFunction": "MATCH (fn:IntegrityFunction) RETURN count(fn) AS cnt",
        "IntegrityTable": "MATCH (t:IntegrityTable) RETURN count(t) AS cnt",
        "IntegrityColumn": "MATCH (c:IntegrityColumn) RETURN count(c) AS cnt",
        "IntegrityDatabase": "MATCH (db:IntegrityDatabase) RETURN count(db) AS cnt",
        "IntegrityService": "MATCH (s:IntegrityService) RETURN count(s) AS cnt",
        "CONTAINS rels": "MATCH ()-[r:CONTAINS]->(:IntegrityFunction) RETURN count(r) AS cnt",
        "IMPORTS rels": "MATCH ()-[r:IMPORTS]->() RETURN count(r) AS cnt",
        "HAS_TABLE rels": "MATCH ()-[r:HAS_TABLE]->() RETURN count(r) AS cnt",
        "HAS_COLUMN rels": "MATCH ()-[r:HAS_COLUMN]->() RETURN count(r) AS cnt",
        "REFERENCES rels": "MATCH (:IntegrityTable)-[r:REFERENCES]->(:IntegrityTable) RETURN count(r) AS cnt",
    }

    print("📊 Integrity Graph Statistics")
    print("=" * 45)

    for label, cypher in queries.items():
        try:
            result = run_query(driver, cypher)
            count = result[0]["cnt"] if result else 0
            print(f"  {label:30s} {count:>6}")
        except Exception as e:
            print(f"  {label:30s}  error: {e}")

    # Top directories by file count
    print("\n📁 Top directories by file count:")
    top_dirs = run_query(driver, """
        MATCH (f:IntegrityFile {status: 'active'})-[:IN_DIRECTORY]->(d:IntegrityDirectory)
        RETURN d.path AS dir, count(f) AS file_count
        ORDER BY file_count DESC
        LIMIT 10
    """)
    for r in top_dirs:
        short_path = r["dir"].replace("/opt/mythos/", "")
        print(f"  {short_path:45s} {r['file_count']:>4} files")

    # Functions without docstrings
    undoc = run_query(driver, """
        MATCH (fn:IntegrityFunction)
        WHERE fn.docstring IS NULL OR fn.docstring = ''
        RETURN count(fn) AS cnt
    """)
    undoc_count = undoc[0]["cnt"] if undoc else 0
    total_funcs = run_query(driver, "MATCH (fn:IntegrityFunction) RETURN count(fn) AS cnt")
    total = total_funcs[0]["cnt"] if total_funcs else 0
    if total > 0:
        pct = (total - undoc_count) / total * 100
        print(f"\n📝 Documentation: {total - undoc_count}/{total} functions have docstrings ({pct:.0f}%)")

    driver.close()


def main():
    parser = argparse.ArgumentParser(
        description="Mythos Integrity Scanner — Iris's immune system",
        prog="python3 -m integrity"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # scan command
    scan_parser = subparsers.add_parser("scan", help="Run integrity scan")
    scan_parser.add_argument("--files", action="store_true", help="Scan files only")
    scan_parser.add_argument("--funcs", action="store_true", help="Extract functions only")
    scan_parser.add_argument("--tables", action="store_true", help="Scan tables only")
    scan_parser.add_argument("--services", action="store_true", help="Scan services only")

    # stats command
    subparsers.add_parser("stats", help="Show graph statistics")

    args = parser.parse_args()

    if args.command == "scan":
        cmd_scan(args)
    elif args.command == "stats":
        cmd_stats(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
