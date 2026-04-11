# eval/results/add_idea/20260305_092557/pass05_attempt03.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 154

---

### Documentation for `eval/results/add_idea/20260305_092557/pass05_attempt03.py`

#### Purpose
This file defines the `AddIdeaSkill` class, which is responsible for capturing new ideas from user messages and storing them in a PostgreSQL database. It processes the user message to extract the idea, detect its domain, and then insert it into the `idea_inbox` table.

#### Architecture
- **Class**: `AddIdeaSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: The main method that processes the user request, extracts the idea, detects the domain, and inserts the idea into the database.
  - `_extract_idea`: Extracts the idea text from the user message.
  - `_detect_domain`: Detects the domain of the idea based on keywords in the message.
  - `_insert_idea`: Inserts the extracted idea into the `idea_inbox` table in the PostgreSQL database.

#### Patterns
- **Factory Pattern**: Not explicitly used.
- **Singleton Pattern**: Not explicitly used.
- **Observer Pattern**: Not explicitly used.
- **Decorator Pattern**: Not explicitly used.

#### Dependencies
- **Imports**:
  - `os`: For accessing environment variables.
  - `logging`: For logging errors.
  - `json`: For JSON serialization.
  - `psycopg2`: For PostgreSQL database operations.
  - `re`: For regular expressions.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and interfaces for skills.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Asynchronous method that takes a `SkillRequest` object and returns a `SkillResponse` object.
  - `_extract_idea`: Synchronous method that takes a message and returns the extracted idea text.
  - `_detect_domain`: Synchronous method that takes a message and returns the detected domain.
  - `_insert_idea`: Synchronous method that takes the idea text, domain, and source message, and returns the idea ID.

#### Database
- **Tables**:
  - `idea_inbox`: Table in the PostgreSQL database where ideas are stored.
  - **Columns**:
    - `id`: Unique identifier for the idea.
    - `conversation_context`: The original message context.
    - `items`: JSON array of items (idea text).
    - `item_count`: Number of items.
    - `disposition`: Status of the idea (e.g., 'pending').
    - `domain`: Domain of the idea.
    - `tags`: JSON array of tags (domain).

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`: Host of the PostgreSQL database.
  - `DB_NAME`: Name of the PostgreSQL database.
  - `DB_USER`: Username for the PostgreSQL database.
  - `DB_PASSWORD`: Password for the PostgreSQL database.
  - `DB_PORT`: Port of the PostgreSQL database.

#### Key Logic
- **Extracting Idea**:
  - Converts the message to lowercase.
  - Removes predefined triggers.
  - Normalizes whitespace and strips punctuation.
  - Ensures ASCII only.

- **Detecting Domain**:
  - Converts the message to lowercase.
  - Matches keywords to predefined domains.

- **Inserting Idea**:
  - Establishes a connection to the PostgreSQL database.
  - Inserts the idea into the `idea_inbox` table.
  - Returns the new idea ID.

#### Integration Points
- **SkillBase Interface**: The `AddIdeaSkill` class implements the `SkillBase` interface, which is part of the Mythos skill system.
- **Database Integration**: Uses `psycopg2` to interact with the PostgreSQL database.
- **Environment Variables**: Loads environment variables using `dotenv` for database connection details.
- **Logging**: Uses `logging` to log errors during database operations.

This file is a crucial component of the Mythos system, enabling the capture and storage of user-generated ideas in a structured manner.
