# core/action_executor.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 449

---

### File: core/action_executor.py

#### Purpose
This file contains functions to execute various actions extracted from messages and commit them to the PostgreSQL database. It handles actions such as marking bills as paid, creating/updating/deleting calendar events, marking tasks as completed, adding new tasks, logging life events, and updating account balances.

#### Architecture
The file consists of several top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute_actions`: The main function that processes the extracted actions and delegates them to specific execution functions.
- `_execute_bill_paid`, `_execute_calendar_create`, `_execute_calendar_update`, `_execute_calendar_delete`, `_execute_task_completed`, `_execute_task_added`, `_execute_routine_done`, `_execute_life_event`, `_execute_balance_update`: Functions that handle specific actions by interacting with the database.

#### Patterns
- **Single Responsibility Principle**: Each function is responsible for a specific action, ensuring that the code is modular and maintainable.
- **Database Connection Management**: The `_get_conn` function manages database connections, ensuring that connections are properly closed after use.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging messages.
- `psycopg2`: For PostgreSQL database operations.
- `datetime`: For date and time manipulation.
- `typing`: For type hints.
- `dotenv`: For loading environment variables from a `.env` file.

#### Interfaces
- `execute_actions(extraction: Dict[str, Any]) -> List[str]`: The main function that takes a dictionary of extracted actions and returns a list of action summaries for logging.
- `_get_conn()`: Returns a PostgreSQL database connection.
- `_execute_bill_paid(conn, data: Dict) -> str`: Marks a bill as paid.
- `_execute_calendar_create(conn, data: Dict) -> str`: Creates a new calendar event.
- `_execute_calendar_update(conn, data: Dict) -> str`: Updates an existing calendar event.
- `_execute_calendar_delete(conn, data: Dict) -> str`: Deletes (deactivates) a calendar event.
- `_execute_task_completed(conn, data: Dict) -> str`: Marks a task as completed.
- `_execute_task_added(conn, data: Dict) -> str`: Adds a new task.
- `_execute_routine_done(conn, data: Dict) -> str`: Marks a routine as complete for today.
- `_execute_life_event(conn, data: Dict) -> str`: Logs a life event.
- `_execute_balance_update(conn, data: Dict) -> str`: Updates an account balance.

#### Database
The file interacts with the following PostgreSQL tables:
- `recurring_bills`
- `bill_overrides`
- `calendar_events`
- `idea_backlog`
- `routine_completions`
- `life_events`
- `accounts`

#### Configuration
The file uses environment variables loaded from a `.env` file located at `/opt/mythos/.env`. The following environment variables are used:
- `POSTGRES_HOST`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_PORT`

#### Key Logic
- **Action Execution**: The `execute_actions` function processes each action in the `extraction` dictionary and delegates to the appropriate `_execute_` function.
- **Database Operations**: Each `_execute_` function performs specific database operations such as inserting, updating, or deleting records.
- **Error Handling**: The `execute_actions` function handles exceptions and ensures that the database connection is properly closed and rolled back in case of errors.

#### Integration Points
- **Message Extraction**: The `execute_actions` function takes the output from the message extraction process, which is a dictionary of actions.
- **Logging**: The file logs actions and errors using the `logging` module.
- **Database**: The file interacts with the PostgreSQL database to commit actions and retrieve necessary data.

### Example Usage
```python
extraction = {
    'bill_paid': {'bill_name': 'Electricity', 'amount': 100},
    'calendar_event': {'title': 'Meeting', 'date': '2023-10-15', 'time': '14:00', 'person': 'adge'},
    'task_completed': {'task_name': 'Write report'},
    'life_event': {'description': 'Visited the doctor', 'domain': 'health', 'person': 'adge'}
}

action_summaries = execute_actions(extraction)
print(action_summaries)
```

This example demonstrates how the `execute_actions` function processes a dictionary of extracted actions and returns a list of action summaries for logging.
