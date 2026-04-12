---
title: "Finance v2 Build Plan"
category: finance
status: active
stream: SYS
location: docs
tags: [finance, plan, ledger, double-entry]
created: 2026-04-12
updated: 2026-04-12
author: Adge Denkers
---

# Finance v2 — Build Plan

> **How to use this doc:** This is the living plan. Start every Finance v2 conversation by reading this file top to bottom. Pick the next work unit that is not marked `✅ DONE`. Work it until it's done — however many patches that takes. Update the checklist as units complete. If architecture changes, update `FINANCE_V2_ARCHITECTURE.md` too.
>
> **One work unit = one conversation.** If a unit needs three patches to land cleanly, fine — all three happen in the same conversation. The doc tracks *what* got built, not *how many patches* it took.
>
> **Patch numbers are not in this doc on purpose.** SYS counter auto-increments. Whatever number is next when you start the patch, that's the number.

---

## Goal

Replace the flat, single-table v1 finance system with a proper **double-entry ledger** backed by a **source observations** layer, supporting **bi-temporal queries** (what did we think was true, when) and **multi-entity separation** (personal vs Denkers Co. LLC) from day one.

## Design Principles

1. **Postgres only.** No Neo4j for finance. Reviewed and agreed with Castor (Gemini) and Jeff (ChatGPT Pro).
2. **Double-entry from day one.** Every transaction is two or more balanced ledger entries. No exceptions.
3. **Source observations layer.** Raw imported lines land in `finance.source_observations` first. They are *never* mutated. The ledger is derived *from* observations via a promotion step — so we can always re-derive the ledger if categorization logic changes.
4. **Clearing accounts for transfers.** Money moving between two real accounts never becomes a single mystery transaction. It becomes two balanced entries routed through a clearing account, which nets to zero.
5. **Bi-temporal where it matters.** `loan_terms` tracks both `valid_from/valid_to` (when the term was in effect) and `recorded_at` (when we learned about it). Query any past state as of any past knowledge date.
6. **Entity dimension everywhere.** Every account belongs to an entity. Personal and Denkers Co. LLC are separate entities from day one — no retrofit later.
7. **Hybrid chart of accounts.** Standard five-root CoA (Assets, Liabilities, Equity, Income, Expenses) with free-form subaccount hierarchy underneath. Not rigid GAAP, not flat — hybrid.
8. **CLI first, API second, UI third.** The `DashboardV2.jsx` and `BillsDetailV2.jsx` frontend already exists and is calling `/api/finance/v2/*` endpoints that don't exist yet. We reconnect it at the end, not the start.
9. **One schema: `finance`.** Everything lives under `finance.*`. No polluting public.

---

## Architecture Summary

See `FINANCE_V2_ARCHITECTURE.md` for the full stable reference. Quick version:

```
Import CSV / Bank feed
        │
        ▼
┌─────────────────────────┐
│ finance.source_         │   Raw lines. Never mutated.
│   observations          │   Dedup hash. Immutable audit trail.
└───────────┬─────────────┘
            │ promotion step (categorize + split into debits/credits)
            ▼
┌─────────────────────────┐
│ finance.ledger_entries  │   Double-entry. Every row references an account.
│                         │   Debits = Credits per transaction_group_id.
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ finance.accounts        │◄──┐
│   (hybrid CoA)          │   │ FK
└───────────┬─────────────┘   │
            │                 │
            ▼                 │
┌─────────────────────────┐   │
│ finance.entities        │───┘  (personal, Denkers Co. LLC, etc.)
└─────────────────────────┘

Bi-temporal side car:
  finance.loan_terms  — (loan_id, term_fields..., valid_from, valid_to, recorded_at)
```

---

## Key Decisions (locked in from Castor + Jeff review rounds)

- **No Neo4j in finance.** Postgres handles this cleanly; the graph adds no value for ledger queries and creates consistency headaches.
- **Clearing account pattern for transfers.** Example: $500 moves from Checking → Savings. That's:
  - Debit Savings $500, Credit Transfer Clearing $500 (transaction_group_id = X)
  - Debit Transfer Clearing $500, Credit Checking $500 (transaction_group_id = X)
  - The clearing account nets to zero if both halves posted. If it's nonzero, something's pending or broken. This is the integrity check.
