#!/usr/bin/env python3
"""
SYS-0070: Documentation update for patch system overhaul (Apr 11-12).

Surgical edits to two docs:

TODO.md:
  1. Header block: Last Updated, Current Focus, Latest Patches
  2. New "Recently Completed" section for Apr 11-12 work

ARCHITECTURE.md:
  1. Version header block: Last Updated, Current Patch
  2. Patch System section rewritten to reflect current reality
     (five streams, PatchBase, wrappers, passive monitor, patch-install,
     lessons learned from SYS-0063 through SYS-0069)

All other content in both files is left untouched.
"""
import sys
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

TODO_PATH = Path('/opt/mythos/docs/TODO.md')
ARCH_PATH = Path('/opt/mythos/docs/ARCHITECTURE.md')
BACKUP_DIR = Path('/tmp')


# ── TODO.md edits ─────────────────────────────────────────────────────────

OLD_TODO_HEADER = """# Mythos Project TODO & Roadmap

> **Last Updated:** 2026-04-02 15:30 EST
> **Current Focus:** Iris voice quality — LoRA fine-tuning exploration
> **Latest Patches:** NEU-0019 (anti-confab v4), SYS-0048 (alias consolidation + docs)
> **Default Model:** iris-deep:latest (FROM qwen3:32b, v4 Modelfile)"""

NEW_TODO_HEADER = """# Mythos Project TODO & Roadmap

> **Last Updated:** 2026-04-12 EST
> **Current Focus:** Patch system stabilized (privilege foundation + passive monitor + git integration)
> **Latest Patches:** SYS-0069 (session note), SYS-0068 (cp * cleanup), SYS-0067 (patch-install git), SYS-0066 (monitor passive mode), SYS-0063 (PatchBase wrapper migration), SYS-0062 (privilege foundation)
> **Default Model:** iris-deep:latest (FROM qwen3:32b, v4 Modelfile)"""

OLD_RECENT_COMPLETED_ANCHOR = """## ✅ Recently Completed

### 2026-04-02: Iris Voice Quality + Alias Consolidation"""

NEW_RECENT_COMPLETED_ANCHOR = """## ✅ Recently Completed

### 2026-04-11 → 2026-04-12: Patch System Overhaul

The patch pipeline underwent a full rework after discovering that the
auto-install monitor was silently running every patch as root, dropping
root-owned artifacts across `/opt/mythos/` and `/tmp/` and breaking
subsequent adge-run operations.

- [x] **SYS-0060:** Git permissions + sync recovery (pre-existing root-owned file cleanup)
- [x] **SYS-0062:** Privilege foundation — 8 root-owned wrappers at `/usr/local/libexec/mythos/`, narrow sudoers allowlist, unit allowlist file
- [x] **SYS-0063:** PatchBase framework migration — `sudo_wrapper()` + 11 convenience methods, `restart_service` migrated to wrapper, privilege-foundation sanity check in `begin()`
- [x] **SYS-0064:** Security cleanup attempt — shipped but rolled back due to buggy post-install verify (substring match false-positive on own comment lines). Replaced by SYS-0068.
- [x] **SYS-0066:** Monitor passive mode — `process_patch()` rewritten to only detect + notify via Telegram; never extract, install, git, or touch the zip. `patch-install.sh` absorbed the git snapshot/commit/tag/push work.
- [x] **SYS-0067:** Completed SYS-0066's `patch-install.sh` edits that were skipped by a buggy idempotency check (first-80-chars of `NEW` was identical to `OLD`). Fixed by matching a unique marker from the middle of new content.
- [x] **SYS-0068:** Security cleanup retry — `cp *` rule removed from `/etc/sudoers.d/mythos-monitor` with regex-based verify (active directives only, comments ignored). Includes self-escalation via existing sudoers rule and chown-back to adge for post-install cleanup.
- [x] **SYS-0069:** Session note smoke test — simplest possible patch (one `deploy_file` call), confirmed the entire pipeline is healthy end-to-end including git push
- [x] **.git/ cleanup:** 38 root-owned files in `/opt/mythos/.git/objects/` and `refs/heads/main` chowned back to adge (left behind by monitor-as-root runs of SYS-0063 and SYS-0064)
- [x] **/tmp/last_patch_* cleanup:** root-owned log files that were crashing every patch via `PatchLogger.write_logs()` chowned back to adge

**Key lessons locked in:**
- The monitor ran as `User=adge` but its `process_patch()` internally `sudo bash`ed the install script, making every auto-installed patch run as root. Passive-mode monitor eliminates this class of bug.
- Patches that escalate to root via `sudo bash install.sh` must either avoid touching `/opt/mythos/` git history from root, or `chown -R adge:adge /opt/mythos` as their final step. Root processes don't have adge's SSH agent, so `git push` fails silently from root.
- `py_compile` writes `.pyc` to `__pycache__/` next to the source; using `/tmp/` collides with pre-existing root-owned `/tmp/__pycache__/`. Use `tempfile.mkdtemp()` + `py_compile.compile(src, cfile=<path inside owned dir>)` to bypass cache resolution entirely.
- `shutil.move()` preserves the tempfile's restrictive default perms (0600). Call `shutil.copystat(target, tmp)` before the move when the target's existing perms must be retained.
- Idempotency markers must be drawn from content that appears ONLY in the NEW version, not from content shared with OLD. The first 80 characters of a `NEW` that just appends is identical to `OLD`.
- Post-install verifies against active-directive sudoers rules need regex (`^\\s*[^#].*NOPASSWD`), not substring matching. Comments referencing removed rules will otherwise false-positive.

### 2026-04-02: Iris Voice Quality + Alias Consolidation"""


