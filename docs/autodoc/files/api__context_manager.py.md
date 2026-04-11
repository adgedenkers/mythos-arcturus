# api/context_manager.py

**Language:** python
**Stream:** SYS
**Module:** FastAPI Gateway
**Lines:** 601

---

### File: api/context_manager.py

#### Purpose
The `ContextManager` class in `context_manager.py` is responsible for assembling a multi-tier context window for conversations in the Mythos system. This context includes mode-specific prompts, summaries, recent exchanges, and relevant context retrieved from various sources.

#### Architecture
The `ContextManager` class is designed with a modular approach, where each method handles a specific aspect of context assembly:
- **Initialization**: The `__init__` method initializes the class with database connection functions and optional clients for Neo4j and Qdrant.
- **Context Assembly**: The `assemble_context` method orchestrates the assembly of the context window by calling various helper methods.
- **Helper Methods**: Methods such as `_load_mode_prompt`, `_get_message_count`, `_get_current_summaries`, `_get_recent_exchanges`, `_retrieve_relevant_context`, `_extract_keywords`, `_semantic_search`, `_search_past_conversations`, `_search_neo4j_entities`, `_search_related_photos`, `_estimate_tokens`, and `format_context_for_llm` handle specific tasks related to context assembly.

#### Patterns
- **Dependency Injection**: The `__init__` method uses dependency injection to pass database connection functions and optional clients for Neo4j and Qdrant.
- **Facade Pattern**: The `assemble_context` method acts as a facade, abstracting the complexity of context assembly by calling various helper methods.

#### Dependencies
- **Imports**: The file imports `os`, `logging`, `psycopg2`, `typing`, `pathlib`, `datetime`, and `dotenv`.
- **External Clients**: The class relies on a PostgreSQL database connection function, an optional Neo4j driver, and an optional Qdrant client.

#### Interfaces
- **Public Methods**: The class exposes the `assemble_context` method to other parts of the system, which assembles the complete context window.
- **Helper Methods**: Internal methods such as `_load_mode_prompt`, `_get_message_count`, `_get_current_summaries`, `_get_recent_exchanges`, `_retrieve_relevant_context`, `_extract_keywords`, `_semantic_search`, `_search_past_conversations`, `_search_neo4j_entities`, `_search_related_photos`, `_estimate_tokens`, and `format_context_for_llm` are used internally to build the context.

#### Database
- **PostgreSQL Tables**: The class interacts with the `chat_messages`, `conversation_summaries`, and `media_files` tables to retrieve messages, summaries, and media files.
- **Neo4j**: The class optionally interacts with Neo4j to retrieve relevant entities.
- **Qdrant**: The class optionally interacts with Qdrant for semantic search.

#### Configuration
- **Environment Variables**: The file loads environment variables from a `.env` file using `dotenv`.
- **Constants**: The file defines constants such as `PROMPTS_DIR`, `RECENT_MESSAGES_LIMIT`, `PAST_CONVERSATIONS_LIMIT`, `NEO4J_ENTITIES_LIMIT`, and `RELATED_PHOTOS_LIMIT`.

#### Key Logic
- **Context Assembly**: The `assemble_context` method assembles the context window by calling various helper methods to load mode-specific prompts, retrieve message counts, get summaries, recent exchanges, and relevant context.
- **Keyword Extraction**: The `_extract_keywords` method extracts meaningful keywords from the current message and recent exchanges to facilitate context retrieval.
- **Semantic Search**: The `_semantic_search` method performs semantic search using a pre-trained sentence transformer model and the Qdrant client.
- **Context Retrieval**: The `_retrieve_relevant_context` method dynamically retrieves relevant context from multiple sources, including Qdrant, past conversations, Neo4j entities, and related photos.

#### Integration Points
- **Database Integration**: The class integrates with the PostgreSQL database to retrieve messages, summaries, and media files.
- **Neo4j Integration**: The class optionally integrates with Neo4j to retrieve relevant entities.
- **Qdrant Integration**: The class optionally integrates with Qdrant for semantic search.
- **API Integration**: The `assemble_context` method is likely called by other parts of the Mythos system, such as the FastAPI endpoints, to provide context for LLM interactions.

### Summary
The `ContextManager` class in `context_manager.py` is a crucial component of the Mythos system, responsible for assembling a comprehensive context window for conversations. It integrates with various data sources, including PostgreSQL, Neo4j, and Qdrant, to provide a rich context for LLM interactions. The class is designed to be modular and extensible, with clear separation of concerns and dependency injection for flexibility.
