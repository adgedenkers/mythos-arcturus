#!/usr/bin/env python3
"""
LOG-0010: Web Search + Skills Awareness
========================================
Three changes:

1. Deploy /opt/mythos/skills/data/web_search.py
   New skill. DuckDuckGo + Wikipedia. No API key. Activates on news,
   current events, temporal queries, and explicit search requests.

2. Rewrite /opt/mythos/core/skills_context.py
   Replace the mechanical REGISTRY.yaml dump with natural-language
   decision guidance. Iris now understands *when* to expect skill results
   and *when* to invoke analytical/builder skills manually.

3. Enable skills_context layer in prompt_layers.yaml
   The missing switch. Without this, Iris never sees the awareness block
   no matter how good the content is.
"""
import sys
import py_compile
import shutil
from pathlib import Path
from datetime import datetime

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=10,
    description='web_search skill and skills awareness layer',
    patch_type='MINOR',
)
patch.begin()

PATCH_DIR = Path(__file__).parent

# ── 1. Deploy web_search skill ────────────────────────────────────────────────
patch.logger.log("Deploying web_search skill...")
patch.deploy_file(
    'opt/mythos/skills/data/web_search.py',
    '/opt/mythos/skills/data/web_search.py',
)
try:
    py_compile.compile('/opt/mythos/skills/data/web_search.py', doraise=True)
    patch.logger.log("✓ web_search.py syntax OK")
except py_compile.PyCompileError as e:
    raise RuntimeError(f"web_search.py failed syntax check: {e}")

# ── 2. Rewrite skills_context.py ──────────────────────────────────────────────
patch.logger.log("Rewriting skills_context.py...")

# Backup original
src = Path('/opt/mythos/core/skills_context.py')
backup = Path(f'/opt/mythos/core/skills_context.py.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
if src.exists():
    shutil.copy2(src, backup)
    patch.logger.log(f"  Backed up original to {backup.name}")

patch.deploy_file(
    'opt/mythos/core/skills_context.py',
    '/opt/mythos/core/skills_context.py',
)
try:
    py_compile.compile('/opt/mythos/core/skills_context.py', doraise=True)
    patch.logger.log("✓ skills_context.py syntax OK")
except py_compile.PyCompileError as e:
    raise RuntimeError(f"skills_context.py failed syntax check: {e}")

# ── 3. Enable skills_context in prompt_layers.yaml ────────────────────────────
patch.logger.log("Enabling skills_context layer in prompt_layers.yaml...")

layers_path = Path('/opt/mythos/prompts/prompt_layers.yaml')
content = layers_path.read_text()

# The skills_context layer block looks like:
#   skills_context:
#     enabled: false
# We need to flip it to true.
old_block = """  skills_context:
    enabled: false"""
new_block = """  skills_context:
    enabled: true"""

if old_block not in content:
    # Check if it's already enabled
    already_enabled = """  skills_context:
    enabled: true"""
    if already_enabled in content:
        patch.logger.log("  skills_context already enabled — no change needed")
    else:
        raise RuntimeError(
            "Could not find skills_context enabled: false in prompt_layers.yaml. "
            "Check the file manually."
        )
else:
    updated = content.replace(old_block, new_block, 1)
    layers_path.write_text(updated)
    patch.logger.log("✓ skills_context layer enabled")

# ── 4. Smoke test the web_search skill ───────────────────────────────────────
patch.logger.log("Running web_search smoke test...")
try:
    import sys
    sys.path.insert(0, '/opt/mythos/skills')
    # Just import and instantiate — don't actually hit the network during install
    from data.web_search import WebSearchSkill, _extract_query
    skill = WebSearchSkill()
    assert skill.name == "web_search"
    assert skill.cache_ttl == 600
    # Test query extraction
    q = _extract_query("can you look up the latest news on PostgreSQL 17")
    assert "postgresql" in q.lower() or "latest" in q.lower(), f"Unexpected query: {q}"
    patch.logger.log(f"  ✓ skill instantiated, query extraction works (got: '{q}')")
except Exception as e:
    patch.logger.log(f"  ⚠ Smoke test warning (non-fatal): {e}")

# ── 5. Verify services will pick up changes ───────────────────────────────────
# No service restart needed — skill engine loads skills dynamically on first use.
# prompt_assembler.py caches layers by mtime, so the yaml change takes effect
# on next message without a restart.
patch.logger.log("No service restart required — changes take effect on next message.")

patch.finish()

print("""
╔══════════════════════════════════════════════════════════════╗
║  LOG-0010: Web Search + Skills Awareness — INSTALLED         ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  1. web_search skill deployed                                ║
║     → DuckDuckGo + Wikipedia, no API key required           ║
║     → Activates on news, current events, explicit searches  ║
║     → 10-minute cache                                        ║
║                                                              ║
║  2. skills_context.py rewritten                              ║
║     → Plain-language decision guide (not a YAML dump)       ║
║     → Tells Iris when to expect skill results                ║
║     → Tells Iris when to invoke analytical skills manually   ║
║                                                              ║
║  3. skills_context layer ENABLED in prompt_layers.yaml       ║
║     → Iris now sees her capabilities on every message        ║
║                                                              ║
║  Test: Ask Iris "what's the latest news on [anything]"       ║
║  or "look up [topic]" — she should search and report back.  ║
║                                                              ║
║  To disable: /layer toggle skills_context off                ║
╚══════════════════════════════════════════════════════════════╝
""")
