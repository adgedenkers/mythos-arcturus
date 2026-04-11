# eval/results/add_idea/20260305_092557/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 151

---

### Documentation for `eval/results/add_idea/20260305_092557/pass04_attempt01.py`

#### Purpose
This file defines the `AddIdeaSkill` class, which is responsible for capturing new ideas from user messages, detecting the domain of the idea, and inserting it into the PostgreSQL `idea_inbox` table.

#### Architecture
The file contains a single class `AddIdeaSkill` that inherits from `SkillBase`. The class has four methods:
- `execute`: The primary method that orchestrates the idea extraction, domain detection, and insertion into the database.
- `_extract_idea`: A helper method to extract the idea text from the user message.
- `_detect_domain`: A helper method to detect the domain of the idea based on keywords in the message.
- `_insert_idea`: A helper method to insert the idea into the PostgreSQL `idea_inbox` table.

#### Patterns
- **Strategy Pattern**: The `AddIdeaSkill` class can be seen as a strategy for handling a specific type of user input (ideas), and it can be extended or replaced with other strategies for different types of inputs.
- **Singleton Pattern**: The `AddIdeaSkill` class is designed to be a singleton, as it is intended to be a single instance handling the idea capture process.

#### Dependencies
- **Imports**: `os`, `logging`, `json`, `psycopg2`, `re`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **Environment Variables**: `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`.

#### Interfaces
- **Public Methods**: `execute` is the primary method that is called to process the idea.
- **SkillResponse**: The `execute` method returns a `SkillResponse` object containing the result of the idea capture process.

#### Database
- **Tables**: The `idea_inbox` table is used to store the captured ideas.
- **Operations**: The `_insert_idea` method performs an `INSERT` operation into the `idea_inbox` table.

#### Configuration
- **Environment Variables**: The database connection details are loaded from environment variables using `dotenv`.

#### Key Logic
- **Idea Extraction**: The `_extract_idea` method removes predefined triggers from the message and normalizes the text.
- **Domain Detection**: The `_detect_domain` method checks for keywords in the message to determine the domain of the idea.
- **Database Insertion**: The `_insert_idea` method inserts the idea into the `idea_inbox` table with the appropriate details.

#### Integration Points
- **SkillBase**: The `AddIdeaSkill` class inherits from `SkillBase`, which provides a framework for handling user inputs.
- **SkillRequest and SkillResponse**: The `execute` method processes a `SkillRequest` and returns a `SkillResponse`, integrating with the broader Mythos system for handling user inputs and responses.

### Detailed Breakdown

#### Class: `AddIdeaSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: 'add_idea'
  - `version`: '1.0'
  - `category`: 'action'
  - `description`: 'Capture a new idea into the inbox'
  - `triggers`: List of phrases that trigger the idea capture process.
  - `cache_ttl`: 0 (no caching).

#### Methods
- **`execute`**:
  - **Purpose**: Processes the user request to capture an idea.
  - **Logic**:
    1. Extracts the idea text using `_extract_idea`.
    2. Detects the domain using `_detect_domain`.
    3. Inserts the idea into the `idea_inbox` table using `_insert_idea`.
    4. Returns a `SkillResponse` with the result.

- **`_extract_idea`**:
  - **Purpose**: Extracts the idea text from the user message.
  - **Logic**:
    1. Converts the message to lowercase.
    2. Removes predefined triggers.
    3. Normalizes whitespace and punctuation.

- **`_detect_domain`**:
  - **Purpose**: Detects the domain of the idea based on keywords in the message.
  - **Logic**:
    1. Checks for keywords in predefined domains.
    2. Returns the domain if a keyword is found, otherwise returns `None`.

- **`_insert_idea`**:
  - **Purpose**: Inserts the idea into the `idea_inbox` table.
  - **Logic**:
    1. Establishes a connection to the PostgreSQL database.
    2. Inserts the idea with the extracted text, domain, and source message.
    3. Returns the `idea_id` of the inserted idea.

### Summary
The `AddIdeaSkill` class is designed to capture new ideas from user messages, detect their domain, and store them in the PostgreSQL `idea_inbox` table. It integrates with the Mythos system by inheriting from `SkillBase` and using `SkillRequest` and `SkillResponse` to process and return results.
