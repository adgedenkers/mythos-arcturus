# docs/finance/FINANCE_SYSTEM.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 190

---

### Purpose
This markdown file (`FINANCE_SYSTEM.md`) serves as a comprehensive documentation for the Personal Finance Tracking System within the Mythos platform. It outlines the system's current state, workflow, commands, reports, database schema, file structure, and planned enhancements.

### Architecture
The file is structured into several sections, each detailing different aspects of the finance system:
1. **Overview**: Provides a high-level description and current state.
2. **Auto-Import Workflow**: Describes the process of automatically importing bank transactions.
3. **Telegram Bot Commands**: Lists commands available via the Telegram bot.
4. **CLI Reports**: Details command-line tools for generating various reports.
5. **Manual Import**: Instructions for manually importing transactions.
6. **Database Schema**: Describes the PostgreSQL tables used.
7. **File Structure**: Outlines the directory structure and key files.
8. **Adding Category Mappings**: Instructions for adding new category mappings.
9. **Planned Enhancements**: Lists future improvements.

### Patterns
- **Observer Pattern**: The `mythos_patch_monitor.py` watches for changes in the `~/Downloads` directory.
- **Factory Pattern**: The `detect_parser()` function in `parsers.py` selects the appropriate parser based on the file content.

### Dependencies
- **Python Modules**: `mythos_patch_monitor.py`, `import_transactions.py`, `reports.py`, `finance_handler.py`.
- **Database**: PostgreSQL.
- **External Tools**: Telegram bot for command handling.

### Interfaces
- **Telegram Bot**: Exposes commands like `/balance`, `/finance`, `/spending`.
- **CLI Tools**: Provides commands for generating reports and importing transactions.
- **Database**: Exposes tables for transactions, accounts, category mappings, and import logs.

### Database
- **PostgreSQL Tables**:
  - `accounts`: Stores account details.
  - `transactions`: Stores transaction details with deduplication via `hash_id`.
  - `category_mappings`: Stores patterns for auto-categorization.
  - `import_logs`: Logs import operations.

### Configuration
- **Environment Variables**: No specific environment variables mentioned, but the system relies on the `~/Downloads` directory for CSV imports.
- **Configuration Files**: No explicit configuration files mentioned, but the system relies on the file structure and database schema defined in `schema.sql`.

### Key Logic
- **Auto-Import Workflow**: The system watches for new CSV files, detects the bank, and imports transactions into PostgreSQL.
- **Category Mappings**: Transactions are auto-categorized based on predefined patterns.
- **Deduplication**: Transactions are deduplicated using a `hash_id` to ensure uniqueness.

### Integration Points
- **Telegram Bot**: Integrates with the Telegram bot via `finance_handler.py` to provide financial summaries and commands.
- **CLI Tools**: Integrates with the command-line interface for manual operations and reporting.
- **Database**: Integrates with PostgreSQL for storing and retrieving financial data.

### Summary
This markdown file provides a detailed overview of the Personal Finance Tracking System within the Mythos platform, covering its workflow, commands, reports, database schema, file structure, and planned enhancements. It serves as a comprehensive guide for understanding and interacting with the finance subsystem.
