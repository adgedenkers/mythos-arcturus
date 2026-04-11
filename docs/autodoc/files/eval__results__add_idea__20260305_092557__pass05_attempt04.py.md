# eval/results/add_idea/20260305_092557/pass05_attempt04.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 154

---

### Documentation for `eval/results/add_idea/20260305_092557/pass05_attempt04.py`

#### 1. Purpose
This file defines the `AddIdeaSkill` class, which is responsible for capturing new ideas from user messages and storing them in a PostgreSQL database. It processes the message to extract the idea text, detects the domain of the idea, and inserts the idea into the `idea_inbox` table.

#### 2. Architecture
- **Classes**: 
  - `AddIdeaSkill` inherits from `SkillBase` and implements the `execute` method to process the user request.
- **Methods**:
  - `execute`: The main method that processes the user request, extracts the idea, detects the domain, and inserts the idea into the database.
  - `_extract_idea`: Helper method to clean and extract the idea text from the message.
  - `_detect_domain`: Helper method to detect the domain of the idea based on keywords in the message.
  - `_insert_idea`: Helper method to insert the idea into the `idea_inbox` table in the PostgreSQL database.
- **Data Flow**:
  - The `execute` method receives a `SkillRequest` object, processes it to extract the idea and detect the domain, and then inserts the idea into the database.
  - The `_extract_idea` and `_detect_domain` methods are called within `execute` to prepare the data for insertion.
  - The `_insert_idea` method handles the database insertion and returns the idea ID.

#### 3. Patterns
- **Singleton**: The `AddIdeaSkill` class does not follow the Singleton pattern.
- **Factory**: The class does not use a Factory pattern.
- **Observer**: The class does not use the Observer pattern.

#### 4. Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `json`: For JSON serialization.
  - `psycopg2`: For PostgreSQL database operations.
  - `re`: For regular expression operations.
  - `dotenv`: For loading environment variables from `.env` files.
  - `engine.base`: For the `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### 5. Interfaces
- **Exposed Methods**:
  - `execute`: Exposed as an asynchronous method to process the user request and return a `SkillResponse` object.
- **Exposed Classes**:
  - `AddIdeaSkill`: Inherits from `SkillBase` and implements the `execute` method.

#### 6. Database
- **Tables**:
  - `idea_inbox`: The table where the new ideas are inserted. The columns include `conversation_context`, `items`, `item_count`, `disposition`, `domain`, and `tags`.

#### 7. Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`: Host address of the PostgreSQL database.
  - `DB_NAME`: Name of the database.
  - `DB_USER`: Username for the database.
  - `DB_PASSWORD`: Password for the database.
  - `DB_PORT`: Port number for the database.

#### 8. Key Logic
- **Extracting Idea**:
  - The `_extract_idea` method cleans the message by removing triggers, normalizing whitespace, and stripping punctuation.
- **Detecting Domain**:
  - The `_detect_domain` method checks for keywords in the message to determine the domain of the idea.
- **Inserting Idea**:
  - The `_insert_idea` method inserts the idea into the `idea_inbox` table, including the conversation context, idea text, domain, and tags.

#### 9. Integration Points
- **Mythos Subsystems**:
  - The `AddIdeaSkill` class integrates with the Mythos system by processing user requests and storing ideas in the PostgreSQL database.
  - It uses the `SkillBase` class from the `engine.base` module to handle the request and response objects.
  - It relies on the PostgreSQL database for storing the ideas in the `idea_inbox` table.
