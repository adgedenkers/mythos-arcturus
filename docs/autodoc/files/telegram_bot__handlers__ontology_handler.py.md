# telegram_bot/handlers/ontology_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 251

---

### File: `telegram_bot/handlers/ontology_handler.py`

#### Purpose
This file contains functions to handle ontology-related commands for a Telegram bot, including defining, adding, and listing ontology terms. It interacts with a Neo4j database to retrieve and manipulate ontology terms.

#### Architecture
The file consists of several top-level functions:
- `moon_term_buttons`: Generates inline keyboard buttons for moon names.
- `term_buttons`: Generates generic inline keyboard buttons for ontology terms.
- `get_driver`: Returns a Neo4j driver instance.
- `handle_define`: Handles the `/define` command, delegating to other functions based on the input.
- `_lookup_term`: Looks up a term in the Neo4j database and returns details.
- `_add_term`: Adds a new term to the Neo4j database.
- `_list_terms`: Lists ontology terms, optionally filtered by category.

#### Patterns
- **Factory Method**: `get_driver` acts as a factory method to create and return a Neo4j driver instance.
- **Singleton**: The Neo4j driver instance is created once and reused, mimicking a singleton pattern.

#### Dependencies
- **Imports**: `os`, `datetime`, `neo4j.GraphDatabase`, `dotenv.load_dotenv`, `telegram.InlineKeyboardButton`, `telegram.InlineKeyboardMarkup`.
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` loaded from `.env` file.

#### Interfaces
- **Public Functions**: `moon_term_buttons`, `term_buttons`, `handle_define`.
- **Private Functions**: `_lookup_term`, `_add_term`, `_list_terms`.

#### Database
- **Neo4j Labels**: `OntologyTerm`.
- **Neo4j Queries**: 
  - `MATCH (t:OntologyTerm) ...`: Used to retrieve ontology terms.
  - `CREATE (t:OntologyTerm { ... })`: Used to create new ontology terms.

#### Configuration
- **Environment Variables**: 
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for the Neo4j database.
  - `NEO4J_PASSWORD`: Password for the Neo4j database.
- **Dotenv File**: `.env` located at `/opt/mythos/.env`.

#### Key Logic
- **Term Lookup**: `_lookup_term` queries the Neo4j database to find ontology terms based on the query. It handles exact matches and partial matches, returning details and related terms.
- **Term Addition**: `_add_term` creates a new ontology term in the Neo4j database, ensuring uniqueness and setting creation and update timestamps.
- **Term Listing**: `_list_terms` retrieves ontology terms from the Neo4j database, optionally filtered by category, and formats the results for display.

#### Integration Points
- **Telegram Bot**: Functions like `moon_term_buttons` and `term_buttons` generate inline keyboard buttons for the Telegram bot, which are used to interact with ontology terms.
- **Neo4j Database**: Functions interact with the Neo4j database to perform CRUD operations on ontology terms.
- **Environment Configuration**: Uses environment variables and `.env` file for configuration, ensuring secure and flexible configuration management.

### Detailed Function Descriptions

1. **`moon_term_buttons`**:
   - **Purpose**: Generates inline keyboard buttons for moon names.
   - **Parameters**: `moon_names` (list of moon names), `cols` (number of columns in the keyboard).
   - **Returns**: `InlineKeyboardMarkup` object with buttons for each moon name.

2. **`term_buttons`**:
   - **Purpose**: Generates generic inline keyboard buttons for ontology terms, with category-specific emojis.
   - **Parameters**: `names` (list of term names), `category` (category of terms), `cols` (number of columns in the keyboard).
   - **Returns**: `InlineKeyboardMarkup` object with buttons for each term name.

3. **`get_driver`**:
   - **Purpose**: Returns a Neo4j driver instance.
   - **Parameters**: None.
   - **Returns**: `GraphDatabase.driver` instance.

4. **`handle_define`**:
   - **Purpose**: Handles the `/define` command, delegating to other functions based on the input.
   - **Parameters**: `text` (command text).
   - **Returns**: String or tuple containing a string and a list of names.

5. **`_lookup_term`**:
   - **Purpose**: Looks up a term in the Neo4j database and returns details.
   - **Parameters**: `query` (term to look up).
   - **Returns**: Tuple containing a string with term details and a list of related term names.

6. **`_add_term`**:
   - **Purpose**: Adds a new term to the Neo4j database.
   - **Parameters**: `text` (input text containing term details).
   - **Returns**: String indicating success or failure.

7. **`_list_terms`**:
   - **Purpose**: Lists ontology terms, optionally filtered by category.
   - **Parameters**: `category` (category to filter by).
   - **Returns**: Tuple containing a string with term list and a list of term names.
