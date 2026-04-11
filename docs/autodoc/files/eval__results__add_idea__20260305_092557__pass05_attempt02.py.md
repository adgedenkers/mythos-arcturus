# eval/results/add_idea/20260305_092557/pass05_attempt02.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 154

---

### Documentation for `eval/results/add_idea/20260305_092557/pass05_attempt02.py`

#### Purpose
This file defines the `AddIdeaSkill` class, which is responsible for capturing new ideas from user messages, detecting the domain of the idea, and storing it in the PostgreSQL `idea_inbox` table.

#### Architecture
The file contains a single class `AddIdeaSkill` that inherits from `SkillBase`. The class has the following methods:
- `execute`: The main method that processes the request, extracts the idea, detects the domain, and inserts the idea into the database.
- `_extract_idea`: A helper method to extract the idea text from the user message.
- `_detect_domain`: A helper method to detect the domain of the idea based on keywords.
- `_insert_idea`: A helper method to insert the idea into the PostgreSQL database.

#### Patterns
- **Factory Pattern**: The `AddIdeaSkill` class can be seen as a factory for creating and processing ideas.
- **Singleton Pattern**: Although not explicitly implemented, the `AddIdeaSkill` class could be used as a singleton if only one instance is needed per application.

#### Dependencies
- **Imports**: `os`, `logging`, `json`, `psycopg2`, `re`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`
- **Environment Variables**: `POSTGRES_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`

#### Interfaces
- **Public Methods**: `execute`
- **Exposed Interfaces**: The `execute` method is the primary interface that other parts of the system use to interact with this class.

#### Database
- **Tables**: `idea_inbox`
- **Operations**: Inserts new ideas into the `idea_inbox` table.

#### Configuration
- **Environment Variables**: The PostgreSQL connection details are loaded from environment variables using `dotenv`.

#### Key Logic
1. **Extract Idea**: The `_extract_idea` method cleans and normalizes the user message to extract the idea text.
2. **Detect Domain**: The `_detect_domain` method checks the message for keywords to determine the domain of the idea.
3. **Insert Idea**: The `_insert_idea` method inserts the idea into the `idea_inbox` table, returning the new idea ID.

#### Integration Points
- **SkillBase**: The `AddIdeaSkill` class inherits from `SkillBase`, integrating with the broader Mythos skill system.
- **Database**: The `_insert_idea` method interacts with the PostgreSQL database to store ideas.
- **Logging**: Uses Python's `logging` module to log errors.

### Detailed Breakdown

#### Class: `AddIdeaSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: 'add_idea'
  - `version`: '1.0'
  - `category`: 'action'
  - `description`: 'Capture a new idea into the inbox'
  - `triggers`: List of phrases that trigger this skill.
  - `cache_ttl`: 0 (no caching).

#### Methods:
- **`execute`**:
  - **Parameters**: `request` (SkillRequest object)
  - **Logic**:
    1. Extracts the idea text using `_extract_idea`.
    2. Checks if the idea text is valid.
    3. Detects the domain using `_detect_domain`.
    4. Inserts the idea into the `idea_inbox` table using `_insert_idea`.
    5. Returns a `SkillResponse` object with the idea ID and summary.

- **`_extract_idea`**:
  - **Parameters**: `message` (string)
  - **Logic**:
    1. Converts the message to lowercase.
    2. Removes specific triggers from the message.
    3. Normalizes whitespace and punctuation.
    4. Ensures the message contains only ASCII characters.
    5. Returns the cleaned idea text.

- **`_detect_domain`**:
  - **Parameters**: `message` (string)
  - **Logic**:
    1. Converts the message to lowercase.
    2. Checks for keywords in predefined domains.
    3. Returns the detected domain or `None` if no domain is found.

- **`_insert_idea`**:
  - **Parameters**: `idea_text` (string), `domain` (string), `source_message` (string)
  - **Logic**:
    1. Establishes a connection to the PostgreSQL database.
    2. Inserts the idea into the `idea_inbox` table.
    3. Returns the new idea ID.
    4. Closes the database connection.

### Summary
The `AddIdeaSkill` class is designed to capture new ideas from user messages, detect their domain, and store them in a PostgreSQL database. It integrates with the Mythos skill system and uses environment variables for database configuration.
