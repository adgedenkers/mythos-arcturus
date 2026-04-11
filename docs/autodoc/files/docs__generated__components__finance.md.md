# docs/generated/components/finance.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 103

---

### Purpose
The `finance.md` file serves as a comprehensive reference for the finance component of the Mythos system. It details the roles of key files, data stores, integration points, configuration, and design patterns used within the finance component.

### Architecture
The finance component is structured around several key files, each responsible for specific tasks such as bank account linking, transaction importing, categorization, and report generation. The component leverages PostgreSQL for data storage and SQLAlchemy for ORM operations. The core transaction import pipeline involves parsing raw data, importing it, categorizing transactions, matching bills, and storing the data.

### Patterns
1. **Transaction Import Pipeline**: A sequential process from raw data parsing to storage.
2. **Report Generation**: Templates are used for dynamic report generation.
3. **Schema-Driven Development**: Data validation against a defined schema.
4. **Idempotent Imports**: Ensures no duplicate transactions.
5. **Plaid Workflow**: Handles OAuth token exchange and bank account setup.
6. **Category Management**: Uses regex rules and user-defined categories.

### Dependencies
- **Plaid API**: For bank account linking and transaction fetching.
- **Telegram Bot**: For sending weekly financial reports.
- **FastAPI**: For exposing endpoints.
- **PostgreSQL**: For storing financial data.
- **SQLAlchemy**: For ORM operations.
- **Alembic**: For database migrations.

### Interfaces
- **Endpoints**: Exposed via FastAPI for transaction imports and report generation.
- **CLI Tools**: `manual_transaction_import.py` for ad-hoc CSV imports.
- **Telegram Bot**: For sending weekly reports.

### Database
- **PostgreSQL Tables**:
  - `transactions`: Core transaction data.
  - `bank_accounts`: Linked bank accounts.
  - `categories`: User-defined transaction categories.
  - `bills`: Recurring bills.
  - `reports`: Generated report metadata.

- **Neo4j**: No direct usage in the finance component.
- **Redis**: No direct usage in the finance component.

### Configuration
- **Environment Variables**:
  - `PLAID_CLIENT_ID`: Plaid API client ID.
  - `PLAID_SECRET`: Plaid API secret.
  - `PLAID_ENV`: Plaid environment (`sandbox`, `development`, `production`).
  - `TELEGRAM_BOT_TOKEN`: Telegram bot token for report delivery.
  - `DB_URL`: PostgreSQL connection string.

### Key Logic
- **Transaction Import Pipeline**: Sequential processing from raw data to storage.
- **Report Generation**: Dynamic data injection into templates.
- **Schema Validation**: Ensuring data integrity against the defined schema.
- **Idempotent Imports**: Avoiding duplicate transactions.
- **Plaid Workflow**: OAuth token exchange and bank account setup.
- **Category Management**: Using regex rules and user-defined categories.

### Integration Points
- **Plaid API**: For bank account linking and transaction fetching.
- **Telegram Bot**: For sending weekly financial reports.
- **FastAPI**: For exposing endpoints for transaction imports and report generation.
- **PostgreSQL**: For storing financial data.
- **Neo4j**: Indirectly via `categorizer.py` for category rules.
- **Redis**: Indirectly for caching elsewhere in the system.

### Detailed Breakdown of Key Files
- **`plaid/link_bank.py`**: Handles initial bank account linking with Plaid.
- **`plaid/link_bank2.py`**: Manages bank account updates/relinking (potentially redundant).
- **`plaid/setup_bank.py`**: Configures new bank accounts in the system.
- **`importer.py`**: Core transaction importer.
- **`parsers.py`**: Converts raw transaction data from various formats.
- **`categorizer.py`**: Assigns categories to transactions using rule-based matching.
- **`bill_matcher.py`**: Matches transactions to recurring bills.
- **`post_import_analyzer.py`**: Detects anomalies and patterns after transaction import.
- **`reports.py` & `report_generator.py`**: Generates financial reports.
- **`weekly_review.py`**: Produces weekly financial summary reports.
- **`schema.sql`**: Defines PostgreSQL schema for finance data.
- **`schema_validator.py`**: Validates data integrity against the schema.
- **`manual_transaction_import.py`**: CLI tool for ad-hoc CSV transaction imports.
- **`rehash_transactions.py`**: Recalculates transaction hashes for deduplication.

This documentation provides a detailed overview of the finance component's architecture, dependencies, interfaces, and key logic, ensuring a comprehensive understanding of its role within the Mythos system.
