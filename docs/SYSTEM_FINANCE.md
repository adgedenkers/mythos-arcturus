---
title: "SYSTEM: Finance v2"
category: system
status: active
stream: SYS
location: docs
tags: [finance, ledger, double-entry, system-doc]
created: 2026-04-12
updated: 2026-04-12
author: Adge Denkers
---

# SYSTEM: Finance v2

> **Workflow:** see `docs/WORKFLOW.md`
> **Design plan:** see `docs/FINANCE_V2.md`
> **This doc:** canonical current state of Finance v2. Updated after
> every patch lands. Read this before starting any finance conversation.

---

## Status

- **Last shipped patch:** B (SYS-0076) — 2026-04-12
- **Next patch:** D — Merchants + merchant_patterns + FK on `transactions.merchant_id`
- **Build phase:** active (A→L sequence, currently at B→C→D)
- **Design plan:** `docs/FINANCE_V2.md`

> Note: Patch C (this one, SYS-0077) is the workflow/documentation
> bootstrap. It ships no schema or code — only `WORKFLOW.md`,
> `SYSTEM_FINANCE.md`, and an `ARCHITECTURE.md` edit. The
> handoff-diag script itself is deferred pending external review
> and will land in a follow-up doc patch.

---

## Architecture Summary

Finance v2 is a **double-entry ledger** running on Postgres, in the
`finance` schema. Every transaction is an envelope around 2+ entries
that sum to zero, enforced by a deferred constraint trigger. All
monetary values are signed `BIGINT amount_minor` (integer cents) — no
floats, no `NUMERIC`, no rounding ambiguity.

Raw bank CSV rows land first in `finance.source_observations` — an
immutable observation layer that sits between bank exports and the
ledger. An observation is *not* a transaction; it's evidence of one.
Multiple observations can link to the same transaction (daily
re-imports, description drift, retroactive bank changes), and the
dedup algorithm runs at the observation layer, not against the
ledger itself. This is the key insight from Jeff Pro's review — it
keeps the ledger append-only while giving the importer room to deal
with the messiness of real bank exports.

Entries carry an `entity_id` dimension (Personal=1, Denkers Co. LLC=2)
so personal and business activity can share the same chart of accounts
but produce independent books for tax and reporting purposes. The LLC
is currently inactive; when it activates, the dimension lights up
automatically without schema migration.

Currently, only the foundation (Patches A+B) is live. Merchants,
categorization, the importer, recurring detection, forecasting,
balance assertions, and reliability infrastructure are all still ahead.

---

## Patch Ledger

| Letter | Scope | Patch # | Shipped | Notes |
|--------|-------|---------|---------|-------|
| A | Schema infra — `finance` schema, entities, accounts, triggers, system seeds | SYS-0075 | 2026-04-12 | Foundation. 5 system accounts seeded, protection trigger verified. |
| B | Ledger core — imports, import_sources (schema only), transactions, entries, source_observations, deferred balance trigger | SYS-0076 | 2026-04-12 | Balance trigger verified via negative + positive tests. |
| C | Workflow bootstrap — WORKFLOW.md, SYSTEM_FINANCE.md, ARCHITECTURE.md edit | SYS-0077 | 2026-04-12 | This patch. No schema or code changes. |
| D | Merchants + merchant_patterns + FK on `transactions.merchant_id` | — | — | **Next up** |
| E | Importer — CSV parsers, 3-phase dedup, observation→transaction flow, opening balances, historical re-import, import_sources seeds | — | — | |
| F | Categorization — rules, categorization_log, learning loop, historical categorization pass | — | — | |
| G | API + dashboard rewrite, split UI, entity selection, correction routing, audit view | — | — | |
| H | Recurring detector — patterns table, worker, semi-monthly vs biweekly, suggestion UI | — | — | |
| I | Forecasting — confidence-weighted projection, `/forecast` update | — | — | |
| J | Balance assertions + pending_reconciliation — drift check, review queue | — | — | |
| K | v1 archive cleanup (after 2 weeks stable) | — | — | |
| L | Reliability — PITR, WAL archiving, pg_dump on import, restore drill, golden fixtures | — | — | |

**Letter sequence is locked.** Re-lettering is not happening again.
Letters are stable even if individual patches take multiple numbers
to land cleanly.

---

## Current Database State (as of SYS-0076)

**Schema:** `finance`

**Enums:**
- `entity_kind` (individual, llc, corporation, trust)
- `account_kind` (asset, liability, income, expense, equity)
- `normal_balance` (debit, credit)
- `transaction_kind` (imported, manual, transfer, adjustment, reversal, opening_balance)
- `observation_status` (new, duplicate, matched, flagged, reversed, ignored)
- `import_status` (running, completed, failed, reversed)
- `direction` (inflow, outflow)

**Tables:**
- `entities` — 2 rows (Personal active, LLC dormant)
- `accounts` — 5 system rows (opening_balances, reconciliation_adjustments, bank_transfers transit, expenses:uncategorized, income:uncategorized)
- `import_sources` — schema only, unseeded
- `imports` — empty
- `transactions` — empty (`merchant_id` is plain BIGINT, FK added in Patch D)
- `entries` — empty
- `source_observations` — empty

