# sdip/sdip_console.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 693

---

### File: `sdip/sdip_console.py`

#### Purpose
This file contains the main console application for the Sovereign Document Intelligence Platform (SDIP), which provides an interactive TUI (Textual User Interface) for browsing documents, chunks, sensitivity findings, and topics. It includes modal screens for viewing document chunks and topic drilldowns.

#### Architecture
The file is structured around three main classes:
1. **`ChunkViewerScreen`**: A modal screen for displaying chunks of a specific document.
2. **`TopicDrilldownScreen`**: A modal screen for showing documents and connections for a specific topic.
3. **`SDIPConsole`**: The main application class that composes the TUI and handles various user interactions and data fetching.

The file also contains several top-level functions for fetching data from PostgreSQL and Neo4j databases.

#### Patterns
- **Factory Method**: Used implicitly in the `SDIPConsole` class for creating and composing different UI elements.
- **Observer Pattern**: The `SDIPConsole` class uses event-driven methods (`on_doc_search`, `on_chunk_search`, etc.) to handle user interactions.

#### Dependencies
- **Imports**: `sys`, `os`, `dotenv`, `textual.app`, `textual.containers`, `textual.widgets`, `textual.binding`, `textual.screen`, `rich.text`, `rich.panel`, `config`, `neo4j`.
- **Database Connections**: Uses `get_db_connection` from `config` for PostgreSQL and `get_neo4j_driver` for Neo4j.

#### Interfaces
- **Public Methods**: 
  - `get_neo4j_driver()`: Returns a Neo4j driver instance.
  - `fetch_stats()`: Fetches document and chunk statistics.
  - `fetch_documents()`: Fetches documents based on search criteria.
  - `fetch_chunks_for_doc()`: Fetches chunks for a specific document.
  - `search_chunks()`: Searches chunks based on a query.
  - `fetch_findings()`: Fetches sensitivity findings.
  - `fetch_hot_documents()`: Fetches documents with high sensitivity levels.
  - `fetch_topics()`: Fetches topics from Neo4j.
  - `fetch_topic_documents()`: Fetches documents covering a specific topic.
  - `fetch_topic_connections()`: Fetches related topics for a given topic.
  - `styled_level()`: Styles a sensitivity level with appropriate color.
  - `main()`: Entry point for the application.

- **Class Methods**:
  - `SDIPConsole.compose()`: Composes the main TUI layout.
  - `SDIPConsole.on_mount()`: Handles initialization logic.
  - `SDIPConsole._load_stats()`: Loads document and chunk statistics.
  - `SDIPConsole._load_documents()`: Loads documents.
  - `SDIPConsole._load_topics()`: Loads topics.
  - `SDIPConsole._load_hot_documents()`: Loads hot documents.
  - `SDIPConsole._load_findings()`: Loads sensitivity findings.
  - `SDIPConsole.on_doc_search()`: Handles document search events.
  - `SDIPConsole.on_chunk_search()`: Handles chunk search events.
  - `SDIPConsole.on_doc_selected()`: Handles document selection events.
  - `SDIPConsole.on_topic_selected()`: Handles topic selection events.
  - `SDIPConsole.action_refresh()`: Refreshes the application state.
  - `SDIPConsole.action_focus_tab()`: Focuses a specific tab.

#### Database
- **PostgreSQL Tables**: `sdip_documents`, `sdip_chunks`, `sdip_sensitivity`.
- **Neo4j Labels**: `SDIPTopic`, `SDIPDocument`, `COVERS_TOPIC`.

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.
- **Configuration File**: `.env` loaded via `dotenv`.

#### Key Logic
- **Data Fetching**: The file contains several functions for fetching data from PostgreSQL and Neo4j databases, including document and chunk statistics, document and chunk details, sensitivity findings, and topic-related data.
- **UI Composition**: The `SDIPConsole` class composes the main TUI layout and handles various user interactions, such as document and chunk searches, document and topic selections, and refreshing the application state.

#### Integration Points
- **PostgreSQL**: The application fetches data from PostgreSQL tables (`sdip_documents`, `sdip_chunks`, `sdip_sensitivity`) for document and chunk details, sensitivity findings, and document statistics.
- **Neo4j**: The application fetches topic-related data from Neo4j, including topics, documents covering specific topics, and related topics.
- **TUI Framework**: The application uses the `textual` framework to create and manage the TUI, including modal screens for viewing document chunks and topic drilldowns.