# ── ARCHITECTURE.md edits ─────────────────────────────────────────────────

OLD_ARCH_HEADER = """# Mythos System Architecture
> **Version:** 6.2.0
> **Last Updated:** 2026-03-31
> **Host:** arcturus (Ubuntu 24.04)
> **Current Patch:** NEU-0013 (Iris Modelfile — baked identity)
> **Legacy Patch:** 0133 (last fully documented prior version)"""

NEW_ARCH_HEADER = """# Mythos System Architecture
> **Version:** 6.3.0
> **Last Updated:** 2026-04-12
> **Host:** arcturus (Ubuntu 24.04)
> **Current Patch:** SYS-0069 (patch system stabilized — monitor passive, privilege foundation live)
> **Legacy Patch:** NEU-0013 (Iris Modelfile — baked identity, last 6.2.0 state)"""

OLD_PATCH_SYSTEM_SECTION = """## 🔧 Patch System

### Monitor (auto-deploy path)
Watches `~/Downloads/` for patch zips. On detection: git snapshot → extract to `/opt/mythos/patches/` → `sudo bash install.sh` → git commit + tag → GitHub push.

**Service:** `mythos-patch-monitor.service`

### Patch Standard v2 (patch 0106+)
```
patch_NNNN_description/
├── install.sh          # 4-line bash wrapper
└── apply_patch.py      # All logic in pure Python
```

**install.sh (always exactly this):**
```bash
#!/bin/bash
set -e
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
sudo /opt/mythos/.venv/bin/python3 "$PATCH_DIR/apply_patch.py"
```

**apply_patch.py rules:**
- `str.replace()` for all edits — NEVER sed or bash heredocs
- Fail-fast if old string not found
- `py_compile` syntax check before service restart
- Auto-rollback if service fails to start
- Backup all files before modifying

### Stream Patch Naming (SYS-0003+)
```
{STREAM}-{NNNN}_{description}.zip

Examples:
  NEU-0001_awareness_loop.zip
  MNE-0001_backlog_schema.zip
  SYS-0004_architecture_update.zip
```

Legacy `patch_NNNN_*.zip` still works. See `docs/STREAMS.md` for ownership and counters.

### Tools
```bash
/opt/mythos/patches/scripts/get_next_patch_info.sh   # Next version
/opt/mythos/patches/scripts/validate_manifest.sh      # Validate manifest.json
/opt/mythos/docs/patch_system/AI_PATCH_GENERATION_GUIDE.md  # AI handoff guide
```"""

