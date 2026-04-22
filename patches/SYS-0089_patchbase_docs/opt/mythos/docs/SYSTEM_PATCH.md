---
title: "Mythos Patch System — Current State"
category: system
status: active
stream: SYS
location: docs
tags: [patch, patchbase, infrastructure, system]
created: 2026-04-21
updated: 2026-04-21
author: Adge Denkers
---

# Mythos Patch System — Current State

> **Three-doc pattern:** This file = current state. `PATCH_HISTORY.md` = full ledger.
> No separate design doc — the patch system is stable infrastructure, not an active build.

> **Version:** stable (SYS-0087)
> **Last Updated:** 2026-04-21
> **Current Patch:** SYS-0089 (docs update — patch system + PatchBase microtool kit)

---

## Overview

Every code change, schema migration, or service update on Arcturus ships as a **patch** — a zip
file with a strict structure that installs via `patch-install`. PatchBase is the Python base class
that every `apply_patch.py` uses. The post-install pipeline runs integrity scan, git commit/tag/push,
and Telegram notification automatically after every successful install.

---

## PatchBase API Reference

**Import:**
```python
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase
```

**Constructor:**
```python
patch = PatchBase(
    stream='SYS',        # NEU | LOG | MNE | SEN | SYS
    number=88,           # integer — always from mythos-diag streams, never hardcoded
    description='...',   # short description for logs and PATCH_HISTORY
    patch_type='MINOR',  # MAJOR | MINOR | PATCH
    review_link=None,    # optional URL to Castor/review artifact
)
```

---

### Core Lifecycle

#### `patch.begin()`
Opens the patch. Logs the patch ID, description, and privilege-foundation status.
**Always the first call after construction.**

#### `patch.finish()`
Closes the patch. Runs post-install pipeline, bumps `STREAMS.json`, writes `PATCH_HISTORY.md`.
Raises `PatchFinishError` (exit 1) if any errors accumulated.
**Always the last call. Never omit.**

---

### File Operations

#### `patch.deploy_file(source_rel, target_abs)`
Copy a file from the patch directory to Arcturus.
- `source_rel`: path relative to the patch root, e.g. `'opt/mythos/some/file.py'`
- `target_abs`: absolute path on Arcturus, e.g. `'/opt/mythos/some/file.py'`
- Creates parent directories automatically. No sudo needed (`/opt/mythos/` is adge:adge owned).
- Dry-run: validates source exists and target is writable.

```python
patch.deploy_file('opt/mythos/skills/data/my_skill.py', '/opt/mythos/skills/data/my_skill.py')
```

#### `patch.str_replace(target_abs, old, new, label=None)` ← SYS-0087
**Canonical in-place file edit.** Replaces the hand-rolled `edit_file()` / `apply_edit()` boilerplate.

Guarantees:
- Fails if `old` appears **0 times** (anchor not found — patch aborts)
- Fails if `old` appears **>1 times** (anchor ambiguous — patch aborts)
- Backs up the file before writing (suffix: `.{patch_id_lower}.bak`)
- Verifies the edit landed and `old` is gone after write
- Runs `py_compile` automatically for `.py` files — rolls back on syntax error
- Appends to `files_deployed` on success
- Dry-run: validates anchor presence, no writes

```python
patch.str_replace(
    '/opt/mythos/telegram_bot/mythos_bot.py',
    old='from handlers.old_handler import old_fn',
    new='from handlers.old_handler import old_fn\nfrom handlers.new_handler import new_fn',
    label='import new handler',
)
```

#### `patch.append_to_file(target_abs, content, guard=None, label=None)` ← SYS-0087
Append content to a file. If `guard` string is provided, skips if already present (idempotency).
Backs up before writing.

```python
patch.append_to_file(
    '/opt/mythos/docs/TODO.md',
    '\n### SYS-0088 notes\n- docs updated\n',
    guard='SYS-0088 notes',
)
```

#### `patch.prepend_to_file(target_abs, content, guard=None, label=None)` ← SYS-0087
Same contract as `append_to_file` but writes at the top of the file.

#### `patch.ensure_line_in_file(target_abs, line, after=None, label=None)` ← SYS-0087
Ensures a single line exists in a file. Idempotent — skips if line already present anywhere.
If `after` anchor is given, inserts the line immediately after the first line containing it.
Otherwise appends to end of file.

```python
# Insert after a specific anchor line
patch.ensure_line_in_file(
    '/opt/mythos/telegram_bot/mythos_bot.py',
    'application.add_handler(CommandHandler("newcmd", new_handler))',
    after='application.add_handler(CommandHandler("existingcmd"',
    label='register /newcmd',
)
```

#### `patch.read_file(target_abs, label=None)` ← SYS-0087
Returns file contents as `str`, or `None` + error on missing file.
Use instead of `Path(x).read_text()` when you want clean error logging.

```python
content = patch.read_file('/opt/mythos/docs/TODO.md')
if content is None:
    patch.finish(); sys.exit(1)
```

