# eval/results/memory_search_composite/20260305_071348/pass03_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 113

---

### File: eval/results/memory_search_composite/20260305_071348/pass03_attempt01.py

#### Purpose
This file defines the `MemorySearchSkill` class, which is responsible for performing a unified memory search across multiple storage types (voice memos, conversations, life events, ideas, documents). It integrates with a router to determine which storage types to search and then merges the results from each search into a single response.

#### Architecture
- **Classes**: 
  - `MemorySearchSkill` inherits from `SkillBase` and implements methods to execute the search, run the router, run individual search skills, and merge results.
- **Methods**:
  - `execute`: Main method to execute the memory search.
  - `_run_router`: Runs the memory router to determine which stores to search.
  - `_run_search_skill`: Executes the search for a specific store.
  - `_merge_results`: Merges the results from multiple searches into a single response.
- **Data Flow**:
  - The `execute` method first runs the router to determine the targets.
  - It then runs the search for each target store.
  - Finally, it merges the results and returns a unified response.

#### Patterns
- **Factory Pattern**: Used to dynamically import and instantiate search skills based on the store name.
- **Composite Pattern**: The `MemorySearchSkill` class acts as a composite that aggregates results from multiple search skills.

#### Dependencies
- **Imports**:
  - `logging`: For logging errors.
  - `importlib`: For dynamically importing modules.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response models.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Asynchronous method to execute the memory search.
  - `_run_router`: Asynchronous method to run the memory router.
  - `_run_search_skill`: Asynchronous method to run the search for a specific store.
  - `_merge_results`: Synchronous method to merge the results from multiple searches.

#### Database
- **PostgreSQL Tables**:
  - `engine`: Used for storing engine-related data.
  - `one`: Used multiple times, likely for storing specific search-related data.

#### Configuration
- **Environment Variables**: None explicitly used in this file.
- **Configuration Files**: None explicitly used in this file.

#### Key Logic
- **Router Execution**: The `_run_router` method dynamically imports and runs the `MemoryRouterSkill` to determine which stores to search.
- **Search Execution**: The `_run_search_skill` method dynamically imports and runs the appropriate search skill for each store.
- **Result Merging**: The `_merge_results` method combines the data and summaries from all search results into a single response.

#### Integration Points
- **Memory Router**: Integrates with the `MemoryRouterSkill` to determine which stores to search.
- **Search Skills**: Integrates with various search skills (`SearchVoiceMemoSkill`, `SearchConversationsSkill`, etc.) to perform searches on different types of data.
- **SkillBase**: Inherits from `SkillBase` and uses `SkillRequest` and `SkillResponse` to handle requests and responses.

### Summary
This file implements a composite memory search skill that dynamically integrates with multiple search skills based on the results from a memory router. It handles the execution, routing, searching, and merging of results into a unified response, making use of dynamic imports and error handling to ensure robust operation.