NEW_PATCH_SYSTEM_SECTION = """## 🔧 Patch System

Stabilized 2026-04-12 after the SYS-0060 through SYS-0069 overhaul.
The current pipeline is: manually drop zip into `~/Downloads/` →
passive monitor sends Telegram notification → user runs
`patch-install STREAM-NNNN` from an adge shell → patch-install handles
all git work → apply_patch.py runs the actual install as adge.

### The five streams

Every patch belongs to exactly one stream. Counter lookup: `mythos-diag streams`.

| Stream | Prefix | Owns |
|--------|--------|------|
| NEURO | NEU | Iris consciousness, Arcturian Grid, `/opt/mythos/neuro/`, `/opt/mythos/iris/` |
| LOGOS | LOG | Skills, orchestration, prompts, model routing |
| MNEMOS | MNE | Memory, conversations, voice, voice memos |
| SENSUS | SEN | Astrology, calendar, transits, sensory routines |
| SYSTEM | SYS | Cross-cutting infra — finance, workers, integrity, bot core, patch system, shared tables |

Registry: `/opt/mythos/docs/STREAMS.json` (machine-readable) and `STREAMS.md` (human-readable). Never hardcode patch numbers — always read from live `mythos-diag streams`.

### Privilege foundation (SYS-0062)

Eight root-owned wrappers at `/usr/local/libexec/mythos/` handle privileged operations. Each wrapper validates its own arguments; the wrapper is the security boundary, not sudoers.

| Wrapper | Purpose |
|---------|---------|
| `mythos-servicectl <action> <unit>` | systemctl on allowlisted units (reads `/etc/mythos/allowed-units.txt`) |
| `mythos-install-unit <basename>` | Deploy systemd unit from `/opt/mythos/systemd/` to `/etc/systemd/system/` |
| `mythos-install-cloudflared-config` | Deploy `/opt/mythos/cloudflared/config.yml` |
| `mythos-fix-ownership` | Recursive chown `/opt/mythos/` to adge:adge |
| `mythos-scan-perms` | Count non-adge-owned files under `/opt/mythos/` |
| `mythos-backup-git` | Timestamped `.git/` tar.gz in `/tmp/` |
| `mythos-clean-tmp-pack` | Remove stale `tmp_pack_*` files |
| `mythos-allowlist-append <unit>` | Atomically add unit to allowed-units.txt |

Sudoers allowlist at `/etc/sudoers.d/mythos-patches` grants passwordless invocation. SYS-0063 migrated `PatchBase` to expose all wrappers via convenience methods (`restart_service`, `install_systemd_unit`, `fix_ownership`, etc.).

### Passive monitor (SYS-0066)

`mythos-patch-monitor.service` (runs as `User=adge`) watches `~/Downloads/` but NEVER auto-installs. Behavior:

1. Detects patch zip by regex `^([A-Z]{3}-\\d{4}|patch_\\d{4})_.*\\.zip$`
2. Validates the zip is readable
3. Sends Telegram notification: `📦 Patch Detected — run: patch-install SYS-NNNN`
4. Returns. Does NOT copy, extract, git, or install. Zip stays in Downloads until the user acts.

The monitor also still handles bank CSVs, sales/shoe ingestion zips, and file cataloging (unchanged by SYS-0066).

### patch-install workflow

`/opt/mythos/bin/patch-install.sh` (sourced in `~/.bashrc`) is the one-and-only path to install a patch. Invocation: `patch-install SYS-NNNN [--clip] [--dry-run]`.

Phases:
1. Find zip in `~/Downloads/` matching `STREAM-NNNN*.zip`
2. Copy (not move) to `/opt/mythos/patches/archive/`
3. Extract to `/opt/mythos/patches/STREAM-NNNN_description/`
4. Pre-patch git snapshot: commit working tree if dirty, tag `pre-patch-<basename>-<timestamp>`
5. `chmod +x install.sh` and run it (plain `bash` — no sudo)
6. On success: `git add -A`, commit `Applied patch: ...`, read version from `manifest.json` or auto-increment, tag, `git push origin main --tags`
7. On failure: auto-rollback via `_patch_auto_rollback` reads `/tmp/STREAM-NNNN_result.json` and reverts files/STREAMS/PATCH_HISTORY/services

### Patch directory layout

```
{STREAM}-{NNNN}_{description}/
├── install.sh              # exactly 4 lines, calls apply_patch.py
├── apply_patch.py          # all logic via PatchBase
└── opt/mythos/...          # files to deploy, mirroring target paths
```

**install.sh (always this):**
```bash
#!/bin/bash
set -e
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
/opt/mythos/.venv/bin/python3 "$PATCH_DIR/apply_patch.py"
```

**apply_patch.py template:**
```python
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(stream='SYS', number=NN, description='...', patch_type='MINOR')
patch.begin()
patch.deploy_file('opt/mythos/some/file.py', '/opt/mythos/some/file.py')
patch.run_sql('opt/mythos/migrations/migration.sql')
patch.restart_service('mythos-bot.service')
patch.finish()
```

`patch.finish()` bumps `STREAMS.json` and writes `PATCH_HISTORY.md` automatically.

### Patches that need root

Some patches must write to `/etc/`, `/usr/`, or otherwise escalate beyond adge. Options, in order of preference:
1. **Use an existing SYS-0062 wrapper.** `install_systemd_unit`, `install_cloudflared_config`, etc.
2. **Self-escalate `install.sh` via the existing sudoers rule.** Add `if [ "$EUID" -ne 0 ]; then exec sudo -n bash "$0" "$@"; fi` after `set -e`. The `/etc/sudoers.d/mythos-monitor` rule `adge ALL=(ALL) NOPASSWD: /bin/bash /opt/mythos/patches/*/install.sh` grants passwordless root. In this case `apply_patch.py` MUST `chown -R adge:adge /opt/mythos` as its final step (in a `try/finally`) to avoid leaving root-owned git objects, docs, logs, or backups that break future adge-run operations.
3. **Do git ops from `patch-install`, not from root.** Root processes do not have adge's SSH agent — `git push` will fail silently from within a root-escalated `apply_patch.py`. Keep the privileged work narrow (just the file write), let `patch-install`'s post-phase handle git.

### Post-install pipeline

After `install.sh` exits successfully, `patch-install.sh` invokes `patch_base.post_install.run_pipeline()` which runs four steps:
1. **Integrity scan** — `python3 -m integrity scan` updates Neo4j file/function/table/service nodes
2. **Git commit + tag + push** — commits anything modified by the patch, tags `stream_NNNN`, pushes to `origin main --tags`
3. **Graph update** — optional, skipped if `integrity.graph` module not available
4. **Telegram notification** — sends patch summary to the bot

### PatchBase rules

- `str.replace()` for ALL in-place file edits — never `sed`, never heredocs, never `awk`
- Fail-fast if the anchor isn't found exactly once — `PatchBase.str_replace` raises on miss
- `py_compile` syntax check happens automatically before any service restart; rollback on failure
- Every modified file is backed up before the edit; auto-rollback restores backups on service failure
- Idempotency markers must come from content unique to the NEW version — first-80-chars doesn't count if NEW appends to OLD (see SYS-0067 lesson)
- In-memory edits using `tempfile.mkdtemp()` + explicit `py_compile.compile(src, cfile=...)` avoids `/tmp/__pycache__/` permission collisions
- `shutil.move()` preserves tempfile perms (usually 0600) — call `shutil.copystat(target, tmp)` first when target perms must be retained
- Never write to another stream's tables without declaring it in the patch; shared table migrations (people, transactions, system_manifest) go through SYS only
- All Telegram `/command` handler registrations go through SYS regardless of which stream owns the handler code
- CLI symlinks go to `/opt/mythos/bin/` only, never `/usr/local/bin/`
- Postgres connections use the Unix socket, never `host=localhost`

### Tools

```bash
mythos-diag streams                            # Live stream counters
patch-install SYS-NNNN                         # Install a patch from ~/Downloads/
patch-install SYS-NNNN --dry-run               # Validate without applying
patch-install SYS-NNNN --clip                  # Copy install output to clipboard
/opt/mythos/patches/scripts/patch_base.py      # PatchBase class + wrappers
```"""


