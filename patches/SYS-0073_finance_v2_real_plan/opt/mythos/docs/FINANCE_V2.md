# Finance v2 — Complete Architecture Plan (v2)

**Status:** Plan locked, pending final review round
**Audience:** Castor (Gemini) and Jeff Thinking (ChatGPT) for final review pass
**Version:** v2 — incorporates all feedback from four prior review rounds plus Jeff Pro's second review
**Context:** Personal finance system rebuild on Mythos (self-hosted Postgres + FastAPI + Python workers). V1 was single-entry, hand-maintained, and recently wiped. V2 is a full rewrite from clean slate.

This document consolidates design decisions from five review rounds. Every significant decision is traced to its source in §17. The intent of this review is to catch anything the prior rounds missed before schema work begins.

**Key changes from v1 of this plan:**
- **Neo4j stripped from finance v2 entirely.** Finance is Postgres-only. Subsystem scoping pattern documented in §17 as a reference for future subsystems if needed, but no Neo4j writes happen in finance patches.
- **Entities dimension added as first-class concern** (new §6). Personal vs. LLC is not just a chart-of-accounts concern — it's an entity attribution dimension at the entry level.
- **Semi-monthly added to recurring detection** (§8.1). Biweekly and semi-monthly are distinct frequencies and payroll will punish you for conflating them.
- **PITR and WAL archiving added to reliability layer** (§13.2). pg_dump is necessary but not sufficient for 10-year durability.
- **SYS-0063 preflight patch added** at the front of the sequence to archive v1 code and drop v1 tables before v2 work begins.
- **Patch sequence renumbered** to SYS-0063 through SYS-0071.

---

## 1. Context and constraints

### 1.1 What this system is

A personal finance ledger running on a self-hosted home server. Postgres is the primary and only datastore for finance data. FastAPI serves a web dashboard; a Telegram bot provides quick commands. Python workers handle imports, recurring detection, forecasting, and reconciliation.

The system is personal-only at day one. An LLC will spin up in a few months and share the same ledger, but business entity separation is handled via an entity dimension on ledger entries, not via a separate system.

### 1.2 Scale

- ~15 real-world accounts (checking, credit cards, loans, savings)
- ~40 expense categories plus ~5 income categories
- ~29 recurring bills historically, auto-detected in v2
- ~1,200 historical transactions per year to import from archived CSVs
- Daily re-imports of the most recent 50 transactions per account (rolling window)

### 1.3 What v1 got wrong

Nine failure modes that v2 must eliminate:

1. **Balance tracking as a side effect.** Current balance was derived from the latest transaction's `balance` column, which only existed because some bank CSVs happened to include running balance. Unreliable.
2. **Transfers double-counted.** Paying AMEX from USAA showed as "-$800 spending" unless manually filtered via a `Transfer` category hack.
3. **Bill matching was fuzzy scoring with an overrides escape hatch.** The existence of a `bill_overrides` table was a smell — it meant the matcher wasn't trusted.
4. **Categorization was hardcoded SQL INSERTs.** 200+ merchant patterns in a schema file. Corrections in the UI didn't update the rules.
5. **Recurring bills and income were separate tables with asymmetric schemas.** Same concept, different shapes.
6. **Imports were fire-and-forget.** No undo. A bad import required hand-crafted DELETE statements.
7. **Forecasting treated stable and variable bills identically.** No confidence weighting.
8. **No backup discipline.** The rebuild only exists because data got wiped.
9. **No audit trail for categorization.** When a transaction got its category, there was no record of why.

### 1.4 Design goals for v2 (all locked in)

1. Double-entry ledger as the foundation
2. Account balance = sum of entries, by definition (always provable)
3. Transfers auto-reconcile across accounts
4. Import reversibility (every import is a first-class, undoable event)
5. Merchant intelligence (normalize "WM SUPERCENTER #1234" → canonical Walmart)
6. Learning categorizer (corrections update rules, full audit trail)
7. Auto-detected recurring patterns (not hand-maintained)
8. Confidence-weighted forecasting
9. Entity attribution at the entry level (personal vs. LLC) from day one
10. Robust dedup against daily re-imports where each export overlaps the last by 40+ transactions
11. **Pending transactions are NOT tracked.** Only posted, real transactions enter the ledger.
12. **Backup and restore as first-class concerns**, including PostgreSQL point-in-time recovery

---

## 2. Core architectural decisions

### 2.1 Double-entry ledger (locked)

Every transaction has 2+ entries summing to zero. No exceptions. This is the foundation that makes transfer reconciliation trivial, balance verification exact, and entity/tax splits mathematically natural.

The complexity cost is real but manageable:
- Every CSV row becomes 2+ ledger entries via the importer
- Expense "categories" become real accounts in the chart of accounts (~40 of them)
- Reporting queries work on entries, not transactions

The UX cost is hidden entirely from the user. The dashboard still shows "your transactions" as a list. The double-entry rigor is under the hood.

### 2.2 Integer cents for all amounts (locked)

All monetary values are stored as `BIGINT amount_minor` (signed integer cents). No `NUMERIC`, no `float`, no decimal confusion.

- Drift tolerance is exact zero, because there's no rounding
- Comparison equality is unambiguous
- Math is fast
- The display layer converts to `$N.NN` at render time

### 2.3 Source observations as first-class objects (Jeff Pro's key insight)

**Every CSV row lands in a `source_observations` table, always, regardless of what happens downstream.** This is the layer between raw bank exports and the ledger.

A bank CSV row is not a transaction. It's an *observation* of a transaction. The same underlying posting can be observed multiple times across overlapping daily imports, with description drift between exports. One real-world transfer produces two observations on two accounts. A retroactive bank change produces a new observation of an already-observed transaction with a different amount.

Without a raw observation layer, all of this pressure has to be absorbed by the ledger itself, which means either the ledger becomes mutable (bad — destroys audit trail) or the importer becomes a fragile heuristic nightmare (worse — silently drops real transactions).

With the observation layer, the flow becomes:

```
CSV row → source_observation (raw, always inserted, fingerprinted)
       → matched to existing observation OR becomes new ledger transaction
       → entries in the ledger, linked back to the observation
```

Benefits:
- **Re-imports are handled at the observation layer**, not by mutating ledger truth
- **Description drift stops being scary** — observations are immutable, multiple observations can link to the same transaction
- **Undo becomes relational**: find observations by import_id, reverse their linked entries, mark the observations reversed — no JSON manifest replay
- **Balance assertions can link to specific observations** for provenance
- **Retroactive bank changes become observable and flaggable** instead of silent mutations
- **Replay and testing become trivial**: golden CSV fixtures run against the observation layer, producing reproducible ledger output every time

### 2.4 Bi-temporal ledger: append-only facts, versioned current state

The core ledger facts are append-only. The current state visible in the UI is a versioned view on top of those facts.

**Append-only (immutable):**
- source observations
- imports
- balance assertions
- match decisions
- audit events

**Versioned current state (superseded, not deleted):**
- transaction envelopes (description, memo, merchant link, category assignments)
- individual entries, when the user corrects amount/account/date

When a user "edits" a transaction in the UI:
1. If only metadata changes (description, memo, merchant, category), update in place with an entry in `categorization_log` or similar audit record
2. If the change affects `amount_minor`, `account_id`, or `entry_date`, the API creates reversing entries (marked with `reversed_by_entry_id`) and writes new entries

This gives cryptographic-level auditability ("show me the ledger as it looked on date X as of what we knew on date Y") without UX friction. Typos don't require accounting ceremony; the system handles the correction workflow invisibly.

### 2.5 Transactions always balance (locked)

No `pending` or `draft` transaction status. The ledger invariant is: `SUM(amount_minor) = 0 per transaction_id`. This is enforced via a deferred trigger that runs at commit time.

When an import encounters a row with no clear offsetting account (unknown merchant, unknown category), it uses the `expenses:uncategorized` or `income:uncategorized` system account as the pressure valve. The transaction still balances; the user can recategorize it later via the void-and-replace UI flow.

This is how Beancount and hledger handle the same problem, and it keeps the invariant absolute without the complexity of draft/pending states.

### 2.6 Postgres-only for finance v2

