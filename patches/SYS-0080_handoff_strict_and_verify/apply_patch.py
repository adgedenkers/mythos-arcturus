#!/usr/bin/env python3
"""
SYS-0080: Handoff strict mode + PatchBase.verify_handoff() helper

Fixes the structural fragility exposed by SYS-0079's false-positive
self-check. Two in-place edits:

1. /opt/mythos/bin/mythos-handoff — add --strict flag. When set, any
   validation failure produces exit code 1. Default behavior (exit 0
   regardless) preserved for interactive use.

2. /opt/mythos/patches/scripts/patch_base.py — add
   PatchBase.verify_handoff(subsystem) helper method. Shells out to
   `mythos-handoff <subsystem> --strict`, captures exit code and
   failed-validation list, appends to patch.validations or
   patch.errors as appropriate. Standard cowpath for all future
   patches that touch a manifest.

This patch dogfoods its own helper by calling
self.verify_handoff('finance') as its own verification step.

No docs changes — those ship in SYS-0081 after another review round.

Per Gemini review of SYS-0080 approach: approved as implemented,
split from process patch per recommendation.
"""
import sys
import os
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase


HANDOFF_BIN = Path('/opt/mythos/bin/mythos-handoff')
PATCHBASE = Path('/opt/mythos/patches/scripts/patch_base.py')


# ═══════════════════════════════════════════════════════════════════════
# Edit 1: mythos-handoff — add --strict flag
# ═══════════════════════════════════════════════════════════════════════

HANDOFF_ARG_OLD = """    ap.add_argument('--stdout', action='store_true', help='write to stdout instead of clipboard')
    ap.add_argument('--file', help='write to file instead of clipboard')
    args = ap.parse_args()"""

HANDOFF_ARG_NEW = """    ap.add_argument('--stdout', action='store_true', help='write to stdout instead of clipboard')
    ap.add_argument('--file', help='write to file instead of clipboard')
    ap.add_argument('--strict', action='store_true',
                    help='exit 1 on validation failure (default: soft warning, exit 0)')
    args = ap.parse_args()"""

# Replace the final exit block so --strict produces exit 1 on failures.
HANDOFF_EXIT_OLD = """    if failed:
        print(f"⚠ {len(failed)} validation(s) FAILED — banner is at top of payload",
              file=sys.stderr)
        for f in failed:
            print(f"  ✗ {f}", file=sys.stderr)
        # Soft warning — exit 0 anyway so scripts don't break
    sys.exit(0)"""

HANDOFF_EXIT_NEW = """    if failed:
        print(f"⚠ {len(failed)} validation(s) FAILED — banner is at top of payload",
              file=sys.stderr)
        for f in failed:
            print(f"  ✗ {f}", file=sys.stderr)
        if args.strict:
            # SYS-0080: strict mode for programmatic callers
            sys.exit(1)
        # Default: soft warning, exit 0 so interactive use isn't broken
    sys.exit(0)"""


# ═══════════════════════════════════════════════════════════════════════
# Edit 2: patch_base.py — add verify_handoff() helper method
# ═══════════════════════════════════════════════════════════════════════

# We anchor on the end of restart_service(). Just before the
# "── Privilege wrappers" comment block, we insert verify_handoff().
PATCHBASE_ANCHOR = """    # ── Privilege wrappers (SYS-0062 / SYS-0063) ──────────────────────────────"""

