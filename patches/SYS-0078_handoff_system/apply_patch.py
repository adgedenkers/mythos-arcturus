#!/usr/bin/env python3
"""
SYS-0078: Handoff System Bootstrap (Patch C.1 for Finance v2)

Implements the three-artifact handoff pattern from Gemini's review:
  - Generic tool: /opt/mythos/bin/mythos-handoff
  - Feature manifest: /opt/mythos/docs/finance/MANIFEST.yaml
  - Next-turn spec: /opt/mythos/docs/finance/NEXT_PATCH_SPEC.md

Also:
  - Deploys /opt/mythos/docs/finance/README.md
  - Edits WORKFLOW.md — replaces placeholder with real doc
  - Edits SYSTEM_FINANCE.md — collapses "Next Up" section to a pointer
    (full spec now lives in NEXT_PATCH_SPEC.md)

Installs PyYAML into the mythos venv if missing (mythos-handoff
needs it).

No schema, no service restarts.
"""
import os
import sys
import subprocess
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase


WORKFLOW_PATH = Path('/opt/mythos/docs/WORKFLOW.md')
SYSFIN_PATH = Path('/opt/mythos/docs/SYSTEM_FINANCE.md')
HANDOFF_BIN = Path('/opt/mythos/bin/mythos-handoff')

# ── WORKFLOW.md replacement ──────────────────────────────────────────
WORKFLOW_OLD = '''## Handoff diag script

*(Location and structure of the handoff diagnostic script is pending
external review. Will be specified in a follow-up doc patch once
settled.)*'''

WORKFLOW_NEW = '''## Handoff System (three-artifact pattern)

<!-- SYS-0078: handoff system documented -->

After Gemini review, the handoff is implemented as **three artifacts**
with different lifecycles, not a single monolithic script:

| Artifact | Path | Lifecycle |
|---|---|---|
| **Generic tool** | `/opt/mythos/bin/mythos-handoff` | Permanent, subsystem-agnostic. Updated rarely, when new capabilities are needed (e.g., "also pull Neo4j integrity state"). |
| **Feature manifest** | `docs/<n>/MANIFEST.yaml` | Versioned per feature. Updated when dependencies change (new tables, new validations). |
| **Next patch spec** | `docs/<n>/NEXT_PATCH_SPEC.md` | Rewritten wholesale each turn. Ephemeral content; history lives in `SYSTEM_<n>.md`. |

### Usage

```bash
mythos-handoff finance           # assemble payload, copy to clipboard
mythos-handoff finance --stdout  # write to stdout
mythos-handoff finance --file F  # write to file
mythos-handoff --list            # list available subsystems
```

The tool reads `docs/<subsystem>/MANIFEST.yaml`, then walks its
sections: docs to include, SQL queries to run, validations to assert,
integrity state to pull, and stream counters to report. The
assembled payload goes to the clipboard via `xclip`.

### Validation policy (soft warning)

If any manifest validation fails, the payload still gets assembled
and copied — but a bright `⚠⚠⚠ VALIDATION FAILURES ⚠⚠⚠` banner
appears at the top. Rationale: failures are information, and
sometimes you hand off *precisely because* something is broken and
you need Claude to fix it. Hard-blocking would prevent that.

### Adding a new subsystem

1. Create `docs/<n>/MANIFEST.yaml` (schema: see `docs/finance/MANIFEST.yaml` as reference)
2. Create `docs/<n>/NEXT_PATCH_SPEC.md`
3. `mythos-handoff <n>` auto-discovers it

The tool does not hardcode any subsystem names. `docs/<n>/` is the convention.'''


# ── SYSTEM_FINANCE.md replacement ────────────────────────────────────
# The SYS-0077 SYSTEM_FINANCE.md has a large "## Next Up: Patch D" section
# that runs until "## Open Questions". We replace the entire block with a
# pointer. Anchor is the exact unique header text from SYS-0077.
# The new block ends with "## Open Questions\n" so that downstream content
# is preserved intact.

SYSFIN_OLD_HEADER = '## Next Up: Patch D — Merchants + merchant_patterns'
SYSFIN_NEW_HEADER = '''## Next Up

<!-- SYS-0078: next-up collapsed to pointer -->
The full spec for the next patch lives in
[`docs/finance/NEXT_PATCH_SPEC.md`](finance/NEXT_PATCH_SPEC.md).
That file is rewritten wholesale at the end of every feature
patch, so it always describes exactly one patch ahead.

Run `mythos-handoff finance` to assemble the full handoff payload
(this doc + WORKFLOW + NEXT_PATCH_SPEC + live DB state + validations)
into your clipboard, ready to paste into a new conversation.'''