- **`transaction_group_id`** (UUID) ties balanced entries together. A transaction is a *set* of ledger_entries sharing a group_id, whose debits and credits balance.
- **`loan_terms` bi-temporal.** For every loan account, we track interest rate, payment amount, term months, etc. as time-bounded rows. Both the real-world validity window (`valid_from`, `valid_to`) and when we recorded the fact (`recorded_at`) are tracked. This lets us answer "what did we think the Honda loan rate was as of last March?" versus "what was the Honda loan rate actually in effect last March?"
- **Entity dimension.** Every account has `entity_id NOT NULL`. Reports filter by entity. LLC separation is structural, not a tag.
- **Source observations never mutate.** If we find a categorization error, we don't edit the observation — we re-run the promotion step and regenerate ledger_entries. Observations are the ground truth; ledger is derived.
- **Dedup hash on source_observations.** `account_id | posted_date | amount | normalized_description`. No balance, no running total, no bank-assigned transaction number (those vary across re-downloads).
- **Account subtypes.** `account_type` is the top-level (asset/liability/equity/income/expense). `account_subtype` is the specific flavor (checking, savings, credit_card, mortgage, auto_loan, etc.). Both are enums.
- **Direction enum.** `entry_side` = `debit` | `credit`. Explicit. No signed amounts, no sign conventions to remember.
- **Amounts are `NUMERIC(14,2)`.** No floats. Ever.
- **All timestamps `TIMESTAMPTZ`.** UTC in the database, formatted in the app.

---

## Work Units (ordered — work top to bottom)

Each unit is one conversation. Mark `✅ DONE` when the unit's done-when criteria are met.

---

### Unit: Plan + Architecture Docs + v1 Cleanup  ✅ DONE

**What:** Create `FINANCE_V2.md` (this doc) and `FINANCE_V2_ARCHITECTURE.md`. Drop all ten `v1_*` tables. Remove `/opt/mythos/finance/` directory if anything remains.

**Why:** Clean slate. Canonical plan on disk so no future conversation has to reconstruct from memory.

**Touches:** `/opt/mythos/docs/FINANCE_V2.md`, `/opt/mythos/docs/FINANCE_V2_ARCHITECTURE.md`, Postgres (drop tables), filesystem (rm finance dir).

**Done when:** Both docs exist, all `v1_*` tables gone from Postgres, `/opt/mythos/finance/` does not exist.

**Shipped in:** This patch.

---

### Unit: Foundation — schema + enums

**What:** Create the `finance` Postgres schema namespace and the core enums.

**Enums to create:**
- `finance.account_type` — `asset`, `liability`, `equity`, `income`, `expense`
- `finance.account_subtype` — `checking`, `savings`, `money_market`, `cash`, `credit_card`, `line_of_credit`, `mortgage`, `auto_loan`, `student_loan`, `personal_loan`, `retained_earnings`, `owner_equity`, `wages`, `interest_income`, `other_income`, `groceries`, `utilities`, `fuel`, `insurance`, `interest_expense`, `other_expense`, `clearing`
- `finance.entry_side` — `debit`, `credit`
- `finance.entity_type` — `individual`, `llc`, `joint`, `trust`

**Touches:** New Postgres schema `finance`. Migration file under `/opt/mythos/migrations/`.

**Done when:** `\dn` shows `finance` schema. `\dT finance.*` shows four enums. Nothing else yet — no tables.

---

### Unit: Entities table + seed rows

**What:** Create `finance.entities` table and seed two rows: Adge personal + Denkers Co. LLC.

**Schema sketch:**
```sql
CREATE TABLE finance.entities (
  entity_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug          TEXT UNIQUE NOT NULL,     -- 'adge_personal', 'denkers_co_llc'
  display_name  TEXT NOT NULL,
  entity_type   finance.entity_type NOT NULL,
  tax_id        TEXT,                      -- EIN for LLCs, null for individuals
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  notes         TEXT
);
```

**Seed rows:** `adge_personal` (individual), `denkers_co_llc` (llc).

**Done when:** Table exists, two rows present, slugs unique.

---

### Unit: Chart of Accounts table

**What:** Create `finance.accounts` with hybrid CoA structure (five roots + free-form subtree under each).