PATCHBASE_HELPER = '''    # ── Handoff verification (SYS-0080) ────────────────────────────────────────

    def verify_handoff(self, subsystem: str) -> bool:
        """Verify a subsystem handoff is clean by running mythos-handoff --strict.

        Shells out to `mythos-handoff <subsystem> --strict`. Exit 0 means all
        validations passed; exit 1 means at least one failed. Captures stderr
        for the failed-validation names and appends to patch.validations or
        patch.errors as appropriate.

        Returns True if handoff is clean, False otherwise.

        Dry-run mode: validates the tool and manifest exist, but does not
        actually run the handoff (since DB state may not reflect the
        in-progress patch's changes yet).

        This is the canonical self-verification path for any patch that
        touches a handoff manifest. Use it instead of substring-matching
        against mythos-handoff stdout — substring matches are structurally
        fragile because the payload includes docs that may themselves
        contain strings like 'VALIDATION FAILURES'.
        """
        import subprocess as _sp
        tool = '/opt/mythos/bin/mythos-handoff'
        manifest = f'/opt/mythos/docs/{subsystem}/MANIFEST.yaml'

        if self.dry_run:
            if not os.path.isfile(tool):
                self.errors.append(f"verify_handoff: {tool} not found")
                return False
            if not os.path.isfile(manifest):
                self.errors.append(f"verify_handoff: {manifest} not found")
                return False
            self.validations.append(f"verify_handoff({subsystem}) — tool+manifest exist")
            self.logger.log(f"  ✓ [validate] verify_handoff({subsystem}) — tool+manifest exist")
            return True

        if not os.path.isfile(tool):
            self.errors.append(f"verify_handoff({subsystem}): tool missing: {tool}")
            self.logger.log(f"  ✗ verify_handoff: tool missing")
            return False
        if not os.path.isfile(manifest):
            self.errors.append(f"verify_handoff({subsystem}): manifest missing: {manifest}")
            self.logger.log(f"  ✗ verify_handoff: manifest missing")
            return False

        try:
            result = _sp.run(
                ['/opt/mythos/.venv/bin/python3', tool, subsystem, '--strict', '--stdout'],
                capture_output=True, text=True, timeout=120,
            )
        except Exception as e:
            self.errors.append(f"verify_handoff({subsystem}): subprocess failed: {e}")
            self.logger.log(f"  ✗ verify_handoff({subsystem}): {e}")
            return False

        if result.returncode == 0:
            self.validations.append(f"verify_handoff({subsystem}) — all validations passed")
            self.logger.log(f"  ✓ verify_handoff({subsystem}) — clean")
            return True

        # Failure — parse stderr for the failed validation names
        failed_names = []
        for line in (result.stderr or '').splitlines():
            line = line.strip()
            if line.startswith('✗ '):
                failed_names.append(line[2:].strip())

        detail = ', '.join(failed_names) if failed_names else 'see tool stderr'
        self.errors.append(f"verify_handoff({subsystem}) FAILED: {detail}")
        self.logger.log(f"  ✗ verify_handoff({subsystem}): {detail}")
        return False

    # ── Privilege wrappers (SYS-0062 / SYS-0063) ──────────────────────────────'''


# ═══════════════════════════════════════════════════════════════════════
# Generic in-place editor with uniqueness + backup + rollback
# ═══════════════════════════════════════════════════════════════════════

def edit_file(patch: PatchBase, path: Path, old: str, new: str,
              marker: str, label: str) -> bool:
    """Idempotent str.replace edit. Returns True on success or idempotent skip."""
    if not path.exists():
        patch.errors.append(f"{label}: {path} not found")
        patch.logger.log(f"  ✗ {label}: missing")
        return False

    content = path.read_text()

    if marker in content:
        patch.validations.append(f"{label} — marker present, idempotent skip")
        patch.logger.log(f"  ✓ {label} already patched (idempotent)")
        return True

    count = content.count(old)
    if count == 0:
        patch.errors.append(f"{label}: anchor not found")
        patch.logger.log(f"  ✗ {label}: anchor missing")
        return False
    if count > 1:
        patch.errors.append(f"{label}: anchor appears {count}× (ambiguous)")
        patch.logger.log(f"  ✗ {label}: anchor ambiguous ({count}×)")
        return False

    if patch.dry_run:
        patch.validations.append(f"{label} — anchor unique, would succeed")
        patch.logger.log(f"  ✓ [validate] {label}")
        return True

    backup = path.with_suffix(path.suffix + '.sys0080.bak')
    backup.write_text(content)
    patch.logger.log(f"  ✓ backed up {path.name} → {backup.name}")

    updated = content.replace(old, new, 1)
    if marker not in updated:
        patch.errors.append(f"{label}: post-edit marker missing, rolled back")
        path.write_text(content)
        patch.logger.log(f"  ✗ {label}: post-edit sanity fail, rolled back")
        return False

    # Python syntax check for .py files
    if path.suffix == '.py' or path.name == 'mythos-handoff':
        import py_compile, tempfile
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tf:
                tf.write(updated)
                tf_path = tf.name
            py_compile.compile(tf_path, doraise=True)
            os.unlink(tf_path)
        except py_compile.PyCompileError as e:
            patch.errors.append(f"{label}: post-edit syntax error, rolled back: {e}")
            path.write_text(content)
            patch.logger.log(f"  ✗ {label}: syntax error, rolled back")
            try: os.unlink(tf_path)
            except Exception: pass
            return False

    path.write_text(updated)
    patch.files_deployed.append(str(path))
    patch.logger.log(f"  ✓ {label}")
    return True