Finance v2 uses Postgres exclusively. Neo4j is intentionally excluded from this subsystem. The decision and its rationale are recorded in §17.

---

## 3. The dedup algorithm (the hardest part)

### 3.1 Why dedup is hard

Daily bank exports include the last 50 transactions per account. Each daily export overlaps the previous by ~40 transactions. The importer must:

- **Never duplicate** a transaction already imported
- **Never drop** a legitimate transaction just because it looks similar to an existing one
- **Handle the case** of two genuinely identical-looking transactions on the same day (two $4.50 Dunkin runs). Both must land in the ledger.
- **Handle description drift** when a bank reformats between exports
- **Not track pending transactions** at all — only posted, real transactions

### 3.2 Algorithm (three-phase, runs against source_observations)

**Phase 1 — Priority identity checks (auto-skip on match, in this order):**

1. **Institution transaction ID match.** If the bank provides a stable `bank_transaction_id` in the CSV, and an existing observation has the same ID, they are definitionally the same posting. Auto-skip.
2. **Exact raw row fingerprint.** Hash the full CSV row after minimal normalization (whitespace, encoding) only. If the hash matches an existing observation, auto-skip.
3. **Running balance + amount + date match.** Only when the observation is at the ledger's current head for that account (no missing transactions between the asserted balance and the current state). Auto-skip if all three match exactly.

**Phase 2 — Coarse bucket + bipartite matching:**

Build coarse candidate buckets keyed on `(account_id, posted_date, signed_amount, normalized_merchant)`. Within each bucket:

1. Collect existing unmatched observations and incoming observations
2. Build all possible pairs between them
3. Score each pair on: description similarity, date delta, running balance continuity (if available), import source profile (per-account tolerance)
4. Solve max-weight bipartite matching across the bucket (Hungarian algorithm — trivial on small buckets)
5. Pairs above the auto-skip threshold are marked as duplicates
6. Unpaired incoming observations proceed to Phase 3

Bipartite matching beats greedy scoring because it handles the "two legitimate identical-looking transactions" case correctly. If existing has `Dunkin A, Dunkin B` and incoming has `Dunkin X, Dunkin Y`, greedy can pair the wrong ones when descriptions drift slightly. Bipartite matching finds the globally optimal assignment.

**Phase 3 — Decision:**

For each incoming observation that didn't auto-skip in Phase 1 or 2:

- **Match score ≥ 95 AND margin from next-best ≥ 20** → auto-skip (mark as duplicate)
- **Match score 70–94, OR score ≥ 95 with thin margin** → flag for review (write to `pending_reconciliation`, notify via Telegram)
- **Match score < 70** → import as new (create ledger transaction with uncategorized pressure-valve entries)

**Key principle: false-positive dedup is worse than false-negative duplicate.** A duplicate in the ledger is visible and fixable. A silent drop poisons balances, forecasts, and reports. The thresholds bias toward importing.

### 3.3 Ledger-State Diff (the multiset cardinality question)

Within each coarse bucket, in addition to bipartite matching, the importer runs a simple cardinality check: count existing unmatched observations (N) and incoming observations (M). Insert exactly `max(0, M - N)` new ones after bipartite matching resolves which is which.

This catches the edge case where the sequence of observations is ambiguous but the total count is clear. If the ledger has 1 Dunkin on Monday and the incoming import has 2 Dunkins on Monday, something was missed — insert the delta.

### 3.4 Per-source import profiles

Different banks have different quirks. An `import_sources` table stores per-institution metadata:

| Column | Purpose |
|---|---|
| `institution_name` | USAA, Sunmark, Sidney FCU, AMEX, etc. |
| `parser_module` | Which parser handles this format |
| `has_transaction_id` | Does the CSV include a stable bank-provided ID? |
| `has_running_balance` | Does the CSV include a running balance column? |
| `date_tolerance_days` | How far can posted dates shift between exports? |
| `description_stable_after_post` | Does the bank rewrite descriptions after posting? |
| `amount_always_exact` | Are amounts ever retroactively adjusted? |
| `date_column_semantics` | `posted` / `effective` / `transacted` |
| `auto_skip_threshold` | Per-source tightness (default 95) |
| `review_threshold` | Per-source review band floor (default 70) |

The matcher reads this profile and tunes its behavior per import. USAA might get `date_tolerance_days=1, has_transaction_id=true` — tight, confident matching. An unfamiliar credit card might get `date_tolerance_days=3, has_transaction_id=false` — looser, more flagging.

### 3.5 Retroactive change handling

When a bank changes a posted transaction (tip adjustment, fee reversal, merchant correction), the new CSV export shows the same `bank_transaction_id` with a different amount or description.

Detection: `bank_transaction_id` exists in `source_observations` with a different amount.

Response:
1. Do NOT auto-apply the change
2. Write the new row as a `source_observation` with `status='flagged'` and `match_reason='retroactive_change'`
3. Telegram alert with the diff
4. User decides manually. Applying the change creates an adjustment transaction (not a mutation of the original observation or ledger entry).

For accounts without stable bank transaction IDs, retroactive changes fall back to heuristic detection via the normal review queue.

---

## 4. Chart of accounts

### 4.1 Structure (hybrid: adjacency list + materialized path)

One `accounts` table. Every account — real-world bank accounts, expense categories, income categories, equity accounts, system accounts — lives in this one table, distinguished by `account_kind` and `account_subtype`.

The table has both:
- **`parent_account_id`** — nullable foreign key for the adjacency list hierarchy. Supports tree traversal and fast "direct children of Expenses:Food" queries.
- **`account_path`** — materialized path column with colon-delimited naming (`expenses:food:groceries`). Supports fast `LIKE 'expenses:food:%'` rollups without recursive CTEs.

The path is derived from the adjacency list on write via a trigger, so they can never be inconsistent. The cost is one extra column; the benefit is both tree-native and flat-path-native queries work optimally.

### 4.2 Account kinds and subtypes

| `account_kind` | `account_subtype` examples | Normal balance |
|---|---|---|
| `asset` | `checking`, `savings`, `cash`, `clearing`, `transit` | debit |
| `liability` | `credit_card`, `loan`, `line_of_credit` | credit |
| `income` | `category` (for `income:salary:va`, etc.) | credit |
| `expense` | `category` (for `expenses:food:groceries`, etc.) | debit |
| `equity` | `opening_balance`, `retained_earnings`, `reconciliation_adjustment` | credit |

### 4.3 Sign convention (locked)

**Debits are positive, credits are negative**, at the entry level. Standard accounting convention.

- Asset account debit (positive) = balance increases
- Asset account credit (negative) = balance decreases
- Liability account debit (positive) = balance decreases (you owe less)
- Liability account credit (negative) = balance increases (you owe more)
- Expense account debit (positive) = expense incurred
- Income account credit (negative) = income received

The UI presents this however makes sense for users ("spending" as positive red numbers, "income" as positive green numbers), but under the hood everything follows standard accounting.

### 4.4 System accounts seeded at patch time

Five mandatory system accounts, created in SYS-0064, flagged with `is_system=true` so they can't be deleted or renamed via the UI:

| Path | Kind | Purpose |
|---|---|---|
| `equity:opening_balances` | equity | Offset for initial account balances (see §4.6) |
| `equity:reconciliation_adjustments` | equity | Explicit corrections only |
| `assets:transit:bank_transfers` | asset | Clearing account for transfers (see §5.1) |
| `expenses:uncategorized` | expense | Pressure valve for unknown expense categorization |
| `income:uncategorized` | income | Pressure valve for unknown income categorization |

### 4.5 Real account naming examples

```
assets:bank:usaa_checking
assets:bank:sunmark_checking
assets:bank:sidney_fcu
assets:bank:nbt
liabilities:cards:amex
liabilities:cards:llbean
liabilities:cards:tsc
liabilities:cards:tjx
liabilities:cards:old_navy
liabilities:loans:usaa_loan
```

### 4.6 Opening balances

Day one, the system has real account balances but no entries to produce them. The solution is standard double-entry practice: an Opening Balance Equity account.

For each account, SYS-0065 generates an opening balance transaction dated the day *before* the earliest CSV row for that account:

