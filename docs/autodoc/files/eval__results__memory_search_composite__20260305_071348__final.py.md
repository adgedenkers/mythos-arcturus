# eval/results/memory_search_composite/20260305_071348/final.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 146

---

### File: eval/results/memory_search_composite/20260305_071348/final.py

#### Purpose
This file contains the `MemorySearchSkill` class, which is responsible for performing a unified memory search across multiple storage types (voice memos, conversations, life events, ideas, documents). It integrates with a router to determine which stores to search and then aggregates the results from each store into a single response.

#### Architecture
- **Class**: `MemorySearchSkill` inherits from `SkillBase` and contains methods for executing the search, running the router, running individual search skills, and merging results.
- **Methods**:
  - `execute`: The main entry point for the skill, which orchestrates the entire search process.
  - `_run_router`: Determines which stores to search based on the input request.
  - `_run_search_skill`: Executes the specific search skill for a given store.
  - `_merge_results`: Combines the results from all executed search skills into a single response.

#### Patterns
- **Factory Pattern**: The `_run_search_skill` method dynamically imports and instantiates the appropriate search skill based on the store name.
- **Composite Pattern**: The `MemorySearchSkill` class acts as a composite that aggregates results from multiple search skills.

#### Dependencies
- **Imports**:
  - `logging`: For logging errors and information.
  - `importlib`: For dynamically importing modules.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response structures for skills.

#### Interfaces
- **Public Methods**:
  - `execute`: Accepts a `SkillRequest` and returns a `SkillResponse`.
- **Private Methods**:
  - `_run_router`: Accepts a `SkillRequest` and returns a dictionary with routing data.
  - `_run_search_skill`: Accepts a store name and a `SkillRequest`, and returns a `SkillResponse`.
  - `_merge_results`: Accepts a dictionary of results and returns a tuple with merged data and summary.

#### Database
- **PostgreSQL Tables**:
  - `engine`: Likely used for storing skill configurations or metadata.
  - `one`: Referenced multiple times, possibly for storing search results or metadata.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Configuration Files**: None explicitly used.

#### Key Logic
- **Routing Logic**: The `_run_router` method dynamically imports and runs the `MemoryRouterSkill` to determine which stores to search based on the input request.
- **Search Execution**: The `_run_search_skill` method dynamically imports and runs the appropriate search skill for each store, handling exceptions and logging errors.
- **Result Aggregation**: The `_merge_results` method combines the results from all executed search skills into a single response, mapping store names to human-friendly labels and summarizing the results.

#### Integration Points
- **Memory Router**: Integrates with the `MemoryRouterSkill` to determine which stores to search.
- **Individual Search Skills**: Dynamically imports and runs specific search skills (`SearchVoiceMemoSkill`, `SearchConversationsSkill`, etc.) for each store.
- **SkillBase**: Inherits from `SkillBase` and uses `SkillRequest` and `SkillResponse` for request handling and response generation.

### Summary
The `MemorySearchSkill` class in `final.py` is designed to provide a unified memory search across multiple storage types. It uses dynamic module importing and exception handling to ensure robust execution and result aggregation. The class integrates with a memory router and individual search skills to provide comprehensive search results, making it a critical component of the Mythos system's memory search functionality.
