# bin/docs_backfill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 435

---

### File: `bin/docs_backfill.py`

#### Purpose
This script backfills YAML frontmatter into all Markdown files within a specified directory that do not already have frontmatter. It reads the content of each file, sends it to the Ollama API for classification, and injects the generated frontmatter. It also logs all actions taken.

#### Architecture
The script consists of several top-level functions:
- `has_frontmatter`: Checks if a file has YAML frontmatter.
- `read_content`: Reads the first N characters of a file.
- `call_ollama`: Calls the Ollama API to generate frontmatter.
- `parse_yaml_response`: Parses the YAML response from Ollama.
- `validate_and_fix`: Validates and fixes frontmatter values.
- `format_frontmatter`: Formats a metadata dictionary as a YAML frontmatter block.
- `inject_frontmatter`: Injects frontmatter at the top of a file.
- `log_action`: Appends a log entry.
- `main`: The main function that orchestrates the backfill process.

#### Patterns
- **No specific design patterns** are used. The script follows a straightforward procedural approach.

#### Dependencies
- `os`: For file system operations.
- `sys`: For system-specific parameters and functions.
- `json`: For JSON serialization and deserialization.
- `re`: For regular expression operations.
- `argparse`: For parsing command-line arguments.
- `subprocess`: For running external commands (e.g., `curl` to call Ollama API).
- `datetime`: For date and time operations.
- `pathlib`: For path operations.

#### Interfaces
- **Command-line Interface**: The script accepts command-line arguments to specify the directory to scan, whether to perform a dry run, which Ollama model to use, and whether to just list files missing frontmatter.
- **Functions**: The script exposes several functions that can be used independently if needed.

#### Database
- **No direct database interactions**: The script does not interact directly with any database tables or Neo4j labels. However, it references some tables in comments, which might be placeholders or placeholders for future integration.

#### Configuration
- **Environment Variables**: No environment variables are used.
- **Configuration Files**: No configuration files are used.
- **Constants**: Several constants are defined at the top of the script, such as `DOCS_ROOT`, `DEFAULT_MODEL`, `OLLAMA_URL`, `SKIP_DIRS`, `SKIP_FILES`, `MAX_CONTENT_CHARS`, `LOG_FILE`, `VALID_CATEGORIES`, `VALID_STATUSES`, `VALID_STREAMS`, `VALID_AUTHORS`, and `DIR_TO_CATEGORY`.

#### Key Logic
1. **File Scanning**: The script scans a specified directory for Markdown files that do not have frontmatter.
2. **Content Reading**: It reads the first N characters of each file.
3. **Ollama API Call**: It sends the content to the Ollama API to generate frontmatter.
4. **Frontmatter Parsing and Validation**: It parses the YAML response from Ollama and validates the frontmatter values.
5. **Frontmatter Injection**: It injects the frontmatter at the top of the file.
6. **Logging**: It logs all actions taken during the process.

#### Integration Points
- **Ollama API**: The script integrates with the Ollama API to generate frontmatter.
- **File System**: The script interacts with the file system to read and write files.
- **Logging**: The script writes log entries to a log file.

### Detailed Explanation

#### `has_frontmatter(filepath)`
- **Purpose**: Checks if a file already has YAML frontmatter.
- **Logic**: Opens the file and checks if the first line is `---`.

#### `read_content(filepath, max_chars=MAX_CONTENT_CHARS)`
- **Purpose**: Reads the first N characters of a file.
- **Logic**: Opens the file and reads up to `max_chars` characters.

#### `call_ollama(prompt, model=DEFAULT_MODEL)`
- **Purpose**: Calls the Ollama API to generate frontmatter.
- **Logic**: Constructs a payload and uses `subprocess.run` to call the Ollama API via `curl`.

#### `parse_yaml_response(text)`
- **Purpose**: Parses the YAML response from Ollama into a dictionary.
- **Logic**: Uses regular expressions to clean and parse the YAML response.

#### `validate_and_fix(meta, filepath, rel_dir)`
- **Purpose**: Validates frontmatter values and fixes any that are out of spec.
- **Logic**: Ensures that all required fields are present and valid, fixing any issues.

#### `format_frontmatter(meta)`
- **Purpose**: Formats a metadata dictionary as a YAML frontmatter block.
- **Logic**: Constructs a YAML block from the metadata dictionary.

#### `inject_frontmatter(filepath, frontmatter_block, dry_run=False)`
- **Purpose**: Injects frontmatter at the top of a file.
- **Logic**: Reads the file, prepends the frontmatter block, and writes the file back.

#### `log_action(filepath, meta, log_file=LOG_FILE)`
- **Purpose**: Appends a log entry.
- **Logic**: Writes a log entry to the specified log file.

#### `main()`
- **Purpose**: Orchestrates the backfill process.
- **Logic**: Parses command-line arguments, scans the directory for files without frontmatter, processes each file, and logs actions.
