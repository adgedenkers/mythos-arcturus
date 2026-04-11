# docs/finance/IMPORT_SYSTEM.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 237

---

### Purpose
The `IMPORT_SYSTEM.md` file provides comprehensive documentation for the finance import system within the Mythos platform. This system handles CSV files from two banks, Sunmark Credit Union and USAA, with different parsing and cleaning logic for each.

### Architecture
The documentation outlines the structure and usage of the `importer.py` script, detailing the CSV formats for both banks, the cleaning process for transaction descriptions, balance handling, and the auto-import workflow. It also covers the database updates and troubleshooting tips.

### Patterns
The documentation does not explicitly mention any design patterns, but it implies the use of a **Factory Method** pattern for handling different bank CSV formats and a **Strategy** pattern for cleaning transaction descriptions based on the bank.

### Dependencies
The documentation does not list explicit dependencies but implies the use of:
- Python standard library for file handling and CSV parsing.
- Custom functions for cleaning descriptions and calculating balances.

### Interfaces
The `importer.py` script exposes a command-line interface for importing CSV files:
- `python /opt/mythos/finance/importer.py <bank> <file_path> --balance <balance> --verbose --dry-run`

### Database
The system updates the following database tables:
- `transactions`: Inserts new transaction records.
- `accounts`: Updates `current_balance` and `balance_updated_at` fields.

### Configuration
The script uses command-line arguments for configuration:
- `--balance`: Required for USAA to provide the current balance.
- `--verbose`: For detailed output.
- `--dry-run`: To test without importing.

### Key Logic
- **CSV Parsing**: Different parsing logic for Sunmark and USAA CSV formats.
- **Description Cleaning**: Specific rules for cleaning transaction descriptions based on the bank.
- **Balance Calculation**: Directly uses the balance column for Sunmark and calculates it for USAA.
- **Deduplication**: Uses a hash of account ID, date, amount, and original description to prevent duplicate imports.

### Integration Points
- **File Monitoring**: The system integrates with a file monitor that triggers the import process when new CSV files are detected in `~/Downloads/`.
- **Database**: The system integrates with the PostgreSQL database to insert new transactions and update account balances.
- **Archiving**: The system archives processed CSV files to `/opt/mythos/finance/archive/imports/`.

### Summary
This documentation provides a detailed guide for the finance import system, covering the handling of CSV files from two banks, the cleaning of transaction descriptions, balance calculations, and integration with the database and file monitoring system. It also includes troubleshooting tips and a list of files involved in the process.