def collapse_next_up_section(patch: PatchBase) -> None:
    """Replace the entire 'Next Up' section in SYSTEM_FINANCE.md with a pointer.

    Anchor: lines from '## Next Up: Patch D' through (exclusive) '## Open Questions'.
    Idempotent via the marker in SYSFIN_NEW_HEADER.
    """
    path = SYSFIN_PATH
    if not path.exists():
        patch.errors.append(f"{path.name} not found")
        return
    content = path.read_text()

    marker = '<!-- SYS-0078: next-up collapsed to pointer -->'
    if marker in content:
        patch.validations.append(f"{path.name} next-up — already collapsed (idempotent)")
        patch.logger.log(f"  ✓ {path.name} already collapsed")
        return

    start_anchor = SYSFIN_OLD_HEADER
    end_anchor = '## Open Questions'
    start_idx = content.find(start_anchor)
    end_idx = content.find(end_anchor, start_idx + 1) if start_idx >= 0 else -1

    if start_idx < 0:
        patch.errors.append(f"{path.name}: Next Up header not found")
        patch.logger.log(f"  ✗ {path.name}: Next Up header missing")
        return
    if end_idx < 0:
        patch.errors.append(f"{path.name}: Open Questions header not found")
        patch.logger.log(f"  ✗ {path.name}: Open Questions header missing")
        return

    if patch.dry_run:
        patch.validations.append(f"{path.name} collapse — anchors unique, would succeed")
        patch.logger.log(f"  ✓ [validate] {path.name} anchors found")
        return

    backup = path.with_suffix(path.suffix + '.sys0078.bak')
    backup.write_text(content)

    updated = content[:start_idx] + SYSFIN_NEW_HEADER + '\n\n---\n\n' + content[end_idx:]
    if marker not in updated:
        patch.errors.append(f"{path.name} post-edit: marker missing")
        path.write_text(content)
        return

    path.write_text(updated)
    patch.files_deployed.append(str(path))
    patch.logger.log(f"  ✓ {path.name} Next Up section collapsed")