def edit_file(patch, path, backup_path, edits, label):
    """Apply a list of (old, new) str.replace pairs to path. Each old must
    match exactly once. Atomic write with preserved perms."""
    if not path.is_file():
        patch.errors.append(f"{label}: not found at {path}")
        patch.logger.log(f"  ✗ {label}: not found")
        return False

    original = path.read_text()
    patch.logger.log(f"  · read {label} ({len(original.splitlines())} lines)")

    new_source = original
    for i, (old, new) in enumerate(edits, 1):
        count = new_source.count(old)
        if count != 1:
            patch.errors.append(f"{label} edit {i}: anchor matched {count} times, expected 1")
            patch.logger.log(f"  ✗ {label} edit {i}: anchor matched {count} times")
            return False
        new_source = new_source.replace(old, new)
        patch.logger.log(f"  ✓ {label} edit {i}: applied")

    if new_source == original:
        patch.logger.log(f"  ⊙ {label}: no changes (idempotent)")
        patch.validations.append(f"{label} no-op")
        return True

    # Backup
    shutil.copy2(str(path), str(backup_path))
    patch.logger.log(f"  ✓ backup → {backup_path}")

    # Write via owned tempdir
    tmp_dir = tempfile.mkdtemp(prefix='sys0070_')
    tmp_path = os.path.join(tmp_dir, path.name)
    try:
        with open(tmp_path, 'w') as f:
            f.write(new_source)
        shutil.copystat(str(path), tmp_path)
        shutil.move(tmp_path, str(path))
        patch.files_deployed.append(str(path))
        patch.logger.log(f"  ✓ {label}: atomic-moved into place ({len(new_source.splitlines())} lines)")
        return True
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main():
    patch = PatchBase(
        stream='SYS',
        number=70,
        description='docs update — patch system overhaul reflected in TODO.md + ARCHITECTURE.md',
        patch_type='MINOR',
    )
    patch.begin()

    ok_todo = edit_file(
        patch, TODO_PATH, BACKUP_DIR / 'TODO.md.pre_SYS-0070.bak',
        [
            (OLD_TODO_HEADER, NEW_TODO_HEADER),
            (OLD_RECENT_COMPLETED_ANCHOR, NEW_RECENT_COMPLETED_ANCHOR),
        ],
        label='TODO.md',
    )
    if not ok_todo:
        patch.finish()
        sys.exit(1)

    ok_arch = edit_file(
        patch, ARCH_PATH, BACKUP_DIR / 'ARCHITECTURE.md.pre_SYS-0070.bak',
        [
            (OLD_ARCH_HEADER, NEW_ARCH_HEADER),
            (OLD_PATCH_SYSTEM_SECTION, NEW_PATCH_SYSTEM_SECTION),
        ],
        label='ARCHITECTURE.md',
    )
    if not ok_arch:
        # TODO.md already applied — roll it back
        todo_bak = BACKUP_DIR / 'TODO.md.pre_SYS-0070.bak'
        if todo_bak.is_file():
            shutil.copy2(str(todo_bak), str(TODO_PATH))
            patch.logger.log("  ⊙ rolled back TODO.md from backup")
        patch.finish()
        sys.exit(1)

    patch.finish()


if __name__ == '__main__':
    main()