**Schema sketch:**
```sql
CREATE TABLE finance.accounts (
  account_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  entity_id        UUID NOT NULL REFERENCES finance.entities(entity_id),
  parent_id        UUID REFERENCES finance.accounts(account_id),  -- for hierarchy
  code             TEXT NOT NULL,          -- e.g. '1000', '1100', '1110'
  name             TEXT NOT NULL,          -- 'Assets', 'Checking', 'NBT Checking'
  account_type     finance.account_type NOT NULL,
  account_subtype  finance.account_subtype NOT NULL,
  currency         CHAR(3) NOT NULL DEFAULT 'USD',
  is_active        BOOLEAN NOT NULL DEFAULT true,
  opened_on        DATE,
  closed_on        DATE,
  institution      TEXT,                    -- 'NBT Bank', 'Sidney FCU'
  account_number_last4 TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (entity_id, code)
);
```

**Done when:** Table exists with FKs and unique constraint. No rows yet (seeding happens in a later unit).

---

### Unit: Source observations layer

**What:** Create `finance.source_observations` — the immutable raw import layer. Every line from every CSV/bank feed lands here exactly once.

**Schema sketch:**
```sql
CREATE TABLE finance.source_observations (
  observation_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id        UUID NOT NULL REFERENCES finance.accounts(account_id),
  posted_date       DATE NOT NULL,
  amount            NUMERIC(14,2) NOT NULL,   -- signed: negative = money out
  raw_description   TEXT NOT NULL,
  normalized_description TEXT NOT NULL,       -- lowercase, whitespace normalized
  source_type       TEXT NOT NULL,            -- 'csv_import', 'manual', 'recurring'
  source_file       TEXT,                      -- filename if from CSV
  source_row_num    INTEGER,                   -- row number in source file
  dedup_hash        TEXT NOT NULL UNIQUE,      -- sha256 of account_id|posted_date|amount|normalized_description
  imported_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  is_promoted       BOOLEAN NOT NULL DEFAULT false,  -- has this been turned into ledger entries yet?
  promoted_at       TIMESTAMPTZ
);

CREATE INDEX ON finance.source_observations (account_id, posted_date);
CREATE INDEX ON finance.source_observations (is_promoted) WHERE is_promoted = false;
```

**Done when:** Table exists with indexes, dedup_hash unique constraint works.

---

### Unit: Ledger entries — the double-entry core

**What:** Create `finance.ledger_entries`. This is the heart. Every row is one side (debit or credit) of a transaction. Rows sharing a `transaction_group_id` must balance.

**Schema sketch:**
```sql
CREATE TABLE finance.ledger_entries (
  entry_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  transaction_group_id  UUID NOT NULL,              -- ties balanced entries together
  account_id            UUID NOT NULL REFERENCES finance.accounts(account_id),
  entry_side            finance.entry_side NOT NULL,
  amount                NUMERIC(14,2) NOT NULL CHECK (amount > 0),  -- always positive; side determines direction
  posted_date           DATE NOT NULL,              -- effective date of the transaction
  description           TEXT NOT NULL,
  source_observation_id UUID REFERENCES finance.source_observations(observation_id),  -- nullable: manual entries have none
  created_at            TIMESTAMPTZ NOT NULL DEFAULT now(),
  created_by            TEXT NOT NULL DEFAULT 'system'
);

CREATE INDEX ON finance.ledger_entries (transaction_group_id);
CREATE INDEX ON finance.ledger_entries (account_id, posted_date);
CREATE INDEX ON finance.ledger_entries (source_observation_id);
```

**Balance integrity:** Enforced by a view or a function that checks `SUM(CASE WHEN entry_side='debit' THEN amount ELSE -amount END) = 0 GROUP BY transaction_group_id`. We'll add the check function in this unit.

**Done when:** Table exists, indexes in place, balance-check function exists and is tested with a synthetic balanced + unbalanced insert.

---

### Unit: Clearing accounts + transfer pattern

**What:** Seed the clearing accounts (`Transfer Clearing`, `Opening Balance Clearing`, `Adjustment Clearing`) under each entity. Document the transfer pattern with a worked example. Optionally add a helper function `finance.record_transfer(from_acct, to_acct, amount, date, description)` that creates the two balanced ledger_entries automatically via the clearing account.

**Done when:** Clearing accounts exist in `finance.accounts` with `account_subtype='clearing'`, helper function works, documented in `FINANCE_V2_ARCHITECTURE.md`.

