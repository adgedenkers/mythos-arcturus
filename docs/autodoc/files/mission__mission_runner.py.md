# mission/mission_runner.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 791

---

### Purpose
The `mission_runner.py` file is responsible for executing missions defined in YAML files. It gathers context from various sources (files, directories, PostgreSQL, Neo4j, shell commands), renders templates with this context, calls Ollama for processing, validates outputs, and logs diagnostics.

### Architecture
The file consists of a main class `MissionRunner` and several top-level functions for context gathering, template rendering, Ollama interaction, and output parsing. The `MissionRunner` class handles the mission execution lifecycle, while the top-level functions provide utility for specific tasks.

### Patterns
- **Factory Method**: The `gather_context` function acts as a factory method to create context dictionaries based on the mission specification.
- **Singleton**: The `MissionRunner` class can be considered a singleton in the context of a single mission execution, as it is instantiated once per mission.

### Dependencies
- **Imports**: `argparse`, `json`, `logging`, `os`, `re`, `subprocess`, `sys`, `time`, `traceback`, `yaml`, `urllib.request`, `datetime`, `pathlib`, `typing`, `neo4j`
- **Environment Variables**: `OLLAMA_URL`, `NEO4J_USER`, `NEO4J_PASSWORD`

### Interfaces
- **Public Methods**: `MissionRunner.run()`, `MissionRunner.validate_mission()`
- **Top-level Functions**: `read_file_context()`, `list_directory_context()`, `run_postgres_query()`, `run_graph_query()`, `run_shell_command()`, `gather_context()`, `resolve_value()`, `render_template()`, `call_ollama()`, `parse_output()`, `run_validations()`, `gather_dynamic_context()`

### Database
- **PostgreSQL**: Queries are executed using `run_postgres_query()`
- **Neo4j**: Queries are executed using `run_graph_query()`

### Configuration
- **Environment Variables**: `OLLAMA_URL`, `NEO4J_USER`, `NEO4J_PASSWORD`
- **Configuration Files**: `.env` for Neo4j credentials

### Key Logic
- **Context Gathering**: `gather_context()` collects context from files, directories, PostgreSQL, Neo4j, and shell commands.
- **Template Rendering**: `render_template()` replaces placeholders in templates with resolved values.
- **Ollama Interaction**: `call_ollama()` sends prompts to Ollama and processes the response.
- **Output Parsing**: `parse_output()` parses the output from Ollama based on the specified format.
- **Validation**: `run_validations()` checks the mission output against defined validations.

### Integration Points
- **Context Gatherers**: `read_file_context()`, `list_directory_context()`, `run_postgres_query()`, `run_graph_query()`, `run_shell_command()` interact with file systems, PostgreSQL, Neo4j, and shell commands.
- **Ollama API**: `call_ollama()` interacts with Ollama's API to generate responses.
- **Logging**: Uses Python's `logging` module for logging mission execution details.
- **Validation**: `run_validations()` integrates with the mission's validation specifications to ensure correctness.

### Detailed Breakdown

#### Classes
- **MissionRunner**
  - **Methods**:
    - `__init__`: Initializes the mission runner with the mission path and dry run flag.
    - `run`: Executes the full mission and returns `True` on success.
    - `_write_diagnostic`: Writes a diagnostic report on failure.
    - `validate_mission`: Validates the mission YAML without executing.

#### Top-level Functions
- **Context Gatherers**
  - `read_file_context(spec)`: Reads a file and optionally truncates it.
  - `list_directory_context(spec)`: Lists directory contents.
  - `run_postgres_query(spec)`: Runs a PostgreSQL query and returns results.
  - `run_graph_query(spec)`: Runs a Neo4j Cypher query and returns results.
  - `run_shell_command(spec)`: Runs a shell command and returns output.
- **Context Assembly**
  - `gather_context(context_spec)`: Gathers all context defined in the mission file.
- **Template Rendering**
  - `resolve_value(path, data)`: Resolves a dot-path from a nested dictionary.
  - `render_template(template, data)`: Replaces placeholders in a template with resolved values.
- **Ollama Interface**
  - `call_ollama(prompt, model, temperature, system)`: Calls Ollama's generate endpoint and returns the response text.
- **Output Parsing**
  - `parse_output(raw, output_format)`: Parses Ollama output according to the expected format.
- **Validation**
  - `run_validations(validations, phase_data)`: Runs validation checks and returns a tuple of (passed, list_of_errors).

#### Configuration and Environment Variables
- **Environment Variables**:
  - `OLLAMA_URL`: URL for Ollama API.
  - `NEO4J_USER`: Username for Neo4j.
  - `NEO4J_PASSWORD`: Password for Neo4j (loaded from `.env` file).

#### Logging
- Uses Python's `logging` module to log mission execution details.

#### Integration Points
- **File System**: Interacts with files and directories.
- **PostgreSQL**: Executes queries using `sudo` and `psql`.
- **Neo4j**: Connects to Neo4j using the `neo4j` driver.
- **Shell Commands**: Executes shell commands using `subprocess`.
- **Ollama API**: Sends HTTP requests to Ollama's API endpoint.

This documentation provides a comprehensive overview of the `mission_runner.py` file, detailing its purpose, architecture, dependencies, interfaces, and key logic.
