# iris/docs/handlers/system_map.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 56

---

### File: `iris/docs/handlers/system_map.py`

#### Purpose
This file contains the logic to process a `system_map` task, which involves generating a system map document based on component data from the latest introspection run. The document is written to a specified directory.

#### Architecture
- **Functions**:
  - `handle(task, dry_run=False)`: Processes the `system_map` task and generates the system map document.
  - `_get_all_components()`: Retrieves component statistics from the latest completed introspection run.
- **Data Flow**:
  1. The `handle` function is called with a task and an optional `dry_run` flag.
  2. It logs the start of the process and creates the necessary directory.
  3. It calls `_get_all_components()` to fetch component data.
  4. If no component data is available, it falls back to using data from the task.
  5. It constructs a prompt for the LLM (Large Language Model) and calls the LLM to generate the content.
  6. The generated content is written to a file in the specified directory.

#### Patterns
- **Singleton**: The `logger` object is a singleton instance of the `logging` module.
- **Factory**: The `call_llm` function acts as a factory for generating content based on the provided prompt.

#### Dependencies
- **Imports**:
  - `os`: For directory operations and file writing.
  - `logging`: For logging messages.
  - `psycopg2`: For database operations.
- **External Functions**:
  - `call_llm(prompt, max_tokens)`: Calls the LLM to generate content.
  - `build_system_map_prompt(components_data)`: Builds the prompt for the LLM based on component data.

#### Interfaces
- **Exposed Functions**:
  - `handle(task, dry_run=False)`: Processes the `system_map` task and returns a tuple `(success, output_path)`.

#### Database
- **PostgreSQL Tables**:
  - `introspection_runs`: Stores introspection run data.
  - `system_manifest`: Stores component manifest data.

#### Configuration
- **Environment Variables**: None.
- **Constants**:
  - `DOCS_DIR`: Path to the directory where the system map document is generated (`/opt/mythos/docs/generated`).

#### Key Logic
- **Component Data Retrieval**:
  - `_get_all_components()` fetches component data from the latest completed introspection run.
  - If no data is available, it falls back to using data from the task.
- **LLM Content Generation**:
  - `handle()` constructs a prompt using `build_system_map_prompt()` and calls `call_llm()` to generate the system map content.
- **File Writing**:
  - The generated content is written to `system_map.md` in the specified directory.

#### Integration Points
- **LLM Integration**:
  - The `call_llm()` function is used to generate the system map content based on the provided prompt.
- **Database Integration**:
  - The `_get_all_components()` function interacts with PostgreSQL to fetch component data from the `introspection_runs` and `system_manifest` tables.
- **Task Queue Integration**:
  - The `handle()` function processes tasks from the `system_map` queue.

### Summary
This file is responsible for generating a system map document based on component data from the latest introspection run. It integrates with the LLM to generate the content and writes it to a file. The file also interacts with the PostgreSQL database to fetch necessary component data.
