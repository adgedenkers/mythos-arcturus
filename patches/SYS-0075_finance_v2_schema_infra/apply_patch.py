#!/usr/bin/env python3
"""
SYS-0075: Finance v2 — Infrastructure & Safety (Patch A)

Creates the finance schema, core enums (entity_kind, account_kind,
normal_balance), the entities and accounts tables, materialized-path
derivation + cascade triggers, system-account protection triggers,
and seeds Personal + Denkers Co. LLC entities plus the 5 system
accounts from FINANCE_V2.md §4.4.

Does NOT touch: transactions, entries, source_observations, imports,
merchants, rules, recurring patterns. Those belong to later patches
in the §15 sequence.
"""
import subprocess
import sys

sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase


def verify_schema(patch: PatchBase) -> None:
    """Post-install sanity checks against the live DB."""
    checks = [
        (
            "schema exists",
            "SELECT 1 FROM pg_namespace WHERE nspname = 'finance'",
            "1",
        ),
        (
            "entities seeded (Personal + LLC)",
            "SELECT count(*)::text FROM finance.entities",
            "2",
        ),
        (
            "system accounts seeded (5)",
            "SELECT count(*)::text FROM finance.accounts WHERE is_system = true",
            "5",
        ),
        (
            "account_path index present",
            "SELECT 1 FROM pg_indexes WHERE schemaname='finance' AND indexname='idx_accounts_path_prefix'",
            "1",
        ),
    ]

    for label, sql, expected in checks:
        try:
            result = subprocess.run(
                ['sudo', '-u', 'postgres', 'psql', '-d', 'mythos', '-tAc', sql],
                capture_output=True, text=True, check=True,
            )
            got = result.stdout.strip()
            if got == expected:
                patch.validations.append(f"{label} — OK")
                patch.logger.log(f"  ✓ verify: {label}")
            else:
                patch.errors.append(f"verify {label}: expected {expected!r}, got {got!r}")
                patch.logger.log(f"  ✗ verify: {label} — expected {expected!r}, got {got!r}")
        except subprocess.CalledProcessError as e:
            patch.errors.append(f"verify {label}: {e.stderr.strip()}")
            patch.logger.log(f"  ✗ verify: {label}: {e.stderr.strip()}")

    # Negative test: system-account protection must block deletes
    try:
        result = subprocess.run(
            ['sudo', '-u', 'postgres', 'psql', '-d', 'mythos', '-tAc',
             "DELETE FROM finance.accounts WHERE account_path = 'equity:opening_balances'"],
            capture_output=True, text=True,
        )
        if result.returncode != 0 and 'Cannot delete system account' in (result.stderr or ''):
            patch.validations.append("system account delete protection — OK")
            patch.logger.log("  ✓ verify: system-account protection blocks DELETE")
        else:
            patch.errors.append(
                f"system protection DID NOT block delete — stdout={result.stdout!r} stderr={result.stderr!r}"
            )
            patch.logger.log("  ✗ verify: protection trigger did not fire on DELETE")
    except Exception as e:
        patch.errors.append(f"verify protection delete: {e}")
        patch.logger.log(f"  ✗ verify: protection delete check failed: {e}")


def main():
    patch = PatchBase(
        stream='SYS',
        number=75,
        description='finance v2 schema infra (entities, accounts, triggers, seeds)',
        patch_type='MINOR',
    )
    patch.begin()

    patch.run_sql('opt/mythos/migrations/SYS-0075_finance_v2_schema_infra.sql')

    if not patch.dry_run and not patch.errors:
        verify_schema(patch)

    patch.finish()


if __name__ == '__main__':
    main()