---

### Validation & Assertions

#### `patch.assert_file_exists(target_abs, label=None)` ← SYS-0087
Returns `True` if file exists. Returns `False` and adds to `self.errors` if not.
Use at phase gates before operating on required files.

```python
if not patch.assert_file_exists('/opt/mythos/astrology/spiral/transit_pressure.py'):
    patch.finish(); sys.exit(1)
```

#### `patch.py_compile_check(target_abs, label=None)` ← SYS-0087
Explicit `py_compile` gate. Use after `deploy_file()` of a `.py` you want to validate before
a service restart. (`str_replace` runs this automatically — use this only for deployed files.)

```python
patch.deploy_file('opt/mythos/some/script.py', '/opt/mythos/some/script.py')
if not patch.py_compile_check('/opt/mythos/some/script.py'):
    patch.finish(); sys.exit(1)
patch.restart_service('mythos-api.service')
```

#### `patch.run_python_check(code, label, timeout=30)` ← SYS-0087
Run a Python snippet in the Mythos venv and assert it succeeds (exit 0).
`sys.path.insert(0, '/opt/mythos')` is prepended automatically — Mythos modules are importable.
Replaces the `subprocess.run([VENV_PYTHON, '-c', ...])` verification pattern.

```python
patch.run_python_check(
    code=(
        "from astrology.spiral.transit_pressure import _load_natal_positions\n"
        "pos = _load_natal_positions(9)\n"
        "assert len(pos) >= 9, f'only {len(pos)} positions'\n"
        "print(f'  positions: {len(pos)}')\n"
    ),
    label='natal positions load',
    timeout=30,
)
```

---

### SQL

#### `patch.run_sql(sql_rel)`
Run a SQL migration from the patch directory.
- `sql_rel`: path relative to patch root, e.g. `'opt/mythos/migrations/SYS-0088_schema.sql'`
- Dry-run: wraps in `BEGIN/ROLLBACK` to validate syntax without committing.
- Appends to `sql_run` on success.

```python
patch.run_sql('opt/mythos/migrations/SYS-0088_schema.sql')
```

---

### Services

#### `patch.restart_service(service_name)`
Restart a systemd service via the privilege wrapper. Backs up deployed files and auto-rolls
back on failure. Appends to `services_restarted` on success.

#### `patch.start_service(service_name)` / `patch.stop_service(service_name)`
Start or stop a service without full restart. Used when sequencing stop→start explicitly.

#### `patch.is_service_active(service_name) → bool`
Returns `True` if the service is currently `active`. Use after start/restart to verify health.

#### `patch.install_systemd_unit(basename)`
Deploy a `.service` file from `/opt/mythos/systemd/` to `/etc/systemd/system/` via the
`mythos-install-unit` privilege wrapper. Runs `daemon-reload` automatically.

#### `patch.allowlist_append_unit(unit)`
Add a unit to `/etc/mythos/allowed-units.txt` — required before `mythos-servicectl` can
control it. Must be called before `restart_service` on a newly registered unit.

---

### Other Wrappers

#### `patch.sudo_wrapper(wrapper_name, *args, timeout=120, check=True)`
Direct call to any `/usr/local/libexec/mythos/<wrapper>`. All service/permission methods
use this internally. Raises `RuntimeError` if the wrapper is not installed (SYS-0062 missing).

#### `patch.fix_ownership()`
Recursive `chown adge:adge /opt/mythos/`. Use in patches that escalate to root — always
call this before `finish()` to avoid leaving root-owned files that break future operations.

#### `patch.scan_perms() → int`
Returns count of non-adge-owned files under `/opt/mythos/`. Use to verify `fix_ownership` worked.

#### `patch.install_cloudflared_config()`
Deploy `/opt/mythos/cloudflared/config.yml` via privilege wrapper.

#### `patch.backup_git() → str`
Create timestamped `.git/` tar.gz backup in `/tmp/`. Returns path to backup.

#### `patch.verify_handoff(subsystem) → bool`
Run `mythos-handoff <subsystem> --strict` against a subsystem MANIFEST.yaml.
Use for high-blast-radius patches with formal handoff specs.

---

## Patch Directory Layout

```
{STREAM}-{NNNN}_{description}/
├── install.sh              ← always exactly these 4 lines
├── apply_patch.py          ← all logic via PatchBase
└── opt/mythos/             ← files mirroring target paths on Arcturus
    └── ...
```

**install.sh — always exactly this, byte for byte:**
```bash
#!/bin/bash
set -e
PATCH_DIR="$(cd "$(dirname "$0")" && pwd)"
/opt/mythos/.venv/bin/python3 "$PATCH_DIR/apply_patch.py"
```

