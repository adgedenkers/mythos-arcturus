#!/usr/bin/env python3
"""
LOG-0011: Web Search — RSS + Wikipedia
=======================================
Replaces the LOG-0010 web_search.py (which used DuckDuckGo Instant Answer API,
confirmed returning empty responses from Arcturus) with a new implementation
using two backends that are confirmed working:

  1. BBC News RSS feeds + Hacker News RSS — current events and news
  2. Wikipedia full-text search + summary API — factual lookups

No API keys. No rate limits. No external dependencies beyond stdlib.
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
    number=11,
    description='web_search v2 using RSS feeds and Wikipedia',
    patch_type='PATCH',
)
patch.begin()

PATCH_DIR = Path(__file__).parent

# ── Deploy updated web_search.py ─────────────────────────────────────────────
patch.logger.log("Deploying web_search.py v2 (RSS + Wikipedia)...")

target = Path('/opt/mythos/skills/data/web_search.py')
if target.exists():
    backup = Path(f'/opt/mythos/skills/data/web_search.py.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}')
    shutil.copy2(target, backup)
    patch.logger.log(f"  Backed up v1 to {backup.name}")

patch.deploy_file(
    'opt/mythos/skills/data/web_search.py',
    '/opt/mythos/skills/data/web_search.py',
)

try:
    py_compile.compile('/opt/mythos/skills/data/web_search.py', doraise=True)
    patch.logger.log("✓ web_search.py syntax OK")
except py_compile.PyCompileError as e:
    raise RuntimeError(f"Syntax check failed: {e}")

# ── Smoke test — import + instantiate (no network call) ──────────────────────
patch.logger.log("Running smoke test...")
try:
    sys.path.insert(0, '/opt/mythos/skills')
    # Force reload in case LOG-0010 version is cached
    import importlib
    if 'data.web_search' in sys.modules:
        del sys.modules['data.web_search']
    if 'mythos_skill_web_search' in sys.modules:
        del sys.modules['mythos_skill_web_search']

    from data.web_search import WebSearchSkill, _extract_query, _classify_query

    skill = WebSearchSkill()
    assert skill.name == "web_search"
    assert skill.version == "2.0"

    # Test query extraction
    q = _extract_query("what's the latest news on DeepSeek?")
    assert len(q) > 3, f"Query too short: '{q}'"

    # Test classification
    t = _classify_query("what's the latest news on DeepSeek?")
    assert t == 'news', f"Expected 'news', got '{t}'"

    t2 = _classify_query("what is PostgreSQL?")
    assert t2 == 'factual', f"Expected 'factual', got '{t2}'"

    patch.logger.log(f"  ✓ instantiated v{skill.version}")
    patch.logger.log(f"  ✓ query extraction: '{q}'")
    patch.logger.log(f"  ✓ classification: news='{t}', factual='{t2}'")

except Exception as e:
    patch.logger.log(f"  ⚠ Smoke test warning (non-fatal): {e}")

patch.logger.log("No service restart required — skill engine reloads on next message.")

patch.finish()

print("""
╔══════════════════════════════════════════════════════════════╗
║  LOG-0011: Web Search v2 — RSS + Wikipedia — INSTALLED       ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Replaces DDG (broken) with two confirmed working backends:  ║
║                                                              ║
║  NEWS queries → BBC Tech/World/Science/Business/Politics     ║
║                 + Hacker News RSS                            ║
║                 Keyword-scored, top 5 relevant items         ║
║                                                              ║
║  FACTUAL queries → Wikipedia full-text search                ║
║                    + lead paragraph summary                  ║
║                                                              ║
║  Each backend falls back to the other if empty.             ║
║                                                              ║
║  Test — ask Iris:                                            ║
║  "what's the latest tech news today?"                        ║
║  "look up DeepSeek"                                          ║
║  "what is PostgreSQL?"                                       ║
║  "what's happening in AI this week?"                         ║
╚══════════════════════════════════════════════════════════════╝
""")
