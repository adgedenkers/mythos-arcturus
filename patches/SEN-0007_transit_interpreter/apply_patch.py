"""
SEN-0007: Transit Interpreter
Adds Ollama-powered personalized transit interpretations to the Spiral Time Walker.

Deploys:
  - astrology/spiral/transit_interpreter.py  (new — Ollama interpretation engine)
  - astrology/spiral/__init__.py             (updated — exports new functions)
  - astrology/spiral/morning_brief.py        (updated — uses interpreted transits + DB fix)
"""

import os
import sys

sys.path.insert(0, "/opt/mythos/patches/scripts")
from patch_base import PatchBase

patch = PatchBase(
    stream="SEN",
    number=7,
    description="transit_interpreter",
    patch_type="MINOR",
)
patch.begin()

# ── Deploy files ──────────────────────────────────────────────────────────────
patch.deploy_file(
    "opt/mythos/astrology/spiral/transit_interpreter.py",
    "/opt/mythos/astrology/spiral/transit_interpreter.py",
)
patch.deploy_file(
    "opt/mythos/astrology/spiral/__init__.py",
    "/opt/mythos/astrology/spiral/__init__.py",
)
patch.deploy_file(
    "opt/mythos/astrology/spiral/morning_brief.py",
    "/opt/mythos/astrology/spiral/morning_brief.py",
)

# ── Restart services ──────────────────────────────────────────────────────────
patch.restart_service("mythos-api.service")
patch.restart_service("mythos-bot.service")

patch.finish()
print("\n✅ SEN-0007 Transit Interpreter deployed.")
print("   Transit aspects now include Ollama-generated personalized readings.")
print("   Morning brief and /spiral brief both use interpreted output.")
print("\n   Test: /spiral brief in Telegram (force-generates today's brief)")
