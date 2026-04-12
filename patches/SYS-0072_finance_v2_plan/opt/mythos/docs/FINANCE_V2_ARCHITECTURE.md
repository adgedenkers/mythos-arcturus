---
title: "Finance v2 Architecture"
category: finance
status: active
stream: SYS
location: docs
tags: [finance, architecture, ledger]
created: 2026-04-12
updated: 2026-04-12
---

# Finance v2 — Architecture Reference

> Stable architecture reference. Update only when architecture actually changes. For the build plan and work units, see `FINANCE_V2.md`.

## Core Model

**Double-entry ledger** on Postgres, derived from an immutable **source observations** layer, with **bi-temporal** loan terms and **multi-entity** separation.

```
CSV / bank feed ──► source_observations (immutable raw layer)
                           │
                           ▼  promotion step (categorize, split)
                    ledger_entries (double-entry, balanced)
                           │
                           ▼  FK
                    accounts (hybrid chart of accounts)
                           │
                           ▼  FK
                    entities (personal, Denkers Co. LLC)
```

## Schema: `finance`

All Finance v2 tables live in the `finance` Postgres schema. Nothing in `public`.

| Table | Purpose |
|-------|---------|
| `finance.entities` | Legal/accounting entity — personal, LLC, trust, etc. |
| `finance.accounts` | Chart of accounts, hierarchical, FK to entity |
| `finance.source_observations` | Raw imported lines. Immutable. Never mutated after insert. |
| `finance.ledger_entries` | Double-entry core. Debits and credits. Always balanced per `transaction_group_id`. |
| `finance.loan_terms` | Bi-temporal loan term history |
| `finance.category_rules` | Pattern → account mapping for the promotion step |

## Enums

- `finance.account_type` — five-root CoA: `asset`, `liability`, `equity`, `income`, `expense`
- `finance.account_subtype` — specific flavor: `checking`, `credit_card`, `mortgage`, `clearing`, etc.
- `finance.entry_side` — `debit`, `credit`
- `finance.entity_type` — `individual`, `llc`, `joint`, `trust`

## Key Patterns

### Double-entry integrity

Every transaction is a set of `ledger_entries` sharing a `transaction_group_id`. For any group:

```
SUM(debits.amount) = SUM(credits.amount)
```

Enforced by a check function, runnable ad-hoc or via a periodic integrity worker.

### Clearing account transfers

Money moving between two real accounts is never a single transaction. It's two transactions sharing a `transaction_group_id`, routed through a clearing account that nets to zero:

```
Transfer $500 Checking → Savings:

  Entry A: Debit  Savings            $500  (group_id = X)
  Entry B: Credit Transfer Clearing  $500  (group_id = X)
  Entry C: Debit  Transfer Clearing  $500  (group_id = X)
  Entry D: Credit Checking           $500  (group_id = X)
```

The Transfer Clearing account balance should always be zero in steady state. Nonzero = pending or broken transfer. This is the self-check.

### Source observations are immutable

Observations never mutate. If categorization is wrong, we re-run the promotion step and regenerate `ledger_entries` for those observations. The audit trail from raw bank feed to ledger is always reconstructable.

### Bi-temporal loan terms

`loan_terms` tracks two time dimensions:

- **Valid time** (`valid_from`, `valid_to`) — when the term was actually in effect in the real world
- **Knowledge time** (`recorded_at`, `superseded_at`) — when we learned about it / when we replaced it

This lets us answer:

- *What was the Honda loan rate on 2025-06-01?* → filter by `valid_from <= '2025-06-01' < valid_to`, pick the currently-known row
- *What did we think the rate was on 2025-06-01, as known on 2025-07-01?* → same valid-time filter, but also `recorded_at <= '2025-07-01' AND (superseded_at IS NULL OR superseded_at > '2025-07-01')`

## Amounts and Types

- Money: `NUMERIC(14,2)`. Never floats.
- Timestamps: `TIMESTAMPTZ`. UTC in DB.
- Dates (for posted_date, valid_from, etc.): `DATE`.
- IDs: `UUID` with `gen_random_uuid()` default.

## Dedup Hash

Source observations dedup on:

```
sha256(account_id || '|' || posted_date || '|' || amount || '|' || normalized_description)
```

No balance. No bank transaction number. Those vary across re-downloads and break dedup.

## Out of Scope

- No Neo4j for finance. Postgres only. Decision locked with Castor + Jeff.
- No multi-currency beyond USD.
- No investment position tracking (shares/prices) — cash balances only.
- No budgeting/envelope system.

## Change Log

| Date | Change |
|------|--------|
| 2026-04-12 | Initial architecture locked in |
