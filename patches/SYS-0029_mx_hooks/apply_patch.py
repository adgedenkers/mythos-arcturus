"""
SYS-0029: mx Pre/Post Hooks with Integrity Integration
- Deploys mx_hooks.py
- Patches mx_session.py to wrap significant commands with pre/post_flight
"""

import subprocess
import sys
import py_compile
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=29,
    description='mx pre/post hooks with integrity scan integration',
    patch_type='MINOR',
)
patch.begin()

PATCH_DIR = Path(__file__).parent

# ── 1. Deploy mx_hooks.py ─────────────────────────────────────────────────────

patch.deploy_file(
    str(PATCH_DIR / 'opt/mythos/mx/mx_hooks.py'),
    '/opt/mythos/mx/mx_hooks.py',
)
py_compile.compile('/opt/mythos/mx/mx_hooks.py', doraise=True)
print("  ✓ mx_hooks.py deployed and validated")

# ── 2. Patch mx_session.py — import mx_hooks ─────────────────────────────────

session_path = Path('/opt/mythos/mx/mx_session.py')
content = session_path.read_text()

# Add import inside main() alongside other late imports
old_imports = (
    "    from mx_intent import IntentResolver\n"
    "    from mx_logger import MxLogger\n"
    "    from mx_journal import MxJournal"
)
new_imports = (
    "    from mx_intent import IntentResolver\n"
    "    from mx_logger import MxLogger\n"
    "    from mx_journal import MxJournal\n"
    "    from mx_hooks import is_significant, pre_flight, post_flight"
)

if 'from mx_hooks import' not in content:
    assert old_imports in content, "Import anchor not found — run SYS-0027 first"
    content = content.replace(old_imports, new_imports)
    print("  ✓ Added mx_hooks import")

# ── 3. Wrap significant commands with pre/post flight ─────────────────────────
# Replace the execute block to check is_significant() first

old_execute = (
    "        logger.log_command(raw, resolved, intent_key)\n"
    "\n"
    "        # ── Execute ────────────────────────────────────────────────────────\n"
    "        ec, stdout, stderr = run_command(resolved)\n"
    "        logger.log_result(ec, stdout, stderr)\n"
    "\n"
    "        if stdout.strip():\n"
    "            print(stdout.rstrip())\n"
    "        if stderr.strip():\n"
    "            print(f\"{DIM}{stderr.rstrip()}{RESET}\", file=sys.stderr)"
)

new_execute = (
    "        logger.log_command(raw, resolved, intent_key)\n"
    "\n"
    "        # ── Execute (with pre/post hooks for significant operations) ───────\n"
    "        pre_snap_path = None\n"
    "        pre_snap_data = None\n"
    "        if is_significant(resolved):\n"
    "            try:\n"
    "                pre_snap_path, pre_snap_data = pre_flight(resolved, journal)\n"
    "            except Exception as _hook_err:\n"
    "                print(f\"{YELLOW}  ⚠ Pre-flight warning: {_hook_err}{RESET}\")\n"
    "\n"
    "        ec, stdout, stderr = run_command(resolved)\n"
    "        logger.log_result(ec, stdout, stderr)\n"
    "\n"
    "        if stdout.strip():\n"
    "            print(stdout.rstrip())\n"
    "        if stderr.strip():\n"
    "            print(f\"{DIM}{stderr.rstrip()}{RESET}\", file=sys.stderr)"
)

if 'pre_snap_path = None' not in content:
    assert old_execute in content, "Execute anchor not found — check mx_session.py"
    content = content.replace(old_execute, new_execute)
    print("  ✓ Wrapped execute block with pre-flight hook")

# ── 4. Add post-flight after the heal block ───────────────────────────────────

old_heal_block = (
    "        if ec != 0 and heal_enabled and not should_suppress(resolved, config.get(\"suppress_heal\", [])):\n"
    "            healed = heal(resolved, ec, stdout, stderr, buffer, model, config, logger)\n"
    "            journal.record_heal(healed)"
)

new_heal_block = (
    "        if ec != 0 and heal_enabled and not should_suppress(resolved, config.get(\"suppress_heal\", [])):\n"
    "            healed = heal(resolved, ec, stdout, stderr, buffer, model, config, logger)\n"
    "            journal.record_heal(healed)\n"
    "\n"
    "        # Post-flight for significant operations\n"
    "        if pre_snap_path and pre_snap_data:\n"
    "            try:\n"
    "                post_flight(resolved, pre_snap_path, pre_snap_data, journal)\n"
    "            except Exception as _hook_err:\n"
    "                print(f\"{YELLOW}  ⚠ Post-flight warning: {_hook_err}{RESET}\")"
)

if 'post_flight(resolved' not in content:
    assert old_heal_block in content, "Heal block anchor not found"
    content = content.replace(old_heal_block, new_heal_block)
    print("  ✓ Added post-flight hook after heal block")

session_path.write_text(content)
py_compile.compile(str(session_path), doraise=True)
print("  ✓ mx_session.py patched and validated")

# ── Done ──────────────────────────────────────────────────────────────────────

patch.finish()

print()
print("╔══════════════════════════════════════════════════╗")
print("║  SYS-0029: mx Hooks ready.                       ║")
print("║                                                  ║")
print("║  Significant commands now trigger:               ║")
print("║    📸 Pre-flight integrity scan + snapshot        ║")
print("║    📸 Post-operation integrity scan + snapshot    ║")
print("║    ── Delta report                               ║")
print("║    ⚠  Rollback offer on regressions              ║")
print("║                                                  ║")
print("║  Triggers: patch-install, systemctl restart,     ║")
print("║            psql migrations, ALTER/CREATE TABLE   ║")
print("╚══════════════════════════════════════════════════╝")
