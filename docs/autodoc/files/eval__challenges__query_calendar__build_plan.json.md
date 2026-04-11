# eval/challenges/query_calendar/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 34

---

### Documentation for `eval/challenges/query_calendar/build_plan.json`

#### Purpose
This JSON file serves as a blueprint for developing a calendar query skill within the Mythos system. It outlines the structure, logic, and implementation steps for a skill that retrieves and summarizes calendar events based on user queries.

#### Architecture
The file is structured as a JSON object with several key sections:
- **plan_id**: Identifies the skill.
- **version**: Specifies the version of the skill.
- **description**: Describes the purpose of the skill.
- **pattern**: Indicates the type of skill.
- **model_hint**: Specifies the AI model to use.
- **context**: Contains detailed information about the database schema, class structure, and mandatory patterns.
- **build_plan**: Provides step-by-step instructions for implementing the skill.
- **test_cases**: Lists test cases to validate the skill's functionality.

#### Patterns
- **Factory Method**: The skill class `QueryCalendarSkill` is a factory method for creating calendar query instances.
- **Singleton**: The `_get_conn` function ensures a single database connection instance.
- **Observer**: The skill observes user messages to detect date ranges and triggers.

#### Dependencies
- **Python Libraries**: `os`, `logging`, `re`, `datetime`, `psycopg2`, `RealDictCursor`, `dotenv`, `engine.base`.
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.

#### Interfaces
- **Class**: `QueryCalendarSkill` extends `SkillBase`.
- **Methods**:
  - `execute(self, request) -> SkillResponse`: Main method to process user requests.
  - `_detect_range(self, message) -> tuple`: Detects the date range from the user message.
  - `_query_events(self, start_date, end_date) -> list`: Queries the database for events within the specified date range.
  - `_format_results(self, rows) -> list`: Formats the query results into a list of dictionaries.
  - `_build_summary(self, results, start_date, end_date) -> str`: Builds a summary of the events.

#### Database
- **Table**: `calendar_events`
- **Columns**: `id`, `title`, `description`, `event_date`, `start_time`, `end_time`, `location`, `person`, `is_recurring`, `source`, `is_active`.
- **Indexes**: `idx_calendar_events_date`, `idx_calendar_events_person`.

#### Configuration
- **Environment Variables**: `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`.
- **Database Connection**: Configured via `_get_conn()` function.

#### Key Logic
1. **Date Range Detection**: Parses user messages to determine the date range (today, this week, next N days, etc.).
2. **Database Query**: Retrieves events from the `calendar_events` table based on the detected date range.
3. **Result Formatting**: Formats the query results into a structured list of dictionaries.
4. **Summary Building**: Constructs a concise summary of the events, showing up to 5 events and indicating if there are more.

#### Integration Points
- **SkillBase Class**: Inherits from `SkillBase` to leverage common skill functionality.
- **Database Connection**: Uses `_get_conn()` to establish a connection to the PostgreSQL database.
- **Skill Response**: Returns a `SkillResponse` object with formatted data and summary.

### Detailed Breakdown of Build Plan

1. **Pass 1**: Write the file skeleton, including necessary imports and class structure.
2. **Pass 2**: Implement `_detect_range()` to parse user messages and determine the date range.
3. **Pass 3**: Implement `_query_events()` to query the database for events within the specified date range.
4. **Pass 4**: Implement `_format_results()` and `_build_summary()` to format the query results and build a summary.
5. **Pass 5**: Implement the `execute()` method to process user requests, query events, format results, and build a summary.
6. **Pass 6**: Review and finalize the implementation, ensuring all connections are closed, summaries are non-empty, and times are formatted cleanly.

### Test Cases
- **Test Case 1**: Message "what is on my calendar today" should return events for today.
- **Test Case 2**: Message "any upcoming events this week" should return events for the upcoming week.
- **Test Case 3**: Message "schedule" should return events based on default behavior.

This JSON file provides a comprehensive guide for developing the calendar query skill, ensuring all aspects of the system are covered from database interaction to user interaction.
