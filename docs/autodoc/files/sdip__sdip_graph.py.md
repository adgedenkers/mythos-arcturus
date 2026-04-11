# sdip/sdip_graph.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 635

---

### File: `sdip/sdip_graph.py`

#### Purpose
This file contains functions for building and managing a Neo4j graph database for the SDIP (System Documentation and Information Processing) system. It includes functions for extracting topics and systems from text, detecting cross-references, and creating nodes and relationships in the Neo4j graph.

#### Architecture
The file is organized into several top-level functions that handle different aspects of graph building:
- **Initialization and Constraints**: Functions like `get_neo4j_driver` and `ensure_constraints` handle the setup of the Neo4j driver and creation of constraints.
- **Data Extraction**: Functions like `extract_topics`, `extract_systems`, and `detect_references` extract relevant information from text and document paths.
- **Graph Building**: Functions like `build_document_nodes`, `build_topic_nodes`, `build_system_nodes`, `build_chunk_nodes`, and `build_references` create nodes and relationships in the Neo4j graph based on data from PostgreSQL.
- **Sensitivity Propagation**: The `run_sensitivity_propagation` function propagates sensitivity levels through document references.
- **Graph Management**: Functions like `show_stats` and `clear_graph` provide utilities for managing the graph.
- **Main Pipeline**: The `build_graph` function orchestrates the graph building process, and `main` is the entry point for command-line execution.

#### Patterns
- **Singleton**: The `get_neo4j_driver` function can be considered a singleton pattern, as it ensures a single instance of the Neo4j driver is used throughout the application.
- **Factory**: The `build_*` functions can be seen as factory methods, as they create and return nodes and relationships in the Neo4j graph.

#### Dependencies
- **Standard Libraries**: `sys`, `os`, `re`, `json`, `argparse`, `pathlib`, `collections`.
- **Custom Modules**: `config` for database connection details.
- **Neo4j Driver**: `neo4j` for interacting with the Neo4j database.

#### Interfaces
- **Public Functions**: `get_neo4j_driver`, `ensure_constraints`, `extract_topics`, `extract_systems`, `detect_references`, `build_document_nodes`, `build_topic_nodes`, `build_system_nodes`, `build_chunk_nodes`, `build_references`, `run_sensitivity_propagation`, `show_stats`, `clear_graph`, `build_graph`, `main`.
- **Entry Point**: `main` function for command-line execution.

#### Database
- **PostgreSQL Tables**: `sdip_documents`, `sdip_chunks`.
- **Neo4j Labels**: `SDIPDocument`, `SDIPTopic`, `SDIPSystem`, `SDIPChunk`.
- **Neo4j Relationships**: `COVERS_TOPIC`, `DESCRIBES_SYSTEM`, `REFERENCES`, `HAS_CHUNK`, `SENSITIVITY_SPREAD`.

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` for Neo4j connection details.
- **Custom Configuration**: `config` module for database connection details.

#### Key Logic
- **Topic Extraction**: Uses predefined keyword mappings to extract topics from text and file paths.
- **System Extraction**: Uses predefined keyword mappings to extract system references from text.
- **Reference Detection**: Uses regular expressions to detect cross-references in document text.
- **Graph Building**: Constructs nodes and relationships in Neo4j based on data from PostgreSQL, ensuring uniqueness constraints and propagating sensitivity levels.

#### Integration Points
- **PostgreSQL**: Fetches document and chunk data from `sdip_documents` and `sdip_chunks` tables.
- **Neo4j**: Creates and manages nodes and relationships in the Neo4j graph.
- **Command-Line Interface**: Provides options to build the graph, show statistics, and manage the graph data.

### Detailed Function Descriptions

1. **`get_neo4j_driver`**
   - **Purpose**: Initializes and returns a Neo4j driver instance.
   - **Dependencies**: `neo4j` module.
   - **Usage**: Singleton pattern to ensure a single Neo4j driver instance.

2. **`ensure_constraints`**
   - **Purpose**: Ensures uniqueness constraints for SDIP nodes in Neo4j.
   - **Dependencies**: `get_neo4j_driver`.
   - **Usage**: Called during graph initialization to set up constraints.

3. **`extract_topics`**
   - **Purpose**: Extracts topic labels from text content and file paths.
   - **Dependencies**: `TOPIC_KEYWORDS` dictionary.
   - **Usage**: Used in graph building to categorize documents.

4. **`extract_systems`**
   - **Purpose**: Extracts system/service references from text.
   - **Dependencies**: `SYSTEM_KEYWORDS` dictionary.
   - **Usage**: Used in graph building to identify systems described in documents.

5. **`detect_references`**
   - **Purpose**: Detects cross-references to other documents.
   - **Dependencies**: Regular expressions.
   - **Usage**: Used in graph building to create `REFERENCES` relationships.

6. **`build_document_nodes`**
   - **Purpose**: Creates `SDIPDocument` nodes from PostgreSQL data.
   - **Dependencies**: PostgreSQL connection, Neo4j driver.
   - **Usage**: Part of the main graph building pipeline.

7. **`build_topic_nodes`**
   - **Purpose**: Creates `SDIPTopic` nodes and `COVERS_TOPIC` relationships.
   - **Dependencies**: PostgreSQL connection, Neo4j driver, `extract_topics`.
   - **Usage**: Part of the main graph building pipeline.

8. **`build_system_nodes`**
   - **Purpose**: Creates `SDIPSystem` nodes and `DESCRIBES_SYSTEM` relationships.
   - **Dependencies**: PostgreSQL connection, Neo4j driver, `extract_systems`.
   - **Usage**: Part of the main graph building pipeline.

9. **`build_chunk_nodes`**
   - **Purpose**: Creates `SDIPChunk` nodes for sensitive chunks and links them to documents.
   - **Dependencies**: PostgreSQL connection, Neo4j driver.
   - **Usage**: Part of the main graph building pipeline.

10. **`build_references`**
    - **Purpose**: Detects and creates `REFERENCES` relationships between documents.
    - **Dependencies**: PostgreSQL connection, Neo4j driver, `detect_references`.
    - **Usage**: Part of the main graph building pipeline.

11. **`run_sensitivity_propagation`**
    - **Purpose**: Propagates sensitivity levels through document references.
    - **Dependencies**: Neo4j driver.
    - **Usage**: Ensures that sensitivity levels are correctly propagated in the graph.

12. **`show_stats`**
    - **Purpose**: Shows statistics about the SDIP graph.
    - **Dependencies**: Neo4j driver.
    - **Usage**: Provides insights into the graph structure.

13. **`clear_graph`**
    - **Purpose**: Removes all SDIP nodes and relationships from the graph.
    - **Dependencies**: Neo4j driver.
    - **Usage**: Used for resetting the graph.

14. **`build_graph`**
    - **Purpose**: Main graph building pipeline.
    - **Dependencies**: All other `build_*` functions.
    - **Usage**: Orchestrates the graph building process.

15. **`main`**
    - **Purpose**: Entry point for command-line execution.
    - **Dependencies**: All other functions.
    - **Usage**: Provides command-line options for building and managing the graph.