```
assets:bank:usaa_checking           +$3452.18
equity:opening_balances             -$3452.18
```

For CSVs that include a running balance, the opening balance is derived automatically: take the balance on the first row, subtract the row's amount, that's the opening balance.

For CSVs without a running balance (most credit cards), the user provides the opening balance manually — a one-time input per account, typically from an old statement PDF. If no statement can be found, the account is seeded at $0 on the earliest date, and the system tolerates a constant offset until a real reconciliation point arrives.

### 4.7 Category naming examples

```
expenses:food:groceries
expenses:food:restaurants
expenses:food:fast_food
expenses:utilities:electric
expenses:utilities:internet
expenses:utilities:phone
expenses:transportation:gas
expenses:transportation:maintenance
expenses:entertainment:streaming
expenses:entertainment:games
expenses:phone
expenses:interest:loan
income:salary:va
income:interest
```

Note: category paths do NOT encode personal vs. LLC. That's the entity dimension, §6. A single `expenses:phone` account holds both personal and business phone expenses, distinguished by `entity_id` on entries.

---

## 5. Transfers and special cases

### 5.1 Transfers via clearing account

When money moves between two of your own accounts, it flows through `assets:transit:bank_transfers` so that each side of the transfer can be imported independently without requiring the two halves to be matched at import time.

**Example: $800 payment from USAA to AMEX**

Monday import of USAA CSV creates:
```
assets:bank:usaa_checking           -$800
assets:transit:bank_transfers       +$800
```

Wednesday import of AMEX CSV creates (a few days later, when the payment posts):
```
assets:transit:bank_transfers       -$800
liabilities:cards:amex              +$800
```

The clearing account's balance is the health check: **if it's zero, all transfers have cleared; if it's non-zero, there's an in-flight transfer or an orphaned leg.**

A background worker scans the clearing account daily. If it's been non-zero for more than 5 days, alert the user — it means one leg imported but the other didn't.

### 5.2 Post-hoc transfer merging

After both legs have posted via the clearing account, a background worker can optionally merge them into a single logical transaction envelope (with a shared `transfer_group_id`) so the UI can display them as one event rather than two.

This merge is:
- **Post-hoc**, not required at import time (the ledger is valid immediately)
- **Cosmetic**, not structural (the underlying entries are unchanged)
- **Reversible** if the merge was wrong

Match criteria for post-hoc merging:
- Opposite signs on the clearing account leg
- Same absolute amount (exact match required)
- Different real-world accounts
- Date delta within account-profile window
- Description pair dictionary match (e.g., "AMEX EPAYMENT" ↔ "PAYMENT - THANK YOU")
- High uniqueness margin vs. next-best candidate

Confidence bands:
- High → auto-merge
- Medium → suggest merge in UI, user confirms
- Low → leave as two separate transactions

### 5.3 Loan payments (special case: three-entry split)

Loan payments are NOT pure transfers. They split into principal and interest:

```
assets:bank:usaa_checking           -$500.00
liabilities:loans:usaa_loan         +$430.00   (principal reduction)
expenses:interest:loan              +$70.00    (interest expense)
```

The principal/interest split is stored on the loan account as `metadata.default_split` (derived from the loan amortization schedule). The importer applies the default split automatically; the user can correct it manually per payment if the actual statement differs.

**Jeff Pro's pushback:** bank-to-loan should not be treated as a transfer candidate by the auto-merger. Bank-to-credit-card auto-merges fine; bank-to-bank auto-merges fine; bank-to-loan stays provisional until explicit user confirmation or lender-side evidence exists.

**Open question:** Is there a cleaner way to represent loan amortization schedules that supports automatic split generation without requiring a full loan-management module? See §16.

### 5.4 Split transactions (entry-level, first-class)

A single CSV row can produce a transaction with 3+ entries when the user splits it. Examples:

- **Mixed-purpose Target run:** $100 charge, split into $60 groceries + $40 household goods
- **Mixed-entity Amazon order:** $200 charge, split into $120 personal + $80 LLC (see §6)
- **Payroll deposit:** Gross → net via multiple entries for tax, retirement, etc.

The UI must support splits as a first-class operation:
- Edit a transaction → "Split into multiple categories"
- Each split row is an entry
- Save templates for recurring splits (e.g., "phone bill: 30% LLC / 70% personal")
- Audit trail shows the original un-split state via the bi-temporal pattern

---

## 6. Entity attribution (new in v2 of this plan)

### 6.1 Why entities are a first-class dimension

Personal vs. LLC is not just a categorization concern. It's an entity attribution dimension that answers the question: *whose economic activity does this entry belong to?*

The chart of accounts tells you *where* a dollar was spent (`expenses:phone`). The entity dimension tells you *whose books it belongs on* (Personal or LLC). These are independent questions and both need to be representable.

**Concrete example:** The LLC is active and you use the business AMEX for a personal meal by accident.

```
Transaction: "Personal meal on business card"

liabilities:cards:amex_business    -$50   entity: LLC
expenses:meals                     +$50   entity: Personal
equity:owner_draw                  +$0    (implicit — Personal owed LLC $50)
```

The account path on the expense side is `expenses:meals`. The entity on that entry is `Personal`, while the liability side sits on the LLC's books. This is "owner uses business card for personal expense" — a real accounting event that needs representing cleanly.

A chart-of-accounts-only approach can't handle this cleanly because you'd need parallel account trees (`expenses:personal:meals` and `expenses:llc:meals`) and you'd lose the ability to ask "total meals spending regardless of entity" without string matching on paths.

### 6.2 Schema

**`entities`** table, seeded at SYS-0064 with two rows:

```
id  name                  kind        is_active
1   Personal              individual  true
2   Denkers Co. LLC       llc         false     (dormant until activated)
```

**`entries`** table gets an `entity_id` column with a NOT NULL constraint and default value `1` (Personal). When the LLC activates, you flip `is_active=true` on entity 2 and start routing business-side entries with `entity_id=2`.

### 6.3 Migration cost: near-zero

Because the column defaults to `Personal`, all existing history lands on the Personal entity correctly and automatically. When the LLC activates, new transactions can split across entities naturally via the existing multi-entry infrastructure. No schema migration, no data migration, just a flag flip and new entries.

### 6.4 Tax treatment lives on entries, not entities

The entity dimension and the tax treatment dimension are separate. An entry has:
- `entity_id` — whose books it belongs on
- `tax_treatment` — how the IRS treats it (50% deductible, depreciable, capitalized, etc.)

A business meal entry might have `entity_id=LLC` and `tax_treatment='meals_50_percent'`. A business office expense might have `entity_id=LLC` and `tax_treatment='fully_deductible'`. A personal meal has `entity_id=Personal` and `tax_treatment=NULL` (irrelevant).

### 6.5 Reporting

Schedule C reporting becomes:

```sql
SELECT a.account_path, SUM(e.amount_minor) / 100.0 AS total
FROM entries e
JOIN accounts a ON a.id = e.account_id
JOIN entities ent ON ent.id = e.entity_id
WHERE ent.name = 'Denkers Co. LLC'
  AND a.account_kind = 'expense'
  AND e.entry_date BETWEEN $1 AND $2
GROUP BY a.account_path;
```

Combined entity + tax-treatment reporting for mixed-deductibility categories:

```sql
SELECT a.account_path, e.tax_treatment, SUM(e.amount_minor) / 100.0
FROM entries e
JOIN accounts a ON a.id = e.account_id
WHERE e.entity_id = (SELECT id FROM entities WHERE name = 'Denkers Co. LLC')
  AND a.account_kind = 'expense'
GROUP BY a.account_path, e.tax_treatment;
```

### 6.6 Non-cash tax adjustments

Things like mileage deductions, home office allocations, and depreciation are not direct ledger entries — they're computed at tax time from other data. These belong in a separate `tax_adjustments` table (not built in SYS-0064; added later when needed).

---

## 7. Merchant resolution and categorization learning

### 7.1 Three-layer model

Merchant resolution and categorization are **separate concerns** and must not be conflated.

**Layer 1 — Merchant resolution.** Raw CSV description → canonical merchant. Handled by `merchant_patterns` table with `exact`, `contains`, or `regex` patterns.

