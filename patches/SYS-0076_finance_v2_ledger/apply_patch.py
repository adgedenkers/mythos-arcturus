#!/usr/bin/env python3
"""
SYS-0076: Finance v2 — Ledger & Data Layer (Patch B)

Creates the transactional core on top of SYS-0075's foundation:
  - enums: transaction_kind, observation_status, import_status, direction
  - tables: import_sources, imports, transactions, entries, source_observations
  - deferred balance constraint trigger on entries

Does NOT touch: merchants, categorization, recurring patterns,
balance_assertions, pending_reconciliation. Those belong to later
patches in the FINANCE_V2.md §15 sequence.
"""
import subprocess
import sys

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase


def _psql(sql: str, check: bool = True):
    return subprocess.run(
        ['sudo', '-u', 'postgres', 'psql', '-d', 'mythos', '-tAc', sql],
        capture_output=True, text=True, check=check,
    )


def verify_schema(patch: PatchBase) -> None:
    """Post-install sanity checks against the live DB."""
    checks = [
        ("enum transaction_kind",
         "SELECT 1 FROM pg_type WHERE typname='transaction_kind'", "1"),
        ("enum observation_status",
         "SELECT 1 FROM pg_type WHERE typname='observation_status'", "1"),
        ("enum import_status",
         "SELECT 1 FROM pg_type WHERE typname='import_status'", "1"),
        ("enum direction",
         "SELECT 1 FROM pg_type WHERE typname='direction'", "1"),
        ("table finance.import_sources",
         "SELECT 1 FROM pg_tables WHERE schemaname='finance' AND tablename='import_sources'", "1"),
        ("table finance.imports",
         "SELECT 1 FROM pg_tables WHERE schemaname='finance' AND tablename='imports'", "1"),
        ("table finance.transactions",
         "SELECT 1 FROM pg_tables WHERE schemaname='finance' AND tablename='transactions'", "1"),
        ("table finance.entries",
         "SELECT 1 FROM pg_tables WHERE schemaname='finance' AND tablename='entries'", "1"),
        ("table finance.source_observations",
         "SELECT 1 FROM pg_tables WHERE schemaname='finance' AND tablename='source_observations'", "1"),
        ("balance constraint trigger",
         "SELECT 1 FROM pg_trigger WHERE tgname='entries_enforce_balance' AND tgdeferrable",
         "1"),
        ("entries.entity_id default = 1",
         "SELECT column_default FROM information_schema.columns "
         "WHERE table_schema='finance' AND table_name='entries' AND column_name='entity_id'",
         "1"),
    ]

    for label, sql, expected in checks:
        try:
            r = _psql(sql)
            got = r.stdout.strip()
            if got == expected:
                patch.validations.append(f"{label} — OK")
                patch.logger.log(f"  ✓ verify: {label}")
            else:
                patch.errors.append(f"verify {label}: expected {expected!r}, got {got!r}")
                patch.logger.log(f"  ✗ verify: {label} — expected {expected!r}, got {got!r}")
        except subprocess.CalledProcessError as e:
            patch.errors.append(f"verify {label}: {e.stderr.strip()}")
            patch.logger.log(f"  ✗ verify: {label}: {e.stderr.strip()}")

    # ── Negative test: unbalanced transaction must be rejected at COMMIT ──
    # Insert one entry (unbalanced), commit, expect exception.
    neg_sql = """
    BEGIN;
    INSERT INTO finance.transactions (id, description, kind, posted_date)
        VALUES (999999, 'BALANCE TRIGGER NEG TEST', 'manual', CURRENT_DATE);
    INSERT INTO finance.entries (transaction_id, account_id, amount_minor, entry_date)
        VALUES (999999, 1, 100, CURRENT_DATE);
    COMMIT;
    """
    r = _psql(neg_sql, check=False)
    combined = (r.stdout + r.stderr).lower()
    if 'unbalanced' in combined:
        patch.validations.append("deferred balance trigger rejects imbalance — OK")
        patch.logger.log("  ✓ verify: deferred balance trigger fires on unbalanced COMMIT")
    else:
        patch.errors.append(
            f"deferred balance trigger DID NOT fire — stdout={r.stdout!r} stderr={r.stderr!r}"
        )
        patch.logger.log("  ✗ verify: balance trigger did not reject unbalanced txn")

    # Cleanup: make sure the failed txn left nothing behind
    cleanup = _psql(
        "DELETE FROM finance.entries WHERE transaction_id = 999999; "
        "DELETE FROM finance.transactions WHERE id = 999999;",
        check=False,
    )
    # Not a hard failure if nothing to clean; the COMMIT above should have rolled back.

    # ── Positive test: balanced 2-entry transaction commits cleanly ──
    pos_sql = """
    BEGIN;
    INSERT INTO finance.transactions (id, description, kind, posted_date)
        VALUES (999998, 'BALANCE TRIGGER POS TEST', 'manual', CURRENT_DATE);
    INSERT INTO finance.entries (transaction_id, account_id, amount_minor, entry_date)
        VALUES (999998, 1, 500, CURRENT_DATE),
               (999998, 3, -500, CURRENT_DATE);
    COMMIT;
    """
    r = _psql(pos_sql, check=False)
    if r.returncode == 0:
        patch.validations.append("balanced transaction commits cleanly — OK")
        patch.logger.log("  ✓ verify: balanced 2-entry txn commits")
        # Clean it up so we don't leave test data in the ledger
        _psql(
            "DELETE FROM finance.entries WHERE transaction_id = 999998; "
            "DELETE FROM finance.transactions WHERE id = 999998;",
            check=False,
        )
    else:
        patch.errors.append(
            f"balanced transaction FAILED — stdout={r.stdout!r} stderr={r.stderr!r}"
        )
        patch.logger.log(f"  ✗ verify: balanced txn rejected: {r.stderr.strip()}")


def main():
    patch = PatchBase(
        stream='SYS',
        number=76,
        description='finance v2 ledger core (imports, observations, transactions, entries)',
        patch_type='MINOR',
    )
    patch.begin()

    patch.run_sql('opt/mythos/migrations/SYS-0076_finance_v2_ledger.sql')

    if not patch.dry_run and not patch.errors:
        verify_schema(patch)

    patch.finish()


if __name__ == '__main__':
    main()
