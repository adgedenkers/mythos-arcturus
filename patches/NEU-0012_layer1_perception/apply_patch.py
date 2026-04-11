#!/usr/bin/env python3
"""
NEU-0012: Layer 1 Perception — 9-Node Knowledge Intake
=======================================================
Deploys:
  - /opt/mythos/neuro/perception/ package
    - __init__.py: 9 node-specific perception prompts
    - engine.py: PerceptionEngine that runs all 9 and writes to manifest + Neo4j
  - Wires PerceptionEngine into grid_worker.py (called after grid scoring)

After this patch, every message Iris processes will:
  1. Get grid-scored (existing flat LLM call → 9 scores)
  2. Get routed to relevant nodes based on scores (threshold: 15)
  3. Have knowledge extracted by each active node's Layer 1 prompt
  4. Write Fact/Preference/Observation/Directive nodes to Neo4j
  5. Record full provenance in grid_processing_manifest
  6. Queue significant extractions (≥4) for Telegram notification
"""

import sys
import os
import shutil

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='NEU',
    number=12,
    description='layer1_perception',
    patch_type='MAJOR',
)
patch.begin()

PATCH_DIR = os.path.dirname(os.path.abspath(__file__))

# ── 1. Deploy perception package ────────────────────────────────────────────

perception_dir = '/opt/mythos/neuro/perception'
os.makedirs(perception_dir, exist_ok=True)

for filename in ['__init__.py', 'engine.py']:
    src = os.path.join(PATCH_DIR, 'opt/mythos/neuro/perception', filename)
    dst = os.path.join(perception_dir, filename)
    shutil.copy2(src, dst)
    os.chmod(dst, 0o644)
    print(f"  Deployed: {dst}")

# ── 2. Wire PerceptionEngine into grid_worker.py ────────────────────────────

grid_worker_path = '/opt/mythos/workers/grid_worker.py'
with open(grid_worker_path, 'r') as f:
    gw_content = f.read()

# Add perception import near the manifest import
perception_import = """
# Layer 1 Perception Engine — NEU-0012
try:
    from perception.engine import PerceptionEngine
    _perception_engine = PerceptionEngine()
    _perception_available = True
except Exception as _pe:
    _perception_available = False
    _perception_engine = None
    import logging as _pl
    _pl.getLogger('worker.grid').warning(f"Perception engine not available: {_pe}")
"""

if '_perception_engine' not in gw_content:
    # Insert after the manifest import block
    marker = "_manifest_available = False\n    _manifest_writer = None"
    if marker in gw_content:
        gw_content = gw_content.replace(
            marker,
            marker + "\n" + perception_import
        )
        print("  Added PerceptionEngine import to grid_worker.py")
    else:
        # Fallback: insert after load_dotenv
        marker2 = 'load_dotenv("/opt/mythos/.env")'
        if marker2 in gw_content:
            gw_content = gw_content.replace(marker2, marker2 + "\n" + perception_import)
            print("  Added PerceptionEngine import (fallback location)")

# Add perception call after the manifest recording block
perception_call = """
    # ── NEU-0012: Layer 1 Perception — knowledge extraction ──────────────
    if _perception_available and _perception_engine and results:
        try:
            grid_scores = {n: results.get(n, 0) for n in GRID_NODES}
            perception_results = _perception_engine.process(
                exchange_id=exchange_id,
                user_message=user_message,
                assistant_response=assistant_response or user_message,
                user_uuid=user_uuid,
                conversation_id=conversation_id,
                grid_scores=grid_scores,
            )
            logger.info(
                f"Perception: {perception_results.get('nodes_activated', 0)} nodes, "
                f"{perception_results.get('total_extractions', 0)} extractions, "
                f"{perception_results.get('processing_ms', 0)}ms"
            )
        except Exception as _pe:
            logger.warning(f"Perception failed (non-fatal): {_pe}")
    # ── End NEU-0012 ─────────────────────────────────────────────────────
"""

if 'NEU-0012' not in gw_content:
    # Insert after the NEU-0011 manifest recording block
    marker = "# ── End NEU-0011 ────────────────────────────────────────────────────"
    if marker in gw_content:
        gw_content = gw_content.replace(marker, marker + "\n" + perception_call)
        print("  Added perception call to process_grid_analysis()")
    else:
        # Fallback: insert before the final return
        final_return = '    return {\n        "status": "success",'
        if final_return in gw_content:
            gw_content = gw_content.replace(final_return, perception_call + "\n" + final_return)
            print("  Added perception call (fallback location)")

with open(grid_worker_path, 'w') as f:
    f.write(gw_content)

# ── 3. Syntax checks ────────────────────────────────────────────────────────

import subprocess

print("\n  Verifying deployment...")
for pyfile in [
    '/opt/mythos/neuro/perception/__init__.py',
    '/opt/mythos/neuro/perception/engine.py',
    '/opt/mythos/workers/grid_worker.py',
]:
    result = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', '-c',
         f"import py_compile; py_compile.compile('{pyfile}', doraise=True)"],
        capture_output=True, text=True
    )
    status = '✓' if result.returncode == 0 else f'✗ {result.stderr[:100]}'
    print(f"  Syntax check {os.path.basename(pyfile)}: {status}")

# ── 4. Restart grid worker ──────────────────────────────────────────────────

patch.restart_service('mythos-worker-grid.service')

patch.finish()

print("""
╔══════════════════════════════════════════════════════════════╗
║  NEU-0012: Layer 1 Perception — DEPLOYED                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  9-node knowledge extraction is now LIVE.                    ║
║  Every message Iris processes will:                          ║
║                                                              ║
║    1. Grid scoring (existing) → 9 node scores                ║
║    2. Route to nodes above threshold (15+)                   ║
║    3. Extract facts/preferences/observations/directives      ║
║    4. Write to Neo4j (Fact, Preference, Observation, etc.)   ║
║    5. Record manifest with version provenance                ║
║    6. Queue significant items for Telegram confirmation      ║
║                                                              ║
║  New package: /opt/mythos/neuro/perception/                  ║
║    - 9 perception prompts (one per grid node)                ║
║    - PerceptionEngine (orchestrator)                         ║
║                                                              ║
║  Test: Send Iris a message, wait 30s, then /grid             ║
║  You should see L1 v1.0 entries with extraction counts.      ║
║                                                              ║
║  Next: NEU-0013 (Backfill + Reprocessing Queue)              ║
╚══════════════════════════════════════════════════════════════╝
""")
