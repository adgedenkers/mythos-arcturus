"""
SYS-0101: Modelfile.convo v2 — AutoDoc2 awareness + anti-menu + temp 0.5

What this patch changes:
- Updates /opt/mythos/prompts/Modelfile.convo with:
  - AutoDoc2 fact sheet (what it is, what it does, 11 languages)
  - Anti-menu instruction (no 'Would you like me to...' patterns)
  - Stronger anti-hallucination for tool features
  - Temperature lowered from 0.7 to 0.5
- Rebakes iris:convo model from updated Modelfile

Services restarted: none (model rebake only)
Tables touched: none
"""
import sys
import subprocess

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=101,
    description='modelfile convo v2 — autodoc2 awareness + anti-menu',
    patch_type='PATCH',
)
patch.begin()

# Deploy updated Modelfile
patch.deploy_file(
    'opt/mythos/prompts/Modelfile.convo',
    '/opt/mythos/prompts/Modelfile.convo',
)

# Rebake iris:convo
patch.logger.log("  · Rebaking iris:convo from updated Modelfile.convo...")
try:
    result = subprocess.run(
        ['ollama', 'create', 'iris:convo', '-f', '/opt/mythos/prompts/Modelfile.convo'],
        capture_output=True, text=True, timeout=120,
    )
    if result.returncode == 0:
        patch.logger.log("  ✓ iris:convo rebaked successfully")
    else:
        stderr = (result.stderr or '').strip()[:200]
        patch.errors.append(f"ollama create iris:convo failed: {stderr}")
        patch.logger.log(f"  ✗ iris:convo rebake failed: {stderr}")
except Exception as e:
    patch.errors.append(f"ollama create iris:convo: {e}")
    patch.logger.log(f"  ✗ iris:convo rebake error: {e}")

patch.finish()