**apply_patch.py skeleton:**
```python
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(stream='SYS', number=88, description='my feature', patch_type='MINOR')
patch.begin()

patch.deploy_file('opt/mythos/some/file.py', '/opt/mythos/some/file.py')
patch.run_sql('opt/mythos/migrations/SYS-0088_schema.sql')
patch.str_replace('/opt/mythos/some/other.py', OLD, NEW, 'label')
patch.restart_service('mythos-bot.service')

patch.finish()
```

---

## patch-install Workflow

```
patch-install SYS-NNNN [--dry-run] [--clip]
```

1. Finds `SYS-NNNN*.zip` in `~/Downloads/`
2. Copies to `/opt/mythos/patches/archive/`
3. Extracts to `/opt/mythos/patches/SYS-NNNN_description/`
4. Git snapshot: commits dirty working tree, tags `pre-patch-<name>-<timestamp>`
5. `chmod +x install.sh` → runs `install.sh` as adge (not root)
6. On success: `git add -A`, commit, tag `stream_NNNN`, push to `origin main --tags`
7. On failure: auto-rollback reads `/tmp/STREAM-NNNN_result.json`, reverts files/STREAMS/PATCH_HISTORY

**Passive monitor (`mythos-patch-monitor.service`):** Detects zip in `~/Downloads/`, sends Telegram
notification with the install command. Does NOT auto-install. User always runs `patch-install` manually.

---

## Post-Install Pipeline

Runs automatically after `install.sh` exits successfully, before `STREAMS.json` is bumped:

1. **Integrity scan** — updates Neo4j `IntegrityFile` / `IntegrityFunction` / `IntegrityTable` / `IntegrityService` nodes
2. **Git commit + tag + push** — commits patch changes, tags `stream_NNNN`, pushes to `origin main --tags`
3. **Graph update** — skipped if `integrity.graph` module unavailable
4. **Telegram notification** — patch summary to bot

Pipeline failure blocks the ledger update (STREAMS.json not bumped, PATCH_HISTORY not written).

---

## Non-Negotiable Rules

### File editing
- **`str_replace()` for ALL in-place edits.** Never `sed`, never heredocs, never `awk`.
- Anchor must appear exactly once — `str_replace` raises on 0 or >1 matches. This is correct behavior.
- `py_compile` runs automatically for `.py` files inside `str_replace`. No need to call separately.
- Backups are automatic. Every modified file gets `.{patch_id}.bak` before any write.

### Self-patching bootstrapping rule (SYS-0087 lesson)
**Any patch that replaces `patch_base.py` itself is a special case.**
The `patch` object is instantiated from the OLD code at the top of the script and stays that
way for the entire run — deploying a new file to disk does NOT hot-swap the running object.

Rules for self-patching patches:
- Phases before `deploy_file()`: use ONLY the old API (raw `Path`, manual `py_compile`, etc.)
- Phases after `deploy_file()`: new methods still not available on the running `patch` object
- To exercise new methods: spawn a **fresh subprocess** (`subprocess.run([VENV_PYTHON, '-c', ...])`)
  that imports the newly deployed `patch_base.py` from disk

### Permissions
- `/opt/mythos/` is `adge:adge` — no sudo for file copies
- sudo only for: `systemctl`, privilege wrappers, `psql` as postgres (all handled by PatchBase internally)
- CLI symlinks → `/opt/mythos/bin/` only, **never** `/usr/local/bin/`

### Database
- Postgres connections use Unix socket. Never `host=localhost` in any DSN.
- Shared table migrations (`people`, `transactions`, `system_manifest`) → SYS stream only
- New Telegram `/commands` register in `mythos_bot.py` via SYS patch, even if handler code lives in another stream

### Idempotency
- Idempotency markers must come from content that appears ONLY in the NEW version
- First N characters of `new` may be identical to `old` if `new` just appends — use a unique string from the middle of new content as the guard

---

## Tools

```bash
mythos-diag streams                          # live stream counters (always use before building)
patch-install SYS-NNNN                       # install patch from ~/Downloads/
patch-install SYS-NNNN --dry-run             # validate without applying
patch-install SYS-NNNN --clip                # copy install output to clipboard
MYTHOS_PATCH_DRY_RUN=1 python3 apply_patch.py   # dry-run a patch directly
```

---

## Patch Ledger

| Patch | Description |
|-------|-------------|
| SYS-0062 | Privilege foundation — 8 root-owned wrappers, sudoers allowlist |
| SYS-0063 | PatchBase wrapper migration — `sudo_wrapper()` + 11 convenience methods |
| SYS-0066 | Monitor passive mode — detect-and-notify only, never auto-install |
| SYS-0067 | `patch-install.sh` git integration — snapshot, commit, tag, push |
| SYS-0084 | `PatchBase.finish()` fix — error gate before ledger update, pipeline before ledger |
| SYS-0087 | PatchBase microtool kit — `str_replace`, `append_to_file`, `prepend_to_file`, `ensure_line_in_file`, `read_file`, `assert_file_exists`, `run_python_check`, `py_compile_check` |
| SYS-0089 | Docs update — this file created, ARCHITECTURE.md + TODO.md updated |
