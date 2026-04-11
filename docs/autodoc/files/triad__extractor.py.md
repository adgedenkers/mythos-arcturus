# triad/extractor.py

**Language:** python
**Stream:** LOG
**Module:** Triad Identity System
**Lines:** 460

---

### Documentation for `triad/extractor.py`

#### Purpose
The `TriadExtractor` class in `triad/extractor.py` is responsible for extracting three layers (Grid, Akashic, Prophetic) from a conversation using a configured LLM backend. It also provides methods to save the extracted data to a PostgreSQL database.

#### Architecture
The `TriadExtractor` class is the core component of this file. It contains methods for initializing the extractor, connecting to the database, calling the LLM backend, parsing responses, and extracting specific layers from the conversation. The class is designed to be flexible, allowing for different LLM backends and embedding services.

#### Patterns
- **Factory Method Pattern**: The `_call_llm` method acts as a factory method, delegating the call to specific LLM backends (`_call_ollama`, `_call_anthropic`).
- **Singleton Pattern**: The database connection is managed internally, ensuring a single connection per instance.

#### Dependencies
- **Imports**: `hashlib`, `json`, `os`, `psycopg2`, `argparse`, `asyncio`, `httpx`, `anthropic`
- **Environment Variables**: `MYTHOS_DB_URL`, `TRIAD_LLM_BACKEND`, `TRIAD_EMBEDDING_BACKEND`, `OLLAMA_URL`, `TRIAD_OLLAMA_MODEL`, `TRIAD_ANTHROPIC_MODEL`, `TRIAD_EMBEDDING_MODEL`

#### Interfaces
- **Public Methods**: `extract_grid`, `extract_akashic`, `extract_prophetic`, `extract_all`, `save_record`
- **Top-level Functions**: `load_prompt`, `hash_content`, `main`

#### Database
- **Tables**: `triad_conversations`, `triad_grid`, `triad_akashic`, `triad_prophetic`
- **Operations**: Insertion of records into `triad_conversations`, `triad_grid`, `triad_akashic`, and `triad_prophetic` tables.

#### Configuration
- **Environment Variables**: `MYTHOS_DB_URL`, `TRIAD_LLM_BACKEND`, `TRIAD_EMBEDDING_BACKEND`, `OLLAMA_URL`, `TRIAD_OLLAMA_MODEL`, `TRIAD_ANTHROPIC_MODEL`, `TRIAD_EMBEDDING_MODEL`
- **Prompts**: Stored in the `prompts` directory and loaded via `load_prompt`

#### Key Logic
- **LLM Interaction**: The `_call_llm` method dynamically selects the appropriate LLM backend (`_call_ollama` or `_call_anthropic`) based on the configuration.
- **Response Parsing**: Methods `_parse_grid_response`, `_parse_akashic_response`, and `_parse_prophetic_response` parse the JSON responses from the LLM into structured models (`Grid`, `Akashic`, `Prophetic`).
- **Embedding Retrieval**: The `_get_embedding` method retrieves embeddings for text using the configured embedding backend.

#### Integration Points
- **Database**: The `save_record` method integrates with the PostgreSQL database to store the extracted data.
- **LLM Backends**: The `_call_ollama` and `_call_anthropic` methods integrate with the Ollama and Anthropic APIs, respectively.
- **Prompts**: The `load_prompt` function loads prompts from files for use in the extraction process.

### Detailed Breakdown

#### Classes
- **TriadExtractor**
  - **Methods**:
    - `__init__`: Initializes the extractor with database and LLM configurations.
    - `_get_db_connection`: Establishes a database connection.
    - `_call_llm`: Calls the configured LLM backend.
    - `_call_ollama`: Calls the Ollama API for extraction.
    - `_call_anthropic`: Calls the Anthropic API for extraction.
    - `_get_embedding`: Retrieves embeddings for text.
    - `_parse_grid_response`: Parses the LLM response into a `Grid` model.
    - `_parse_akashic_response`: Parses the LLM response into an `Akashic` model.
    - `_parse_prophetic_response`: Parses the LLM response into a `Prophetic` model.
    - `extract_grid`: Extracts the Grid layer from a conversation.
    - `extract_akashic`: Extracts the Akashic layer from a conversation.
    - `extract_prophetic`: Extracts the Prophetic layer from a conversation.
    - `extract_all`: Extracts all three layers from a conversation.
    - `save_record`: Saves a `TriadRecord` to the PostgreSQL database.

#### Top-level Functions
- **load_prompt**: Loads an extraction prompt from a file.
- **hash_content**: Creates a SHA256 hash of conversation content.
- **main**: CLI for testing extraction.
- **_get_db_connection**: Gets a database connection.
- **_call_llm**: Calls the configured LLM backend.
- **_call_ollama**: Calls the Ollama API for extraction.
- **_call_anthropic**: Calls the Anthropic API for extraction.
- **_get_embedding**: Retrieves embeddings for text.
- **_parse_grid_response**: Parses the LLM response into a `Grid` model.
- **_parse_akashic_response**: Parses the LLM response into an `Akashic` model.
- **_parse_prophetic_response**: Parses the LLM response into a `Prophetic` model.
- **extract_grid**: Extracts the Grid layer from a conversation.
- **extract_akashic**: Extracts the Akashic layer from a conversation.
- **extract_prophetic**: Extracts the Prophetic layer from a conversation.
- **extract_all**: Extracts all three layers from a conversation.
- **save_record**: Saves a `TriadRecord` to the PostgreSQL database.

This file is integral to the Mythos system, providing the necessary functionality to extract and store structured data from conversations using various LLM backends.
