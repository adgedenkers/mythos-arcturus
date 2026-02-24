#!/usr/bin/env python3
"""
Patch 0118: People System → Neo4j Backend

Replaces the Postgres-backed people API with Neo4j.
The web UI now shows all Person/Soul/Entity/GenPerson nodes
with relationship viewing, type filtering, and full CRUD.
"""
import os
import sys
import shutil
import py_compile
from datetime import datetime

PATCH_DIR = os.path.dirname(os.path.abspath(__file__))
MYTHOS = '/opt/mythos'

FILES = {
    f'{PATCH_DIR}/opt/mythos/api/routes/people.py': f'{MYTHOS}/api/routes/people.py',
    f'{PATCH_DIR}/opt/mythos/web/templates/people.html': f'{MYTHOS}/web/templates/people.html',
}


def backup(path):
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    bak = f"{path}.bak.{ts}"
    if os.path.exists(path):
        shutil.copy2(path, bak)
        print(f"  Backed up → {bak}")
    return bak


def main():
    print("=" * 60)
    print("  Patch 0118: People System → Neo4j Backend")
    print("=" * 60)

    # Step 1: Backup and copy files
    print("\n[1/3] Installing files")
    for src, dst in FILES.items():
        backup(dst)
        shutil.copy2(src, dst)
        os.chmod(dst, 0o644)
        print(f"  ✓ {os.path.basename(dst)}")

    # Step 2: Syntax check Python files
    print("\n[2/3] Syntax checking")
    py_files = [v for v in FILES.values() if v.endswith('.py')]
    errors = []
    for f in py_files:
        try:
            py_compile.compile(f, doraise=True)
            print(f"  ✓ {os.path.basename(f)}")
        except py_compile.PyCompileError as e:
            print(f"  ✗ {os.path.basename(f)}: {e}")
            errors.append(f)

    if errors:
        print("\n❌ Syntax errors — NOT restarting services")
        sys.exit(1)

    # Step 3: Restart API service
    print("\n[3/3] Restarting mythos-api")
    os.system("sudo systemctl restart mythos-api.service")

    import time
    time.sleep(3)

    rc = os.system("sudo systemctl is-active --quiet mythos-api.service")
    if rc == 0:
        print("  ✓ mythos-api is running")
    else:
        print("  ✗ mythos-api failed to start")
        print("  Check: journalctl -u mythos-api -n 30 --no-pager")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  ✅ Patch 0118 complete")
    print("=" * 60)
    print("\nWhat changed:")
    print("  • /api/people/ now queries Neo4j (was Postgres)")
    print("  • Web UI shows all Person/Entity/Soul/GenPerson nodes")
    print("  • Type filter sidebar (Canonical, Aspects, Souls, Genealogy)")
    print("  • Detail view shows all relationships")
    print("  • Full CRUD on Neo4j nodes from web UI")
    print("  • Relationship management API endpoints")
    print("\nTest:")
    print("  https://mythos-api.denkers.co/app/people/")
    print("  curl -s https://mythos-api.denkers.co/api/people/stats")
    print("\nNote: Postgres 'people' table is preserved but no longer used.")
    print("  The /people Telegram command still uses Postgres.")
    print("  Consider migrating that too in a future patch.")


if __name__ == '__main__':
    main()
