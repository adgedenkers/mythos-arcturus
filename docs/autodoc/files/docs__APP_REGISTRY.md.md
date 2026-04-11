# docs/APP_REGISTRY.md

**Language:** markdown
**Stream:** SYS
**Module:** Documentation
**Lines:** 509

---

### Documentation for `docs/APP_REGISTRY.md`

#### Purpose
This markdown file serves as a comprehensive registry for applications and their corresponding Neo4j graph nodes and relationships within the Mythos system. It documents the structure, purpose, and cleanup procedures for each registered application.

#### Architecture
The file is structured as a markdown document with sections for each registered application. Each section includes:
- **Purpose**: Describes the application's function.
- **Source code**: Points to the relevant source code files.
- **Node count**: Provides the number of nodes in the Neo4j graph.
- **Labels and Relationships**: Lists the Neo4j labels and relationships used by the application.
- **Cleanup query**: Provides Cypher queries to count and delete nodes associated with the application.

#### Patterns
This file does not implement any design patterns but serves as a documentation and registry pattern, ensuring that all Neo4j nodes and relationships are tracked and managed properly.

#### Dependencies
The file does not import any dependencies directly but references various source code files and Neo4j queries.

#### Interfaces
The file does not expose any interfaces but serves as a reference document for developers and system administrators to understand the Neo4j graph structure and manage nodes and relationships.

#### Database
The file documents the Neo4j graph structure, including labels and relationships for each registered application. It also provides cleanup queries to manage the graph nodes.

#### Configuration
The file does not use any configuration files or environment variables directly but relies on the Neo4j database and the source code files mentioned.

#### Key Logic
The key logic involves documenting and managing the Neo4j graph structure for each application, ensuring that nodes and relationships are correctly registered and can be cleaned up when necessary.

#### Integration Points
This file integrates with the Neo4j database and various source code files within the Mythos system, providing a centralized reference for managing the graph structure.

### Detailed Analysis of Each Registered Application

#### 1. `genealogy` — Genealogical Research Data
- **Purpose**: Manages GEDCOM-imported family tree data.
- **Source code**: Managed via `db_manager.py`.
- **Node count**: ~3,872 nodes.
- **Labels and Relationships**: Includes labels like `GenPerson`, `GenPlace`, `GenFamily`, `GenSurname` and relationships like `PARENT_OF`, `CHILD_OF`, `BORN_IN`, etc.
- **Cleanup query**: Provides Cypher queries to count and delete genealogy nodes.

#### 2. `grid_worker` — Arcturian Grid Processing
- **Purpose**: Processes messages through the grid and stores dimensional analysis results.
- **Source code**: `/opt/mythos/workers/grid_worker.py`.
- **Node count**: ~9 permanent GridNodes + ~100 output nodes per full analysis.
- **Labels and Relationships**: Includes labels like `GridNode`, `Theme`, `AnchorOutput`, `EchoOutput`, etc., and relationships like `HAS_THEME`, `ACTIVATED`, `DISCUSSED`, etc.
- **Cleanup query**: Provides Cypher queries to count and delete grid output nodes.

#### 3. `ontology` — Ontology & Concept System
- **Purpose**: Defines the Mythos vocabulary and knowledge structure.
- **Source code**: `/opt/mythos/core/ontology_seed.py`, `/opt/mythos/api/routes/ontology.py`.
- **Node count**: ~448 nodes.
- **Labels and Relationships**: Includes labels like `OntologyTerm`, `Concept` and relationships like `RELATED_TO`, `DESCRIBES`, `DEFINES`, etc.
- **Cleanup query**: Provides Cypher queries to count and delete ontology nodes.

#### 4. `conversation_logger` — Conversation & Exchange Tracking
- **Purpose**: Logs conversations and message exchanges.
- **Source code**: `/opt/mythos/llm_diagnostics/src/conversation_logger.py`.
- **Node count**: ~169 nodes.
- **Labels and Relationships**: Includes labels like `Exchange`, `Conversation` and relationships like `HAD_CONVERSATION`, `INCLUDES`, `FOLLOWED_BY`, etc.
- **Cleanup query**: Provides Cypher queries to count and delete conversation nodes.

#### 5. `people_manager` — People & Contact Management
- **Purpose**: Manages living contacts and known individuals.
- **Source code**: `/opt/mythos/api/routes/people.py`, `/opt/mythos/api/routes/rolodex.py`.
- **Node count**: ~50 nodes.
- **Labels and Relationships**: Includes labels like `Person`, `PersonOwner` and relationships like `INVOLVES`, `MENTIONED`, `IDENTITY_OF`, etc.
- **Cleanup query**: Provides Cypher queries to count and delete people nodes.

#### 6. `system_monitor` — System Infrastructure Mapping
- **Purpose**: Maps the Arcturus system infrastructure.
- **Source code**: `/opt/mythos/graph_logging/src/system_monitor.py`.
- **Node count**: Not specified.
- **Labels and Relationships**: Not specified in the provided content.
- **Cleanup query**: Not provided in the snippet.

### Summary
This document serves as a critical reference for managing the Neo4j graph structure within the Mythos system, ensuring that all nodes and relationships are properly registered and can be cleaned up when necessary. It integrates with various source code files and the Neo4j database to maintain the integrity of the graph.
