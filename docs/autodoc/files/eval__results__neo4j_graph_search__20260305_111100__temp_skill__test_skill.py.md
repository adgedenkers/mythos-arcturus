# eval/results/neo4j_graph_search/20260305_111100/temp_skill/test_skill.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 98

---

### Documentation for `test_skill.py`

#### Purpose
This file defines a skill (`Neo4jGraphSearchSkill`) that performs searches on a Neo4j graph database to find ontology terms and related nodes based on a given search term. The skill is part of the Mythos system and interacts with the Neo4j database to retrieve and summarize relevant information.

#### Architecture
- **Class**: `Neo4jGraphSearchSkill` inherits from `SkillBase`.
- **Methods**:
  - `execute`: The main method that processes the request and orchestrates the search and response building.
  - `_extract_search_term`: Extracts the search term from the request message.
  - `_search_ontology`: Queries the Neo4j database to find ontology terms matching the search term.
  - `_search_nodes`: Queries the Neo4j database to find nodes matching the search term.
  - `_build_summary`: Placeholder method for building a summary of the search results.
- **Top-level Functions**:
  - `_get_driver`: Returns a Neo4j driver instance using environment variables for connection details.

#### Patterns
- **Singleton**: The `_get_driver` function can be considered a singleton pattern as it ensures only one instance of the Neo4j driver is created.
- **Factory**: The `execute` method acts as a factory, creating and returning a `SkillResponse` object based on the search results.

#### Dependencies
- **Imports**:
  - `os`: For environment variable handling.
  - `logging`: For logging exceptions.
  - `dotenv`: For loading environment variables from a `.env` file.
  - `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`: Base classes and request/response structures.
  - `GraphDatabase` from `neo4j`: Neo4j driver for database interactions.

#### Interfaces
- **Exposed Methods**:
  - `execute`: Exposed to other parts of the system for processing search requests.
- **Exposed Classes**:
  - `Neo4jGraphSearchSkill`: Exposed as a skill that can be triggered by specific keywords.

#### Database
- **Neo4j**:
  - **Label**: `OntologyTerm` - Used in the `_search_ontology` method to find ontology terms.
  - **Nodes**: `Person`, `Soul`, `SpiritualConcept` - Used in the `_search_nodes` method to find related nodes.

#### Configuration
- **Environment Variables**:
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for the Neo4j database.
  - `NEO4J_PASSWORD`: Password for the Neo4j database.
- **Config Files**:
  - `.env`: Loaded using `dotenv` to set environment variables.

#### Key Logic
- **Search Term Extraction**: The `_extract_search_term` method cleans and extracts the search term from the request message.
- **Ontology Search**: The `_search_ontology` method queries the Neo4j database to find ontology terms that match the search term.
- **Node Search**: The `_search_nodes` method queries the Neo4j database to find nodes (of types `Person`, `Soul`, `SpiritualConcept`) that match the search term.
- **Response Construction**: The `execute` method constructs a `SkillResponse` object with the search results and a summary.

#### Integration Points
- **Mythos System**: The `Neo4jGraphSearchSkill` class integrates with the Mythos system through the `SkillBase` class, which likely provides a framework for handling skills and requests.
- **Neo4j Database**: The skill interacts with the Neo4j database using the `_get_driver` function to retrieve relevant ontology terms and nodes based on the search term.

### Summary
This file implements a Neo4j graph search skill that extracts a search term from a request, queries the Neo4j database for ontology terms and related nodes, and constructs a response with the search results. It integrates with the Mythos system and uses environment variables for database connection details.
