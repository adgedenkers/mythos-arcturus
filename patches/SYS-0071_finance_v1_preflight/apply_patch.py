#!/usr/bin/env python3
"""
SYS-0071: Finance v1 preflight — archive code and rename tables.

Prepares Arcturus for the Finance v2 rebuild. Does NOT create v2 tables;
only gets v1 out of the way.

Actions:
    1. Preflight safety checks (always run, read-only):
       - Verify all 10 v1 finance tables exist and are empty
       - Verify no v1_* prefixed tables already exist (idempotency)
       - Verify /opt/mythos/finance/ exists
       - Verify /opt/mythos/archives/finance_v1_20260412/ does NOT exist
       - Scan /opt/mythos/ for lingering imports of finance.* modules
    2. Archive /opt/mythos/finance/ -> /opt/mythos/archives/finance_v1_20260412/
       (skipped in dry-run)
    3. Rename v1 tables with v1_ prefix via patch.run_sql()
       (dry-run wraps in BEGIN/ROLLBACK automatically)
    4. Post-verification: v1_* tables exist, unprefixed tables don't
       (skipped in dry-run)

Dry-run usage:
    MYTHOS_PATCH_DRY_RUN=1 patch-install SYS-0071

Per plan v3 §15: rename, not drop. v1_* tables stay until SYS-0079
archive cleanup after v2 is proven stable.
"""
import sys
import os
import shutil
import subprocess
import re

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase


# --- Constants ------------------------------------------------------------

V1_TABLES = [
    'accounts',
    'transactions',
    'recurring_bills',
    'recurring_income',
    'bill_payments',
    'bill_overrides',
    'categories',
    'category_mappings',
    'category_rules',
    'import_logs',
]

FINANCE_DIR = '/opt/mythos/finance'
ARCHIVE_ROOT = '/opt/mythos/archives'
ARCHIVE_DIR = '/opt/mythos/archives/finance_v1_20260412'

SCAN_ROOT = '/opt/mythos'
SCAN_EXCLUDES = (
    '/opt/mythos/patches',
    '/opt/mythos/archives',
    '/opt/mythos/.venv',
    '/opt/mythos/.git',
    '/opt/mythos/finance',
)


# --- Postgres helpers (read-only, safe in dry-run) ------------------------

def psql_query(sql: str) -> str:
    result = subprocess.run(
        ['sudo', '-u', 'postgres', 'psql', '-d', 'mythos', '-tAc', sql],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def table_exists(table_name: str) -> bool:
    out = psql_query(
        f"SELECT 1 FROM information_schema.tables "
        f"WHERE table_schema='public' AND table_name='{table_name}';"
    )
    return out == '1'


def table_row_count(table_name: str) -> int:
    out = psql_query(f'SELECT COUNT(*) FROM "{table_name}";')
    return int(out)


# --- Preflight safety checks (read-only, always run) ----------------------

def preflight_checks(patch: PatchBase) -> bool:
    patch.logger.log("=== PREFLIGHT SAFETY CHECKS ===")
    ok = True

    # 1. All 10 v1 tables must exist
    patch.logger.log("  Checking v1 tables exist...")
    missing = [t for t in V1_TABLES if not table_exists(t)]
    if missing:
        msg = f"expected v1 tables missing: {missing}"
        patch.errors.append(f"preflight: {msg}")
        patch.logger.log(f"    X {msg}")
        ok = False
    else:
        patch.logger.log(f"    + all {len(V1_TABLES)} v1 tables present")

    # 2. All 10 v1 tables must be empty
    if not missing:
        patch.logger.log("  Verifying v1 tables are empty...")
        non_empty = []
        for t in V1_TABLES:
            count = table_row_count(t)
            if count > 0:
                non_empty.append((t, count))
        if non_empty:
            details = ', '.join(f"{t}={c}" for t, c in non_empty)
            msg = f"refusing to rename non-empty v1 tables: {details}"
            patch.errors.append(f"preflight: {msg}")
            patch.logger.log(f"    X {msg}")
            ok = False
        else:
            patch.logger.log("    + all v1 tables empty - safe to rename")

    # 3. No v1_* tables should already exist (idempotency)
    patch.logger.log("  Checking for pre-existing v1_ prefixed tables...")
    already_renamed = [t for t in V1_TABLES if table_exists(f'v1_{t}')]
    if already_renamed:
        msg = f"v1_ prefixed tables already exist: {already_renamed}"
        patch.errors.append(f"preflight: {msg}")
        patch.logger.log(f"    X {msg}")
        ok = False
    else:
        patch.logger.log("    + no v1_ conflicts")

    # 4. /opt/mythos/finance/ must exist
    patch.logger.log(f"  Checking {FINANCE_DIR} exists...")
    if not os.path.isdir(FINANCE_DIR):
        msg = f"{FINANCE_DIR} does not exist"
        patch.errors.append(f"preflight: {msg}")
        patch.logger.log(f"    X {msg}")
        ok = False
    else:
        patch.logger.log(f"    + {FINANCE_DIR} present")

    # 5. Archive destination must NOT exist
    patch.logger.log(f"  Checking archive destination {ARCHIVE_DIR} is clear...")
    if os.path.exists(ARCHIVE_DIR):
        msg = f"archive destination already exists: {ARCHIVE_DIR}"
        patch.errors.append(f"preflight: {msg}")
        patch.logger.log(f"    X {msg}")
        ok = False
    else:
        patch.logger.log("    + archive destination clear")

    # 6. Scan for lingering finance imports
    patch.logger.log("  Scanning for lingering `from finance` / `import finance` references...")
    offenders = scan_finance_imports()
    if offenders:
        patch.logger.log(f"    X found {len(offenders)} files importing from finance:")
        for path, line_no, line in offenders[:20]:
            patch.logger.log(f"      {path}:{line_no}: {line.strip()[:100]}")
        if len(offenders) > 20:
            patch.logger.log(f"      ... and {len(offenders) - 20} more")
        patch.errors.append(
            f"preflight: {len(offenders)} files still import from finance module - "
            f"update or remove them before archiving"
        )
        ok = False
    else:
        patch.logger.log("    + no lingering finance imports")

    if ok:
        patch.logger.log("=== PREFLIGHT PASSED ===")
    else:
        patch.logger.log("=== PREFLIGHT FAILED ===")
    return ok


def scan_finance_imports():
    pattern = re.compile(r'^\s*(?:from\s+finance(?:\.|\s)|import\s+finance(?:\.|\s|$))')
    offenders = []
    for root, dirs, files in os.walk(SCAN_ROOT):
        if any(root == ex or root.startswith(ex + '/') for ex in SCAN_EXCLUDES):
            dirs[:] = []
            continue
        dirs[:] = [d for d in dirs if d != '__pycache__' and not d.startswith('.')]
        for fname in files:
            if not fname.endswith('.py'):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, 'r', encoding='utf-8', errors='replace') as f:
                    for line_no, line in enumerate(f, start=1):
                        code = line.split('#', 1)[0]
                        if pattern.match(code):
                            offenders.append((fpath, line_no, line))
            except (OSError, UnicodeDecodeError):
                continue
    return offenders


