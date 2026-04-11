# api/routes/smart_overview.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 244

---

### File: api/routes/smart_overview.py

#### Purpose
This file contains the implementation of the `/smart-overview` endpoint for the Mythos system, which provides a comprehensive financial overview including safe to spend amounts, paycheck countdown, spending velocity, afford windows, and bill triage.

#### Architecture
The file consists of several functions and a class:
- **Classes**: `DecimalEncoder` (inherits from `json.JSONEncoder`) for custom JSON encoding.
- **Functions**:
  - `get_db`: Establishes a database connection.
  - `json_response`: Serializes data to a JSON response.
  - `_parse_account_filter`: Parses account parameters to filter database queries.
  - `_load_forecast`: Loads financial forecasts based on account parameters.
  - `smart_overview`: The main endpoint handler for `/smart-overview`.

#### Patterns
- **Factory Method**: `get_db` can be seen as a factory method for creating database connections.
- **Singleton**: The database connection is managed as a singleton pattern within the function scope.

#### Dependencies
- **Imports**: `os`, `json`, `logging`, `sys`, `datetime`, `decimal`, `calendar`, `fastapi`, `psycopg2`, `dotenv`.
- **External Modules**: `forecast_handler` from `telegram_bot/handlers`.

#### Interfaces
- **Endpoints**: 
  - `GET /smart-overview`: Returns a comprehensive financial overview.
- **Functions**:
  - `get_db`: Returns a database connection.
  - `json_response`: Converts data to a JSON response.
  - `_parse_account_filter`: Parses account parameters.
  - `_load_forecast`: Loads financial forecasts.

#### Database
- **Tables**: 
  - `accounts`: Stores account information.
  - `transactions`: Stores transaction records.
  - `recurring_bills`: Stores recurring bill information.
- **Neo4j Labels**: None.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.
- **Config Files**: `.env` file loaded using `dotenv`.

#### Key Logic
1. **Safe to Spend Calculation**:
   - Calculates the lowest balance over the next 14 days and applies a safety buffer.
2. **Paycheck Countdown**:
   - Identifies the next paycheck date and calculates the balance before the paycheck.
3. **Spending Velocity**:
   - Computes the current and historical daily spending rates and projects the monthly spending.
4. **Afford Windows**:
   - Determines the maximum spendable amount for each of the next 30 days.
5. **Bill Triage**:
   - Classifies upcoming bills as fixed or flexible based on categories and keywords.

#### Integration Points
- **Forecast Handler**: Integrates with `forecast_handler` to load financial forecasts.
- **Database**: Connects to PostgreSQL to fetch account, transaction, and recurring bill data.
- **FastAPI**: Uses FastAPI to define and handle the `/smart-overview` endpoint.

### Detailed Breakdown

#### `DecimalEncoder` Class
- **Purpose**: Custom JSON encoder to handle `Decimal` and `datetime` types.
- **Methods**: `default` method to serialize `Decimal` and `datetime` objects.

#### `get_db` Function
- **Purpose**: Establishes a database connection using environment variables.
- **Dependencies**: `psycopg2`, `os`.

#### `json_response` Function
- **Purpose**: Converts data to a JSON response using `DecimalEncoder`.
- **Dependencies**: `json`, `fastapi.responses.JSONResponse`.

#### `_parse_account_filter` Function
- **Purpose**: Maps account parameters to database account abbreviations.
- **Dependencies**: `psycopg2`.

#### `_load_forecast` Function
- **Purpose**: Loads financial forecasts based on account parameters.
- **Dependencies**: `forecast_handler`, `psycopg2`.

#### `smart_overview` Endpoint
- **Purpose**: Handles the `/smart-overview` endpoint, providing a comprehensive financial overview.
- **Logic**:
  - Parses account parameters.
  - Loads financial forecasts.
  - Calculates safe to spend, paycheck countdown, spending velocity, afford windows, and bill triage.
- **Dependencies**: `psycopg2`, `forecast_handler`, `json_response`.

### Conclusion
The `smart_overview.py` file is a critical component of the Mythos system, providing a detailed financial overview through the `/smart-overview` endpoint. It integrates with PostgreSQL to fetch financial data and uses custom logic to compute various financial metrics.
