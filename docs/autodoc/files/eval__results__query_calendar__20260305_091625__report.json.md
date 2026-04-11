# eval/results/query_calendar/20260305_091625/report.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 182

---

### Documentation for `eval/results/query_calendar/20260305_091625/report.json`

#### Purpose
This JSON file contains the results of a series of tests performed on a calendar query module within the Mythos system. It documents the outcomes of each test pass, including the number of passes, total Ollama calls, and detailed information about the final behavioral test.

#### Architecture
The JSON structure is organized into several key sections:
- **Metadata**: Contains `plan_id`, `model`, `timestamp`, `total_passes`, `total_ollama_calls`, `final_parse`, and `final_import`.
- **Behavioral Test Results**: `final_behavioral` section includes `pass`, `errors`, `passed`, `failed`, and `total`.
- **Step-by-Step Test Details**: `steps` array, where each step contains `pass`, `instruction`, `test_type`, `recursive`, `attempts`, `elapsed_seconds`, and `final_code_lines`.

#### Patterns
No specific design patterns are directly applicable to this JSON file, as it is a data structure rather than a code implementation.

#### Dependencies
This JSON file does not import or rely on any external dependencies directly. However, it references the following:
- PostgreSQL database (`mythos_user` authentication issues)
- Ollama calls
- Python modules (`os`, `logging`, `re`, `datetime`, `psycopg2`, `dotenv`)

#### Interfaces
This JSON file serves as a report and does not expose any interfaces. It is used for logging and analysis purposes.

#### Database
The JSON file references the following PostgreSQL tables and operations:
- `calendar_events` table is queried for `id`, `title`, `description`, `event_date`, `start_time`, `end_time`, `location`, and `person` fields.
- The query uses `is_active` filter and ranges based on `event_date`.

#### Configuration
The JSON file indirectly references configuration settings:
- `POSTGRES_HOST` is used in `_get_conn()`.
- Environment variables and configuration files are implied by the use of `dotenv`.

#### Key Logic
The key logic described in the JSON file includes:
- **_detect_range()**: Determines the date range based on keywords in the message.
- **_query_events()**: Queries the `calendar_events` table based on the date range.
- **_format_results()**: Formats the query results into a dictionary.
- **_build_summary()**: Builds a summary of the events, ensuring it is concise and includes up to 5 events with a count of additional events.
- **execute()**: Combines the above functions to produce a `SkillResponse` object.

#### Integration Points
The JSON file integrates with the following Mythos subsystems:
- **Database**: PostgreSQL for querying calendar events.
- **Ollama**: For processing and generating responses.
- **Logging and Configuration**: Uses `logging` and `dotenv` for logging and configuration management.

### Summary
This JSON file serves as a comprehensive report on the testing process of a calendar query module in the Mythos system. It captures the outcomes of each test pass, including detailed error messages and performance metrics, and provides insights into the integration and functionality of the module with the underlying PostgreSQL database and other components of the Mythos infrastructure.
