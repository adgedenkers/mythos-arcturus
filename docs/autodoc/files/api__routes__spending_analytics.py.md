# api/routes/spending_analytics.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 250

---

### Purpose
The `spending_analytics.py` file provides an API endpoint to fetch aggregated spending data for the React Spending Analytics component. It supports filtering by account and returns monthly spending by category, income totals, and top merchants.

### Architecture
The file is structured around a FastAPI router and includes several utility functions and a custom JSON encoder class. The main logic is encapsulated in the `spending_analytics` function, which handles database queries and data processing.

- **Classes**: 
  - `DecimalEncoder`: Extends `json.JSONEncoder` to handle `Decimal` and `datetime` types.
  
- **Functions**:
  - `get_db`: Establishes a connection to the PostgreSQL database.
  - `json_response`: Returns a JSON response with data encoded using `DecimalEncoder`.
  - `_parse_account_filter`: Maps frontend account parameters to database account abbreviations.
  - `_acct_join_clause`: Builds a SQL JOIN clause to filter transactions by account.
  - `spending_analytics`: Main endpoint function that fetches and processes spending analytics data.

### Patterns
- **Singleton**: The database connection (`get_db`) can be considered a singleton pattern, as it returns a single connection instance.
- **Factory**: The `DecimalEncoder` class can be seen as a factory for JSON encoding, handling specific data types.

### Dependencies
- **Imports**: 
  - `os`, `json`, `logging`: Standard Python libraries.
  - `datetime`, `date`, `timedelta`: From the `datetime` module.
  - `Decimal`: From the `decimal` module.
  - `monthrange`: From the `calendar` module.
  - `APIRouter`, `Request`, `Query`, `JSONResponse`: From `fastapi`.
  - `psycopg2`, `RealDictCursor`: For PostgreSQL database operations.
  - `load_dotenv`: From `dotenv` to load environment variables.

### Interfaces
- **Endpoints**:
  - `GET /api/finance/spending/analytics`: Returns monthly spending by category, income totals, and top merchants.

### Database
- **Tables/Labels**:
  - `transactions`: Stores transaction data.
  - `accounts`: Stores account information.
  - `datetime`, `decimal`, `calendar`, `fastapi`, `psycopg2`, `dotenv`, `clause`, `average`: These are not actual tables but rather modules or types used in the code.

### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Used to configure the PostgreSQL database connection.

### Key Logic
1. **Account Filtering**:
   - `_parse_account_filter` maps the `account` query parameter to a list of account abbreviations.
   - `_acct_join_clause` generates a SQL JOIN clause to filter transactions by account.

2. **Monthly Spending by Category**:
   - Fetches monthly spending by category for the specified months.
   - Aggregates and pivots data to format it as `{month: {category: amount}}`.

3. **Monthly Income**:
   - Fetches monthly income totals for the specified months.
   - Adds income and net spending to the monthly data.

4. **Top Merchants**:
   - Fetches top merchants based on transaction count and total spending.
   - Calculates a trend for each merchant based on recent spending patterns.

5. **Current Month Burn Rate**:
   - Calculates the daily burn rate and projects spending for the current month.
   - Computes the runway based on current income and projected spending.

### Integration Points
- **Mythos Subsystems**:
  - **Database**: Connects to PostgreSQL to fetch transaction and account data.
  - **FastAPI**: Uses FastAPI to define and handle the `/analytics` endpoint.
  - **React Frontend**: Provides data to the React Spending Analytics component.

This file serves as a critical integration point between the backend database and the frontend analytics component, ensuring that the data is correctly aggregated and formatted for display.