---

### Unit: Loan terms bi-temporal table

**What:** Create `finance.loan_terms` with bi-temporal tracking.

**Schema sketch:**
```sql
CREATE TABLE finance.loan_terms (
  loan_term_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  account_id        UUID NOT NULL REFERENCES finance.accounts(account_id),
  principal_amount  NUMERIC(14,2),
  interest_rate     NUMERIC(6,4),              -- e.g. 0.0649 for 6.49%
  term_months       INTEGER,
  monthly_payment   NUMERIC(14,2),
  origination_date  DATE,
  -- bi-temporal
  valid_from        DATE NOT NULL,             -- real-world: when this term took effect
  valid_to          DATE,                       -- real-world: when it stopped (null = still valid)
  recorded_at       TIMESTAMPTZ NOT NULL DEFAULT now(),  -- knowledge time: when we learned it
  superseded_at     TIMESTAMPTZ,                -- knowledge time: when we replaced it with a better record
  notes             TEXT
);

CREATE INDEX ON finance.loan_terms (account_id, valid_from);
```

**Done when:** Table exists. Test query: "what was the Honda loan rate as of 2025-06-01, as we knew it on 2025-07-01?" returns the right row once seeded with test data.

---

### Unit: Import CLI — `finance-import`

**What:** Build the `finance-import` CLI that reads a CSV (bank export) and writes rows to `finance.source_observations` only. **No ledger writes yet.** Just raw import with dedup.

**Scope:**
- Accepts `--account <slug>` and `--file <path>`
- Parses CSV (start with one format — NBT or Sidney FCU, whichever you pick)
- Computes dedup_hash per row
- Inserts into `source_observations`, skipping duplicates (ON CONFLICT DO NOTHING)
- Reports: rows read, rows inserted, rows skipped as duplicates

**Touches:** New directory `/opt/mythos/finance/` (finally), `/opt/mythos/bin/finance-import` symlink.

**Done when:** Running `finance-import --account nbt_checking --file sample.csv` populates source_observations correctly and is idempotent on re-run.

---

### Unit: Observation → Ledger promotion

**What:** The step that turns `source_observations` into `ledger_entries`. For each unpromoted observation, apply categorization rules to pick a counter-account, create two balanced ledger_entries (one debit, one credit), mark observation as promoted.

**Scope:**
- Categorization rules table: `finance.category_rules` (match on normalized_description pattern → target account)
- Default fallback account: `Uncategorized Expense` / `Uncategorized Income`
- CLI: `finance-promote [--account <slug>] [--dry-run]`
- Idempotent: re-running skips already-promoted observations

**Done when:** Observations promote cleanly, ledger balance integrity holds, uncategorized rows land in fallback account.

---

### Unit: Bi-temporal query CLI — `finance-ledger-as-of`

**What:** CLI that reconstructs account balances and ledger state as of any past date, with optional knowledge-time parameter.

**Scope:**
- `finance-ledger-as-of <date>` — what was the state of the ledger on that date?
- `finance-ledger-as-of <date> --known-at <knowledge-date>` — what did we *think* the state was, as of the knowledge date?
- Outputs balance per account, respecting `valid_from/valid_to` for loan_terms and `created_at`/`superseded_at` for ledger corrections

**Done when:** Point-in-time reconstruction works against a seeded test dataset.

---

### Unit: Reporting API — reconnect the frontend

**What:** Build the `/api/finance/v2/*` endpoints that `DashboardV2.jsx` and `BillsDetailV2.jsx` already expect.

**Known endpoints needed (from existing frontend):**
- `GET /api/finance/v2/dashboard` — accounts grouped (checking, debt), summary strips (cash, debt, net worth), upcoming bills + income
- `GET /api/finance/v2/bills-detail?month=YYYY-MM` — bill list for month with payment history and current-month transactions

**Done when:** Frontend loads real data from the new schema with no mocks.

---

## Out of scope for v2 (explicitly deferred)

- Neo4j integration for finance entities (reviewed, rejected)
- Multi-currency beyond USD
- Investment account position tracking (shares × price) — only cash balances for now
- Tax categorization beyond basic account subtype
- Budgeting / envelope system (separate subsystem if ever built)

---

## Change Log

| Date | Change |
|------|--------|
| 2026-04-12 | Doc created, v1 dropped, plan locked in |
