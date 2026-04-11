# eval/challenges/memory_search_composite/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 76

---

### Documentation for `build_plan.json`

#### Purpose
This JSON file serves as a blueprint for constructing a composite skill named `memory_search_composite`. It outlines the steps and logic required to integrate multiple memory search skills into a unified memory search functionality.

#### Architecture
The file is structured as a JSON object with several key sections:
- **plan_id**: Identifies the plan.
- **version**: Specifies the version of the plan.
- **description**: Describes the purpose of the composite skill.
- **pattern**: Indicates the type of skill pattern (composite_skill).
- **model_hint**: Suggests the model to use for the skill.
- **context**: Contains system context and scaffold details.
- **mandatory_patterns**: Lists mandatory patterns and guidelines for the skill.
- **build_plan**: Outlines the step-by-step instructions for building the skill.
- **test_cases**: Provides test cases to validate the skill's functionality.

#### Patterns
- **Composite Pattern**: The skill combines multiple memory search skills into a single composite skill.
- **Factory Pattern**: Used for dynamically importing and instantiating sub-skills based on the `STORE_SKILLS` mapping.

#### Dependencies
- **Imports**: The skill imports `logging`, `importlib`, and `engine.base` for `SkillBase`, `SkillRequest`, and `SkillResponse`.
- **Sub-skills**: The skill dynamically imports and uses sub-skills from the `data` module.

#### Interfaces
- **Public Methods**: The skill exposes the `execute` method, which is the entry point for executing the composite skill.
- **Internal Methods**: 
  - `_run_router`: Runs the memory router to determine which stores to search.
  - `_run_search_skill`: Runs the specific search skill for a given store.
  - `_merge_results`: Merges the results from all search skills into a unified response.

#### Database
- **No Direct Database Access**: The skill does not directly interact with the database. It relies on sub-skills that may interact with the database.

#### Configuration
- **Environment Variables**: No explicit environment variables are used.
- **System Context**: The `context` section provides system-level configuration such as database details and virtual environment paths.

#### Key Logic
- **Memory Router**: Determines which memory stores to search based on the input request.
- **Sub-skill Execution**: Dynamically imports and executes sub-skills for each memory store.
- **Result Merging**: Combines the results from all executed sub-skills into a unified response.

#### Integration Points
- **Memory Router Skill**: The skill integrates with the `MemoryRouterSkill` to determine which memory stores to search.
- **Sub-skills**: The skill integrates with multiple sub-skills (`SearchVoiceMemoSkill`, `SearchConversationsSkill`, `SearchLifeEventsSkill`, `SearchIdeasSkill`, `SearchDocumentsSkill`) to perform the actual memory searches.

### Detailed Breakdown of Build Plan

#### Pass 1: Skeleton
- **Instruction**: Write the complete file skeleton, including necessary imports and the `MemorySearchSkill` class with all attributes and methods.
- **Test**: `parse_check` to ensure the file parses correctly.

#### Pass 2: Implement `_run_router`
- **Instruction**: Implement the `_run_router` method to dynamically import and run the `MemoryRouterSkill`.
- **Test**: `parse_check` to ensure the method parses correctly.

#### Pass 3: Implement `_run_search_skill`
- **Instruction**: Implement the `_run_search_skill` method to dynamically import and run the specific search skill for a given store.
- **Test**: `parse_check` to ensure the method parses correctly.

#### Pass 4: Implement `_merge_results`
- **Instruction**: Implement the `_merge_results` method to combine the results from all executed sub-skills into a unified response.
- **Test**: `parse_check` to ensure the method parses correctly.

#### Pass 5: Implement `execute`
- **Instruction**: Implement the `execute` method to orchestrate the entire process: running the router, executing sub-skills, and merging results.
- **Test**: `import_check` to ensure the method imports and executes correctly.

#### Pass 6: Final Review
- **Instruction**: Review the complete file to ensure it adheres to all guidelines and is production-ready.
- **Test**: `full_behavioral` to ensure the skill behaves as expected in all scenarios.

### Test Cases
- **Test Case 1**: Input: "do you remember anything about love", Expected: Successful execution with data containing `stores_searched` and summary containing "Voice Memo" and "Conversation".
- **Test Case 2**: Input: "search everything for emerald flame", Expected: Successful execution with data containing `stores_searched`.
- **Test Case 3**: Input: "what do you remember", Expected: Successful execution.

This JSON file serves as a comprehensive guide for developing the `memory_search_composite` skill, ensuring it integrates multiple memory search functionalities into a unified and robust solution.
