# core/convergence.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 306

---

### File: `core/convergence.py`

#### Purpose
The `convergence.py` file is responsible for synthesizing research results from various nodes into a structured context package that can be injected into the main model's system prompt. It also includes a stub for dispatching data to an asynchronous processing grid for further analysis.

#### Architecture
The file consists of several top-level functions:
- `_format_neo4j_results`: Formats Neo4j results into natural language.
- `_format_pg_results`: Formats PostgreSQL results into natural language, with node-specific formatting.
- `_estimate_tokens`: Estimates the number of tokens in a given text.
- `build_context_package`: Builds the context package from research results.
- `dispatch_to_grid`: Dispatches data to the Arcturian Grid for unconscious processing.
- `sort_key`: A helper function for sorting results.

The file uses logging for informational messages and imports `json` and `logging`.

#### Patterns
- **Helper Functions**: `_format_neo4j_results` and `_format_pg_results` are helper functions used by `build_context_package`.
- **Stubbing**: `dispatch_to_grid` is a stub function that will be expanded in future phases.

#### Dependencies
- `json`
- `logging`
- `typing`
- `datetime`

#### Interfaces
- `build_context_package`: Exposes a function to build a context package from research results.
- `dispatch_to_grid`: Exposes a function to dispatch data to the Arcturian Grid for further processing.

#### Database
- **PostgreSQL**: References multiple tables including `accounts`, `recurring_bills`, `transactions`, `calendar_events`, `routines`, `checkin_log`, `people`, `life_events`, and `chat_messages`.
- **Neo4j**: References results from Neo4j queries.

#### Configuration
- `MAX_CONTEXT_TOKENS`: Maximum tokens for the entire research context block.
- `CHARS_PER_TOKEN`: Rough estimate of characters per token.

#### Key Logic
- **Context Package Construction**: `build_context_package` constructs a context package by formatting results from Neo4j and PostgreSQL, ensuring token budget constraints are met.
- **Token Estimation**: `_estimate_tokens` calculates the number of tokens in a text.
- **Result Formatting**: `_format_neo4j_results` and `_format_pg_results` format raw data into natural language.

#### Integration Points
- **Research Results**: Integrates with the research phase to gather and format results.
- **Main Model Prompt**: Injects the context package into the main model's system prompt.
- **Arcturian Grid**: Dispatches data to the Arcturian Grid for unconscious processing, currently a stub.

### Detailed Analysis

#### `_format_neo4j_results`
- **Purpose**: Formats Neo4j results into natural language.
- **Parameters**: `results` (List[Dict])
- **Logic**: Iterates over the first 5 results, extracting labels, names, and details, and formats them into a list of strings.

#### `_format_pg_results`
- **Purpose**: Formats PostgreSQL results into natural language, with node-specific formatting.
- **Parameters**: `results` (List[Dict]), `node_name` (str)
- **Logic**: Groups results by table and formats them based on the table type. Handles specific tables like `accounts`, `recurring_bills`, `transactions`, etc., with custom formatting.

#### `_estimate_tokens`
- **Purpose**: Estimates the number of tokens in a given text.
- **Parameters**: `text` (str)
- **Logic**: Divides the length of the text by the estimated characters per token.

#### `build_context_package`
- **Purpose**: Builds the context package from research results.
- **Parameters**: `node_results` (List[Dict]), `research_plan` (Dict), `max_tokens` (int)
- **Logic**: Constructs a context package by formatting Neo4j and PostgreSQL results, ensuring the total length does not exceed the token budget. Sorts results by priority and data availability, and formats them into a structured text block.

#### `dispatch_to_grid`
- **Purpose**: Dispatches data to the Arcturian Grid for unconscious processing.
- **Parameters**: `message` (str), `response` (str), `node_results` (List[Dict]), `research_plan` (Dict), `chat_id` (int), `telegram_id` (int)
- **Logic**: Logs that the grid received data and is currently a stub. Future plans include dispatching to Redis streams for asynchronous processing.

#### `sort_key`
- **Purpose**: Helper function for sorting results.
- **Parameters**: `r` (Dict)
- **Logic**: Sorts results based on whether they are from the priority node and whether they have data.

### Summary
The `convergence.py` file is a crucial component of the Mythos system, responsible for synthesizing research results into a context package for the main model and dispatching data for unconscious processing. It integrates with PostgreSQL and Neo4j databases and uses logging for informational purposes. The file is designed to be extensible, with a stub for future asynchronous processing capabilities.
