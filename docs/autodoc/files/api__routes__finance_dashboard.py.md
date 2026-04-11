# api/routes/finance_dashboard.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 349

---

### File: api/routes/finance_dashboard.py

#### Purpose
This file provides API endpoints for the finance dashboard, including views for account balances, upcoming bills, and expected income within the next 14 days. It also includes detailed bill payment history.

#### Architecture
- **Classes**: 
  - `DecimalEncoder`: A custom JSON encoder that handles `Decimal` and `datetime` types.
- **Top-level Functions**:
  - `get_db`: Establishes a connection to the PostgreSQL database.
  - `json_response`: Converts data to a JSON response using `DecimalEncoder`.
  - `get_dashboard`: Retrieves and formats data for the main dashboard view.
  - `get_bills_detail`: Retrieves and formats data for detailed bill payment history.
- **Data Flow**: 
  - The file connects to the PostgreSQL database using `get_db`.
  - Data is fetched from various tables (`accounts`, `recurring_bills`, `bill_payments`, `recurring_income`, `transactions`).
  - Data is processed and formatted into a structured JSON response.

#### Patterns
- **Singleton**: The database connection (`get_db`) can be considered a singleton pattern, as it provides a single point of access to the database.
- **Factory**: The `DecimalEncoder` class can be seen as a factory for creating JSON encoders that handle specific types.

#### Dependencies
- **Imports**: 
  - `os`, `json`, `logging`, `psycopg2`, `datetime`, `decimal`, `calendar`, `typing`, `fastapi`, `dotenv`.
- **External Modules**: 
  - `psycopg2` for database connection.
  - `fastapi` for API routing and responses.
  - `dotenv` for loading environment variables.

#### Interfaces
- **Endpoints**:
  - `/api/finance/v2/dashboard`: GET request to fetch the main dashboard view.
  - `/api/finance/v2/bills-detail`: GET request to fetch detailed bill payment history.

#### Database
- **Tables/Labels**:
  - `accounts`: Retrieves account details.
  - `recurring_bills`: Retrieves recurring bills.
  - `bill_payments`: Retrieves bill payment history.
  - `recurring_income`: Retrieves recurring income.
  - `transactions`: Retrieves transaction details.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` are loaded from `.env` file.

#### Key Logic
- **get_dashboard**:
  - Fetches active accounts, upcoming bills, and expected income within the next 14 days.
  - Filters and processes bills and income based on expected dates.
  - Calculates upcoming outflow and inflow for each account.
  - Computes totals for checking accounts and debt.
- **get_bills_detail**:
  - Fetches active bills and their payment history.
  - Matches transactions for the current month to bills.
  - Determines if bills are paid and calculates the total amount paid.

#### Integration Points
- **Mythos Subsystems**:
  - **Database**: Connects to PostgreSQL to fetch account, bill, and transaction data.
  - **FastAPI**: Uses FastAPI to define and handle API routes.
  - **Ollama**: Not directly referenced, but the system likely integrates with Ollama for AI-driven insights or predictions.
  - **Redis**: Not directly referenced, but Redis might be used for caching or session management.
  - **Neo4j**: Not directly referenced, but Neo4j might be used for graph-based financial relationships or recommendations.

### Detailed Analysis

#### `get_db` Function
- **Purpose**: Establishes a connection to the PostgreSQL database using environment variables for configuration.
- **Dependencies**: `psycopg2`, `os`.

#### `DecimalEncoder` Class
- **Purpose**: Custom JSON encoder to handle `Decimal` and `datetime` types.
- **Methods**: `default`: Handles `Decimal` and `datetime` types by converting them to float and ISO format, respectively.

#### `json_response` Function
- **Purpose**: Converts data to a JSON response using `DecimalEncoder`.
- **Dependencies**: `json`, `json_response` from `fastapi`.

#### `get_dashboard` Function
- **Purpose**: Fetches and formats data for the main dashboard view.
- **Dependencies**: `psycopg2`, `datetime`, `date`, `timedelta`.
- **Key Logic**:
  - Fetches active accounts and sorts them.
  - Fetches upcoming bills and filters based on expected dates.
  - Fetches upcoming income and filters based on expected dates.
  - Attaches upcoming events to accounts and calculates totals.

#### `get_bills_detail` Function
- **Purpose**: Fetches and formats data for detailed bill payment history.
- **Dependencies**: `psycopg2`, `datetime`, `date`, `timedelta`.
- **Key Logic**:
  - Fetches active bills and their payment history.
  - Matches transactions for the current month to bills.
  - Determines if bills are paid and calculates the total amount paid.
  - Determines due dates and overdue status.

This file is crucial for providing financial insights and managing bill payments within the Mythos system.
