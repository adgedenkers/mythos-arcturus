#!/usr/bin/env python3
"""
SYS-0067: Finish SYS-0066's patch-install.sh migration.

SYS-0066 successfully migrated the monitor to passive mode, but a bug in
the idempotency check caused the patch-install.sh edits to be skipped
with a false-positive "already migrated" match. (The first 80 chars of
NEW_CHMOD_ANCHOR are identical to OLD_CHMOD_ANCHOR because the edit
appends after an existing anchor.)

This patch applies the two patch-install.sh edits that SYS-0066 missed:
  1. Pre-patch git snapshot after chmod +x
  2. Post-install git commit + tag + push after "✅ $patch_id installed"

Idempotency is checked via a unique marker that ONLY appears in the new
content: "# ── SYS-0066: Pre-patch git snapshot" — appears in neither
the original file nor anywhere else.

No services restarted. Pure shell-script edit.
"""
import sys
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

TARGET = Path('/opt/mythos/bin/patch-install.sh')
BACKUP = Path('/tmp/patch-install.sh.pre_SYS-0067.bak')

UNIQUE_MARKER = "# ── SYS-0066: Pre-patch git snapshot"

OLD_CHMOD_ANCHOR = '''    # Make install.sh executable
    chmod +x "$patch_dir/install.sh" 2>/dev/null'''

NEW_CHMOD_ANCHOR = '''    # Make install.sh executable
    chmod +x "$patch_dir/install.sh" 2>/dev/null
    # ── SYS-0066: Pre-patch git snapshot ──────────────────────────────────
    local ts=$(date +%Y%m%d_%H%M%S)
    local pre_tag="pre-patch-${base_name}-${ts}"
    if cd "$mythos_root" 2>/dev/null; then
        if [ -d .git ]; then
            if [ -n "$(git status --porcelain 2>/dev/null)" ]; then
                git add -A >/dev/null 2>&1
                git commit -m "Auto-commit before ${pre_tag}" >/dev/null 2>&1
            fi
            git tag -a "$pre_tag" -m "State before $base_name" >/dev/null 2>&1 && \\
                echo "  📌 Git snapshot: $pre_tag"
        fi
        cd - >/dev/null 2>&1
    fi'''

OLD_SUCCESS_ANCHOR = '''    if [ $exit_code -eq 0 ]; then
        echo "✅ $patch_id installed"
    else'''

NEW_SUCCESS_ANCHOR = '''    if [ $exit_code -eq 0 ]; then
        echo "✅ $patch_id installed"
        # ── SYS-0066: Post-install git commit + tag + push ───────────────
        if cd "$mythos_root" 2>/dev/null; then
            if [ -d .git ]; then
                git add -A >/dev/null 2>&1
                if [ -n "$(git status --porcelain --cached 2>/dev/null)" ]; then
                    git commit -m "Applied patch: ${base_name}.zip" >/dev/null 2>&1 && \\
                        echo "  📌 Git: committed patch changes"
                fi
                local new_version=""
                if [ -f "$patch_dir/manifest.json" ]; then
                    new_version=$(python3 -c "
import json, sys
try:
    m = json.load(open('$patch_dir/manifest.json'))
    v = (m.get('versioning', {}).get('new_system_version')
         or m.get('patch', {}).get('semantic_version'))
    if v and not v.startswith('v'):
        v = 'v' + v
    print(v or '')
except Exception:
    print('')
" 2>/dev/null)
                fi
                if [ -z "$new_version" ]; then
                    local current=$(git tag -l 'v*' --sort=-v:refname 2>/dev/null | head -1)
                    [ -z "$current" ] && current="v0.0.0"
                    new_version=$(python3 -c "
import re
m = re.match(r'v(\\d+)\\.(\\d+)\\.(\\d+)', '$current')
if m:
    a, b, c = map(int, m.groups())
    print(f'v{a}.{b}.{c+1}')
else:
    print('v1.0.0')
" 2>/dev/null)
                fi
                if [ -n "$new_version" ]; then
                    git tag -a "$new_version" -m "After applying ${base_name}.zip" >/dev/null 2>&1 && \\
                        echo "  📌 Git: tagged $new_version"
                    echo "${new_version#v}" > "$mythos_root/.version"
                fi
                if git remote get-url origin >/dev/null 2>&1; then
                    if git push origin main --tags >/dev/null 2>&1; then
                        echo "  📌 Git: pushed to origin/main"
                    else
                        echo "  ⚠ Git push failed (check SSH / network)"
                    fi
                fi
            fi
            cd - >/dev/null 2>&1
        fi
    else'''


