#!/usr/bin/env python3
"""
SYS-0083: Finance v2 Patch D — Merchants & Patterns.

Ships one SQL migration that creates:
  - finance.pattern_type enum
  - finance.normalize_merchant_name() function
  - finance.merchants table + derive-key trigger
  - finance.merchant_patterns table (with CHECK + UNIQUE + CASCADE)
  - FK on finance.transactions.merchant_id (RESTRICT)
  - Inline DO block verification (7 checks, SAVEPOINT-rolled)

Castor-reviewed 2 rounds (2026-04-12):
  - Round 1: finance review, 4 revisions required, all incorporated
  - Round 2: 3-question pre-build consultation, all 3 decisions locked
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=83,
    description='finance v2 patch D — merchants & patterns',
    patch_type='MINOR',
)
patch.begin()

patch.run_sql('opt/mythos/migrations/SYS-0083_finance_v2_merchants.sql')

patch.finish()
