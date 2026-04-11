import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=1,
    description='SDIP foundation - chunker and ingester',
    patch_type='MAJOR',
)
patch.begin()

# ── Deploy SDIP directory and files ──────────────────────────

# Create the sdip directory structure
os.makedirs('/opt/mythos/sdip/migrations', exist_ok=True)

# Deploy all SDIP files
patch.deploy_file('opt/mythos/sdip/__init__.py', '/opt/mythos/sdip/__init__.py')
patch.deploy_file('opt/mythos/sdip/config.py', '/opt/mythos/sdip/config.py')
patch.deploy_file('opt/mythos/sdip/sdip_chunker.py', '/opt/mythos/sdip/sdip_chunker.py')
patch.deploy_file('opt/mythos/sdip/sdip_ingest.py', '/opt/mythos/sdip/sdip_ingest.py')
patch.deploy_file('opt/mythos/sdip/migrations/001_create_tables.sql', '/opt/mythos/sdip/migrations/001_create_tables.sql')

# Make ingester executable
os.chmod('/opt/mythos/sdip/sdip_ingest.py', 0o755)
os.chmod('/opt/mythos/sdip/sdip_chunker.py', 0o755)

# ── Create CLI symlinks in /opt/mythos/bin/ ──────────────────

os.makedirs('/opt/mythos/bin', exist_ok=True)

symlinks = {
    '/opt/mythos/bin/sdip-ingest': '/opt/mythos/sdip/sdip_ingest.py',
    '/opt/mythos/bin/sdip-chunk': '/opt/mythos/sdip/sdip_chunker.py',
}

for link_path, target in symlinks.items():
    if os.path.islink(link_path) or os.path.exists(link_path):
        os.remove(link_path)
    os.symlink(target, link_path)
    print(f"  Symlinked {link_path} → {target}")

# ── Run SQL migration ────────────────────────────────────────

patch.run_sql('opt/mythos/sdip/migrations/001_create_tables.sql')

# ── Done ─────────────────────────────────────────────────────

patch.finish()
