# api/routes/projection.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 456

---

### File: api/routes/projection.py

#### Purpose
This file contains the endpoint logic for generating a full-month daily financial projection, including per-account balances and mapping of income/bill events to specific accounts.

#### Architecture
The file is structured around a FastAPI router and includes several helper functions and a custom JSON encoder class:
- **Classes**: `DecimalEncoder` extends `json.JSONEncoder` to handle `Decimal` and `datetime` types.
- **Functions**: 
  - `get_db`: Establishes a connection to the PostgreSQL database.
  - `json_response`: Converts data to a JSON response using the custom `DecimalEncoder`.
  - `_get_account_balances`: Retrieves current balances for specific accounts.
  - `_get_biweekly_dates`: Calculates biweekly pay dates for a given month.
  - `get_projection`: Main endpoint function that generates the full-month projection.

#### Patterns
- **Singleton**: The database connection (`get_db`) can be considered a singleton pattern as it ensures a single connection instance.
- **Factory**: The `DecimalEncoder` class acts as a factory for JSON encoding, handling specific data types.

#### Dependencies
- **Imports**: `os`, `json`, `logging`, `datetime`, `decimal`, `calendar`, `typing`, `fastapi`, `psycopg2`, `dotenv`.
- **External Modules**: `forecast_handler` from `telegram_bot/handlers`.

#### Interfaces
- **Endpoints**: 
  - `GET /api/finance/projection`: Returns a full-month daily projection with per-account balances and income/bill events.
- **Functions**: 
  - `get_db`: Returns a database connection.
  - `json_response`: Converts data to a JSON response.
  - `_get_account_balances`: Retrieves account balances.
  - `_get_biweekly_dates`: Calculates biweekly pay dates.

#### Database
- **Tables**: `recurring_bills`, `accounts`, `recurring_income`, `transactions`, `bill_overrides`.
- **Operations**: 
  - Retrieves recurring bills and income.
  - Fetches account balances.
  - Retrieves actual transactions for the month.
  - Fetches bill overrides for the month.

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.
- **Dotenv**: Loads environment variables from `/opt/mythos/.env`.

#### Key Logic
- **Projection Calculation**:
  - Retrieves current account balances.
  - Fetches recurring bills and income.
  - Calculates biweekly pay dates.
  - Maps bills and income to specific dates.
  - Builds a day-by-day projection with running balances.
- **Handling Different Month Types**:
  - **Current Month**: Adjusts balances based on actual transactions up to today.
  - **Future Month**: Projects forward from current balances.
  - **Past Month**: Adjusts balances based on past transactions.

#### Integration Points
- **Database**: Connects to PostgreSQL to fetch account balances, recurring bills and income, actual transactions, and bill overrides.
- **Forecast Handler**: Integrates with `forecast_handler` to get current account balances.
- **FastAPI**: Integrates with FastAPI to expose the projection endpoint.

### Detailed Breakdown

#### Classes
- **DecimalEncoder**: Extends `json.JSONEncoder` to handle `Decimal` and `datetime` types.
  - **Methods**: `default` method to encode `Decimal` and `datetime` objects.

#### Functions
- **get_db**: Establishes a connection to the PostgreSQL database using environment variables.
- **json_response**: Converts data to a JSON response using the `DecimalEncoder`.
- **_get_account_balances**: Retrieves current balances for USAA and Sunmark checking accounts by calling `forecast_handler.get_current_balances`.
- **_get_biweekly_dates**: Calculates biweekly pay dates for a given month, either by projecting forward from a known date or using a fallback of the 1st and 15th.
- **get_projection**: Main endpoint function that generates the full-month projection.
  - Parses the month parameter.
  - Retrieves current account balances.
  - Fetches recurring bills and income.
  - Calculates biweekly pay dates.
  - Maps bills and income to specific dates.
  - Builds a day-by-day projection with running balances.
  - Handles different month types (current, future, past) to adjust balances accordingly.

#### Database Operations
- **Recurring Bills**: Fetches active recurring bills with expected days.
- **Accounts**: Joins with recurring bills and income to get account abbreviations.
- **Recurring Income**: Fetches active recurring income with expected days.
- **Transactions**: Retrieves actual transactions for the month.
- **Bill Overrides**: Fetches bill overrides for the specified month.

#### Configuration and Environment Variables
- **Environment Variables**: Configures the PostgreSQL database connection.
- **Dotenv**: Loads environment variables from `/opt/mythos/.env`.

#### Key Logic and Algorithms
- **Projection Calculation**:
  - Retrieves current account balances.
  - Fetches recurring bills and income.
  - Calculates biweekly pay dates.
  - Maps bills and income to specific dates.
  - Builds a day-by-day projection with running balances.
- **Handling Different Month Types**:
  - **Current Month**: Adjusts balances based on actual transactions up to today.
  - **Future Month**: Projects forward from current balances.
  - **Past Month**: Adjusts balances based on past transactions.

This file is crucial for generating financial projections and integrates with the PostgreSQL database and other components of the Mythos system.
