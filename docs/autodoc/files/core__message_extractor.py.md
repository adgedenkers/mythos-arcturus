# core/message_extractor.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 498

---

### File: core/message_extractor.py

#### Purpose
This file contains functions to extract structured data from incoming messages using a small model (qwen2.5:7b). The extracted data includes bill payments, spending, calendar events, task completions, mood, and life events. It also enriches the message context for the main model and commits actions to the database.

#### Architecture
The file consists of several top-level functions:
- `_validate_extracted_date`: Post-processes the extracted date to ensure it aligns with day-of-week references in the original message.
- `_load_knowledge_map`: Loads and caches the knowledge map based on file modification time.
- `_build_dynamic_context`: Builds the dynamic part of the extractor context, including current routines, open tasks, and upcoming calendar events.
- `_build_extractor_prompt`: Constructs the full extractor system prompt, combining the knowledge map and dynamic context.
- `extract`: Runs the extractor on an incoming message and returns a dictionary of extracted actions.
- `format_extraction_for_context`: Formats the extraction result as a context block to be injected into the main model's message.

#### Patterns
- **Singleton Pattern**: `_load_knowledge_map` uses a global cache to ensure the knowledge map is loaded only once and refreshed based on file modification time.
- **Factory Pattern**: `_build_extractor_prompt` and `_build_dynamic_context` act as factories to construct the full prompt and dynamic context, respectively.

#### Dependencies
- `os`: For environment variable access and file operations.
- `json`: For JSON handling.
- `logging`: For logging messages.
- `psycopg2`: For PostgreSQL database operations.
- `re`: For regular expression operations.
- `ollama.Client`: For interacting with the Ollama model.
- `dotenv.load_dotenv`: For loading environment variables from a `.env` file.

#### Interfaces
- `extract(message: str) -> Dict[str, Any]`: Processes an incoming message and returns a dictionary of extracted actions.
- `format_extraction_for_context(extraction: Dict[str, Any]) -> str`: Formats the extraction result as a context block for the main model.

#### Database
The file interacts with several PostgreSQL tables:
- `routines`
- `routine_completions`
- `calendar_events`
- `idea_backlog`
- `recurring_bills`
- `open`
- `an`
- `UPCOMING`
- `the`
- `datetime`
- `calendar_formatter`

#### Configuration
- Environment variables:
  - `EXTRACTOR_MODEL`: Specifies the model to use for extraction (default: `qwen2.5:7b`).
  - `OLLAMA_HOST`: Host address for the Ollama service (default: `http://localhost:11434`).
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`: PostgreSQL database connection parameters.

#### Key Logic
- **Date Validation**: `_validate_extracted_date` ensures the extracted date aligns with day-of-week references in the original message.
- **Dynamic Context Building**: `_build_dynamic_context` queries the database to gather current routines, open tasks, and upcoming calendar events.
- **Prompt Construction**: `_build_extractor_prompt` combines the knowledge map and dynamic context to form the full prompt for the extractor model.

#### Integration Points
- **Message Extraction**: The `extract` function is called to process incoming messages and extract structured data.
- **Context Enrichment**: The `format_extraction_for_context` function enriches the main model's message context with the extracted data.
- **Database Interaction**: The `_build_dynamic_context` function interacts with the PostgreSQL database to gather dynamic context information.
- **Ollama Model**: The `extract` function uses the Ollama model to process the message and extract data.

This file plays a crucial role in the Mythos system by preprocessing messages to extract actionable data, enriching the context for the main model, and ensuring the extracted data is correctly formatted and validated.
