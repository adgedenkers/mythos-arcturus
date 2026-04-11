# eval/results/memory_search_composite/20260305_071348/pass04_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 133

---

### Documentation for `pass04_attempt01.py`

#### Purpose
This file implements the `MemorySearchSkill` class, which provides a unified memory search across multiple storage types (voice memos, conversations, life events, ideas, documents). It orchestrates the search process by routing requests to appropriate search skills and merging their results.

#### Architecture
The file contains a single class `MemorySearchSkill` that inherits from `SkillBase`. The class has four methods:
- `execute`: The main entry point that orchestrates the search process.
- `_run_router`: Determines which stores to search based on the request.
- `_run_search_skill`: Executes the search for a specific store.
- `_merge_results`: Combines the results from different stores into a unified response.

Additionally, there are top-level functions that are not directly part of the class but are used for specific tasks.

#### Patterns
- **Factory Method**: The `_run_search_skill` method dynamically imports and instantiates the appropriate search skill based on the store name.
- **Composite Pattern**: The `MemorySearchSkill` class acts as a composite that aggregates results from multiple search skills.

#### Dependencies
- **Imports**: `logging`, `importlib`, `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.
- **External Modules**: Dynamically imports modules and classes based on the `STORE_SKILLS` dictionary.

#### Interfaces
- **Public Methods**: `execute` is the primary method exposed to other parts of the system.
- **Data Structures**: Uses `SkillRequest` and `SkillResponse` for request and response handling.

#### Database
- **PostgreSQL Tables**: The file references the `engine` and `one` tables, though the specific operations on these tables are not detailed within the provided code.

#### Configuration
- **Environment Variables**: No explicit use of environment variables.
- **Configuration Files**: No explicit use of configuration files.

#### Key Logic
1. **Routing**: The `_run_router` method determines which stores to search based on the request.
2. **Dynamic Skill Execution**: The `_run_search_skill` method dynamically imports and runs the appropriate search skill for each store.
3. **Result Merging**: The `_merge_results` method combines the results from different stores into a unified response.

#### Integration Points
- **Memory Router**: Integrates with the `MemoryRouterSkill` to determine which stores to search.
- **Search Skills**: Integrates with various search skills (`SearchVoiceMemoSkill`, `SearchConversationsSkill`, etc.) to perform the actual search operations.
- **SkillBase**: Inherits from `SkillBase` to leverage common skill functionalities.

### Detailed Breakdown

#### `MemorySearchSkill` Class
- **Attributes**:
  - `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`: Metadata about the skill.
  - `STORE_SKILLS`: Dictionary mapping store names to their corresponding search skill modules and classes.

- **Methods**:
  - `execute`: The main method that orchestrates the search process. It first runs the router to determine which stores to search, then executes the search for each targeted store, and finally merges the results.
  - `_run_router`: Determines which stores to search by running the `MemoryRouterSkill`. It dynamically imports the router module and class.
  - `_run_search_skill`: Executes the search for a specific store by dynamically importing the corresponding search skill module and class.
  - `_merge_results`: Combines the results from different stores into a unified response. It maps store names to human-friendly labels and constructs a summary of the results.

#### Top-Level Functions
- **Not Applicable**: The top-level functions listed in the metadata are not part of the class and are not present in the provided code.

#### Database Operations
- **PostgreSQL Tables**: The file references the `engine` and `one` tables, but the specific database operations (queries, updates, etc.) are not detailed within the provided code.

#### Configuration and Environment
- **No Explicit Configuration**: The file does not explicitly use configuration files or environment variables for its operations.

This documentation provides a comprehensive overview of the `MemorySearchSkill` class and its role within the Mythos system, detailing its architecture, dependencies, and integration points.
