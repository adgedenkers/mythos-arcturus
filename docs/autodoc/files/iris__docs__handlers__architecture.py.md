# iris/docs/handlers/architecture.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 86

---

### File: `iris/docs/handlers/architecture.py`

#### Purpose
This file contains the logic to process architecture documentation tasks, generating Markdown files for each component in the Mythos system.

#### Architecture
The file consists of two primary functions:
1. `handle(task, dry_run=False)`: Processes an architecture documentation task and generates a Markdown file.
2. `_get_component_files(component)`: Retrieves file metadata for a given component from the latest introspection run.

#### Patterns
- **Helper Function**: `_get_component_files` is a helper function used within `handle` to fetch necessary data.
- **Logging**: Extensive use of logging to track the progress and errors during the documentation generation process.

#### Dependencies
- **Standard Libraries**: `os`, `json`, `logging`
- **External Libraries**: `psycopg2` for PostgreSQL database interactions
- **Internal Modules**: `iris.docs.llm` for calling the LLM and building prompts

#### Interfaces
- **Public Interface**: `handle(task, dry_run=False)` is the main entry point for processing tasks.
- **Private Interface**: `_get_component_files(component)` is used internally by `handle`.

#### Database
- **PostgreSQL Tables**: 
  - `introspection_runs`: Stores information about introspection runs.
  - `system_manifest`: Contains file metadata for each component.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Constants**: `DOCS_DIR` is set to `"/opt/mythos/docs/generated/architecture"`.

#### Key Logic
1. **Task Handling**:
   - The `handle` function processes a task by fetching file metadata, building a prompt, and calling the LLM to generate content.
   - If `dry_run` is `True`, it logs the intended actions without writing to the file system.
2. **Database Interaction**:
   - `_get_component_files` connects to the PostgreSQL database to retrieve file metadata for the specified component from the latest completed introspection run.
   - It handles exceptions and ensures the database connection is closed.

#### Integration Points
- **LLM Integration**: The `handle` function uses `call_llm` and `build_architecture_prompt` from `iris.docs.llm` to generate the content.
- **File System**: Writes the generated Markdown content to the file system under `DOCS_DIR`.
- **Database**: Interacts with PostgreSQL to fetch necessary metadata for generating the documentation.

### Detailed Analysis

#### `handle(task, dry_run=False)`
- **Purpose**: Processes an architecture documentation task and generates a Markdown file.
- **Parameters**:
  - `task`: A dictionary containing the task details, including the component name and purpose.
  - `dry_run`: A boolean indicating whether to perform a dry run (log actions without writing files).
- **Flow**:
  1. Logs the start of the task.
  2. Ensures the output directory exists.
  3. Retrieves file metadata using `_get_component_files`.
  4. Builds a prompt using `build_architecture_prompt` and calls the LLM to generate content.
  5. Writes the generated content to a Markdown file in `DOCS_DIR`.
  6. Logs the completion or failure of the task.

#### `_get_component_files(component)`
- **Purpose**: Retrieves file metadata for a given component from the latest completed introspection run.
- **Parameters**:
  - `component`: The name of the component for which to retrieve metadata.
- **Flow**:
  1. Connects to the PostgreSQL database.
  2. Fetches the latest completed introspection run ID.
  3. Retrieves file metadata for the specified component from the `system_manifest` table.
  4. Handles exceptions and ensures the database connection is closed.
  5. Returns the file metadata as a list of dictionaries.

### Summary
The `architecture.py` file is responsible for generating architecture documentation for components in the Mythos system. It interacts with the PostgreSQL database to fetch file metadata and uses an LLM to generate the content, which is then written to the file system. The file is designed to be robust, with extensive logging and error handling to ensure reliable documentation generation.
