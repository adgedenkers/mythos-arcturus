# Finance System

**Stream:** SYS
**Files:** 23

## Files in this Module

- `finance/README.md` (67L)
- `finance/bill_matcher.py` (333L)
- `finance/categorizer.py` (273L)
- `finance/importer.py` (868L)
- `finance/migration_0051_credit_cards.sql` (51L)
- `finance/migration_add_csv_columns.sql` (134L)
- `finance/parsers.py` (436L)
- `finance/post_import_analyzer.py` (340L)
- `finance/report_generator.py` (300L)
- `finance/report_template.html` (628L)
- `finance/reports.py` (416L)
- `finance/schema.sql` (377L)
- `finance/schema_report.md` (705L)
- `finance/schema_validator.py` (381L)
- `finance/update_sunmark_descriptions.py` (131L)
- `finance/weekly_review.py` (563L)
- `finance/scripts/backfill_balances.py` (173L)
- `finance/scripts/manual_transaction_import.py` (82L)
- `finance/scripts/rehash_transactions.py` (190L)
- `finance/scripts/reimport_account.py` (472L)
- `finance/reports/2026-01-30_financial_status.md` (186L)
- `finance/reports/TEMPLATE.md` (169L)
- `finance/reports/report_20260206.html` (628L)

---

# Mythos Finance System Module Documentation

---

## **1. Module Purpose**
The **Finance System** in Mythos is a comprehensive financial management module designed to handle personal and household finance tracking. It supports transaction importation, categorization, recurring bill matching, balance tracking, and report generation. Key capabilities include:
- **CSV Import**: Parse and normalize transactions from banks (e.g., Sunmark, USAA).
- **Categorization**: Assign transaction categories using rule-based mappings.
- **Bill Matching**: Identify and track payments against recurring bills.
- **Reporting**: Generate structured financial reports (HTML) and send notifications via Telegram.
- **Database Migrations**: Maintain schema evolution for credit card tracking and CSV import support.

---

## **2. Architecture Overview**
The Finance System follows a layered architecture with clear separation of concerns:
1. **Data Ingestion**:
   - **Parsers** (`parsers.py`): Parse bank-specific CSV formats into normalized `Transaction` objects.
   - **Importer** (`importer.py`): Deduplicates transactions, imports them into PostgreSQL, and updates account balances.
2. **Core Logic**:
   - **Categorizer** (`categorizer.py`): Applies category rules to transactions using `category_mappings`.
   - **BillMatcher** (`bill_matcher.py`): Matches transactions to recurring bills and records payments.
3. **Reporting**:
   - **PostImportAnalyzer** (`post_import_analyzer.py`): Analyzes new transactions and sends Telegram reports.
   - **ReportGenerator** (`report_generator.py`): Generates monthly HTML reports with spending breakdowns and bill tracking.
4. **Database**:
   - **PostgreSQL**: Central database for storing transactions, accounts, bills, and mappings.
   - **Migrations** (`migration_*.sql`): Schema updates for credit card tracking and CSV import compatibility.

**Data Flow**:
```
CSV File → Parser → Importer → Database
                                  ↘
                                   Categorizer → Category Mappings
                                   BillMatcher → Recurring Bills
                                   ReportGenerator → HTML Report
                                   PostImportAnalyzer → Telegram Notification
```

---

## **3. Key Components**
### **Core Classes**
| Class/Function | Role |
|----------------|------|
| `BillMatcher` | Matches transactions to recurring bills and records payments. |
| `Categorizer` | Applies category rules to transactions using `category_mappings`. |
| `Importer` | Imports and deduplicates transactions from CSV files. |
| `USAAParser/SunmarkParser` | Parses bank-specific CSV formats into normalized transactions. |
| `PostImportAnalyzer` | Analyzes new transactions and sends Telegram reports. |
| `ReportGenerator` | Generates HTML reports with spending breakdowns and bill tracking. |

