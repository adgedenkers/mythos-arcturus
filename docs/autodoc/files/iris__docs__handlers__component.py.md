# iris/docs/handlers/component.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 90

---

### File: `iris/docs/handlers/component.py`

#### Purpose
This file contains functions to process documentation generation tasks for components in the Mythos system. It interacts with a PostgreSQL database to retrieve file metadata and uses a language model (LLM) to generate markdown documentation.

#### Architecture
- **Functions**:
  - `handle(task, dry_run=False)`: Processes a component documentation task, retrieves file metadata, generates documentation using an LLM, and writes the output to a file.
  - `_get_component_files(component)`: Retrieves file metadata from the latest introspection run stored in the PostgreSQL database.
- **Data Flow**:
  1. The `handle` function is called with a task and an optional `dry_run` flag.
  2. It retrieves file metadata using `_get_component_files`.
  3. If no metadata is found, it uses task data.
  4. It builds a prompt for the LLM and calls the LLM to generate content.
  5. It writes the generated content to a markdown file.

#### Patterns
- **Singleton**: The `logger` object is a singleton instance of the logging module.
- **Factory**: The `build_component_prompt` function can be seen as a factory method that constructs the prompt for the LLM.

#### Dependencies
- **Imports**: `os`, `json`, `logging`, `psycopg2`
- **Internal Imports**: `call_llm`, `build_component_prompt` from `iris.docs.llm`

#### Interfaces
- **Exposed Functions**:
  - `handle(task, dry_run=False)`: Processes a component documentation task.
  - `_get_component_files(component)`: Retrieves file metadata from the latest introspection run.

#### Database
- **PostgreSQL Tables**:
  - `introspection_runs`: Stores information about introspection runs.
  - `system_manifest`: Stores file metadata for each component in the latest introspection run.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Constants**:
  - `DOCS_DIR`: Path where generated documentation files are stored (`/opt/mythos/docs/generated/components`).

#### Key Logic
- **Retrieving File Metadata**:
  - `_get_component_files` queries the `introspection_runs` and `system_manifest` tables to get the latest file metadata for a given component.
- **Generating Documentation**:
  - `handle` builds a prompt using `build_component_prompt` and calls the LLM (`call_llm`) to generate the documentation content.
- **Writing Documentation**:
  - `handle` writes the generated content to a markdown file in the `DOCS_DIR` directory.

#### Integration Points
- **LLM Integration**:
  - `call_llm`: Calls the LLM to generate documentation content.
- **Database Integration**:
  - `psycopg2`: Connects to the PostgreSQL database to retrieve file metadata.
- **Task Queue Integration**:
  - The `handle` function processes tasks from a queue, likely part of a larger task management system within Mythos.

### Summary
This file is responsible for generating component documentation by retrieving file metadata from a PostgreSQL database and using an LLM to produce markdown files. It integrates with the Mythos system's task queue and database infrastructure to ensure that documentation is up-to-date and accurate.
