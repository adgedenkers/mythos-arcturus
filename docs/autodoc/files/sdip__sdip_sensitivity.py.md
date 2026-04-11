# sdip/sdip_sensitivity.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 565

---

### File: `sdip/sdip_sensitivity.py`

#### Purpose
This file contains the core logic for scanning text chunks for sensitive content using both regex patterns and Large Language Model (LLM) classification. It processes chunks from a PostgreSQL database, identifies sensitive information, and updates the database with findings.

#### Architecture
The file is organized into several top-level functions:
- `run_regex_scan`: Processes a chunk of text using predefined regex patterns to identify sensitive information.
- `get_highest_level`: Determines the highest sensitivity level from a list of findings.
- `collect_sensitivity_tags`: Collects unique sensitivity type tags from findings.
- `run_llm_scan`: Uses an LLM to classify text chunks for sensitive content.
- `scan_chunks`: Orchestrates the scanning process, deciding whether to use regex, LLM, or both.
- `show_stats`: Displays sensitivity scan results.
- `main`: Entry point for the script.

#### Patterns
- **Factory Pattern**: The `run_llm_scan` function uses a factory-like approach to dynamically select the LLM model.
- **Singleton Pattern**: The `get_db_connection` function likely returns a singleton database connection.

#### Dependencies
- `sys`, `os`, `re`, `json`, `argparse`, `requests`: Standard Python libraries for system operations, regular expressions, JSON handling, argument parsing, and HTTP requests.
- `config`: Custom module for database connection configuration.

#### Interfaces
- **Functions**: Exposes functions for regex scanning (`run_regex_scan`), LLM scanning (`run_llm_scan`), and the main scanning pipeline (`scan_chunks`).
- **Command-line Interface**: The `main` function provides a command-line interface for running scans with various options.

#### Database
- **Tables**: 
  - `datetime`, `config`, `a`, `findings`, `response`, `sdip_chunks`, `sdip_sensitivity`, `chunk`, `sdip_documents`.
- **Operations**: 
  - Reads chunks from `sdip_chunks` and `sdip_documents`.
  - Writes findings to `sdip_sensitivity`.

#### Configuration
- **Environment Variables**: None explicitly used.
- **Config Files**: Uses `get_db_connection` from `config` module, likely for database connection details.

#### Key Logic
- **Regex Scanning**: Uses predefined regex patterns to identify sensitive information in text chunks. Filters out common false positives.
- **LLM Classification**: Sends text chunks to an LLM for classification, parsing the JSON response to extract findings.
- **Sensitivity Level Determination**: Combines findings from regex and LLM to determine the highest sensitivity level for each chunk.

#### Integration Points
- **Database**: Integrates with PostgreSQL to fetch chunks and store findings.
- **LLM Service**: Integrates with an LLM service (Ollama) via HTTP requests.
- **Command-line Interface**: Integrates with the command-line for user interaction and configuration.

### Detailed Analysis

#### `run_regex_scan`
- **Purpose**: Scans a chunk of text using predefined regex patterns to identify sensitive information.
- **Logic**: Iterates over predefined patterns, matches them against the text, and filters out false positives. Returns a list of findings with details like type, pattern name, detected pattern, level, and confidence.

#### `get_highest_level`
- **Purpose**: Determines the highest sensitivity level from a list of findings.
- **Logic**: Iterates over findings, compares sensitivity levels using a predefined order, and returns the highest level.

#### `collect_sensitivity_tags`
- **Purpose**: Collects unique sensitivity type tags from findings.
- **Logic**: Extracts `sensitivity_type` from each finding and returns a list of unique tags.

#### `run_llm_scan`
- **Purpose**: Uses an LLM to classify text chunks for sensitive content.
- **Logic**: Sends text chunks to an LLM via HTTP request, parses the JSON response, and extracts findings. Filters out low-confidence findings.

#### `scan_chunks`
- **Purpose**: Orchestrates the scanning process, deciding whether to use regex, LLM, or both.
- **Logic**: Fetches chunks from the database, processes them using regex and/or LLM, and updates the database with findings. Supports various scanning modes (full, regex-only, LLM-only, specific document).

#### `show_stats`
- **Purpose**: Displays sensitivity scan results.
- **Logic**: Likely queries the database for findings and prints statistics.

#### `main`
- **Purpose**: Entry point for the script, providing a command-line interface for running scans.
- **Logic**: Parses command-line arguments, calls `scan_chunks` with appropriate parameters, and handles user interaction.

### Summary
This file is the core of the SDIP Sensitivity Scanner, providing a robust mechanism for identifying sensitive content in text chunks using both regex and LLM classification. It integrates with a PostgreSQL database for data storage and retrieval, and provides a flexible command-line interface for running scans with various options.
