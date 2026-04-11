# eval/results/query_natal_chart/20260305_103408/pass06_attempt05.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 129

---

### Documentation for `eval/results/query_natal_chart/20260305_103408/pass06_attempt05.py`

#### Purpose
This file contains the implementation of a skill (`QueryNatalChartSkill`) that queries and formats natal chart data from a PostgreSQL database. The skill is designed to respond to user queries about natal charts, placements, and other astrological information.

#### Architecture
The file consists of a single class `QueryNatalChartSkill` that inherits from `SkillBase`. The class contains several methods to handle different aspects of the query process:
- `_resolve_name`: Resolves the user-provided name to a standardized name.
- `_query_chart`: Queries the natal chart data from the database.
- `_query_placements`: Queries the placements data from the database.
- `_format`: Formats the chart and placements data into a human-readable string.
- `_build_summary`: Builds a summary of the major planet placements.

Additionally, there are top-level functions:
- `_get_conn`: Establishes a connection to the PostgreSQL database.
- `execute`: The main entry point for the skill, which orchestrates the query and response process.

#### Patterns
- **Singleton Pattern**: The `_get_conn` function ensures a single database connection is established and closed properly.
- **Factory Method**: The `execute` method acts as a factory method, creating the final response object by orchestrating the other methods.

#### Dependencies
- `os`: For accessing environment variables.
- `logging`: For logging errors.
- `psycopg2`: For PostgreSQL database operations.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For the `SkillBase` class and related types (`SkillRequest`, `SkillResponse`).

#### Interfaces
- **Public Methods**:
  - `execute`: Takes a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**:
  - `_resolve_name`: Resolves the input name to a standardized name.
  - `_query_chart`: Queries the natal chart data.
  - `_query_placements`: Queries the placements data.
  - `_format`: Formats the chart and placements data.
  - `_build_summary`: Builds a summary of the major planet placements.

#### Database
The file interacts with the following PostgreSQL tables:
- `astro_natal_charts`: Stores natal chart data.
- `astro_chart_objects`: Stores placements data.

#### Configuration
The file uses environment variables loaded from a `.env` file to configure the PostgreSQL database connection:
- `DB_HOST`
- `DB_NAME`
- `DB_USER`
- `DB_PASS`
- `DB_PORT`

#### Key Logic
1. **Name Resolution**: The `_resolve_name` method maps user input names to standardized names using a predefined `NAME_MAP`.
2. **Database Query**: The `_query_chart` and `_query_placements` methods fetch data from the `astro_natal_charts` and `astro_chart_objects` tables, respectively.
3. **Data Formatting**: The `_format` method combines the chart and placements data into a formatted string.
4. **Summary Building**: The `_build_summary` method creates a concise summary of the major planet placements.

#### Integration Points
- **SkillBase**: The `QueryNatalChartSkill` class inherits from `SkillBase`, integrating with the Mythos skill system.
- **Database Connection**: The `_get_conn` function integrates with the PostgreSQL database to fetch astrological data.
- **Environment Variables**: The `.env` file integration allows configuration of the database connection details.

This file is a critical component of the Mythos system, enabling users to query and receive detailed astrological information about specific individuals.
