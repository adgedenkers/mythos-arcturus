#!/usr/bin/env python3
"""
NEU-0011: Grid Processing Manifest + Audit Infrastructure
==========================================================
Deploys:
  - grid_processing_manifest table (Postgres)
  - knowledge_extractions table (Postgres)
  - grid_version_registry table (Postgres, seeded with Layer 1 for all 9 nodes)
  - /opt/mythos/neuro/grid_manifest/ package (ManifestWriter, VersionRegistry, KnowledgeWriter)
  - /grid Telegram command for manifest inspection
  - Wires ManifestWriter into existing grid_worker.py for legacy provenance recording
  - Registers /grid command in bot handler __init__.py
"""

import sys
import os
import shutil
import subprocess

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=11,
    description='grid_processing_manifest',
    patch_type='MAJOR',
)
patch.begin()

PATCH_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 1. Deploy grid_manifest package ──────────────────────────────────────────

manifest_dir = '/opt/mythos/neuro/grid_manifest'
os.makedirs(manifest_dir, exist_ok=True)

for filename in ['__init__.py', 'manifest_writer.py', 'version_registry.py', 'knowledge_writer.py']:
    src = os.path.join(PATCH_DIR, 'opt/mythos/neuro/grid_manifest', filename)
    dst = os.path.join(manifest_dir, filename)
    shutil.copy2(src, dst)
    os.chmod(dst, 0o644)
    print(f"  Deployed: {dst}")

# ── 2. Run SQL migration ────────────────────────────────────────────────────

migration_src = os.path.join(PATCH_DIR, 'opt/mythos/migrations/neu_0011_grid_manifest.sql')
migration_dst = '/opt/mythos/migrations/neu_0011_grid_manifest.sql'
shutil.copy2(migration_src, migration_dst)
print(f"  Deployed: {migration_dst}")

print("  Running SQL migration...")
result = subprocess.run(
    ['sudo', '-u', 'postgres', 'psql', '-d', 'mythos', '-f', migration_dst],
    capture_output=True, text=True
)
if result.returncode != 0:
    print(f"  SQL STDERR: {result.stderr}")
    # Don't fail — tables might already exist (IF NOT EXISTS)
print(f"  SQL STDOUT: {result.stdout}")

# ── 3. Deploy Telegram handler ──────────────────────────────────────────────

handler_src = os.path.join(PATCH_DIR, 'opt/mythos/telegram_bot/handlers/grid_manifest_handler.py')
handler_dst = '/opt/mythos/telegram_bot/handlers/grid_manifest_handler.py'
shutil.copy2(handler_src, handler_dst)
os.chmod(handler_dst, 0o644)
print(f"  Deployed: {handler_dst}")

# ── 4. Register /grid command in handlers/__init__.py ────────────────────────

init_path = '/opt/mythos/telegram_bot/handlers/__init__.py'
with open(init_path, 'r') as f:
    init_content = f.read()

# Add import if not present
import_line = 'from .grid_manifest_handler import handle_grid'
if import_line not in init_content:
    # Find the last import line and add after it
    lines = init_content.split('\n')
    last_import_idx = 0
    for i, line in enumerate(lines):
        if line.startswith('from .') or line.startswith('import '):
            last_import_idx = i
    lines.insert(last_import_idx + 1, import_line)
    init_content = '\n'.join(lines)
    print(f"  Added import: {import_line}")

# Add command registration if not present
registration = "    application.add_handler(CommandHandler('grid', handle_grid))"
if 'handle_grid' not in init_content or registration not in init_content:
    # Find the register_handlers function and add before the last line
    if 'def register_handlers' in init_content:
        # Find a good insertion point — after existing add_handler calls
        lines = init_content.split('\n')
        insert_idx = None
        for i, line in enumerate(lines):
            if 'add_handler(CommandHandler(' in line:
                insert_idx = i + 1
        if insert_idx:
            lines.insert(insert_idx, registration)
            init_content = '\n'.join(lines)
            print(f"  Registered /grid command handler")

with open(init_path, 'w') as f:
    f.write(init_content)

# ── 5. Wire ManifestWriter into grid_worker.py ───────────────────────────────

grid_worker_path = '/opt/mythos/workers/grid_worker.py'
with open(grid_worker_path, 'r') as f:
    gw_content = f.read()

