# workers/subject_worker.py

**Language:** python
**Stream:** SYS
**Module:** Background Workers
**Lines:** 230

---

### Documentation for `workers/subject_worker.py`

#### Purpose
This file contains the logic for enriching subject points in the Mythos system. It processes assignments from a Redis stream, extracts refined subject summaries and tags using a small LLM, generates embedding vectors, and updates the corresponding records in the PostgreSQL database.

#### Architecture
The file consists of several top-level functions:
- `get_db`: Establishes a connection to the PostgreSQL database.
- `get_embed_model`: Lazy-loads the sentence transformer model for generating embeddings.
- `process_subject`: Main function that processes a subject enrichment assignment.
- `_extract_subject_llm`: Uses a small LLM to extract a refined subject summary and tags.
- `_update_subject_point`: Updates a subject point with LLM-enriched data.
- `_update_subject_vector`: Updates a subject point with its embedding vector.

#### Patterns
- **Lazy Initialization**: The `get_embed_model` function uses lazy initialization to load the sentence transformer model only when needed.
- **Error Handling**: Each function includes comprehensive error handling to log issues and ensure database transactions are rolled back on failure.

#### Dependencies
- `os`: For environment variable handling.
- `json`: For JSON parsing.
- `logging`: For logging.
- `psycopg2`: For PostgreSQL database operations.
- `requests`: For making HTTP requests to the LLM service.
- `dotenv`: For loading environment variables from a `.env` file.
- `sentence_transformers`: For generating embeddings.

#### Interfaces
- **Exposed Functions**:
  - `process_subject`: Processes a subject enrichment assignment.
  - `get_db`: Establishes a connection to the PostgreSQL database.
  - `get_embed_model`: Lazy-loads the sentence transformer model.

#### Database
- **Tables/Labels**:
  - `conversation_subject_points`: Table where subject points are updated with enriched data and embedding vectors.
  - `information_schema.columns`: Used to check if the `subject_vector` column exists in the `conversation_subject_points` table.

#### Configuration
- **Environment Variables**:
  - `OLLAMA_HOST`: Host for the LLM service.
  - `SUBJECT_EXTRACTION_MODEL`: Model used for subject extraction.
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: PostgreSQL database connection details.

#### Key Logic
- **LLM Subject Extraction**: Uses a small LLM to extract a refined subject summary, tags, tone, and energy level from the message text.
- **Embedding Generation**: Generates an embedding vector for the message text using the sentence transformer model.
- **Database Updates**: Updates the `conversation_subject_points` table with the extracted subject summary, tags, tone, energy level, and embedding vector.

#### Integration Points
- **Redis Stream**: Consumes assignments from the `mythos:assignments:subject` Redis stream.
- **LLM Service**: Makes HTTP requests to the LLM service to extract subject summaries and tags.
- **PostgreSQL Database**: Updates the `conversation_subject_points` table with enriched data and embedding vectors.

### Detailed Function Descriptions

#### `get_db`
- **Purpose**: Establishes a connection to the PostgreSQL database.
- **Parameters**: None.
- **Returns**: A `psycopg2` database connection object.

#### `get_embed_model`
- **Purpose**: Lazy-loads the sentence transformer model for generating embeddings.
- **Parameters**: None.
- **Returns**: The loaded sentence transformer model or `None` if loading fails.

#### `process_subject`
- **Purpose**: Processes a subject enrichment assignment.
- **Parameters**: `assignment` (Dict[str, Any]): The assignment payload.
- **Returns**: A dictionary indicating the status and enrichments applied.

#### `_extract_subject_llm`
- **Purpose**: Uses a small LLM to extract a refined subject summary and tags.
- **Parameters**: `message_text` (str): The message text to analyze.
- **Returns**: A dictionary containing the extracted summary, tags, tone, and energy level, or `None` if extraction fails.

#### `_update_subject_point`
- **Purpose**: Updates a subject point with LLM-enriched data.
- **Parameters**: `point_id` (int): The ID of the subject point. `enrichment` (Dict): The enrichment data.
- **Returns**: None.

#### `_update_subject_vector`
- **Purpose**: Updates a subject point with its embedding vector.
- **Parameters**: `point_id` (int): The ID of the subject point. `vector` (list): The embedding vector.
- **Returns**: None.

### Example Usage
```python
assignment = {
    "point_id": 123,
    "message_text": "the original message",
    "chat_id": 456,
    "role": "user"
}

result = process_subject(assignment)
print(result)
```

This file is a critical component of the Mythos system, responsible for enriching subject points with refined summaries, tags, and embedding vectors, enhancing the system's ability to perform similarity matching and emotional tone analysis.