def verify_strict_flag(patch: PatchBase) -> None:
    """Run mythos-handoff finance --strict and confirm exit 0."""
    if patch.dry_run:
        return
    import subprocess
    try:
        r = subprocess.run(
            ['/opt/mythos/.venv/bin/python3', str(HANDOFF_BIN),
             'finance', '--strict', '--stdout'],
            capture_output=True, text=True, timeout=120,
        )
        if r.returncode == 0:
            size = len(r.stdout)
            patch.validations.append(
                f"mythos-handoff finance --strict → exit 0 ({size} bytes)"
            )
            patch.logger.log(f"  ✓ --strict mode: exit 0, {size} bytes")
        else:
            patch.errors.append(
                f"mythos-handoff finance --strict → exit {r.returncode}; "
                f"stderr: {r.stderr[:400]}"
            )
            patch.logger.log(f"  ✗ --strict mode: exit {r.returncode}")
    except Exception as e:
        patch.errors.append(f"--strict verification: {e}")


def main():
    patch = PatchBase(
        stream='SYS',
        number=80,
        description='handoff --strict flag + PatchBase.verify_handoff() helper',
        patch_type='MINOR',
    )
    patch.begin()

    # ── Edit 1: mythos-handoff arg parser ──
    ok1 = edit_file(
        patch, HANDOFF_BIN, HANDOFF_ARG_OLD, HANDOFF_ARG_NEW,
        marker="action='store_true',\n                    help='exit 1 on validation failure",
        label="mythos-handoff: add --strict arg",
    )

    # ── Edit 2: mythos-handoff exit semantics ──
    if ok1:
        edit_file(
            patch, HANDOFF_BIN, HANDOFF_EXIT_OLD, HANDOFF_EXIT_NEW,
            marker="# SYS-0080: strict mode for programmatic callers",
            label="mythos-handoff: --strict exit semantics",
        )

    # ── Edit 3: patch_base.py — add verify_handoff() helper ──
    if not patch.errors:
        edit_file(
            patch, PATCHBASE, PATCHBASE_ANCHOR, PATCHBASE_HELPER,
            marker="# ── Handoff verification (SYS-0080)",
            label="patch_base.py: add verify_handoff()",
        )

    # ── Live verification of --strict flag ──
    if not patch.errors and not patch.dry_run:
        verify_strict_flag(patch)

    # ── Dogfood verify_handoff() by importing the fresh patch_base ──
    # Since we just edited patch_base.py in place, the already-imported
    # PatchBase in this process is stale. We use importlib to reload it
    # and call the new method, proving end-to-end that the helper works.
    if not patch.errors and not patch.dry_run:
        try:
            import importlib
            import patch_base as pb_module
            importlib.reload(pb_module)
            if hasattr(pb_module.PatchBase, 'verify_handoff'):
                patch.validations.append(
                    "PatchBase.verify_handoff() method present after reload"
                )
                patch.logger.log("  ✓ verify_handoff() attribute present after reload")
                # Actually invoke it against finance
                ok = pb_module.PatchBase.verify_handoff(patch, 'finance')
                if ok:
                    patch.logger.log("  ✓ dogfood: self.verify_handoff('finance') → clean")
                else:
                    patch.logger.log("  ⚠ dogfood: verify_handoff returned False")
            else:
                patch.errors.append(
                    "PatchBase.verify_handoff() not found after reload — "
                    "edit may have landed in wrong location"
                )
        except Exception as e:
            patch.errors.append(f"dogfood verify_handoff import: {e}")
            patch.logger.log(f"  ⚠ dogfood reload failed: {e}")

    patch.finish()


if __name__ == '__main__':
    main()
