# telegram_bot/handlers/registry_handler.py

**Language:** python
**Stream:** SYS
**Module:** Telegram Bot
**Lines:** 163

---

### Purpose
The `registry_handler.py` file in the `telegram_bot/handlers` directory handles the `/registry` command for the Telegram bot. It interacts with the Neo4j database to provide audit reports, orphan labels, and cleanup queries for registered applications.

### Architecture
The file contains three main functions:
1. `_get_neo4j_driver`: Retrieves the Neo4j driver using environment variables.
2. `handle_registry`: Processes the `/registry` command and handles various subcommands like full audit, orphan labels, and cleanup queries.
3. `_split_message`: Splits long messages into chunks to comply with Telegram's character limit.

### Patterns
- **Factory Method**: The `_get_neo4j_driver` function acts as a factory method to create and return a Neo4j driver instance.
- **Singleton**: The Neo4j driver is created and closed within the `handle_registry` function, ensuring that it is used as a singleton within the scope of the command handling.

### Dependencies
- **Imports**: The file imports `os` and `logging` for environment variable access and logging, respectively.
- **External Modules**: It also imports `Update` and `ContextTypes` from the `telegram` and `telegram.ext` modules for handling Telegram bot updates and context.

### Interfaces
- **Public Functions**: The `handle_registry` function is the main entry point for handling the `/registry` command. It takes `Update` and `ContextTypes.DEFAULT_TYPE` as parameters.
- **Internal Functions**: `_get_neo4j_driver` and `_split_message` are helper functions used internally within the file.

### Database
- **PostgreSQL Tables**: The file references several PostgreSQL tables (`telegram`, `from`, `environment`, `neo4j`, `core`, `chunks`), though these are not directly accessed in the provided code.
- **Neo4j**: The file interacts with Neo4j to retrieve and process application registry data.

### Configuration
- **Environment Variables**: The file reads environment variables `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD` to configure the Neo4j driver.

### Key Logic
- **Audit Report Generation**: The `handle_registry` function generates a full audit report of all applications, node counts, and orphan labels.
- **Orphan Label Detection**: It identifies orphan labels that are not registered to any application.
- **Cleanup Query Generation**: It provides cleanup queries for specific applications, including a count query and a delete query.
- **Message Chunking**: The `_split_message` function ensures that long messages are split into chunks that comply with Telegram's character limit.

### Integration Points
- **Telegram Bot**: The file integrates with the Telegram bot framework to handle user commands and send responses.
- **App Registry**: It interacts with the `AppRegistry` class from the `core.app_registry` module to retrieve and process application registry data.
- **Neo4j**: The file connects to the Neo4j database to fetch and manipulate application data.

### Detailed Breakdown
1. **_get_neo4j_driver**:
   - **Purpose**: Retrieves the Neo4j driver using environment variables.
   - **Logic**: Uses `os.getenv` to fetch the Neo4j URI, user, and password from environment variables and returns a Neo4j driver instance.

2. **handle_registry**:
   - **Purpose**: Handles the `/registry` command and processes various subcommands.
   - **Logic**:
     - Retrieves the Neo4j driver.
     - Initializes the `AppRegistry` with the driver.
     - Processes different subcommands:
       - Full audit: Generates a full audit report and sends it in chunks if necessary.
       - Orphan labels: Identifies and lists orphan labels.
       - Cleanup queries: Provides cleanup queries for a specific application.
       - List of applications: Lists all registered applications.
       - Detailed app information: Provides detailed information about a specific application.
     - Closes the Neo4j driver after processing.

3. **_split_message**:
   - **Purpose**: Splits a long message into chunks at newline boundaries to comply with Telegram's character limit.
   - **Logic**: Iterates through the lines of the input text and splits it into chunks, ensuring each chunk does not exceed the specified maximum length.

### Conclusion
The `registry_handler.py` file is a crucial component of the Mythos system, providing detailed and interactive registry management through the Telegram bot interface. It effectively integrates with Neo4j and handles various commands to provide comprehensive application registry information.
