# api/routes/finance.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 708

---

### Documentation for `api/routes/finance.py`

#### Purpose
This file contains the FastAPI routes and logic for handling financial operations such as transactions, categories, accounts, and bills within the Mythos system. It provides endpoints for retrieving summaries, transactions, categories, accounts, and bills, as well as updating and managing these entities.

#### Architecture
The file is structured around FastAPI routes and Pydantic models. It includes:
- **Pydantic Models**: Define the structure of incoming and outgoing data for various operations.
- **FastAPI Routes**: Define the endpoints for different financial operations.
- **Database Interaction**: Uses psycopg2 to interact with PostgreSQL for retrieving and updating financial data.

#### Patterns
- **Factory Pattern**: Not explicitly used.
- **Singleton Pattern**: Not explicitly used.
- **Observer Pattern**: Not explicitly used.

#### Dependencies
- **Imports**:
  - `os`: For environment variables.
  - `json`: For JSON encoding.
  - `logging`: For logging.
  - `datetime`, `date`, `timedelta`: For date and time operations.
  - `decimal`: For handling decimal numbers.
  - `calendar`: For month-related operations.
  - `typing`: For type hints.
  - `fastapi`: For defining API routes.
  - `psycopg2`: For PostgreSQL database interactions.
  - `dotenv`: For loading environment variables from a `.env` file.

#### Interfaces
- **Exposed Routes**:
  - GET `/summary`: Retrieves financial summary.
  - GET `/transactions`: Retrieves transactions.
  - PATCH `/transactions/{txn_id}`: Updates a transaction.
  - POST `/transactions/{txn_id}/apply-category`: Applies a category to all matching transactions.
  - GET `/categories`: Retrieves categories.
  - POST `/categories/rename`: Renames a category.
  - POST `/categories/merge`: Merges categories.
  - DELETE `/categories/{name}`: Deletes a category.
  - GET `/accounts`: Retrieves accounts.
  - PATCH `/accounts/{account_id}/balance`: Updates an account balance.
  - PATCH `/bills/{bill_id}`: Updates a bill.
  - GET `/bills/test-pattern`: Tests a match pattern against recent transactions.
  - GET `/bills/tracker`: Retrieves bill tracker.
  - PATCH `/bills/{bill_id}/override`: Overrides a bill status.
  - DELETE `/bills/{bill_id}/override`: Clears a bill override.
  - GET `/forecast`: Retrieves financial forecast.
  - GET `/report`: Retrieves financial report.
  - GET `/spending`: Retrieves spending details.
  - GET `/bills`: Retrieves bills.
  - GET `/income`: Retrieves income sources.

#### Database
- **Tables/Labels**:
  - `transactions`: Stores transaction details.
  - `accounts`: Stores account details.
  - `category_mappings`: Stores category mapping rules.
  - `recurring_bills`: Stores recurring bill details.
  - `bill_overrides`: Stores manual bill overrides.
  - `forecast_handler`: Handles financial forecasts.
  - `report_generator`: Generates financial reports.
  - `recurring_income`: Stores recurring income details.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`: PostgreSQL host.
  - `POSTGRES_DB`: PostgreSQL database name.
  - `POSTGRES_USER`: PostgreSQL user.
  - `POSTGRES_PASSWORD`: PostgreSQL password.
  - `POSTGRES_PORT`: PostgreSQL port.

#### Key Logic
- **get_summary**: Retrieves financial summary including account balances, monthly spending, and income.
- **get_transactions**: Retrieves transactions based on various filters like month, category, account, and search.
- **update_transaction**: Updates a specific transaction with new details.
- **apply_category_to_all**: Applies a category to all matching transactions and updates the category mapping rule.
- **get_categories**: Retrieves a list of categories with transaction counts.
- **rename_category**: Renames a category and updates all transactions with the new category name.
- **merge_categories**: Merges categories by updating transactions.
- **delete_category**: Deletes a category and updates transactions accordingly.
- **update_account_balance**: Updates the balance of an account.
- **update_bill**: Updates a recurring bill's details.
- **test_bill_pattern**: Tests a match pattern against recent transactions.
- **get_bills_tracker**: Retrieves the bill tracker for a specific month.
- **override_bill_status**: Overrides the status of a bill for a specific month.
- **clear_bill_override**: Clears a manual override for a bill.
- **get_forecast**: Retrieves financial forecast.
- **get_report**: Retrieves financial report.
- **get_spending**: Retrieves spending details.
- **get_bills**: Retrieves a list of bills.
- **get_income_sources**: Retrieves income sources.

#### Integration Points
- **Database Integration**: Uses psycopg2 to interact with PostgreSQL for database operations.
- **Environment Configuration**: Loads environment variables using `dotenv` for database connection details.
- **FastAPI Integration**: Uses FastAPI to define and handle API routes.
- **Pydantic Models**: Uses Pydantic models to validate and structure incoming and outgoing data.
- **Logging**: Uses Python's logging module to log operations and errors.

This file is a critical component of the Mythos system, providing the backend logic for financial operations and ensuring data integrity and consistency through database interactions and validation.
