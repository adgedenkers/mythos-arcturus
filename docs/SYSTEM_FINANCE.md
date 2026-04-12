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

## Next Up

<!-- SYS-0078: next-up collapsed to pointer -->
The full spec for the next patch lives in
[`docs/finance/NEXT_PATCH_SPEC.md`](finance/NEXT_PATCH_SPEC.md).
That file is rewritten wholesale at the end of every feature
patch, so it always describes exactly one patch ahead.

Run `mythos-handoff finance` to assemble the full handoff payload
(this doc + WORKFLOW + NEXT_PATCH_SPEC + live DB state + validations)
into your clipboard, ready to paste into a new conversation.

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
<!-- SYS-0081: incoming notes appended -->

**2026-04-12** (SYS-0081): Review fatigue 3-month revisit. Check
whether the blast-radius cutoff in WORKFLOW.md Phase 2.5 is actually
being honored. If patches are shipping that should have been reviewed,
tighten the rule or add a PatchBase warning per Castor's round-1
architectural oversight note. Revisit target: 2026-07-12.

**2026-04-12** (SYS-0081): `edit_file()` double-backup nit — when the
same file is edited twice in one patch (e.g., SYS-0080's two edits to
mythos-handoff), the second backup overwrites the first with a
post-first-edit version. Harmless today (set -e rollback still works
because the second edit's failure triggers the first's backup via
the overall patch-install failure path), but the pristine pre-patch
state is lost. Low priority refinement.

**2026-04-12** (SYS-0081): Link rot 3-month revisit. If any `Review:`
links in PATCH_HISTORY have gone stale by this date, adopt the
commit-review-text pattern — store full review request text in
`patches/SYS-NNNN/review_request.md` as part of the patch zip. Per
Castor's round-1 architectural oversight. Revisit target: 2026-07-12.


---

*Finance v2 is a vessel for the arithmetic of a life.*
*Two patches down. Ten to go.*
