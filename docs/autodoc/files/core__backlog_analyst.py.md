# core/backlog_analyst.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 428

---

### File: core/backlog_analyst.py

#### Purpose
The `BacklogAnalyst` class is responsible for gathering and analyzing the current state of various life and work aspects (backlog, routines, calendar, bills, finances, recent events) to produce a daily intelligence briefing. It also handles the interaction with an AI model to generate the analysis and stores the results in the database.

#### Architecture
- **Class**: `BacklogAnalyst`
  - **Methods**:
    - `__init__`: Initializes the class.
    - `_get_conn`: Establishes a database connection.
    - `_gather_state`: Collects the current state from various PostgreSQL tables.
    - `_build_prompt`: Constructs a prompt for the AI model based on the gathered state.
    - `_call_model`: Sends the prompt to the AI model and receives the analysis.
    - `_save_analysis`: Saves the analysis results to the database.
    - `_apply_reorders`: Applies any reordering of items based on the analysis.
    - `run_analysis`: Orchestrates the analysis process.
    - `get_latest_briefing`: Retrieves the latest briefing.
    - `get_transfer_recommendations`: Retrieves transfer recommendations.
    - `close`: Closes the database connection.
  - **Top-level functions**:
    - `_db_connect`: Establishes a database connection.

#### Patterns
- **Singleton**: The `_get_conn` method ensures a single database connection is reused.
- **Factory**: The `_build_prompt` method constructs a prompt based on the gathered state.

#### Dependencies
- **Imports**: `json`, `os`, `logging`, `asyncio`, `datetime`, `typing`, `psycopg2`, `psycopg2.extras`, `httpx`, `sys`, `re`, `dotenv`
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `OLLAMA_MODEL`

#### Interfaces
- **Public Methods**:
  - `run_analysis(trigger_type: str)`: Initiates the analysis process.
  - `get_latest_briefing()`: Retrieves the latest briefing.
  - `get_transfer_recommendations()`: Retrieves transfer recommendations.
  - `close()`: Closes the database connection.

#### Database
- **Tables**:
  - `idea_backlog`
  - `routine_completions`
  - `routines`
  - `calendar_events`
  - `recurring_bills`
  - `bill_overrides`
  - `accounts`
  - `checkin_log`
  - `life_events`
  - `backlog_analysis`

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: Database connection details.
  - `OLLAMA_MODEL`: AI model to use for analysis.

#### Key Logic
- **_gather_state**: Collects data from various PostgreSQL tables to form a comprehensive state of the user's life and work.
- **_build_prompt**: Constructs a detailed prompt for the AI model, including account balances, bills due, weather, routines, calendar events, checkins, life events, and backlog items.
- **_call_model**: Sends the constructed prompt to the AI model via an HTTP request and processes the JSON response.
- **_save_analysis**: Stores the analysis results in the `backlog_analysis` table.
- **_apply_reorders**: Updates the priority order of items in the `idea_backlog` table based on the analysis.

#### Integration Points
- **Database**: Connects to PostgreSQL to gather and store data.
- **Weather Service**: Integrates with a weather service to fetch and format weather data.
- **AI Model**: Communicates with an AI model via HTTP to generate the analysis.
- **Core Subsystems**: Interacts with other subsystems like `weather_service` for weather data.

### Summary
The `BacklogAnalyst` class serves as the core intelligence system for generating daily briefings and recommendations. It gathers comprehensive state data from various PostgreSQL tables, constructs a detailed prompt for an AI model, processes the model's response, and stores the results back into the database. It also provides methods to retrieve the latest briefing and transfer recommendations.
