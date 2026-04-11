#!/usr/bin/env python3
"""LOG-0018: Conversation Engine Foundation — Pydantic-native, chainable tools."""
import os
import sys
import subprocess

sys.path.insert(0, "/opt/mythos/patches/scripts")
from patch_base import PatchBase

patch = PatchBase(
    stream="LOG",
    number=18,
    description="conversation_engine_foundation",
    patch_type="MAJOR",
)
patch.begin()

PATCH_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Deploy engine package ────────────────────────────────────────────────────

# Create directory structure
dirs = [
    "/opt/mythos/engine",
    "/opt/mythos/engine/tools",
    "/opt/mythos/engine/chains",
    "/opt/mythos/engine/response",
    "/opt/mythos/engine/response/formatters",
    "/opt/mythos/config",
]
for d in dirs:
    os.makedirs(d, exist_ok=True)

# Deploy all engine files
files = [
    # Core
    ("opt/mythos/engine/__init__.py", "/opt/mythos/engine/__init__.py"),
    ("opt/mythos/engine/models.py", "/opt/mythos/engine/models.py"),
    ("opt/mythos/engine/ollama_client.py", "/opt/mythos/engine/ollama_client.py"),
    # Tools
    ("opt/mythos/engine/tools/__init__.py", "/opt/mythos/engine/tools/__init__.py"),
    ("opt/mythos/engine/tools/base.py", "/opt/mythos/engine/tools/base.py"),
    ("opt/mythos/engine/tools/registry.py", "/opt/mythos/engine/tools/registry.py"),
    ("opt/mythos/engine/tools/schemas.py", "/opt/mythos/engine/tools/schemas.py"),
    # Chains
    ("opt/mythos/engine/chains/__init__.py", "/opt/mythos/engine/chains/__init__.py"),
    ("opt/mythos/engine/chains/chain.py", "/opt/mythos/engine/chains/chain.py"),
    ("opt/mythos/engine/chains/executor.py", "/opt/mythos/engine/chains/executor.py"),
    # Response
    ("opt/mythos/engine/response/__init__.py", "/opt/mythos/engine/response/__init__.py"),
    ("opt/mythos/engine/response/response.py", "/opt/mythos/engine/response/response.py"),
    ("opt/mythos/engine/response/formatters/__init__.py", "/opt/mythos/engine/response/formatters/__init__.py"),
    ("opt/mythos/engine/response/formatters/telegram.py", "/opt/mythos/engine/response/formatters/telegram.py"),
    # Validation
    ("opt/mythos/engine/validate_foundation.py", "/opt/mythos/engine/validate_foundation.py"),
    # Config
    ("opt/mythos/config/conversation_modes.yaml", "/opt/mythos/config/conversation_modes.yaml"),
]

for src_rel, dst in files:
    patch.deploy_file(os.path.join(PATCH_DIR, src_rel), dst)

# ── Deploy spec document ─────────────────────────────────────────────────────

# Copy the spec into docs if it exists in the patch
spec_src = os.path.join(PATCH_DIR, "opt/mythos/docs/CONVERSATION_ENGINE_SPEC.md")
if os.path.exists(spec_src):
    patch.deploy_file(spec_src, "/opt/mythos/docs/CONVERSATION_ENGINE_SPEC.md")

# ── Run validation ───────────────────────────────────────────────────────────

print("\n🔍 Running foundation validation...")
result = subprocess.run(
    ["/opt/mythos/.venv/bin/python3", "/opt/mythos/engine/validate_foundation.py"],
    capture_output=True,
    text=True,
)
print(result.stdout)
if result.stderr:
    print(result.stderr)

if result.returncode != 0:
    print("⚠️  Validation had failures — review output above.")
    print("   The files are deployed but some tests didn't pass.")
else:
    print("✅ All validation tests passed.")

patch.finish()
