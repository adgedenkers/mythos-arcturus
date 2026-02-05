# Finance Import System

> **Location:** `/opt/mythos/finance/importer.py`
> **Last Updated:** 2026-02-04
> **Version:** 2.0

---

## Overview

The finance import system handles CSV exports from two banks:
- **Sunmark Credit Union** - Primary checking
- **USAA** - Secondary checking

Each bank has a different CSV format requiring separate parsing logic.

---

## Usage

```bash
# Sunmark (balance is in the CSV)
python /opt/mythos/finance/importer.py sunmark /path/to/file.CSV --verbose

# USAA (must provide current balance from website)
python /opt/mythos/finance/importer.py usaa /path/to/file.csv --balance 1243.19 --verbose

# Dry run (test without importing)
python /opt/mythos/finance/importer.py sunmark /path/to/file.CSV --dry-run --verbose
```

---

## Bank CSV Formats

### Sunmark

**File characteristics:**
- Extension: `.CSV` (uppercase)
- Encoding: UTF-8
- 3 header lines before data (Account Name, Account Number, Date Range)
- Line 4: Column headers
- Line 5+: Data rows

**Columns:**
```
Transaction Number, Date, Description, Memo, Amount Debit, Amount Credit, Balance, Check Number
```

**Key features:**
- **HAS running balance** - each row includes balance after transaction
- Separate debit/credit columns (debit is negative, credit is positive)
- Date format: `MM/DD/YYYY`
- Description contains transaction type prefix
- Memo contains merchant name and address

**Sample row:**
```csv
"873",02/02/2026,"Point Of Sale Withdrawal","WALMART.COM 800 702 SW 8TH ST BENTONVILLE ARUS",-293.13,,-321.08,
```

### USAA

**File characteristics:**
- Extension: `.csv` (lowercase)
- Encoding: UTF-8
- Standard CSV with header row
- No balance column

**Columns:**
```
Date, Description, Original Description, Category, Amount, Status
```

**Key features:**
- **NO balance column** - must calculate from known endpoint
- Single amount column (negative = debit, positive = credit)
- Date format: `YYYY-MM-DD`
- Description is already clean merchant name
- Status: Posted, Pending, Scheduled Bill Pay, etc.
- May include future-dated scheduled transactions (filtered out)

**Sample row:**
```csv
2026-02-03,"Amazon","AMAZON.COM               SEATTLE      WA",Shopping,-25.05,Posted
```

---

## Sunmark Description Cleaning

The Sunmark CSV has verbose transaction descriptions that need cleaning.

### Transaction Type Prefixes

These prefixes are stripped or abbreviated:

| Raw Prefix | Cleaned |
|------------|---------|
| `Point Of Sale Withdrawal` | *(stripped)* |
| `Point Of Sale Deposit` | *(stripped)* |
| `Point Of Sale Purchase` | *(stripped)* |
| `External Withdrawal` | `EXT:` |
| `External Deposit` | `DEP:` |
| `ATM Withdrawal` | `ATM:` |
| `Deposit Shared Branch Mobile` | `Mobile Deposit:` |
| `Overdraft Fee` | `OD Fee:` |
| `Internet Transfer to/from` | `Xfer to/from:` |

### Payment Processors

Payment processors (PayPal, Venmo, Zelle, CashApp) become the transaction type:

| Raw | Cleaned |
|-----|---------|
| `Point Of Sale Withdrawal PAYPAL`, `*DISNEY 7700...` | `Paypal: DISNEY` |
| `Overdraft Fee PAYPAL *DISNEY`, `7700...` | `OD Fee: Paypal: DISNEY` |

### Merchant Extraction Logic

1. **Strip transaction type prefix** from Description
2. **If merchant remains in Description** (e.g., `DUNKIN`, `Amazon`), use it
3. **If Description is empty after stripping**, extract merchant from Memo:
   - Remove leading asterisks (`*`)
   - Remove state+country suffix (`NYUS`, `CAUS`)
   - Remove address portion (numbers + street names)
   - Keep only merchant name

### Examples

| Description | Memo | Result |
|-------------|------|--------|
| `Point Of Sale Withdrawal` | `WALMART.COM 800 702 SW 8TH ST...` | `WALMART.COM` |
| `Point Of Sale Withdrawal DUNKIN` | `#358342 155 KINGSTON AVE...` | `DUNKIN` |
| `Point Of Sale Withdrawal PAYPAL` | `*DISNEY 7700 EASTPORT...` | `Paypal: DISNEY` |
| `External Withdrawal Blueox` | `Corporati 264...` | `EXT: Blueox` |
| `Deposit Shared Branch Mobile` | `Latham MD` | `Mobile Deposit: Latham` |
| `Point Of Sale Withdrawal Amazon` | `web serv 440 Terry Ave...` | `Amazon` |

---

## USAA Description Cleaning

USAA descriptions are already clean merchant names. Minimal processing:

| Raw | Cleaned |
|-----|---------|
| `Defense Finance and Accounting Service` | `DFAS Salary` |
| `Social Security` | `SSA` |
| `*UNSECURED FIXED RATE LOAN*` | `USAA Loan Payment` |

---

## Balance Handling

### Sunmark
- Balance column in CSV is used directly
- Most recent transaction's balance updates `accounts.current_balance`

### USAA
- No balance in CSV
- Must provide current balance via `--balance` argument
- System calculates running balance backwards:
  - Start with known current balance
  - Work through transactions in reverse chronological order
  - `balance_before = balance_after - amount`

---

## Deduplication

Transactions are deduplicated by hash:
```
hash = SHA256(account_id | date | amount | original_description)[:16]
```

If a transaction with the same hash already exists, it's skipped.

---

## Auto-Import Workflow

1. Download CSV from bank website
2. Save to `~/Downloads/` as:
   - Sunmark: `download.CSV`
   - USAA: `bk_download.csv`
3. Patch monitor detects file and triggers import
4. Transactions imported to `transactions` table
5. `accounts.current_balance` updated
6. CSV archived to `/opt/mythos/finance/archive/imports/`

---

## Database Updates

After successful import:
1. New transactions inserted to `transactions` table
2. `accounts.current_balance` set to latest balance
3. `accounts.balance_updated_at` set to NOW()

---

## Troubleshooting

### "File too short - no data rows"
Sunmark CSV needs at least 5 lines (3 headers + column header + 1 data row)

### Balance mismatch
For USAA, ensure `--balance` matches current bank website balance

### Duplicates not importing
This is expected - hash-based deduplication prevents double-imports

### Description still has junk
Check the memo extraction regex patterns in `clean_description_sunmark()`

---

## Files

| Path | Purpose |
|------|---------|
| `/opt/mythos/finance/importer.py` | Main import script |
| `/opt/mythos/finance/archive/imports/` | Archived CSVs |
| `/opt/mythos/docs/finance/IMPORT_SYSTEM.md` | This documentation |