**Triggers:**
- `accounts_derive_path` (BEFORE INSERT/UPDATE) — materialized path from parent chain
- `accounts_cascade_path` (AFTER UPDATE) — rewrites descendants on parent path change
- `accounts_protect_system_update` / `_delete` — blocks mutation of is_system rows
- `entries_enforce_balance` (CONSTRAINT TRIGGER, DEFERRABLE INITIALLY DEFERRED) — rejects any transaction whose entries do not sum to zero at commit time

**What does NOT exist yet:**
- merchants, merchant_patterns
- categorization_rules, categorization_log
- recurring_patterns
- balance_assertions, pending_reconciliation
- importer code (`/opt/mythos/finance/` is archived v1 only)
- finance API routes against v2 schema
- any v2 data at all — the ledger is empty

---

## Next Up: Patch D — Merchants + merchant_patterns

### Why
Patch B left `transactions.merchant_id` as an unconstrained `BIGINT` on
purpose — the merchants table didn't exist yet. Patch D creates the
merchants registry and the pattern-matching table, then adds the FK.
This unlocks Patch E (the importer), which needs to resolve raw CSV
descriptions to canonical merchants before entries can be categorized.

Merchants and categorization are **separate concerns** (per Jeff Pro's
review). Patch D only handles merchant *resolution* (raw description →
canonical merchant). Categorization rules (merchant → category, with
context overrides) come in Patch F.

### What
- **Table: `finance.merchants`** — canonical merchant registry with
  `canonical_name`, `display_name`, `default_category_account_id`
  (nullable FK to accounts), `default_tax_treatment`,
  `normalized_name_key`, `metadata`
- **Table: `finance.merchant_patterns`** — raw description → merchant
  mapping with `pattern`, `pattern_type` enum (exact/contains/regex),
  `merchant_id` FK, `priority`, `confidence`, `match_count`,
  `last_matched_at`, `is_active`
- **Enum: `finance.pattern_type`** (exact, contains, regex)
- **FK constraint added:** `transactions.merchant_id` → `merchants.id`
  (nullable; existing rows are zero so no data migration needed)
- **Indexes:** `merchants(normalized_name_key)`,
  `merchant_patterns(pattern_type, priority DESC)`,
  `merchant_patterns(merchant_id)`, `merchant_patterns(is_active) WHERE is_active`

### How
Follows the SYS-0075/0076 pattern exactly:
- One SQL migration file wrapped in a transaction
- `apply_patch.py` using `PatchBase`, runs SQL then verifies
- Verification checks: tables exist, enum exists, FK exists, negative
  test that inserting a `transactions.merchant_id` pointing to a
  non-existent merchant is rejected

No seeds in Patch D. Seeding merchants from archived v1 patterns
happens in Patch E or F, once the importer exists to actually use
them.

### Success criteria
- Both tables created, indexes in place
- FK on `transactions.merchant_id` exists and rejects orphaned values
- Positive test: insert merchant row, insert merchant_patterns row
  referencing it, insert transaction referencing the merchant — all
  succeed and commit cleanly
- Negative test: transaction with nonexistent merchant_id rejected
- Patch C workflow docs reflect Patch D as "shipped"

### Depends on
- Patch A (finance schema, accounts table for FK target)
- Patch B (transactions table for FK source)

### Does NOT include
- Any merchant/pattern rows (deferred to E or F)
- Categorization rules (Patch F)
- Importer logic (Patch E)
- FK re-verification of pre-existing transactions (there are none yet)

---

## Open Questions

*(Carried forward from FINANCE_V2.md §16 until resolved. See that
section for full context on each.)*

1. **Loan payment amortization storage** — current plan uses
   `metadata.default_split` on the loan account. Cleaner pattern?
   *Resolution target: Patch E or later.*
2. **Retroactive change handling without bank transaction IDs** —
   heuristic flagging vs. something more robust.
   *Resolution target: Patch E.*
3. **Opening balance data quality** — is statement PDF parsing worth
   building into Patch L?
   *Resolution target: Patch E decides, Patch L implements.*
4. **Import reversal with downstream edits** — hard block, soft warn,
   or partial?
   *Resolution target: Patch E or G.*
5. **Entity activation retroactive attribution** — migration tool or
   manual-only?
   *Resolution target: when LLC actually activates, probably between G and H.*
6. **`tax_treatment` vocabulary** — free text, enum, or lookup table?
   *Resolution target: Patch F.*
7. **Recurring pattern re-detection cadence** — per import, daily,
   weekly?
   *Resolution target: Patch H.*
8. **Bi-temporal query surface** — `/api/finance/as-of/<date>`
   endpoint, or YAGNI?
   *Resolution target: Patch G.*

---

## Incoming Notes

> **Rules:** append-only, date-stamped, never edit. Review when the
> next patch starts. Triage into "Next Up", defer to a later letter,
> or resolve inline. Never lose a note.

<!-- Add new notes below this line -->

---

*Finance v2 is a vessel for the arithmetic of a life.*
*Two patches down. Ten to go.*
