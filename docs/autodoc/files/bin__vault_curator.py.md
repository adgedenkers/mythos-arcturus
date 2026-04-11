# bin/vault_curator.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 515

---

### File: `bin/vault_curator.py`

#### Purpose
The `vault_curator.py` script ingests a directory of markdown/text files, classifies each file using a local Language Model (LLM) via Ollama, and reorganizes them into a clean output structure. It supports various modes such as dry runs and resuming from previous runs.

#### Architecture
The script consists of several top-level functions that handle different aspects of the file processing pipeline:
- `slugify`: Converts text to a clean filename-safe slug.
- `file_hash`: Generates a SHA-256 hash of file contents.
- `read_file_content`: Reads file content while handling encoding issues.
- `call_ollama`: Sends a prompt to Ollama and parses the JSON response.
- `collect_files`: Walks source directories and collects supported files.
- `classify_file`: Classifies a single file using the LLM.
- `build_output`: Copies files into the new organized structure and returns stats.
- `generate_report`: Writes a classification report as markdown and JSON manifest.
- `main`: Entry point for the script, parses command-line arguments and orchestrates the workflow.

#### Patterns
- **Singleton Pattern**: Not explicitly used, but the script relies on a single instance of the Ollama service.
- **Factory Pattern**: Not used, but the script could be extended to use different models or classification strategies.
- **Observer Pattern**: Not used, but the script could be extended to notify observers of classification progress or errors.

#### Dependencies
- **Standard Libraries**: `argparse`, `hashlib`, `json`, `os`, `shutil`, `sys`, `time`, `re`, `unicodedata`, `requests`
- **External Services**: Ollama (via HTTP requests)

#### Interfaces
- **Command-line Interface**: The script is designed to be run from the command line, accepting source directories and an output directory as arguments.
- **Function Interfaces**: Each function is designed to be self-contained and can be called independently, though they are typically used in sequence within the `main` function.

#### Database
- **PostgreSQL Tables**: The script references several PostgreSQL tables (`a`, `datetime`, `pathlib`, `another`, `response`, `source`, `the`), though these references are not explicitly used in the provided code. They may be part of a larger system or configuration.

#### Configuration
- **Environment Variables**: No explicit environment variables are used.
- **Configuration Constants**: The script uses several constants defined at the top, such as `OLLAMA_URL`, `DEFAULT_MODEL`, `MAX_CONTENT_CHARS`, `SUPPORTED_EXTENSIONS`, `SKIP_DIRS`, `SKIP_FILES`.

#### Key Logic
1. **File Collection**: The `collect_files` function walks through source directories, collects supported files, and generates a list of file metadata.
2. **File Classification**: The `classify_file` function sends file content to Ollama for classification and parses the JSON response.
3. **Output Building**: The `build_output` function organizes and copies files into a new structure based on their classification.
4. **Report Generation**: The `generate_report` function generates a markdown report and a JSON manifest summarizing the classification results.

#### Integration Points
- **Ollama Service**: The script integrates with the Ollama service to classify files.
- **File System**: The script interacts with the file system to read, write, and organize files.
- **PostgreSQL**: The script references PostgreSQL tables, indicating potential integration with a database for storing classification results or metadata.

### Detailed Analysis

#### `slugify`
- **Purpose**: Converts text to a clean filename-safe slug.
- **Logic**: Normalizes the text to ASCII, removes non-alphanumeric characters, and ensures the slug is within 80 characters.

#### `file_hash`
- **Purpose**: Generates a SHA-256 hash of file contents.
- **Logic**: Reads the file in chunks and updates the hash object.

#### `read_file_content`
- **Purpose**: Reads file content while handling encoding issues.
- **Logic**: Opens the file with UTF-8 encoding and reads up to `MAX_CONTENT_CHARS` characters.

#### `call_ollama`
- **Purpose**: Sends a prompt to Ollama and parses the JSON response.
- **Logic**: Sends a POST request to Ollama, parses the JSON response, and handles potential errors.

#### `collect_files`
- **Purpose**: Walks source directories and collects all supported files.
- **Logic**: Walks through directories, skips excluded directories and files, and collects metadata for supported files.

#### `classify_file`
- **Purpose**: Classifies a single file through the LLM.
- **Logic**: Reads file content, constructs a classification prompt, sends it to Ollama, and parses the response.

#### `build_output`
- **Purpose**: Copies files into the new organized structure and returns stats.
- **Logic**: Builds output paths based on classification results, handles name collisions, and copies files to the output directory.

#### `generate_report`
- **Purpose**: Writes a classification report as markdown and JSON manifest.
- **Logic**: Groups files by category, generates markdown and JSON reports summarizing the classification results.

#### `main`
- **Purpose**: Entry point for the script, parses command-line arguments and orchestrates the workflow.
- **Logic**: Parses command-line arguments, collects files, classifies them, builds the output structure, and generates a report.

### Example Usage
```bash
python3 vault_curator.py /path/to/source /path/to/output
python3 vault_curator.py --model qwen2.5:32b /path/to/source /path/to/output
python3 vault_curator.py --dry-run /path/to/source /path/to/output
python3 vault_curator.py --resume /path/to/source /path/to/output
```