**Layer 2 — Default categorization.** Each merchant has a `default_category_account_id` — Walmart defaults to `expenses:shopping:general`, Dunkin defaults to `expenses:food:fast_food`. This is the baseline.

**Layer 3 — Context-sensitive overrides.** `categorization_rules` table with a specificity ladder:

1. Exact raw description match (most specific)
2. Merchant + account scope ("Walmart on Sidney FCU = Groceries")
3. Merchant + amount range ("Walmart over $100 = Groceries")
4. Merchant + memo keyword
5. Merchant default (least specific)

The categorizer walks the ladder top-to-bottom and applies the first matching rule.

### 7.2 Learning loop: append-first, promote-later

User corrections in the UI do NOT mutate existing rules. They flow through a staged promotion workflow:

1. **First correction on a pattern:** Write a `correction_event` to `categorization_log`. No rule created.
2. **Second matching correction:** Create a `suggested_rule` in `categorization_rules` with `status='suggested'`. The user sees it in the UI as "Create this rule? It would fix 2 similar past transactions."
3. **Third matching correction OR user explicitly accepts:** Promote to `status='active'`.

Rules are versioned via `supersedes_rule_id`. You can trace why any transaction got its current category back through the rule that fired, to the correction that created the rule, to the original import. Full audit trail.

### 7.3 Deciding merchant vs. category errors

When a user corrects a category on a transaction, the system asks internally: **was the merchant wrong, or was the merchant right and the category wrong?**

- If merchant was correct, the fix is at the categorization layer (new/updated `categorization_rules` entry)
- If merchant was wrong, the fix is at the merchant resolution layer (new/updated `merchant_patterns` entry)

This routing is done heuristically on the backend: if the displayed merchant name matches the CSV description's canonical merchant (per current rules), assume the merchant was correct and route the correction to categorization. Otherwise, surface both options in the UI and let the user pick.

---

## 8. Recurring pattern detection

### 8.1 Frequency set (updated)

Test against these frequencies:

- **Weekly** (6–8 day gaps)
- **Biweekly** (13–15 day gaps) — 26 occurrences per year
- **Semi-monthly** (twice a month on fixed dates, e.g., 1st and 15th) — 24 occurrences per year
- **Monthly** (27–33 day gaps)
- **Quarterly** (85–97 day gaps)
- **Annual** (350–380 day gaps)

**Critical: biweekly and semi-monthly are distinct.** Biweekly has 26 occurrences per year; semi-monthly has 24. A semi-monthly pay schedule misclassified as biweekly will produce systematic forecasting errors. The detector must distinguish them by calendar anchor analysis — semi-monthly has tight day-of-month clusters (e.g., always 1st and 15th), biweekly drifts through the calendar.

### 8.2 Algorithm: gap histogram + calendar anchoring + rolling stats

**Not FFT/autocorrelation.** Sparse, irregular, calendar-driven, business-day-shifted event sequences are not clean continuous signals. Signal-processing tools are the wrong hammer.

**Step 1 — Compute inter-arrival gaps.** For each merchant+account+direction stream, sort occurrences by date and compute `gap_i = date_i - date_(i-1)`.

**Step 2 — Weighted gap histogram against frequency buckets.** If ≥70% of gaps land in one bucket, that's the candidate frequency.

**Step 3 — Calendar anchoring.** For monthly-ish candidates, check:
- Day-of-month distribution
- "First business day" / "last business day" behavior
- Nth-weekday patterns
- For semi-monthly: two distinct day-of-month clusters

Utilities and payroll often aren't "every 30 days" — they're "around the first weekday."

**Step 4 — Amount stability classification.** Use rolling mean, rolling standard deviation, and EWMA for drift detection:

- `fixed` — coefficient of variation < 1%
- `bounded_variable` — CoV < 10%
- `drifting` — linear trend slope detected
- `irregular` — high variance, no trend

**Step 5 — Confidence score.** A 0–1 score combining:

```
confidence = 0.45 * interval_fit   (date residual tightness)
           + 0.25 * coverage        (observed / expected)
           + 0.20 * recency         (decays if expected date passes without occurrence)
           + 0.10 * amount_fit      (lightly weighted amount stability)
```

Minimum observation requirements:
- Weekly/biweekly/semi-monthly: 5 observations before high confidence
- Monthly/quarterly: 4 observations
- Annual: 2 observations for tentative detection, 3 for high confidence
- Deactivate only after multiple consecutive missed windows, not one

**Step 6 — Online updates.** When a new event arrives for an active pattern:
- Update gap histogram
- Update calendar anchor distribution
- Update EWMA amount stats
- Update confidence
- Downgrade if too many consecutive misses

### 8.3 Step-change detection

For `drifting` patterns, a separate detector handles sudden jumps (insurance premium goes from $85 to $110 on Jan 1). Rule: if `abs(new_amount - EWMA) > 20% * EWMA` for two consecutive occurrences, reset the EWMA window and log a `step_change_event`.

### 8.4 Provider switches (future abstraction)

"Electric company changes name but the bill is conceptually the same" is an **obligation identity** problem, not a recurrence detection problem. The raw pattern detector should not try to infer "this replaced that" from thin air.

**Current plan:** Leave a nullable `series_id` column on `recurring_patterns` in SYS-0064. A future `recurring_series` or `obligations` table handles cross-merchant obligation identity when the provider-switch problem actually bites. Zero cost now, future-proofed.

### 8.5 Transfer exclusion

Entries hitting `assets:transit:bank_transfers` are explicitly excluded from recurring detection. Transfers are their own concept and shouldn't pollute the pattern detector.

### 8.6 Suggestion-first, never auto-applied

Detected patterns are written with `status='suggested'`. The user reviews them in the dashboard and confirms or rejects each one. Only confirmed patterns feed forecasting.

Low-confidence patterns (below minimum observation thresholds) are marked `needs_more_data` and not shown until they mature.

---

## 9. Forecasting

### 9.1 Confidence-weighted projection

Walks forward from today using `status='active'` recurring patterns:

- **Fixed stability:** Project exact EWMA amount on expected date. Tight band.
- **Bounded variable:** Project EWMA mean ± stddev. Medium band.
- **Drifting:** Project trend-extrapolated amount ± stddev. Wider band.
- **Irregular:** Flag as "not forecastable," exclude from projection line.

Forecast output for each day includes:
- Central projection (most likely balance)
- Lower bound (95th percentile worst case)
- Upper bound (95th percentile best case)

The dashboard renders the central line as solid and the bounds as a shaded region.

### 9.2 Daily cash flow projection

Day-by-day for the next N days (14, 30, 60):

1. Start from current balance
2. For each day, add the sum of projected recurring transactions for that day
3. Propagate the balance forward
4. Render with confidence bands

---

## 10. Balance assertions (the gold-standard check)

### 10.1 Source running balance vs. balance assertions

**Not every running balance from a CSV is an authoritative assertion.** If an export has a 50-transaction window and rows are missing before the window, the running balance on row 1 reflects the bank's state but may not be reproducible from the ledger's current state.

Two separate concepts:

**`source_observations.source_running_balance_minor`** — every observation that has a running balance gets this column populated. Always.

**`balance_assertions`** — a derived, promoted subset of source running balances that are confirmed to be authoritative reconciliation points. An observation's running balance is promoted to an assertion only when:

- The observation is the *latest* row for its account in the ledger's history, OR
- The ledger has a continuous chain of observations from the beginning to this observation (no gaps)

### 10.2 Drift check

After every import, for each account with at least one new assertion:

```
sum(entries for account X through assertion date) ≟ asserted_balance
```

**Drift severity bands:**

- **$0.00 exact match** → silent success
- **$0.01–$0.09** → warning severity, logged, non-urgent Telegram notification
- **$0.10 and above** → critical severity, immediate Telegram alert, block further imports for that account until resolved

Integer cents means $0.00 is the default expected state. Any drift is information worth investigating, even at the penny level.

### 10.3 Manual reconciliation

For accounts without running balance in CSVs (most credit cards), the user can manually assert a balance:

```
/reconcile liabilities:cards:amex 2026-04-15 -1247.89
```

This creates a `balance_assertion` with `source='manual'` and runs the drift check.

