# patterns/PATTERNS.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 171

---

### Documentation for `patterns/PATTERNS.json`

#### Purpose
This JSON file defines various solution patterns used in the Mythos system. Each pattern describes a specific composition of chunks that solve a category of problems, detailing the methods, integration points, and build plans for each pattern.

#### Architecture
The file is structured as a JSON object with the following key components:
- **pattern_version**: Version of the pattern definitions.
- **last_updated**: Date when the patterns were last updated.
- **description**: Overview of the purpose of the patterns.
- **patterns**: A dictionary containing multiple pattern definitions, each with its own structure including:
  - **name**: Name of the pattern.
  - **description**: Detailed description of the pattern.
  - **chunk_slots**: List of required and optional slots (chunks) that make up the pattern.
  - **scaffold**: Details on the methods, integration points, and test patterns.
  - **examples**: Example skills or commands that use this pattern.
  - **build_plan_template**: Step-by-step instructions for building a skill using this pattern.

#### Patterns
- **Data Query Skill**: Common pattern for querying PostgreSQL and returning structured data and summaries.
- **Memory Search**: Pattern for full-text search across memory stores.
- **Action Skill**: Pattern for writing to PostgreSQL and returning confirmations.
- **Composite Skill**: Pattern for chaining multiple skills together.
- **API Endpoint**: Pattern for exposing skills via FastAPI routes.
- **Telegram Command**: Pattern for handling Telegram bot commands.

#### Dependencies
This JSON file does not directly import or rely on any external modules or libraries. It serves as a configuration file for defining patterns and build plans.

#### Interfaces
The file exposes pattern definitions and build plans to other parts of the Mythos system, particularly to the skill-building and deployment processes.

#### Database
- **Data Query Skill**: Interacts with PostgreSQL tables.
- **Memory Search**: Interacts with PostgreSQL tables for full-text search.
- **Action Skill**: Writes to PostgreSQL tables.
- **Composite Skill**: Aggregates data from multiple skills, which may interact with various databases.
- **API Endpoint**: May interact with PostgreSQL tables or call skills that do.
- **Telegram Command**: May interact with PostgreSQL tables or call skills that do.

#### Configuration
The file itself serves as a configuration file, defining the patterns and build plans. It does not directly use any external configuration files or environment variables.

#### Key Logic
- **Data Query Skill**: Extracts parameters, builds and executes a SQL query, formats results, and builds a summary.
- **Memory Search**: Extracts search terms, performs full-text search, ranks results, and builds a summary.
- **Action Skill**: Parses input, validates it, writes to the database, and builds a confirmation summary.
- **Composite Skill**: Runs multiple sub-skills, collects results, and merges summaries.
- **API Endpoint**: Validates requests, executes skills or queries, and formats responses.
- **Telegram Command**: Parses command arguments, executes skills, and formats replies for Telegram.

#### Integration Points
- **Data Query Skill**: Integrates with PostgreSQL and uses `SkillBase` subclass.
- **Memory Search**: Integrates with PostgreSQL and uses `SkillBase` subclass.
- **Action Skill**: Integrates with PostgreSQL and uses `SkillBase` subclass.
- **Composite Skill**: Integrates with multiple `SkillBase` subclasses.
- **API Endpoint**: Integrates with FastAPI and registers routes in `api/main.py`.
- **Telegram Command**: Integrates with the Telegram bot framework and registers handlers in `telegram_bot/bot.py`.

### Summary
The `PATTERNS.json` file is a comprehensive configuration file that defines various patterns used in the Mythos system. Each pattern includes detailed descriptions, required slots, scaffold structures, and build plans, facilitating the creation and integration of skills and endpoints within the system.
