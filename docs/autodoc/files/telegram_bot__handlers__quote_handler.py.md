# telegram_bot/handlers/quote_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 379

---

### File: `telegram_bot/handlers/quote_handler.py`

#### Purpose
This file contains functions to handle various `/quote` commands in a Telegram bot, including adding, searching, listing, and retrieving quotes from a Neo4j database.

#### Architecture
The file consists of several top-level functions that handle different `/quote` commands. Each function performs a specific task related to the manipulation and retrieval of quotes stored in a Neo4j database. The main function `handle_quote` acts as a dispatcher for different commands, calling the appropriate helper functions based on the input text.

#### Patterns
- **Dispatcher Pattern**: The `handle_quote` function acts as a dispatcher, routing the command to the appropriate handler function based on the command text.
- **Helper Functions**: The file uses helper functions like `_add_quote`, `_lookup_quote`, `_list_quotes`, `_search_quotes`, `_random_quote`, `_add_tag`, `_relate_term`, and `_set_interpretation` to encapsulate specific functionalities.

#### Dependencies
- **Standard Libraries**: `os`, `uuid`, `datetime`, `timezone`
- **Neo4j Driver**: `GraphDatabase` from `neo4j`
- **Environment Variables**: `dotenv` for loading environment variables

#### Interfaces
- **Public Functions**:
  - `handle_quote(text: str)`: Handles the `/quote` command and returns a string or a tuple with inline buttons.
  - `get_driver()`: Returns a Neo4j driver instance.

#### Database
- **Neo4j Labels**:
  - `Quote`: Represents a quote node.
  - `OntologyTerm`: Represents ontology terms that can be linked to quotes.
- **Neo4j Relationships**:
  - `TAGGED_WITH`: Relationship between a quote and a tag.
  - `RELATES_TO`: Relationship between a quote and an ontology term.

#### Configuration
- **Environment Variables**:
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for Neo4j.
  - `NEO4J_PASSWORD`: Password for Neo4j.

#### Key Logic
- **Adding Quotes**: The `_add_quote` function creates a new `Quote` node in Neo4j and auto-links it to ontology terms based on tags.
- **Searching Quotes**: The `_search_quotes` function searches quotes by text, description, or interpretation.
- **Listing Quotes**: The `_list_quotes` function lists quotes, optionally filtered by speaker.
- **Random Quote**: The `_random_quote` function returns a random quote from the database.
- **Tagging Quotes**: The `_add_tag` function adds a tag to a quote and updates the `Quote` node.
- **Relating Terms**: The `_relate_term` function links a quote to an ontology term.
- **Setting Interpretation**: The `_set_interpretation` function sets the interpretation for a quote.

#### Integration Points
- **Telegram Bot**: This file is part of the Telegram bot infrastructure and integrates with the bot's command handling system.
- **Neo4j Database**: The file interacts with the Neo4j database to store and retrieve quotes and related information.
- **Environment Configuration**: The file reads environment variables for database connection details using `dotenv`.

### Detailed Analysis of Functions

1. **`get_driver()`**
   - **Purpose**: Returns a Neo4j driver instance.
   - **Dependencies**: `GraphDatabase` from `neo4j`.
   - **Logic**: Uses environment variables for Neo4j URI, user, and password to create a driver instance.

2. **`handle_quote(text: str)`**
   - **Purpose**: Dispatches the `/quote` command to the appropriate handler function.
   - **Logic**: Parses the input text and calls the corresponding helper function based on the command.

3. **`_add_quote(text: str)`**
   - **Purpose**: Adds a new quote to the Neo4j database.
   - **Logic**: Parses the input text to extract quote details, creates a new `Quote` node, and auto-links it to ontology terms based on tags.

4. **`_lookup_quote(qid: str)`**
   - **Purpose**: Retrieves a quote by its ID and related information.
   - **Logic**: Queries the Neo4j database for the quote and related terms, returning the details as a tuple.

5. **`_list_quotes(speaker: str = None)`**
   - **Purpose**: Lists quotes, optionally filtered by speaker.
   - **Logic**: Queries the Neo4j database for quotes, optionally filtering by speaker, and returns the list as a string.

6. **`_search_quotes(query: str)`**
   - **Purpose**: Searches quotes by text, description, or interpretation.
   - **Logic**: Queries the Neo4j database for quotes matching the query and returns the results as a string.

7. **`_random_quote()`**
   - **Purpose**: Returns a random quote from the database.
   - **Logic**: Queries the Neo4j database for a random quote and returns it as a string.

8. **`_add_tag(qid: str, tag: str)`**
   - **Purpose**: Adds a tag to a quote.
   - **Logic**: Updates the `Quote` node in Neo4j to include the new tag.

9. **`_relate_term(qid: str, term_name: str)`**
   - **Purpose**: Links a quote to an ontology term.
   - **Logic**: Creates a relationship between the `Quote` node and the `OntologyTerm` node in Neo4j.

10. **`_set_interpretation(qid: str, text: str)`**
    - **Purpose**: Sets the interpretation for a quote.
    - **Logic**: Updates the `Quote` node in Neo4j to include the new interpretation.

This file is a critical component of the Mythos system, providing the functionality to manage and interact with quotes through a Telegram bot interface.