Assertions also come from statement imports (PDF parsing, future feature) and can be flagged as `source='statement_closing'`.

---

## 11. Imports and undo

### 11.1 Import lifecycle

1. **User drops CSV in `~/Downloads/`.** Patch monitor detects it, routes to the finance importer.
2. **Importer opens an `imports` record** with status `running`, timestamps, source file, account.
3. **For each CSV row:**
   - Create a `source_observation`
   - Run the dedup algorithm (Phase 1 → 2 → 3)
   - If new, create a ledger transaction with entries
   - If duplicate, link the observation to the existing transaction
   - If flagged, create a `pending_reconciliation` entry
4. **After all rows processed:**
   - Run balance assertion promotion
   - Run the drift check
   - Update the `imports` record with final counts and status
5. **Post-import:**
   - Run the background recurring pattern updater
   - Run the transfer clearing account health check
   - Trigger pg_dump backup (see §13)
   - Send a Telegram summary: "USAA import: 12 new, 38 already present, 0 flagged. Balance check ✓."

### 11.2 Undo (reversal)

Undoing an import is a relational operation:

1. Find all `source_observations` where `import_id = N`
2. For each observation with a `matched_transaction_id`:
   - Create reversing entries (void-and-replace pattern)
   - Mark the original entries with `reversed_by_entry_id`
3. Mark the observations with `status='reversed'`
4. Mark the import with `reversed_at = now()` and `reversed_by = user`

**No JSON manifest replay.** The `change_manifest jsonb` column on `imports` exists as an audit artifact, but it's not the source of truth for reversal. The source of truth is the relational links between observations and entries.

### 11.3 Import reversibility constraints

Some imports can't be cleanly reversed:

- If downstream transactions have been manually edited since the import, the reversal might conflict
- If the import is old enough that subsequent imports have established new reconciliation points, rolling back invalidates those points

In these cases, the import is marked `can_reverse=false` and the UI prevents undo (or requires explicit user override).

**Open question (§16):** what's the right UX for partial reversal when downstream edits exist?

---

## 12. (Reserved — previously Neo4j subsystem scoping)

Finance v2 is Postgres-only. Neo4j integration was considered and deliberately excluded. See §17 for the decision rationale and the subsystem scoping pattern (preserved as a reference for future subsystems that may need it).

---

## 13. Reliability layer (backup, restore, replay)

### 13.1 Why this exists

The only reason this rebuild is happening is because data got wiped. V1 had no backup discipline. V2 must not repeat that mistake. This is non-negotiable.

### 13.2 Two-tier durability

**Tier 1: PostgreSQL point-in-time recovery (PITR) with WAL archiving.** This is the primary durability mechanism.

- Continuous WAL (write-ahead log) shipping to off-host encrypted storage
- Allows restore to *any second* in the retention window, not just to snapshot boundaries
- Standard PostgreSQL feature, well-documented, battle-tested
- Retention: 30 days of continuous PITR capability

**Tier 2: `pg_dump` snapshots after every import.** Secondary mechanism for convenience and disaster recovery.

- Compressed and encrypted (gpg with a key stored in the Mythos secrets vault)
- Stored off-host alongside WAL archives
- Easy to inspect, easy to restore on a fresh machine without full PITR setup
- Retention: rolling 90 days of dumps, monthly full dumps kept indefinitely

The pg_dump is still useful for portability and spot-checks, but PITR is the real durability guarantee.

### 13.3 Restore drill

Documented procedure in `/opt/mythos/finance/RESTORE_PROCEDURE.md`.

Runnable commands:

```bash
finance-restore --dry-run <backup-id>
# Verifies: backup exists, is readable, passes integrity check,
#           schema is compatible, restore would succeed
# Does NOT touch the live database

finance-restore --execute <backup-id>
# 1. Creates a staging schema
# 2. Restores the backup into staging
# 3. Runs invariant checks (ledger balance, referential integrity, assertion drift)
# 4. If all pass, swaps staging into place
# 5. Archives the current state first

finance-restore-pitr --target-time '2026-04-15 14:23:00'
# Uses PITR to restore to a specific point in time
# Runs into a staging schema, verifies, then swaps
```

### 13.4 Golden CSV fixture corpus

`/opt/mythos/finance/test_fixtures/` contains anonymized real CSV exports committed to git. Covers:
- All 11 account types
- Edge cases: retroactive changes, description drift, same-day duplicates, pending→posted transitions, semi-monthly payroll
- At least 6 months of history

Used by `finance-replay-test` to verify the importer produces identical ledger output on every run. Any divergence is a regression.

### 13.5 Monthly automated restore drill

A systemd timer runs `finance-restore --dry-run <latest>` on the first of every month. Restores to a temporary schema, verifies it matches current state, drops the temp schema. Alerts if anything fails.

This is the drill that catches "backups succeeded every day but no one ever verified you could restore from them" — the classic disaster recovery failure mode.

---

## 14. Complete table schema (outline)

This is a structural overview. Full SQL is SYS-0064's deliverable.

### 14.1 Entities and accounts

**`entities`** — entity attribution dimension
```
id              BIGSERIAL PK
name            TEXT UNIQUE NOT NULL
kind            entity_kind_enum NOT NULL  -- individual/llc/corporation/trust
is_active       BOOLEAN NOT NULL DEFAULT true
tax_id_masked   TEXT
metadata        JSONB DEFAULT '{}'::jsonb
created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
```

Seeded at SYS-0064 with `Personal` (active) and `Denkers Co. LLC` (inactive).

**`accounts`** — chart of accounts
```
id                  BIGSERIAL PK
account_path        TEXT UNIQUE NOT NULL      -- 'expenses:food:groceries'
name                TEXT NOT NULL
account_kind        account_kind_enum NOT NULL
account_subtype     TEXT NOT NULL
parent_account_id   BIGINT REFERENCES accounts(id)
normal_balance      normal_balance_enum NOT NULL  -- 'debit' or 'credit'
currency_code       TEXT NOT NULL DEFAULT 'USD'
is_postable         BOOLEAN NOT NULL DEFAULT true
is_system           BOOLEAN NOT NULL DEFAULT false
is_active           BOOLEAN NOT NULL DEFAULT true
institution         TEXT
account_number_masked TEXT
abbreviation        TEXT                       -- 'USAA', 'AMEX'
metadata            JSONB DEFAULT '{}'::jsonb
created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at          TIMESTAMPTZ NOT NULL DEFAULT now()
```

### 14.2 Transactions and entries

**`transactions`** — the envelope around entries
```
id                    BIGSERIAL PK
description           TEXT NOT NULL
merchant_id           BIGINT REFERENCES merchants(id)
memo                  TEXT
kind                  transaction_kind_enum NOT NULL  -- imported/manual/transfer/adjustment/reversal/opening_balance
posted_date           DATE NOT NULL
effective_date        DATE
imported_at           TIMESTAMPTZ
transfer_group_id     UUID                          -- links pair of transfer transactions
reversed_by_transaction_id BIGINT REFERENCES transactions(id)
metadata              JSONB DEFAULT '{}'::jsonb
created_at            TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at            TIMESTAMPTZ NOT NULL DEFAULT now()
```

**`entries`** — the ledger itself, append-only
```
id                    BIGSERIAL PK
transaction_id        BIGINT NOT NULL REFERENCES transactions(id)
account_id            BIGINT NOT NULL REFERENCES accounts(id)
entity_id             BIGINT NOT NULL REFERENCES entities(id) DEFAULT 1
amount_minor          BIGINT NOT NULL                -- signed integer cents
entry_date            DATE NOT NULL
tax_treatment         TEXT                          -- nullable, controlled vocab
reversed_by_entry_id  BIGINT REFERENCES entries(id)
created_at            TIMESTAMPTZ NOT NULL DEFAULT now()

-- Deferred trigger enforces: SUM(amount_minor) = 0 per transaction_id
```

### 14.3 Source observations and imports

