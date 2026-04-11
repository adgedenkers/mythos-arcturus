# api/routes/overview.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 326

---

### File: api/routes/overview.py

#### Purpose
This file contains the endpoint for the Mythos Overview dashboard, which aggregates and returns financial data such as account balances, upcoming bills, forecast alerts, monthly spending vs income, and top spending categories.

#### Architecture
- **Classes**: 
  - `DecimalEncoder`: A custom JSON encoder class that extends `json.JSONEncoder` to handle `Decimal` and `datetime` types.
- **Functions**: 
  - `get_db`: Establishes a connection to the PostgreSQL database.
  - `json_response`: Converts Python data to a JSON response using the `DecimalEncoder`.
  - `finance_overview`: The main endpoint function that fetches and processes financial data.
  - `default`: A method within `DecimalEncoder` to handle custom JSON serialization.
- **Data Flow**: 
  - The `finance_overview` function fetches data from multiple PostgreSQL tables, processes it, and returns it in a structured JSON format.

#### Patterns
- **Singleton**: The database connection is established using a singleton pattern through the `get_db` function, ensuring a single connection instance.
- **Factory**: The `DecimalEncoder` class acts as a factory for custom JSON encoding.

#### Dependencies
- **Imports**: 
  - `os`, `json`, `logging`, `datetime`, `decimal`, `calendar`, `psycopg2`, `dotenv`, `fastapi`, `fastapi.responses`.
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Endpoints**: 
  - `GET /api/finance/overview`: Returns a comprehensive overview of financial data.
- **Exposed Functions**: 
  - `get_db`: Establishes a database connection.
  - `json_response`: Converts data to a JSON response.

#### Database
- **Tables/Labels**: 
  - `accounts`: Fetches account details.
  - `recurring_bills`: Fetches recurring bills.
  - `bill_overrides`: Fetches bill overrides.
  - `transactions`: Fetches transaction details.
  - `recurring_income`: Fetches recurring income details.

#### Configuration
- **Environment Variables**: 
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT` are used to configure the database connection.
- **Dotenv File**: 
  - `/opt/mythos/.env` is loaded to access the environment variables.

#### Key Logic
- **Account Balances**: Fetches and aggregates checking, credit, and loan account balances.
- **Upcoming Bills**: Fetches bills due in the next 7 days, checks for overrides, and determines payment status.
- **Forecast Alert**: Calculates a 14-day forecast to identify potential overdraft risks.
- **Monthly Spending vs Income**: Computes spending and income for the current month.
- **Top Spending Categories**: Identifies the top spending categories for the current month.
- **Recent Large Transactions**: Fetches recent large transactions for awareness.

#### Integration Points
- **Mythos Subsystems**: 
  - Connects to the PostgreSQL database to fetch financial data.
  - Integrates with the FastAPI framework to expose the endpoint.
  - Uses `DecimalEncoder` for custom JSON serialization.

### Detailed Breakdown

#### `get_db` Function
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Logic**: Uses environment variables to configure the connection and sets the cursor factory to `RealDictCursor`.

#### `DecimalEncoder` Class
- **Purpose**: Custom JSON encoder to handle `Decimal` and `datetime` types.
- **Methods**: 
  - `default`: Handles custom serialization for `Decimal` and `datetime` types.

#### `json_response` Function
- **Purpose**: Converts Python data to a JSON response using `DecimalEncoder`.
- **Logic**: Uses `json.dumps` with `DecimalEncoder` and returns a `JSONResponse`.

#### `finance_overview` Function
- **Purpose**: Aggregates and returns financial data for the Overview dashboard.
- **Logic**: 
  - Fetches account balances, upcoming bills, forecast alerts, monthly spending vs income, and top spending categories.
  - Processes and aggregates the data into a structured format.
  - Returns the data as a JSON response using `json_response`.

### Example Data Flow
1. **Database Connection**: Establishes a connection using `get_db`.
2. **Account Balances**: Fetches and aggregates balances from the `accounts` table.
3. **Upcoming Bills**: Fetches bills from `recurring_bills` and checks for overrides in `bill_overrides`.
4. **Forecast Alert**: Calculates a 14-day forecast using transactions and recurring income.
5. **Monthly Spending vs Income**: Computes spending and income for the current month using `transactions`.
6. **Top Spending Categories**: Identifies top categories using `transactions`.
7. **Recent Large Transactions**: Fetches recent large transactions using `transactions`.
8. **Response**: Converts the aggregated data into a JSON response using `json_response`.

This file is a critical component of the Mythos system, providing a comprehensive financial overview for the dashboard.
