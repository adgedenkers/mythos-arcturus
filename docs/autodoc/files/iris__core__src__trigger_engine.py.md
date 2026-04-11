# iris/core/src/trigger_engine.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 777

---

### Documentation for `trigger_engine.py`

#### 1. Purpose
The `trigger_engine.py` file implements the core logic for scheduling and executing triggers based on cron expressions and other conditions. It loads triggers from a PostgreSQL database, computes their next fire times, and executes the associated actions. It also handles logging and state management.

#### 2. Architecture
The file is organized into three main classes:
- **CronParser**: A minimal cron expression parser that supports basic cron syntax.
- **ActionHandlers**: A registry of action handlers that execute specific actions based on trigger payloads.
- **TriggerEngine**: The main trigger scheduler that loads triggers, computes fire times, and executes them.

#### 3. Patterns
- **Registry Pattern**: `ActionHandlers` acts as a registry for different action handlers.
- **Singleton Pattern**: The `TriggerEngine` class can be instantiated once and manages its state internally.

#### 4. Dependencies
- **Standard Libraries**: `asyncio`, `json`, `logging`, `os`, `subprocess`, `time`, `datetime`, `typing`
- **External Libraries**: `psycopg2`, `redis`
- **Internal Modules**: `context_engine`, `decision_gate`, `task_registry`

#### 5. Interfaces
- **CronParser**:
  - `parse_field(field: str, min_val: int, max_val: int) -> set`: Parses a single cron field.
  - `next_fire(cron_expr: str, after: Optional[datetime] = None) -> datetime`: Computes the next fire time for a cron expression.
- **ActionHandlers**:
  - `__init__(self, db_config: dict, task_registry=None)`: Initializes the action handlers with database configuration and task registry.
  - `can_handle(self, action_type: str) -> bool`: Checks if an action type is supported.
  - `execute(self, action_type: str, trigger: dict, payload: dict) -> dict`: Executes the specified action and returns the result.
- **TriggerEngine**:
  - `__init__(self, db_config: dict, task_registry=None)`: Initializes the trigger engine with database configuration and task registry.
  - `load_triggers(self)`: Loads triggers from the PostgreSQL database.
  - `get_due_triggers(self)`: Returns triggers that are due to fire.
  - `fire_trigger(self, trigger)`: Fires a single trigger and logs the result.
  - `run(self, shutdown_event)`: Main loop that runs the trigger engine as a standalone service.
  - `poll_and_fire(self)`: Non-blocking method to fire due triggers and return results.
  - `get_state(self)`: Returns the current state for health checks.

#### 6. Database
- **PostgreSQL Tables**:
  - `scheduled_triggers`: Stores trigger definitions.
  - `trigger_log`: Logs trigger firing events.
  - `state`: Stores the state of triggers.

#### 7. Configuration
- **Environment Variables**:
  - `REDIS_HOST`: Host for Redis.
  - `REDIS_PORT`: Port for Redis.

#### 8. Key Logic
- **CronParser**:
  - Parses cron expressions to determine the next fire time.
- **ActionHandlers**:
  - Executes different types of actions based on the trigger payload.
  - Supports actions like `reflex`, `run_task`, `telegram_notify`, `run_command`, and `redis_push`.
- **TriggerEngine**:
  - Loads triggers from the database and computes their next fire times.
  - Runs a loop to fire triggers on schedule and logs the results.
  - Supports both standalone operation and integration with the consciousness loop.

#### 9. Integration Points
- **Redis**:
  - Publishes events for services that are down.
  - Pushes messages to Redis streams or channels for notifications.
- **Task Registry**:
  - Retrieves and executes tasks from the task registry.
- **PostgreSQL**:
  - Loads triggers from the `scheduled_triggers` table.
  - Logs trigger firing events in the `trigger_log` table.
  - Updates the state of triggers in the `state` table.

### Summary
The `trigger_engine.py` file is a critical component of the Mythos system, responsible for scheduling and executing triggers based on cron expressions and other conditions. It integrates with PostgreSQL for data storage and Redis for event publishing, and supports various action types through a registry of action handlers.