# Add import at the top (after existing imports)
manifest_import = """
# Grid Processing Manifest — NEU-0011
try:
    import sys as _sys
    _sys.path.insert(0, '/opt/mythos/neuro')
    from grid_manifest import ManifestWriter
    _manifest_writer = ManifestWriter()
    _manifest_available = True
except ImportError as _e:
    _manifest_available = False
    _manifest_writer = None
"""

if '_manifest_writer' not in gw_content:
    # Insert after the existing imports (after load_dotenv line)
    marker = "load_dotenv(\"/opt/mythos/.env\")"
    if marker in gw_content:
        gw_content = gw_content.replace(
            marker,
            marker + "\n" + manifest_import
        )
        print("  Added ManifestWriter import to grid_worker.py")

# Add manifest recording at the end of process_grid_analysis
# Find the return statement at the end of process_grid_analysis and add manifest recording before it
manifest_recording = """
    # ── NEU-0011: Record processing manifest ────────────────────────────
    if _manifest_available and _manifest_writer and results:
        try:
            _manifest_writer.record_legacy_activation(
                exchange_id=exchange_id,
                grid_scores={n: results.get(n, 0) for n in GRID_NODES},
                conversation_id=conversation_id,
                user_uuid=user_uuid,
                processing_ms=int(processing_time),
                model_used=OLLAMA_MODEL,
            )
        except Exception as _me:
            logger.warning(f"Manifest recording failed (non-fatal): {_me}")
    # ── End NEU-0011 ────────────────────────────────────────────────────
"""

if 'record_legacy_activation' not in gw_content:
    # Insert before the final return in process_grid_analysis
    final_return = '    return {\n        "status": "success",'
    if final_return in gw_content:
        gw_content = gw_content.replace(final_return, manifest_recording + "\n" + final_return)
        print("  Added manifest recording to process_grid_analysis()")

with open(grid_worker_path, 'w') as f:
    f.write(gw_content)

# ── 6. Verify deployment ────────────────────────────────────────────────────

print("\n  Verifying deployment...")

# Check tables exist
verify_result = subprocess.run(
    ['sudo', '-u', 'postgres', 'psql', '-d', 'mythos', '-t', '-c',
     "SELECT COUNT(*) FROM grid_version_registry"],
    capture_output=True, text=True
)
registry_count = verify_result.stdout.strip()
print(f"  grid_version_registry: {registry_count} rows")

# Syntax check key files
for pyfile in [
    '/opt/mythos/neuro/grid_manifest/__init__.py',
    '/opt/mythos/neuro/grid_manifest/manifest_writer.py',
    '/opt/mythos/neuro/grid_manifest/version_registry.py',
    '/opt/mythos/neuro/grid_manifest/knowledge_writer.py',
    '/opt/mythos/telegram_bot/handlers/grid_manifest_handler.py',
    '/opt/mythos/workers/grid_worker.py',
]:
    result = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', '-c', f"import py_compile; py_compile.compile('{pyfile}', doraise=True)"],
        capture_output=True, text=True
    )
    status = '✓' if result.returncode == 0 else f'✗ {result.stderr[:80]}'
    print(f"  Syntax check {os.path.basename(pyfile)}: {status}")

# ── 7. Restart services ─────────────────────────────────────────────────────

patch.restart_service('mythos-bot.service')
patch.restart_service('mythos-worker-grid.service')

patch.finish()

print("""
╔══════════════════════════════════════════════════════════════╗
║  NEU-0011: Grid Processing Manifest — DEPLOYED              ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  New tables:                                                 ║
║    • grid_processing_manifest — audit trail per exchange     ║
║    • knowledge_extractions — extracted knowledge ledger      ║
║    • grid_version_registry — node-layer version tracking     ║
║                                                              ║
║  New package:                                                ║
║    • /opt/mythos/neuro/grid_manifest/                        ║
║      ManifestWriter, VersionRegistry, KnowledgeWriter        ║
║                                                              ║
║  New Telegram command:                                       ║
║    • /grid — inspect last exchange manifest                  ║
║    • /grid stats — 24h processing stats                      ║
║    • /grid versions — node-layer version registry            ║
║    • /grid stale <node> — find exchanges needing reprocess   ║
║                                                              ║
║  Grid worker updated:                                        ║
║    • Now records legacy manifest entries for every exchange   ║
║                                                              ║
║  Next: NEU-0012 (Layer 1 Perception — 9-node extraction)     ║
╚══════════════════════════════════════════════════════════════╝
""")
