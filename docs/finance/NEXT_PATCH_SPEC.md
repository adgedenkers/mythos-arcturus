---
title: "Finance v2 — Next Patch Spec"
category: system
status: active
stream: SYS
location: docs/finance
tags: [finance, next-patch, spec]
created: 2026-04-12
updated: 2026-04-12
author: Adge Denkers
---

# Next Patch Spec — Finance v2

> **This file is rewritten every turn.** It describes the *next*
> patch in the locked Finance v2 letter sequence (see
> `SYSTEM_FINANCE.md` for the full ledger and `FINANCE_V2.md` for
> the design plan). At the end of every successful feature patch,
> the follow-up doc patch replaces this file wholesale with the
> spec for the patch after that.
>
> **Never use this file for history.** History lives in
> `SYSTEM_FINANCE.md` → Patch Ledger.

---

## Next: Patch D — Merchants & Patterns

**Intended patch number:** assigned at build time via `mythos-diag streams`.
Do not pre-assign.

### Why
Patch B left `finance.transactions.merchant_id` as an unconstrained
`BIGINT` on purpose — the `merchants` table didn't exist yet.
Patch D creates the merchants registry and the pattern-matching
table, then adds the FK. This unlocks Patch E (the importer), which
needs to resolve raw CSV descriptions to canonical merchants before
entries can be categorized.

**Critical design principle from Jeff Pro's review:** merchant
*resolution* and *categorization* are separate concerns. Patch D
only handles resolution (raw description → canonical merchant).
Categorization rules (merchant → category, with context overrides)
come later in Patch F.

### What

**New enum:** `finance.pattern_type` — values: `exact`, `contains`, `regex`

**New table: `finance.merchants`**

| Column | Type | Notes |
|---|---|---|
| id | BIGSERIAL PK | |
| canonical_name | TEXT NOT NULL | "Walmart", "Dunkin", "Stewart's" |
| display_name | TEXT | optional user-facing override |
| default_category_account_id | BIGINT REFERENCES finance.accounts(id) | nullable, baseline category |
| default_tax_treatment | TEXT | nullable, free-text for now |
| normalized_name_key | TEXT NOT NULL UNIQUE | lowercased, whitespace-collapsed, used for dedup |
| metadata | JSONB NOT NULL DEFAULT '{}' | |
| created_at | TIMESTAMPTZ NOT NULL DEFAULT now() | |
| updated_at | TIMESTAMPTZ NOT NULL DEFAULT now() | |

**New table: `finance.merchant_patterns`**

| Column | Type | Notes |
|---|---|---|
| id | BIGSERIAL PK | |
| pattern | TEXT NOT NULL | e.g. "WM SUPERCENTER" |
| pattern_type | finance.pattern_type NOT NULL | |
| merchant_id | BIGINT NOT NULL REFERENCES finance.merchants(id) | |
| priority | INTEGER NOT NULL DEFAULT 100 | higher wins |
| confidence | INTEGER NOT NULL DEFAULT 100 | 0–100 |
| match_count | INTEGER NOT NULL DEFAULT 0 | incremented by importer |
| last_matched_at | TIMESTAMPTZ | |
| is_active | BOOLEAN NOT NULL DEFAULT true | |
| created_at | TIMESTAMPTZ NOT NULL DEFAULT now() | |

**FK constraint added to existing `finance.transactions`:**
- `transactions.merchant_id` → `merchants.id` (nullable, ON DELETE SET NULL)

**Indexes:**
- `merchants(normalized_name_key)` — already UNIQUE
- `merchant_patterns(pattern_type, priority DESC)`
- `merchant_patterns(merchant_id)`
- `merchant_patterns(is_active) WHERE is_active`

**Trigger (light):** `updated_at` auto-update on `merchants` (simple
`BEFORE UPDATE` that sets `NEW.updated_at = now()`). Optional — skip
if we don't care, since the existing pattern in `accounts` and
`entities` doesn't have this either. **Decision:** skip. Consistency
with existing tables beats extra ceremony.

### How
Follows the SYS-0075/0076 pattern exactly:
1. One SQL migration file, wrapped in `BEGIN`/`COMMIT`, `ON_ERROR_STOP=on`
2. `apply_patch.py` using `PatchBase`
3. Single `run_sql` call
4. Verification block with positive test (insert merchant + pattern,
   reference from a transaction) AND negative test (transaction with
   bogus merchant_id rejected by FK)

**No seeds.** No merchants, no patterns. Those get populated in
Patch E (importer) or Patch F (categorization), whichever needs
them first.

### Success criteria
- `finance.pattern_type` enum exists with 3 values
- `finance.merchants` and `finance.merchant_patterns` exist
- All indexes exist
- FK on `transactions.merchant_id` exists and is enforced
- Positive test passes: insert merchant → insert pattern → insert
  transaction referencing merchant → commit clean, then delete
- Negative test passes: transaction with nonexistent merchant_id
  rejected by FK
- `SYSTEM_FINANCE.md` updated in follow-up doc patch showing D shipped
- `NEXT_PATCH_SPEC.md` replaced by spec for Patch E

### Depends on
- Patch A (SYS-0075) — `finance` schema, `accounts` table for FK target
- Patch B (SYS-0076) — `transactions` table for FK source
- **Does NOT depend on** Patch C (docs) or C.1 (handoff tool)

### Does NOT include
- Any merchant rows (no seed data)
- Any pattern rows
- Categorization rules (Patch F)
- Importer logic (Patch E)
- Archived v1 merchant pattern import (that work happens in E or F)
- Merchant → transaction join queries (Patch G, when the API rewrites)

---

## Open questions relevant to Patch D

*(None block the build. Noted for awareness.)*

- **Normalized name key algorithm:** simple lowercase + whitespace
  collapse for v1. Can upgrade to soundex/metaphone later if dedup
  proves loose. No decision needed in D.
- **`ON DELETE` behavior for transactions.merchant_id:** `SET NULL`
  is safest — deleting a merchant shouldn't orphan transactions.
  This matches the "transactions are envelopes, metadata is mutable"
  rule from §2.4.

---

## After Patch D ships

The follow-up doc patch will:
1. Update `SYSTEM_FINANCE.md` patch ledger (D = shipped)
2. Update `SYSTEM_FINANCE.md` status block (next = E)
3. Replace this file wholesale with Patch E's spec (importer)
4. Update `docs/finance/MANIFEST.yaml` if new validation hooks are needed
   (e.g., "merchants table has row count X")

---

*This spec is ephemeral. The history is in SYSTEM_FINANCE.md.*