**`source_observations`** — every CSV row, always inserted
```
id                          BIGSERIAL PK
import_id                   BIGINT NOT NULL REFERENCES imports(id)
account_id                  BIGINT NOT NULL REFERENCES accounts(id)
bank_transaction_id         TEXT
posted_date                 DATE NOT NULL
effective_date              DATE
amount_minor                BIGINT NOT NULL
raw_description             TEXT NOT NULL
normalized_description      TEXT NOT NULL
dedup_normalized_description TEXT NOT NULL
source_running_balance_minor BIGINT
row_order                   INTEGER
raw_row                     JSONB NOT NULL
exact_fingerprint           TEXT NOT NULL
coarse_fingerprint          TEXT NOT NULL
matched_transaction_id      BIGINT REFERENCES transactions(id)
matched_observation_id      BIGINT REFERENCES source_observations(id)
status                      observation_status_enum NOT NULL  -- new/duplicate/matched/flagged/reversed/ignored
match_method                TEXT
match_score                 INTEGER
match_margin                INTEGER
created_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
```

**`imports`** — first-class import events
```
id                  BIGSERIAL PK
source_file         TEXT NOT NULL
account_id          BIGINT NOT NULL REFERENCES accounts(id)
import_source_id    BIGINT REFERENCES import_sources(id)
started_at          TIMESTAMPTZ NOT NULL DEFAULT now()
completed_at        TIMESTAMPTZ
status              import_status_enum NOT NULL  -- running/completed/failed/reversed
rows_total          INTEGER
rows_new            INTEGER
rows_updated        INTEGER
rows_skipped        INTEGER
rows_flagged        INTEGER
drift_detected      BOOLEAN DEFAULT false
drift_amount_minor  BIGINT
change_manifest     JSONB                        -- audit artifact only
can_reverse         BOOLEAN NOT NULL DEFAULT true
reversed_at         TIMESTAMPTZ
reversed_by         TEXT
```

**`import_sources`** — per-institution profiles
```
id                              BIGSERIAL PK
institution_name                TEXT UNIQUE NOT NULL
parser_module                   TEXT NOT NULL
has_transaction_id              BOOLEAN NOT NULL DEFAULT false
has_running_balance             BOOLEAN NOT NULL DEFAULT false
date_tolerance_days             INTEGER NOT NULL DEFAULT 1
description_stable_after_post   BOOLEAN NOT NULL DEFAULT true
amount_always_exact             BOOLEAN NOT NULL DEFAULT true
date_column_semantics           TEXT NOT NULL DEFAULT 'posted'
auto_skip_threshold             INTEGER NOT NULL DEFAULT 95
review_threshold                INTEGER NOT NULL DEFAULT 70
notes                           TEXT
created_at                      TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at                      TIMESTAMPTZ NOT NULL DEFAULT now()
```

### 14.4 Merchants and categorization

**`merchants`** — canonical merchant registry
```
id                          BIGSERIAL PK
canonical_name              TEXT NOT NULL
display_name                TEXT
default_category_account_id BIGINT REFERENCES accounts(id)
default_tax_treatment       TEXT
normalized_name_key         TEXT NOT NULL
metadata                    JSONB DEFAULT '{}'::jsonb
created_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
```

**`merchant_patterns`** — raw description → merchant
```
id                  BIGSERIAL PK
pattern             TEXT NOT NULL
pattern_type        pattern_type_enum NOT NULL  -- exact/contains/regex
merchant_id         BIGINT NOT NULL REFERENCES merchants(id)
priority            INTEGER NOT NULL DEFAULT 100
confidence          INTEGER NOT NULL DEFAULT 100
match_count         INTEGER NOT NULL DEFAULT 0
last_matched_at     TIMESTAMPTZ
is_active           BOOLEAN NOT NULL DEFAULT true
created_at          TIMESTAMPTZ NOT NULL DEFAULT now()
```

**`categorization_rules`** — context-sensitive category overrides
```
id                      BIGSERIAL PK
merchant_id             BIGINT REFERENCES merchants(id)
account_id              BIGINT REFERENCES accounts(id)
entity_id               BIGINT REFERENCES entities(id)
amount_min_minor        BIGINT
amount_max_minor        BIGINT
description_pattern     TEXT
direction               direction_enum            -- inflow/outflow
category_account_id     BIGINT NOT NULL REFERENCES accounts(id)
tax_treatment           TEXT
priority                INTEGER NOT NULL DEFAULT 100
status                  rule_status_enum NOT NULL -- suggested/active/retired
confidence              INTEGER NOT NULL DEFAULT 50
source                  TEXT NOT NULL             -- manual/derived/system
supersedes_rule_id      BIGINT REFERENCES categorization_rules(id)
hit_count               INTEGER NOT NULL DEFAULT 0
last_hit_at             TIMESTAMPTZ
is_active               BOOLEAN NOT NULL DEFAULT true
created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
```

**`categorization_log`** — every categorization event
```
id                      BIGSERIAL PK
transaction_id          BIGINT REFERENCES transactions(id)
entry_id                BIGINT REFERENCES entries(id)
account_id              BIGINT REFERENCES accounts(id)
source                  TEXT NOT NULL             -- rule/manual/system/correction
rule_id                 BIGINT REFERENCES categorization_rules(id)
confidence              INTEGER
created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
superseded_by           BIGINT REFERENCES categorization_log(id)
```

### 14.5 Recurring patterns

**`recurring_patterns`** — auto-detected recurring cash flows
```
id                      BIGSERIAL PK
merchant_id             BIGINT REFERENCES merchants(id)
account_id              BIGINT NOT NULL REFERENCES accounts(id)
category_account_id     BIGINT REFERENCES accounts(id)
entity_id               BIGINT REFERENCES entities(id)
direction               direction_enum NOT NULL
frequency               frequency_enum NOT NULL   -- weekly/biweekly/semi_monthly/monthly/quarterly/annual/irregular
day_rule                TEXT                      -- exact_day/business_day/nth_weekday/end_of_month/semi_monthly_days
expected_days           INTEGER[]                 -- e.g., [1, 15] for semi-monthly
amount_stats            JSONB NOT NULL            -- {mean, stddev, min, max, ewma, sample_size}
stability               stability_enum NOT NULL   -- fixed/bounded_variable/drifting/irregular
confidence              INTEGER NOT NULL
last_occurrence         DATE
next_expected           DATE
series_id               BIGINT                    -- nullable, reserved for future recurring_series
status                  pattern_status_enum NOT NULL  -- suggested/active/retired/needs_more_data
created_at              TIMESTAMPTZ NOT NULL DEFAULT now()
updated_at              TIMESTAMPTZ NOT NULL DEFAULT now()
```

### 14.6 Balance assertions

**`balance_assertions`** — authoritative balance points
```
id                          BIGSERIAL PK
account_id                  BIGINT NOT NULL REFERENCES accounts(id)
asserted_at                 TIMESTAMPTZ NOT NULL
asserted_balance_minor      BIGINT NOT NULL
balance_type                assertion_type_enum NOT NULL  -- running/statement_closing/manual/opening
source                      TEXT NOT NULL                 -- bank_export/manual/statement
source_observation_id       BIGINT REFERENCES source_observations(id)
import_id                   BIGINT REFERENCES imports(id)
is_authoritative            BOOLEAN NOT NULL DEFAULT true
drift_amount_minor          BIGINT                        -- computed at check time
notes                       TEXT
created_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
```

### 14.7 Pending reconciliation

**`pending_reconciliation`** — the review queue
```
id                          BIGSERIAL PK
source_observation_id       BIGINT NOT NULL REFERENCES source_observations(id)
import_id                   BIGINT NOT NULL REFERENCES imports(id)
candidate_transaction_ids   BIGINT[]
score                       INTEGER
margin                      INTEGER
reason                      TEXT NOT NULL
created_at                  TIMESTAMPTZ NOT NULL DEFAULT now()
resolved_at                 TIMESTAMPTZ
resolution                  reconciliation_resolution_enum  -- imported/skipped/merged
resolved_by                 TEXT
```

---

## 15. Patch sequence (nine patches, SYS-0063 through SYS-0071)

Each patch is independently buildable and verifiable. The system is functional (with fewer features) after every patch.

### SYS-0063 — `finance_v1_preflight`

**What it does:** Clears v1 out of the way before v2 work begins.

