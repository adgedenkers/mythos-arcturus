#!/usr/bin/env python3
"""
LOG-0017: Browser Automation for Iris
======================================
Adds Playwright-based headless browser automation to Mythos/Iris.

Components:
  /opt/mythos/browser/           — Core browser library (BrowserSession, BrowserResult)
  /opt/mythos/browser/__init__.py
  /opt/mythos/browser/core.py
  /opt/mythos/skills/data/web_browser.py  — Auto-discovered skill for Iris
  /opt/mythos/bin/iris-browse     — CLI tool for manual browser use

Dependencies installed:
  - playwright (pip)
  - chromium browser binary (playwright install)

The skill auto-activates when Iris sees URLs with action intent or explicit
browser commands. It does NOT activate for simple search queries (web_search
handles those).

Screenshots are saved to /opt/mythos/browser/screenshots/.
"""

import subprocess
import sys

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=17,
    description='browser_automation',
    patch_type='MAJOR',
)
patch.begin()

# ── Deploy files ──────────────────────────────────────────────────────────

# Browser core library
patch.deploy_file(
    'opt/mythos/browser/__init__.py',
    '/opt/mythos/browser/__init__.py',
)
patch.deploy_file(
    'opt/mythos/browser/core.py',
    '/opt/mythos/browser/core.py',
)

# Skill (auto-discovered by SkillEngine from /opt/mythos/skills/data/)
patch.deploy_file(
    'opt/mythos/skills/data/web_browser.py',
    '/opt/mythos/skills/data/web_browser.py',
)

# CLI tool
patch.deploy_file(
    'opt/mythos/bin/iris-browse',
    '/opt/mythos/bin/iris-browse',
)

# Make CLI executable
subprocess.run(['chmod', '+x', '/opt/mythos/bin/iris-browse'], check=True)

# Create screenshots directory
subprocess.run(['mkdir', '-p', '/opt/mythos/browser/screenshots'], check=True)

# ── Install Playwright + Chromium ─────────────────────────────────────────

print("\n📦 Installing Playwright...")
pip_result = subprocess.run(
    ['/opt/mythos/.venv/bin/pip', 'install', 'playwright'],
    capture_output=True, text=True,
)
if pip_result.returncode != 0:
    print(f"  ⚠️  pip install playwright failed: {pip_result.stderr}")
    print("  You can install manually: /opt/mythos/.venv/bin/pip install playwright")
else:
    print("  ✅ Playwright installed")

print("\n🌐 Installing Chromium browser...")
chromium_result = subprocess.run(
    ['/opt/mythos/.venv/bin/playwright', 'install', 'chromium'],
    capture_output=True, text=True,
)
if chromium_result.returncode != 0:
    print(f"  ⚠️  Chromium install failed: {chromium_result.stderr}")
    print("  You can install manually: /opt/mythos/.venv/bin/playwright install chromium")
    print("  You may also need system deps: /opt/mythos/.venv/bin/playwright install-deps chromium")
else:
    print("  ✅ Chromium installed")

# ── Update skills_context.py if it exists ─────────────────────────────────

skills_context_path = '/opt/mythos/core/skills_context.py'
try:
    with open(skills_context_path, 'r') as f:
        content = f.read()

    # Add browser awareness to the skills context block if not already present
    if 'web_browser' not in content:
        # Find the KNOWLEDGE & SEARCH section and add browser after web_search
        marker = "• web_search —"
        if marker in content:
            insert_after = content.index(marker)
            # Find the end of the web_search description
            next_newline = content.index('\n\n', insert_after)
            browser_block = (
                "\n\n"
                "BROWSER AUTOMATION:\n"
                "• web_browser — opens and interacts with real web pages using a headless browser.\n"
                "  Activates when someone shares a URL and wants content extracted, tables scraped,\n"
                "  screenshots taken, or forms interacted with. Different from web_search — this\n"
                "  actually loads the page in a browser and renders JavaScript.\n"
                "  If browser results appear in your context, use them to answer the question."
            )
            content = content[:next_newline] + browser_block + content[next_newline:]
            with open(skills_context_path, 'w') as f:
                f.write(content)
            print("\n📝 Updated skills_context.py with browser awareness")
        else:
            print("\n⚠️  Could not find insertion point in skills_context.py — update manually")
    else:
        print("\n📝 skills_context.py already has web_browser awareness")

except FileNotFoundError:
    print(f"\n⚠️  {skills_context_path} not found — skill awareness not updated")
except Exception as e:
    print(f"\n⚠️  Error updating skills_context.py: {e}")

# ── Restart services ──────────────────────────────────────────────────────

patch.restart_service('mythos-bot.service')
patch.restart_service('mythos-api.service')

# ── Finish ────────────────────────────────────────────────────────────────

patch.finish()

print("""
╔══════════════════════════════════════════════════════════════╗
║  LOG-0017: Browser Automation — INSTALLED                    ║
║                                                              ║
║  New capabilities:                                           ║
║  • Iris can browse real web pages (JS-rendered, SPAs, etc.)  ║
║  • Extract text, tables, links from any URL                  ║
║  • Take screenshots of web pages                             ║
║  • Auto-activates when URLs appear with action intent        ║
║                                                              ║
║  CLI tool:                                                   ║
║    iris-browse https://example.com                           ║
║    iris-browse https://example.com --tables                  ║
║    iris-browse https://example.com --screenshot              ║
║    iris-browse https://example.com --links --json            ║
║                                                              ║
║  Test with Iris:                                             ║
║    "Read this page: https://news.ycombinator.com"            ║
║    "Scrape the tables from https://example.com/data"         ║
║                                                              ║
║  If Chromium install failed, run:                            ║
║    /opt/mythos/.venv/bin/playwright install-deps chromium     ║
║    /opt/mythos/.venv/bin/playwright install chromium          ║
╚══════════════════════════════════════════════════════════════╝
""")
