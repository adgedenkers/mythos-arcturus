# Finance System

> **Last Updated:** 2026-01-29
> **Status:** ✅ Operational

---

## Overview

Personal finance tracking with auto-import from bank CSVs, automatic categorization, and Telegram interface.

### Current State
- **743 transactions** (410 USAA, 333 Sunmark)
- **199 category mappings** for auto-categorization
- **2 accounts:** Sunmark Primary Checking, USAA Simple Checking

---

## Auto-Import Workflow

The patch monitor (`mythos_patch_monitor.py`) watches `~/Downloads` for bank CSVs:

```
Bank CSV lands in ~/Downloads
        │
        ▼
Patch Monitor detects file
(bk_download.csv or download.CSV)
        │
        ▼
Auto-detect bank from content
(USAA has "Original Description" column)
(Sunmark has "Account Name" header)
        │
        ▼
Run import_transactions.py
        │
        ├─► Deduplicate via hash_id
        ├─► Apply category mappings
        ├─► Insert to PostgreSQL
        │
        ▼
Archive CSV to /opt/mythos/finance/archive/imports/
```

### Supported Files

| Bank | Download Filename | Account ID |
|------|-------------------|------------|
| USAA | `bk_download.csv` | 2 |
| Sunmark | `download.CSV` | 1 |

No renaming needed - bank is auto-detected from file content.

---

## Telegram Bot Commands

| Command | Description |
|---------|-------------|
| `/balance` | Current account balances |
| `/finance` | Full summary (balances + month activity + recent transactions) |
| `/spending` | Spending by category this month |

---

## CLI Reports

```bash
cd /opt/mythos/finance
python reports.py summary      # Account overview
python reports.py monthly      # Monthly breakdown
python reports.py category     # Spending by category
python reports.py merchants    # Top merchants
python reports.py search <term> # Search transactions
python reports.py uncategorized # Find uncategorized
python reports.py recurring    # Detect recurring charges
```

---

## Manual Import

```bash
cd /opt/mythos/finance
python import_transactions.py <file.csv> --account-id <1|2> [--dry-run]
```

---

## Database Schema

### PostgreSQL Tables

**accounts**
```sql
id SERIAL PRIMARY KEY
bank_name VARCHAR(100)
account_name VARCHAR(100)
account_type VARCHAR(50)
created_at TIMESTAMP
```

**transactions**
```sql
id SERIAL PRIMARY KEY
account_id INTEGER REFERENCES accounts(id)
date DATE
description TEXT
amount DECIMAL(12,2)
category VARCHAR(100)
hash_id VARCHAR(64) UNIQUE  -- For deduplication
raw_data JSONB
created_at TIMESTAMP
```

**category_mappings**
```sql
id SERIAL PRIMARY KEY
pattern VARCHAR(255)
category VARCHAR(100)
priority INTEGER DEFAULT 0
created_at TIMESTAMP
```

**import_logs**
```sql
id SERIAL PRIMARY KEY
filename VARCHAR(255)
account_id INTEGER
records_imported INTEGER
records_skipped INTEGER
import_time TIMESTAMP
```

---

## File Structure

```
/opt/mythos/finance/
├── parsers.py              # USAA + Sunmark parsers with detect_parser()
├── import_transactions.py  # CLI import with dedup + categorization
├── reports.py              # CLI reporting tools
├── schema.sql              # Database schema
└── archive/
    └── imports/            # Processed CSVs (timestamped)
        └── errors/         # Failed imports

/opt/mythos/telegram_bot/handlers/
└── finance_handler.py      # /balance, /finance, /spending commands
```

---

## Adding Category Mappings

```sql
INSERT INTO category_mappings (pattern, category, priority)
VALUES ('AMAZON', 'Shopping', 10);
```

Higher priority = checked first. Patterns are case-insensitive substring matches against description.

---

## Planned Enhancements

- [ ] Forecasting (30/60/90 day projections)
- [ ] Recurring transaction detection
- [ ] Budget alerts per category
- [ ] Weekly spending digest via Telegram
- [ ] Receipt photo matching
- [ ] Obligation calendar integration

---

*This document details the finance system. See `docs/ARCHITECTURE.md` for system overview.*