1. Verify every v1 finance table is empty (safety check; abort if any table has rows)
2. Archive v1 code from `/opt/mythos/finance/` to `/opt/mythos/finance/archive/v1_20260410/`
3. Drop v1 tables in reverse dependency order:
   - `bill_overrides`, `bill_payments`, `recurring_bills`, `recurring_income`, `import_logs`, `categories`, `category_mappings`, `category_rules`, `transactions`, `accounts`
4. Drop any v1-specific triggers, functions, sequences
5. Verify Postgres is clean (no orphaned references)
6. Update `ARCHITECTURE.md` to remove v1 finance section
7. Update `TODO.md` to mark v1 archived

**Why a separate patch?** v1 removal and v2 creation have different rollback semantics. Splitting them provides a natural checkpoint to verify the DB is clean before committing to v2 schema.

**Verification:** `\dt` shows no v1 finance tables. `/opt/mythos/finance/archive/v1_20260410/` contains the archived code.

**Rollback:** Restore the archive directory to `/opt/mythos/finance/`. V1 tables cannot be recreated (they were empty anyway, so nothing is actually lost).

### SYS-0064 — `finance_v2_schema`

**What it does:** Creates every v2 table listed in §14. Creates all enums. Seeds the `entities` table (Personal + LLC). Seeds the five system accounts. Seeds `import_sources` for the 11 known accounts. Creates the deferred balance constraint trigger. Creates the materialized path derivation trigger. Updates STREAMS.json, PATCH_HISTORY.md, ARCHITECTURE.md.

**Verification after install:**
- `\dt` shows all new tables
- `SELECT name FROM entities` returns Personal and Denkers Co. LLC
- `SELECT account_path FROM accounts WHERE is_system = true` returns the 5 seeded accounts
- `SELECT institution_name FROM import_sources` returns the 11 expected banks
- Deferred balance constraint rejects unbalanced test transactions
- Materialized path trigger correctly derives `account_path` when a new account is inserted

**Rollback:** DROP every v2 table in reverse dependency order. DROP enums.

### SYS-0065 — `finance_v2_importer`

**What it does:** Builds the importer pipeline:
- CSV parsers for USAA, Sunmark, Sidney FCU, NBT, and credit card formats (built fresh, not ported from v1 — but informed by the archived v1 parsers)
- Ingestion writes raw rows to `source_observations` first
- Three-phase dedup algorithm (priority identity → bipartite bucket matching → decision)
- Transaction generation with uncategorized pressure-valve categorization
- Opening balance generation per account
- Balance assertion promotion and drift checking
- Import record creation with change_manifest
- All entries default to `entity_id = Personal`

Then runs the historical re-import from `/opt/mythos/finance/archive/imports/` in chronological order.

**Verification:**
- `SELECT account_path, SUM(e.amount_minor)/100.0 FROM accounts a JOIN entries e ON e.account_id=a.id WHERE a.account_kind='asset' GROUP BY account_path` matches the current bank balances to the penny
- All observations have `status IN ('matched', 'duplicate', 'flagged')`, none are 'new' (unprocessed)
- Drift check passes on every account with assertions

**Rollback:** DELETE all `source_observations`, `entries`, `transactions`, `imports`, `balance_assertions` rows. System accounts and entities stay.

### SYS-0066 — `finance_v2_merchants_and_rules`

**What it does:** Seeds merchant patterns from v1's archived hardcoded patterns. Seeds the merchants registry from distinct pattern targets. Runs a one-time categorization pass over all historical entries, applying Layer 1 (merchant resolution) and Layer 2 (merchant default category).

**Verification:**
- `SELECT COUNT(*) FROM transactions WHERE merchant_id IS NULL` is small (< 10% of transactions, ideally)
- All entries have a non-uncategorized `account_id` on the expense/income side where a merchant resolved

**Rollback:** DELETE rows from `merchants`, `merchant_patterns`, `categorization_rules`, `categorization_log`. NULL-out `merchant_id` on transactions; reset expense-side entries to `uncategorized`.

### SYS-0067 — `finance_v2_api`

**What it does:** Rewrites `/opt/mythos/api/routes/finance.py` against v2 schema. Updates dashboard templates. Repoints Telegram handlers. Adds UI affordances for:
- Split transaction editing
- Save-as-template for splits
- Entity selection on entries (Personal vs. LLC — LLC option hidden until entity activated)
- Correction routing (merchant vs. category vs. entity vs. tax)
- Audit history view

**Verification:**
- Dashboard loads, displays correct balances and transaction list
- Telegram `/balance`, `/spending`, `/bills` return v2 data
- Editing a transaction in the UI creates a void-and-replace pair in the database

**Rollback:** Git revert route and handler files.

### SYS-0068 — `finance_v2_recurring`

**What it does:** Builds the recurring pattern detector as a background worker. Runs detection over all historical entries, including semi-monthly detection for payroll. Writes results to `recurring_patterns` with `status='suggested'`. Adds dashboard section for reviewing and confirming suggestions.

**Verification:**
- `SELECT COUNT(*) FROM recurring_patterns WHERE status='suggested'` returns ~25-40 patterns
- Semi-monthly payroll patterns are distinct from biweekly
- Confirmed patterns move to `status='active'` via the dashboard

**Rollback:** Stop and remove the worker service. DELETE all `recurring_patterns` rows.

### SYS-0069 — `finance_v2_forecast`

**What it does:** Builds the confidence-weighted forecaster. Updates `/forecast` Telegram command and dashboard forecast view to render projection + confidence bands.

**Verification:**
- `/forecast` returns a projection with a confidence band
- Dashboard forecast view shows shaded bounds around projected balance line

**Rollback:** Revert forecast code changes.

### SYS-0070 — `finance_v1_archive_cleanup`

**What it does:** After v2 has proven stable in production for at least 2 weeks:

1. Verify v2 is healthy (balance checks passing, no import failures in last 14 days)
2. Delete `/opt/mythos/finance/archive/v1_20260410/`
3. Update `ARCHITECTURE.md` to remove the "v1 archive exists" note
4. Git commit with a clear "v1 retired" message

**Verification:** Archive directory no longer exists. Git log shows the retirement commit.

**Rollback:** Not cleanly reversible. This is the point of no return for v1 code. By this point, v2 has been running for 2+ weeks and v1 is no longer needed.

### SYS-0071 — `finance_v2_reliability`

**What it does:**

- **PITR setup:** Configure PostgreSQL for WAL archiving to off-host encrypted storage. Enable continuous archival. Set 30-day retention.
- **pg_dump on import:** Hook into importer completion to trigger `pg_dump` of finance tables after every successful import.
- **Encrypted off-host backup:** Both WAL archives and pg_dump snapshots go off-host via gpg-encrypted transport.
- **Restore commands:** `finance-restore --dry-run`, `finance-restore --execute`, `finance-restore-pitr --target-time` (see §13.3)
- **Golden CSV fixture corpus:** Create `/opt/mythos/finance/test_fixtures/` with anonymized real CSVs covering the edge cases listed in §13.4
- **`finance-replay-test` CLI command:** Runs importer against fixtures, compares ledger checksum, fails if divergent
- **`RESTORE_PROCEDURE.md`** documentation
- **Monthly automated restore drill** via systemd timer

**Verification:**
- `finance-replay-test` succeeds
- `finance-restore --dry-run <latest>` succeeds
- `finance-restore-pitr --target-time <recent>` succeeds
- WAL archives are visible in the off-host storage location
- The systemd timer fires correctly on test

**Rollback:** Disable the timer, remove the restore scripts. Backups continue to exist.

---

## 16. Open questions for final review

I want Castor and Jeff Thinking to specifically push back on these before SQL is written:

### 16.1 Loan payment amortization storage

Current plan stores the principal/interest default split on the loan account as `metadata.default_split` (§5.3). This works but feels inelegant.

**Question:** Is there a cleaner way to represent loan amortization schedules that supports automatic split generation without requiring a full loan-management module? Is there a standard accounting pattern I'm missing?

### 16.2 Retroactive change handling for accounts without bank transaction IDs

Current plan detects retroactive changes via `bank_transaction_id` mismatch (§3.5). Accounts without stable IDs fall back to heuristic detection via the normal review queue.

**Question:** Is there a robust approach for bank-transaction-ID-less accounts beyond "flag everything ambiguous"? My worry is that credit cards which don't provide stable IDs will constantly flag things for review.