### **Key Functions**
- `detect_parser(file_path)`: Auto-detects the correct bank parser.
- `match_transactions(transaction_ids)`: Matches transactions to recurring bills.
- `recategorize_db()`: Re-categorizes all transactions in the database.
- `generate_report(months=1)`: Generates an HTML report for the specified number of months.

---

## **4. Design Patterns**
| Pattern | Usage |
|---------|-------|
| **Singleton** | `get_db_connection()` ensures a single PostgreSQL connection is reused. |
| **Factory Method** | `detect_parser()` creates the appropriate parser for a CSV file. |
| **Abstract Factory** | `BaseParser` defines an interface for bank-specific parsers. |
| **Database Migration** | SQL scripts (`migration_*.sql`) evolve the schema for new features. |

---

## **5. Data Model**
### **Database Tables**
| Table | Description |
|-------|-------------|
| `accounts` | Stores account details (e.g., balances, credit limits). |
| `transactions` | Stores parsed transaction data (e.g., description, amount, category). |
| `recurring_bills` | Tracks recurring bills (e.g., merchant, amount, due date). |
| `category_mappings` | Defines rules for transaction categorization. |
| `bill_payments` | Records matched transactions and their associated bills. |

### **Key Columns Added by Migrations**
- `accounts`: `current_balance`, `credit_limit`, `min_payment`, `payment_due_day`.
- `transactions`: `hash_id` (unique transaction identifier), `source_file`.

---

## **6. API Surface**
### **Public Methods**
| Component | Method | Description |
|----------|--------|-------------|
| `BillMatcher` | `match_transactions(transaction_ids)` | Matches transactions to recurring bills. |
| `Categorizer` | `categorize(description)` | Assigns a category to a transaction description. |
| `Importer` | `import_transactions(file_path)` | Imports and deduplicates a CSV file. |
| `ReportGenerator` | `generate_report(months=1)` | Generates an HTML report for the specified number of months. |

### **CLI Commands**
- `python categorizer.py --recategorize`: Re-categorizes all transactions.
- `python report_generator.py --months 3`: Generates a 3-month report.
- `python post_import_analyzer.py`: Sends a Telegram report after import.

### **Telegram Integration**
- Sends structured HTML reports to users via a Telegram bot (configurable via `TELEGRAM_ID_*`).

---

## **7. Dependencies**
### **External**
- **PostgreSQL**: Central database for transaction and account data.
- **Python Libraries**: `psycopg2`, `dotenv`, `argparse`, `datetime`, `decimal`.

### **Internal**
- **Modules**:
  - `bill_matcher` (for bill tracking).
  - `categorizer` (for transaction categorization).
  - `parsers` (for CSV parsing).
- **Tables**:
  - `recurring_bills`, `transactions`, `category_mappings`.

---

## **8. Configuration**
### **Environment Variables**
| Variable | Description |
|----------|-------------|
| `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` | PostgreSQL connection details. |
| `TELEGRAM_ID_KA`, `TELEGRAM_ID_SERAPHE` | Telegram user IDs for notifications. |

### **Configuration Files**
- `.env`: Loads environment variables using `dotenv`.
- `finance/README.md`: Documents directory structure and future enhancements.

### **Code Constants**
- `ACCOUNT_IDS`: Hardcoded account identifiers in `importer.py`.
- `ARCHIVE_DIR`: Directory for archiving processed CSV files.

---

## **Integration Points**
- **Telegram Bot**: Sends post-import analysis reports.
- **Plaid Schema Compatibility**: Maintains backward compatibility with existing Plaid integrations.
- **Mythos Witness Log**: Future integration for tracking financial milestones.

---

## **Next Steps**
1. Implement `budget/cashflow.csv` for historical cashflow tracking.
2. Link with the Mythos witness log for financial milestone events.
3. Expand parser support for additional banks (e.g., Chase, Bank of America).
