# core/life_context.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 241

---

### File: core/life_context.py

#### Purpose
This file is responsible for building a compact life-state context block for Iris, which includes information about routines, tasks, financial status, and other relevant details. This context block is appended to Iris's system prompt to provide a comprehensive overview of the current life state.

#### Architecture
The file contains three main functions:
1. `_get_conn`: Establishes a connection to the PostgreSQL database.
2. `build_life_context`: Constructs the life-state context block by querying various PostgreSQL tables and assembling the information into a concise string.
3. `get_system_health_context`: Retrieves system health information for Iris and formats it for prompt injection.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function can be considered a singleton pattern as it provides a single point of connection to the database.
- **Factory Method Pattern**: The `build_life_context` function acts as a factory method, assembling different parts of the context block based on the current state and database queries.

#### Dependencies
- **Standard Libraries**: `os`, `logging`, `datetime`, `decimal`
- **External Libraries**: `psycopg2`, `dotenv`

#### Interfaces
- `build_life_context`: Exposes a function that returns a string containing the life-state context block.
- `get_system_health_context`: Exposes a function that returns a string containing system health information.

#### Database
- **Tables**: The file interacts with multiple PostgreSQL tables, including `routines`, `routine_completions`, `idea_backlog`, `calendar_events`, `accounts`, `recurring_bills`, `bill_overrides`, `checkin_log`, and `iris_integrity`.

#### Configuration
- **Environment Variables**: The file uses environment variables to configure the PostgreSQL connection, loaded from a `.env` file using `dotenv`.

#### Key Logic
1. **Date/Time Context**: Constructs a string indicating the current date and time.
2. **Routine Context**: Queries the `routines` and `routine_completions` tables to determine which routines are due and which have been completed.
3. **Overdue Routines**: Queries overdue routines from the `routine_completions` table.
4. **Open Tasks**: Queries open tasks from the `idea_backlog` table.
5. **Calendar Events**: Queries today's calendar events from the `calendar_events` table.
6. **Financial Pulse**: Queries account balances from the `accounts` table and upcoming bills from the `recurring_bills` and `bill_overrides` tables.
7. **Last Checkin**: Queries the last checkin from the `checkin_log` table.
8. **System Health**: Retrieves system health information from the `iris_integrity` module.

#### Integration Points
- **Database Integration**: The file integrates with the PostgreSQL database to fetch various pieces of information.
- **System Integrity**: The `get_system_health_context` function integrates with the `iris_integrity` module to fetch system health information.
- **Prompt Injection**: The assembled context block is intended to be injected into Iris's system prompt to provide context-aware responses.

### Detailed Breakdown

#### `_get_conn`
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Logic**: Uses environment variables to configure the connection parameters and returns a connection object with a `RealDictCursor`.

#### `build_life_context`
- **Purpose**: Constructs a life-state context block by querying various PostgreSQL tables and assembling the information into a concise string.
- **Logic**:
  - Queries the current date and time.
  - Queries routines due today and their completion status.
  - Queries overdue routines.
  - Queries open tasks.
  - Queries today's calendar events.
  - Queries account balances and upcoming bills.
  - Queries the last checkin.
  - Assembles all the queried information into a concise string.

#### `get_system_health_context`
- **Purpose**: Retrieves system health information for Iris and formats it for prompt injection.
- **Logic**:
  - Imports and uses the `iris_integrity` module to build a health summary.
  - Formats the health summary for prompt injection if a scan has been run.

### Example Usage
```python
context = build_life_context()
print(context)
```
This would print the assembled life-state context block, which can be appended to Iris's system prompt.
