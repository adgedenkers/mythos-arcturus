# core/research_router.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 272

---

### Documentation for `core/research_router.py`

#### Purpose
The `research_router.py` file is responsible for routing user messages to the appropriate research nodes based on the context of the conversation and the content of the message. It constructs a research plan that guides the system on which data to gather before responding to the user.

#### Architecture
The file contains several functions that work together to build and execute the research plan:
- `_build_node_descriptions`: Constructs a string describing the grid nodes.
- `_build_segment_context`: Builds a context string from the current conversation segment.
- `get_segment_context`: Retrieves the current conversation segment from the PostgreSQL database.
- `route_message`: The main function that routes the message and generates the research plan.
- `_empty_plan`: Returns an empty research plan when no research is needed.

#### Patterns
- **Singleton**: The `Client` from the `ollama` module is used as a singleton to interact with the Ollama service.
- **Factory**: The `route_message` function acts as a factory for generating research plans based on the input message and context.

#### Dependencies
- **Standard Libraries**: `os`, `sys`, `json`, `logging`, `re`
- **External Libraries**: `psycopg2`, `ollama`, `dotenv`

#### Interfaces
- **Public Functions**:
  - `route_message(message: str, chat_id: int, telegram_id: int, segment_override: Optional[Dict] = None) -> Dict[str, Any]`: Routes a message and returns a research plan.
  - `get_segment_context(chat_id: int) -> Optional[Dict]`: Retrieves the current conversation segment from the database.

#### Database
- **PostgreSQL Tables**:
  - `conversation_segments`: Used to fetch the current conversation segment.

#### Configuration
- **Environment Variables**:
  - `OLLAMA_ROUTER_MODEL`: Model name for the router.
  - `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: PostgreSQL database connection details.
  - `OLLAMA_HOST`: Host for the Ollama service.

#### Key Logic
1. **Building Context**:
   - `_build_node_descriptions` constructs a string describing the grid nodes.
   - `_build_segment_context` builds a context string from the current conversation segment.
   - `get_segment_context` retrieves the current conversation segment from the PostgreSQL database.

2. **Routing Logic**:
   - `route_message` constructs a system prompt using the built context and node descriptions.
   - It sends the prompt and the user message to the Ollama service to generate a research plan.
   - The response is parsed and validated to ensure it meets the expected structure.

3. **Error Handling**:
   - If the response from the Ollama service is not valid JSON, `_empty_plan` is returned.

#### Integration Points
- **Ollama Service**: The `route_message` function interacts with the Ollama service to generate the research plan.
- **PostgreSQL Database**: The `get_segment_context` function retrieves the current conversation segment from the PostgreSQL database.
- **Grid Nodes**: The `GRID_NODES` dictionary defines the available grid nodes and their domains, which are used to build the system prompt and validate the research plan.

### Summary
The `research_router.py` file is a critical component of the Mythos system, responsible for analyzing user messages and generating a research plan to guide the system on which data to gather before responding. It integrates with the Ollama service and the PostgreSQL database to provide context-aware routing and research planning.
