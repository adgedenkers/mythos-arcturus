# eval/results/add_idea/20260305_092557/pass05_attempt05.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 154

---

### File: `eval/results/add_idea/20260305_092557/pass05_attempt05.py`

#### Purpose
This file defines the `AddIdeaSkill` class, which is responsible for capturing new ideas from user messages and storing them in a PostgreSQL database table named `idea_inbox`.

#### Architecture
- **Classes**: 
  - `AddIdeaSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: The main method that processes the incoming request, extracts the idea, detects the domain, and inserts the idea into the database.
  - `_extract_idea`: Helper method to extract the idea text from the user message.
  - `_detect_domain`: Helper method to detect the domain of the idea based on keywords in the message.
  - `_insert_idea`: Helper method to insert the idea into the `idea_inbox` table in the PostgreSQL database.
- **Data Flow**:
  1. The `execute` method receives a `SkillRequest` object.
  2. It calls `_extract_idea` to get the idea text.
  3. It calls `_detect_domain` to determine the domain of the idea.
  4. It calls `_insert_idea` to store the idea in the database.
  5. It returns a `SkillResponse` object with the result.

#### Patterns
- **Observer Pattern**: The `execute` method acts as an observer, processing incoming requests and triggering the extraction, domain detection, and insertion processes.
- **Factory Pattern**: The `execute` method can be seen as a factory method that creates and returns a `SkillResponse` object based on the processed request.

#### Dependencies
- **Imports**:
  - `os`: For environment variable access.
  - `logging`: For logging errors.
  - `json`: For JSON serialization.
  - `psycopg2`: For PostgreSQL database operations.
  - `re`: For regular expression operations.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse` classes.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Asynchronous method that processes the request and returns a `SkillResponse` object.
- **Exposed Classes**:
  - `AddIdeaSkill`: Inherits from `SkillBase` and implements the `execute` method.

#### Database
- **Tables**:
  - `idea_inbox`: The table where new ideas are inserted. The table has columns such as `conversation_context`, `items`, `item_count`, `disposition`, `domain`, and `tags`.

#### Configuration
- **Environment Variables**:
  - `POSTGRES_HOST`: Host of the PostgreSQL database.
  - `DB_NAME`: Name of the PostgreSQL database.
  - `DB_USER`: Username for the PostgreSQL database.
  - `DB_PASSWORD`: Password for the PostgreSQL database.
  - `DB_PORT`: Port of the PostgreSQL database.

#### Key Logic
- **Extracting Idea**:
  - The `_extract_idea` method removes specific triggers from the message and normalizes the text.
- **Detecting Domain**:
  - The `_detect_domain` method checks for keywords in predefined domains and returns the domain if a match is found.
- **Inserting Idea**:
  - The `_insert_idea` method inserts the idea into the `idea_inbox` table with the extracted idea text, detected domain, and source message.

#### Integration Points
- **Mythos System**:
  - The `AddIdeaSkill` class integrates with the Mythos system by processing incoming `SkillRequest` objects and returning `SkillResponse` objects.
  - It interacts with the PostgreSQL database to store ideas in the `idea_inbox` table.
  - It uses environment variables and configuration files to manage database connections and other settings.

This file is a critical component of the Mythos system, enabling the capture and storage of user-generated ideas in a structured manner.
