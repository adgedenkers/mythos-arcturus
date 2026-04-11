# skills/data/memory_search_composite.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 147

---

### Documentation for `skills/data/memory_search_composite.py`

#### Purpose
The `MemorySearchSkill` class in this file is designed to perform a unified memory search across multiple data stores (voice memos, conversations, life events, ideas, documents). It routes the search request to the appropriate stores, collects the results, and merges them into a single response.

#### Architecture
- **Classes**: 
  - `MemorySearchSkill` inherits from `SkillBase`. It contains methods for executing the search (`execute`), running the router (`_run_router`), running individual search skills (`_run_search_skill`), and merging results (`_merge_results`).
- **Functions**: 
  - `execute`: The main entry point for the skill, which orchestrates the entire search process.
  - `_run_router`: Determines which stores to search based on the input request.
  - `_run_search_skill`: Executes the search for a specific store.
  - `_merge_results`: Combines the results from multiple stores into a single response.

#### Patterns
- **Factory Pattern**: The `_run_search_skill` method dynamically imports and instantiates the appropriate search skill based on the store name.
- **Composite Pattern**: The `MemorySearchSkill` class acts as a composite that aggregates results from multiple individual search skills.

#### Dependencies
- **Imports**: 
  - `logging`: For logging errors and information.
  - `importlib`: For dynamically importing modules.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response structures.

#### Interfaces
- **Exposed Methods**: 
  - `execute`: Asynchronous method that takes a `SkillRequest` and returns a `SkillResponse`.
  - `_run_router`, `_run_search_skill`, `_merge_results`: Helper methods used internally by `execute`.

#### Database
- **References**: 
  - The file interacts with PostgreSQL tables named `engine` and `one`, but the exact operations (read/write) are not explicitly detailed in the provided code.

#### Configuration
- **Environment Variables/Config Files**: 
  - No explicit configuration or environment variables are used in this file. The configuration is hardcoded within the class and methods.

#### Key Logic
- **Execution Flow**:
  1. **Routing**: The `_run_router` method determines which stores to search based on the input request.
  2. **Search Execution**: The `_run_search_skill` method dynamically imports and executes the appropriate search skill for each targeted store.
  3. **Result Merging**: The `_merge_results` method combines the results from all stores into a single response.

- **Error Handling**: 
  - Errors are logged, and the system continues to process other stores if an individual store's search fails.

#### Integration Points
- **Mythos Subsystems**:
  - **Memory Router**: The `_run_router` method interacts with the `MemoryRouterSkill` to determine which stores to search.
  - **Individual Search Skills**: The `_run_search_skill` method dynamically imports and executes individual search skills for each store.
  - **PostgreSQL**: The file interacts with PostgreSQL tables, though the exact operations are not detailed in the provided code.

### Summary
The `MemorySearchSkill` class in `memory_search_composite.py` serves as a composite skill that orchestrates memory searches across multiple data stores. It dynamically routes and executes individual search skills, merges their results, and provides a unified response. The class leverages dynamic imports and error handling to ensure robust operation.