def install_pyyaml(patch: PatchBase) -> None:
    """Ensure PyYAML is available in the mythos venv."""
    if patch.dry_run:
        patch.validations.append("PyYAML install — skipped (dry run)")
        return
    try:
        r = subprocess.run(
            ['/opt/mythos/.venv/bin/python3', '-c', 'import yaml'],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            patch.validations.append("PyYAML already present in venv")
            patch.logger.log("  ✓ PyYAML already in venv")
            return
        # Install
        r = subprocess.run(
            ['/opt/mythos/.venv/bin/pip', 'install', '--quiet', 'pyyaml'],
            capture_output=True, text=True,
        )
        if r.returncode == 0:
            patch.validations.append("PyYAML installed into venv")
            patch.logger.log("  ✓ installed PyYAML into venv")
        else:
            patch.errors.append(f"PyYAML install failed: {r.stderr.strip()}")
            patch.logger.log(f"  ✗ PyYAML install: {r.stderr.strip()}")
    except Exception as e:
        patch.errors.append(f"PyYAML check/install: {e}")


def edit_file(patch: PatchBase, path: Path, old: str, new: str, marker: str) -> None:
    """Idempotent in-place edit with uniqueness check + backup."""
    if not path.exists():
        patch.errors.append(f"{path.name} not found at {path}")
        patch.logger.log(f"  ✗ {path.name} missing")
        return

    content = path.read_text()

    if marker in content:
        patch.validations.append(f"{path.name} edit — marker already present (idempotent)")
        patch.logger.log(f"  ✓ {path.name} already edited (idempotent skip)")
        return

    count = content.count(old)
    if count == 0:
        patch.errors.append(f"{path.name}: anchor not found — cannot edit")
        patch.logger.log(f"  ✗ {path.name}: anchor not found")
        return
    if count > 1:
        patch.errors.append(f"{path.name}: anchor appears {count}×, ambiguous")
        patch.logger.log(f"  ✗ {path.name}: anchor ambiguous ({count} matches)")
        return

    if patch.dry_run:
        patch.validations.append(f"{path.name} edit — anchor unique, would succeed")
        patch.logger.log(f"  ✓ [validate] {path.name} anchor unique")
        return

    backup = path.with_suffix(path.suffix + '.sys0078.bak')
    backup.write_text(content)
    patch.logger.log(f"  ✓ backed up {path.name} → {backup.name}")

    updated = content.replace(old, new, 1)
    if updated.count(marker) != 1:
        patch.errors.append(f"{path.name} post-edit: marker not exactly 1×")
        path.write_text(content)
        return

    path.write_text(updated)
    patch.files_deployed.append(str(path))
    patch.logger.log(f"  ✓ {path.name} edited")


def verify_handoff_tool(patch: PatchBase) -> None:
    """Sanity: tool is executable, --list works, finance manifest parses."""
    if not HANDOFF_BIN.exists():
        patch.errors.append(f"{HANDOFF_BIN} not deployed")
        return
    if not os.access(str(HANDOFF_BIN), os.X_OK):
        patch.errors.append(f"{HANDOFF_BIN} not executable")
        patch.logger.log(f"  ✗ {HANDOFF_BIN} not executable")
        return

    # Test --list
    r = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', str(HANDOFF_BIN), '--list'],
        capture_output=True, text=True,
    )
    if r.returncode == 0 and 'finance' in r.stdout:
        patch.validations.append("mythos-handoff --list discovers finance subsystem")
        patch.logger.log("  ✓ mythos-handoff --list sees finance")
    else:
        patch.errors.append(
            f"mythos-handoff --list failed: rc={r.returncode} "
            f"stdout={r.stdout!r} stderr={r.stderr!r}"
        )
        patch.logger.log(f"  ✗ mythos-handoff --list failed")

    # Test that manifest parses and tool assembles something (--stdout, don't need xclip)
    r = subprocess.run(
        ['/opt/mythos/.venv/bin/python3', str(HANDOFF_BIN), 'finance', '--stdout'],
        capture_output=True, text=True,
    )
    if r.returncode == 0 and 'SESSION CONTEXT' in r.stdout and 'END HANDOFF PAYLOAD' in r.stdout:
        size = len(r.stdout)
        patch.validations.append(f"mythos-handoff finance assembles payload ({size} bytes)")
        patch.logger.log(f"  ✓ mythos-handoff finance → {size} bytes")
    else:
        patch.errors.append(
            f"mythos-handoff finance failed: rc={r.returncode} stderr={r.stderr[:400]!r}"
        )
        patch.logger.log(f"  ✗ mythos-handoff finance failed")


def main():
    patch = PatchBase(
        stream='SYS',
        number=78,
        description='handoff system bootstrap — tool, manifest, spec',
        patch_type='MINOR',
    )
    patch.begin()

    # 1. Deploy the tool
    patch.deploy_file(
        'opt/mythos/bin/mythos-handoff',
        '/opt/mythos/bin/mythos-handoff',
    )

    # Ensure executable
    if not patch.dry_run and HANDOFF_BIN.exists():
        os.chmod(str(HANDOFF_BIN), 0o755)
        patch.logger.log(f"  ✓ chmod 755 {HANDOFF_BIN}")

    # 2. Deploy finance subsystem docs
    patch.deploy_file(
        'opt/mythos/docs/finance/MANIFEST.yaml',
        '/opt/mythos/docs/finance/MANIFEST.yaml',
    )
    patch.deploy_file(
        'opt/mythos/docs/finance/NEXT_PATCH_SPEC.md',
        '/opt/mythos/docs/finance/NEXT_PATCH_SPEC.md',
    )
    patch.deploy_file(
        'opt/mythos/docs/finance/README.md',
        '/opt/mythos/docs/finance/README.md',
    )

    # 3. Make sure PyYAML is available
    install_pyyaml(patch)

    # 4. Edit WORKFLOW.md — replace placeholder section
    if not patch.errors:
        edit_file(
            patch,
            WORKFLOW_PATH,
            WORKFLOW_OLD,
            WORKFLOW_NEW,
            '<!-- SYS-0078: handoff system documented -->',
        )

    # 5. Edit SYSTEM_FINANCE.md — collapse Next Up section to pointer
    if not patch.errors:
        collapse_next_up_section(patch)

    # 6. Verify tool works
    if not patch.dry_run and not patch.errors:
        verify_handoff_tool(patch)

    patch.finish()


if __name__ == '__main__':
    main()
