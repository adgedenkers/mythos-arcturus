# skills/data/astro_context.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 177

---

### Documentation for `skills/data/astro_context.py`

#### Purpose
This file implements the `AstroContextSkill` class, which retrieves natal chart placements from PostgreSQL tables `astro_natal_charts` and `astro_chart_objects`. It provides astrological context based on the user's request.

#### Architecture
- **Classes**: 
  - `AstroContextSkill` inherits from `SkillBase` and implements the `execute` method to process requests and return astrological data.
- **Functions**:
  - `_get_conn`: A utility function to establish a connection to the PostgreSQL database.
  - `execute`: An asynchronous function that processes the request and retrieves the natal chart data.
- **Data Flow**:
  - The `execute` method processes the incoming `SkillRequest`, determines the appropriate chart to retrieve based on the request context, and queries the PostgreSQL database for the natal chart and planetary positions.
  - The retrieved data is then formatted into a `SkillResponse` object, which includes a summary and detailed placements.

#### Patterns
- **Singleton**: The `_get_conn` function can be considered a singleton pattern as it provides a single connection instance.
- **Factory**: The `execute` method acts as a factory for creating `SkillResponse` objects based on the retrieved data.

#### Dependencies
- **Imports**: 
  - `os`: For accessing environment variables.
  - `logging`: For logging errors.
  - `psycopg2`: For PostgreSQL database connection and querying.
  - `typing`: For type annotations.
  - `dotenv`: For loading environment variables from `.env` files.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute`: An asynchronous method that processes a `SkillRequest` and returns a `SkillResponse` containing astrological data.

#### Database
- **Tables**:
  - `astro_natal_charts`: Stores natal chart information.
  - `astro_chart_objects`: Stores planetary positions within the natal chart.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: Configured in `/opt/mythos/.env` for database connection.
- **Configuration Files**:
  - `.env`: Loaded using `dotenv.load_dotenv` to set environment variables.

#### Key Logic
- **Determine Chart**: The `execute` method determines which chart to retrieve based on the `soul_name` in the request context or by searching the message content.
- **Database Queries**: 
  - Retrieves chart information from `astro_natal_charts`.
  - Retrieves planetary positions from `astro_chart_objects`.
- **Summary Construction**: Constructs a summary of key planetary placements in the chart.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos skill system.
- **Database Connection**: Uses `_get_conn` to connect to PostgreSQL, integrating with the database subsystem.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` to interface with the Mythos skill execution framework.

### Detailed Breakdown

#### `_get_conn` Function
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Logic**: Uses `psycopg2.connect` with environment variables for database credentials and sets `RealDictCursor` as the cursor factory.

#### `AstroContextSkill` Class
- **Attributes**:
  - `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`: Define metadata and behavior of the skill.
- **Methods**:
  - `execute`: Processes the request, retrieves chart data, and constructs a `SkillResponse` with the summary and detailed placements.

#### `execute` Method
- **Steps**:
  1. Establishes a database connection using `_get_conn`.
  2. Determines the chart name based on the request context or message content.
  3. Queries `astro_natal_charts` for chart details.
  4. Queries `astro_chart_objects` for planetary positions.
  5. Constructs a summary of key placements and detailed data.
  6. Returns a `SkillResponse` object with the summary and detailed placements.

This file is crucial for providing astrological context within the Mythos system, integrating with the database and skill execution framework to deliver personalized astrological information.
