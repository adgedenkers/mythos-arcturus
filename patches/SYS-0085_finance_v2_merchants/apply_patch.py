#!/usr/bin/env python3
"""
SYS-0085 — Finance v2 Patch D re-land (merchants & patterns).

Re-lands the SYS-0083 schema with SAVEPOINT/ROLLBACK removed from
the inline DO block. Every schema decision was cleared by Castor in
rounds 1-3. The only structural delta from SYS-0083 is the DO block
cleanup mechanism: instead of rolling back to a savepoint at the end,
the test flow deletes the test transaction and merchant explicitly
(CASCADE handles merchant_patterns). Tables exit empty.

This patch ships under the new SYS-0084 PatchBase.finish() error
gate — if run_sql fails, self.errors will be populated and
STREAMS.json/PATCH_HISTORY will NOT be updated. PatchFinishError
will be raised and install.sh's set -e will propagate to
patch-install's rollback path.
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=85,
    description='finance v2 patch D re-land — merchants & patterns',
    patch_type='MINOR',
    review_link='Castor round 1 (finance review), round 2 (3-question pre-build), round 3 (inline DO block clearance). Re-land of SYS-0083 with SAVEPOINT/ROLLBACK removed from DO block (not permitted in PL/pgSQL anonymous blocks).',
)
patch.begin()

patch.run_sql('opt/mythos/migrations/SYS-0085_finance_v2_merchants.sql')

patch.finish()