### 16.3 Opening balance data quality

Current plan derives opening balances from running balance columns where available, or requires manual input per account otherwise (§4.6). Seeding at $0 and accepting a constant offset is the fallback.

**Question:** Is statement PDF parsing worth building into SYS-0071 as an optional path for accounts without CSV running balance? Or is that scope creep?

### 16.4 Import reversal with downstream edits

Current plan (§11.3) says some imports can't be cleanly reversed if downstream transactions have been manually edited.

**Question:** What's the right UX for this? Hard block ("cannot reverse, downstream edits detected")? Soft warning with override? Partial reversal (reverse everything except the edited transactions)? This could get messy in practice.

### 16.5 Entity activation workflow

When the LLC activates, the user flips `is_active=true` on entity 2 and starts routing new transactions with `entity_id=2`. But what about existing transactions that should be retroactively attributed to the LLC?

**Question:** Does the entity attribution need a migration tool ("mark all transactions on the business AMEX since date X as LLC")? Or is this a manual per-transaction operation via the correction workflow? What's the right balance between convenience and audit trail integrity?

### 16.6 Tax treatment vocabulary

Current plan has `tax_treatment` as a free-text column on entries (§6.4). This is flexible but has no controlled vocabulary.

**Question:** Should `tax_treatment` be an enum or reference a `tax_treatments` lookup table? Enum is simpler but less extensible; lookup table adds complexity but enables per-treatment metadata (deductibility percentage, IRS form reference, etc.).

### 16.7 Recurring pattern re-detection cadence

Current plan doesn't specify how often the recurring detector re-runs (§8.6). Options: on every import, daily via systemd timer, weekly, on-demand only.

**Question:** What's the right cadence? On every import is most responsive but potentially wasteful. Weekly is efficient but misses fast-developing patterns.

### 16.8 Bi-temporal query surface

Current plan supports "ledger as of date X" queries via the reversed_by chain (§2.4), but doesn't specify how the API exposes this.

**Question:** Is there value in building a dedicated `/api/finance/as-of/<date>` endpoint for historical state queries, or is this a YAGNI feature to defer until there's a concrete use case?

### 16.9 Anything else

What's the architectural oversight I'm not seeing? What breaks in month 6 that this plan doesn't anticipate? Now that the plan is consolidated across five review rounds, what's the remaining gap?

---

## 17. Prior review attribution and deferred decisions

### 17.1 Who caught what

- **Double-entry as the right foundation:** all five reviewers confirmed
- **Sequence counter bug in original dedup:** Gemini review 1 (caught the hole)
- **Floating-point tolerance is wrong:** Gemini review 1
- **Opening balance question surfaced:** Gemini review 1
- **Materialized path naming for COA:** Gemini review 2 (Castor)
- **Clearing account pattern for transfers:** Gemini review 2 (Castor)
- **Ledger splits for tax handling:** Gemini review 2 (Castor)
- **Bi-temporal ledger (append-only facts + versioned state):** Gemini review 2 (Castor), refined by Jeff Pro review 2
- **Source observations as first-class layer:** Jeff Pro review 1 (the biggest single insight)
- **Dedup auto-skip threshold was dangerously permissive:** Jeff Pro review 1
- **Merchant resolution vs. categorization are separate concerns:** Jeff Pro review 1
- **Backup/restore gap in the original design:** Jeff Pro review 1 (named the post-wipe omission)
- **Loan payments are not pure transfers:** Jeff Pro review 1
- **Bipartite matching within dedup buckets:** Jeff Thinking review 1
- **Margin-aware confidence scoring:** Jeff Thinking review 1
- **Per-source import profiles:** Jeff Thinking review 1
- **Staged promotion for categorization learning:** Jeff Thinking review 1
- **Source running balance vs. authoritative assertion distinction:** Jeff Thinking review 1
- **Adjacency list hybrid with materialized path:** Jeff Thinking review 1 (final refinement)
- **Gap histogram + calendar anchoring for recurring detection:** Jeff Thinking review 1 (concrete algorithm)
- **Post-hoc transfer merging as enhancement:** Jeff Thinking review 1
- **Entity dimension as first-class (Personal vs. LLC):** Jeff Pro review 2 ⭐
- **Semi-monthly vs. biweekly frequency distinction:** Jeff Pro review 2 ⭐
- **PITR with WAL archiving, not just pg_dump:** Jeff Pro review 2 ⭐

### 17.2 Neo4j decision (deferred)

Finance v2 is Postgres-only. Neo4j was considered and deliberately excluded. Rationale:

1. **Nothing in finance's core workload benefits from graph traversal.** Ledger operations are relational. Dedup is multiset matching. Recurring detection is statistical. Forecasting is arithmetic. Postgres handles all of this better than Neo4j.

2. **Dual-write complexity.** Maintaining Postgres and Neo4j in sync on every merchant insert, every transaction, every rule change adds a synchronization burden with its own failure modes. The cost is real; the benefit is speculative.

3. **Cross-subsystem graph queries are speculative.** The imagined use case ("show me every transaction at every business owned by someone in Seraphe's family") is plausible but has no concrete current demand. YAGNI.

4. **Neo4j can be added later as a separate patch** using the subsystem scoping pattern documented below. A background worker mirrors finance data into the graph when and if needed.

### 17.3 Subsystem scoping pattern (reference)

Preserved here for future subsystems that may want to use Neo4j for cross-subsystem queries. If a future subsystem needs Neo4j integration, this is the pattern to follow.

**Node labeling:**
- Subsystem-native nodes get a subsystem label in addition to their specific label: `(:Finance:Merchant)`, `(:Genealogy:Person)`, `(:Integrity:File)`
- A `subsystem` property in addition to the label for generic tooling: `{subsystem: "finance"}`

**Relationship scoping:**
- Every subsystem-created relationship carries a `subsystem` property: `{subsystem: "finance", created_at: timestamp()}`
- Neo4j supports relationship property indexes, making this efficient to query

**Shared vs. owned nodes:**
- Subsystem labels go ONLY on subsystem-native nodes
- Shared ontology nodes (Person, Location, Entity) keep their global labels even when finance links to them
- Rule: subsystems own relationships they create, but shared nodes belong to whoever created them first

**Query patterns:**
```cypher
-- All finance-owned nodes
MATCH (n:Finance) RETURN n

-- All finance-owned relationships
MATCH ()-[r {subsystem: "finance"}]->() RETURN r

-- Full finance subgraph including cross-subsystem edges
MATCH (n:Finance)-[r]-(m)
WHERE "Finance" IN labels(m) OR r.subsystem = "finance"
RETURN n, r, m
```

**Schema versioning:**
- Version in properties (`schema_version: 2`), not labels
- Labels are expensive to change at scale; properties are free

### 17.4 Revision number for this plan

This is **plan v2**, generated after incorporating feedback from Jeff Pro's second review and Jeff Thinking's second review (both on the follow-up question set). Plan v1 existed briefly; this supersedes it.

---

## 18. What reviewers should focus on

I'm specifically looking for:

1. **Architectural oversights** — things that will break in month 6 that we haven't anticipated
2. **Over-engineering** — places where the design is more complex than the problem warrants
3. **Under-engineering** — places where the design is simpler than the problem warrants
4. **Open questions** — push back on §16 items or flag any I've missed
5. **Entity dimension validation** — this was added late. Is the approach sound? Any gotchas?
6. **PITR operational complexity** — is PITR setup realistic for a home server, or am I overselling the ease?
7. **Sequencing issues** — does the patch order make sense? Is there a dependency I've gotten wrong?
8. **Invariants I should be enforcing in the schema but am not** — deferred constraints, check constraints, trigger-based validations
9. **The SYS-0063 preflight patch** — is archiving v1 code (vs. deleting immediately) the right call? Any risks with keeping v1 around for two weeks after v2 ships?

Direct, opinionated critique is more valuable than validation. If parts of this are clearly right and don't need further review, ignore them. Focus on what's wrong, unclear, or risky.

This is the final planning document before schema work begins. Once this review round completes and objections are addressed, SYS-0063 gets written and the build begins.

---

*End of plan.*