# --- Archive operation (skipped in dry-run) -------------------------------

def archive_finance_dir(patch: PatchBase) -> bool:
    patch.logger.log("=== ARCHIVING v1 FINANCE CODE ===")
    patch.logger.log(f"  source:      {FINANCE_DIR}")
    patch.logger.log(f"  destination: {ARCHIVE_DIR}")

    if not os.path.isdir(ARCHIVE_ROOT):
        patch.logger.log(f"  Creating {ARCHIVE_ROOT}...")
        try:
            os.makedirs(ARCHIVE_ROOT, mode=0o755)
        except Exception as e:
            patch.errors.append(f"create {ARCHIVE_ROOT}: {e}")
            patch.logger.log(f"    X {e}")
            return False

    try:
        shutil.move(FINANCE_DIR, ARCHIVE_DIR)
    except Exception as e:
        patch.errors.append(f"archive move: {e}")
        patch.logger.log(f"    X {e}")
        return False

    if os.path.exists(FINANCE_DIR):
        patch.errors.append(f"after move, {FINANCE_DIR} still exists")
        patch.logger.log(f"    X source still present after move")
        return False
    if not os.path.isdir(ARCHIVE_DIR):
        patch.errors.append(f"after move, {ARCHIVE_DIR} does not exist")
        patch.logger.log(f"    X destination missing after move")
        return False

    count = sum(len(files) for _, _, files in os.walk(ARCHIVE_DIR))
    patch.logger.log(f"  + archived {count} files")
    patch.validations.append(f"archived finance dir ({count} files)")
    return True


# --- Post-rename verification (skipped in dry-run) ------------------------

def verify_rename(patch: PatchBase) -> bool:
    patch.logger.log("=== VERIFYING TABLE RENAME ===")
    ok = True
    for t in V1_TABLES:
        if table_exists(t):
            patch.errors.append(f"verify: unprefixed '{t}' still exists after rename")
            patch.logger.log(f"    X unprefixed '{t}' still exists")
            ok = False
        if not table_exists(f'v1_{t}'):
            patch.errors.append(f"verify: 'v1_{t}' does not exist after rename")
            patch.logger.log(f"    X 'v1_{t}' missing")
            ok = False
    if ok:
        patch.logger.log(f"  + all {len(V1_TABLES)} tables renamed with v1_ prefix")
        patch.validations.append(f"renamed {len(V1_TABLES)} tables with v1_ prefix")
    return ok


# --- Main -----------------------------------------------------------------

def main():
    patch = PatchBase(
        stream='SYS',
        number=71,
        description='finance v1 preflight - archive code and rename tables',
        patch_type='MAJOR',
    )
    patch.begin()

    if not preflight_checks(patch):
        patch.finish()
        return

    if patch.dry_run:
        patch.logger.log("  . archive move - skipped (dry run)")
        patch.validations.append("archive move - would proceed")
    else:
        if not archive_finance_dir(patch):
            patch.finish()
            return

    patch.run_sql('opt/mythos/migrations/SYS-0071_rename_v1_finance_tables.sql')

    if patch.dry_run:
        patch.logger.log("  . rename verification - skipped (dry run)")
        patch.validations.append("rename verification - would run")
    else:
        if patch.errors:
            patch.finish()
            return
        verify_rename(patch)

    patch.finish()


if __name__ == '__main__':
    main()
