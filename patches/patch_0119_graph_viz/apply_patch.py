#!/usr/bin/env python3
"""
Patch 0119: Graph Visualization + Relationship Management + Person Types

1. Cytoscape.js interactive graph visualization
2. Add/delete relationships from detail view
3. person_type classification field
4. Ego graph (per-person neighborhood view)
5. Node search for relationship target picker
"""
import os, sys, shutil, py_compile
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

def main():
    print("=" * 60)
    print("  Patch 0119: Graph Viz + Relationship Mgmt + Person Types")
    print("=" * 60)

    print("\n[1/3] Installing files")
    for src, dst in FILES.items():
        backup(dst)
        shutil.copy2(src, dst)
        os.chmod(dst, 0o644)
        print(f"  ✓ {os.path.basename(dst)}")

    print("\n[2/3] Syntax checking")
    for v in FILES.values():
        if v.endswith('.py'):
            try:
                py_compile.compile(v, doraise=True)
                print(f"  ✓ {os.path.basename(v)}")
            except py_compile.PyCompileError as e:
                print(f"  ✗ {os.path.basename(v)}: {e}")
                sys.exit(1)

    print("\n[3/3] Restarting mythos-api")
    os.system("sudo systemctl restart mythos-api.service")
    import time; time.sleep(3)
    rc = os.system("sudo systemctl is-active --quiet mythos-api.service")
    if rc == 0:
        print("  ✓ mythos-api is running")
    else:
        print("  ✗ mythos-api failed"); sys.exit(1)

    print("\n" + "=" * 60)
    print("  ✅ Patch 0119 complete")
    print("=" * 60)
    print("\nNew features:")
    print("  • Graph View — sidebar button, Cytoscape.js force-directed layout")
    print("  • Ego Graph — per-person 'Graph' button shows 2-hop neighborhood")
    print("  • Relationship CRUD — add/delete from detail view with search picker")
    print("  • Person Type — classify nodes (Family, Personal, Business, etc.)")
    print("  • Node Search — /api/people/search-nodes for target picker")
    print("  • Rel Types — /api/people/rel-types lists all relationship types")

if __name__ == '__main__':
    main()