def main():
    patch = PatchBase(
        stream='SYS',
        number=67,
        description='finish SYS-0066 patch-install.sh git integration',
        patch_type='PATCH',
    )
    patch.begin()

    if not TARGET.is_file():
        patch.errors.append(f"{TARGET} not found")
        patch.logger.log(f"  ✗ {TARGET} not found")
        patch.finish()
        sys.exit(1)

    original = TARGET.read_text()
    patch.logger.log(f"  · read {TARGET.name} ({len(original.splitlines())} lines)")

    # Unique-marker idempotency check
    if UNIQUE_MARKER in original:
        patch.logger.log(f"  ⊙ already migrated (found unique marker)")
        patch.validations.append("patch-install.sh already has SYS-0066 git integration")
        patch.finish()
        return

    # Verify anchors
    new_source = original
    for i, (old, new) in enumerate(
        [(OLD_CHMOD_ANCHOR, NEW_CHMOD_ANCHOR),
         (OLD_SUCCESS_ANCHOR, NEW_SUCCESS_ANCHOR)], 1):
        count = new_source.count(old)
        if count != 1:
            patch.errors.append(f"edit {i}: anchor matched {count} times, expected 1")
            patch.logger.log(f"  ✗ edit {i}: anchor matched {count} times")
            patch.finish()
            sys.exit(1)
        new_source = new_source.replace(old, new)
        patch.logger.log(f"  ✓ edit {i}: applied")

    # Backup
    if patch.dry_run:
        patch.logger.log(f"  · [dry run] would backup → {BACKUP}")
    else:
        shutil.copy2(str(TARGET), str(BACKUP))
        patch.logger.log(f"  ✓ backup → {BACKUP}")

    # Tempdir + bash -n in a dir we own
    tmp_dir = tempfile.mkdtemp(prefix='sys0067_')
    tmp_path = os.path.join(tmp_dir, TARGET.name)
    try:
        with open(tmp_path, 'w') as f:
            f.write(new_source)

        r = subprocess.run(['/bin/bash', '-n', tmp_path], capture_output=True, text=True)
        if r.returncode != 0:
            patch.errors.append(f"bash -n failed: {r.stderr.strip()}")
            patch.logger.log(f"  ✗ bash -n failed: {r.stderr.strip()}")
            patch.finish()
            sys.exit(1)
        patch.logger.log(f"  ✓ bash -n passed")

        # Verify the unique marker is now present
        if UNIQUE_MARKER not in new_source:
            patch.errors.append("post-edit check: unique marker missing")
            patch.logger.log(f"  ✗ post-edit: unique marker missing (should never happen)")
            patch.finish()
            sys.exit(1)
        patch.logger.log(f"  ✓ unique marker present in new content")

        if patch.dry_run:
            patch.logger.log(f"  · [dry run] would atomic-move → {TARGET}")
            patch.validations.append("dry-run OK")
            patch.finish()
            return

        shutil.copystat(str(TARGET), tmp_path)
        shutil.move(tmp_path, str(TARGET))
        patch.files_deployed.append(str(TARGET))
        patch.logger.log(f"  ✓ atomic-moved → {TARGET}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

    # Post-install sanity: grep the deployed file for the marker
    final = TARGET.read_text()
    if UNIQUE_MARKER in final:
        patch.logger.log(f"  ✓ post-install verify: marker present in deployed file")
        patch.validations.append("marker present after install")
    else:
        patch.errors.append("post-install verify: marker missing from deployed file")
        patch.logger.log(f"  ✗ post-install verify FAILED")
        if BACKUP.is_file():
            shutil.copy2(str(BACKUP), str(TARGET))
            patch.logger.log(f"  ⊙ restored from backup")

    patch.finish()


if __name__ == '__main__':
    main()
