# iris/introspection/analyzer.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 146

---

### File: `iris/introspection/analyzer.py`

#### Purpose
This file contains functions to analyze individual files and entire components within the Mythos system using an LLM (iris-thinking-v2) via Ollama. It provides summaries, purposes, dependencies, and issues for both files and components.

#### Architecture
The file consists of three main functions:
1. `analyze_file`: Analyzes a single file and returns a detailed analysis.
2. `analyze_component`: Analyzes a group of files (component) and returns a component-level summary.
3. `_empty_analysis`: Returns an empty analysis dictionary when analysis fails.

The functions use the `requests` library to send prompts to the LLM and process the JSON responses.

#### Patterns
- **Helper Function**: `_empty_analysis` is a helper function used to return a default empty analysis when the main functions encounter errors.

#### Dependencies
- **Imports**:
  - `json`: For JSON parsing.
  - `logging`: For logging errors and warnings.
  - `requests`: For making HTTP requests to the LLM.
- **Environment Variables**:
  - `OLLAMA_MODEL`: Specifies the model to use for LLM analysis.

#### Interfaces
- **Exposed Functions**:
  - `analyze_file(file_meta: dict, content: str = None) -> dict`: Analyzes a single file and returns a dictionary with summary, purpose, dependencies, and issues.
  - `analyze_component(component_name: str, file_list: list[dict]) -> dict`: Analyzes a component (group of files) and returns a component-level summary.

#### Database
- **PostgreSQL Tables**:
  - `the`: Not explicitly used in this file.
  - `response`: Not explicitly used in this file.

#### Configuration
- **Environment Variables**:
  - `OLLAMA_MODEL`: Specifies the LLM model to use (default is `qwen3:30b-a3b`).

#### Key Logic
1. **File Analysis (`analyze_file`)**:
   - Reads file content if not provided.
   - Constructs a prompt for the LLM to analyze the file.
   - Sends the prompt to the LLM and processes the JSON response.
   - Handles various exceptions and returns an empty analysis if any step fails.

2. **Component Analysis (`analyze_component`)**:
   - Aggregates summaries from individual file analyses.
   - Constructs a prompt for the LLM to summarize the component.
   - Sends the prompt to the LLM and processes the JSON response.
   - Handles exceptions and returns a default summary if analysis fails.

#### Integration Points
- **Ollama API**: The file interacts with the Ollama API (`http://localhost:11434/api/generate`) to perform LLM analysis.
- **Logging**: Uses the `logging` module to log errors and warnings.
- **File Metadata**: Expects file metadata and content as inputs, which are likely provided by other parts of the Mythos system.

### Summary
The `iris/introspection/analyzer.py` file is crucial for performing LLM-based analysis of files and components within the Mythos system. It leverages the Ollama API to generate summaries, purposes, dependencies, and issues, providing valuable insights into the system's architecture and potential issues.
