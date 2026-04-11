# eval/results/neo4j_graph_search/20260305_110247/pass06_attempt02.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 164

---

### File: eval/results/neo4j_graph_search/20260305_110247/pass06_attempt02.py

#### Purpose
This file contains a class `Neo4jGraphSearchSkill` that implements a skill for searching an ontology and graph nodes in a Neo4j database based on user queries. It processes the query to extract a search term and then performs searches in the Neo4j database to find matching ontology terms and graph nodes.

#### Architecture
- **Class**: `Neo4jGraphSearchSkill` extends `SkillBase` and contains methods for executing the search, extracting the search term, and performing searches in the ontology and nodes.
- **Methods**:
  - `execute`: The main method that processes the user query, extracts the search term, and performs searches.
  - `_extract_search_term`: Extracts the search term from the query by removing specific triggers and normalizing the text.
  - `_search_ontology`: Searches the Neo4j database for ontology terms matching the search term.
  - `_search_nodes`: Searches the Neo4j database for nodes matching the search term.
- **Top-level Functions**:
  - `_get_driver`: Returns a Neo4j driver instance.
  - `execute`: A top-level function that is likely used for testing or standalone execution.

#### Patterns
- **Singleton**: The `_get_driver` function can be considered a singleton pattern as it returns a single instance of the Neo4j driver.
- **Factory**: The `execute` method acts as a factory for creating `SkillResponse` objects based on the search results.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `dotenv`, `engine.base`, `neo4j`.
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.

#### Interfaces
- **Exposed Methods**: `execute` is the primary method exposed to other parts of the system for executing the search.
- **Responses**: Returns `SkillResponse` objects containing the search results and a summary.

#### Database
- **Neo4j Labels**: `OntologyTerm` is used for ontology searches.
- **Neo4j Nodes**: Nodes with labels `Person`, `Soul`, `SpiritualConcept` are searched.

#### Configuration
- **Config Files**: Uses `.env` file for configuration.
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.

#### Key Logic
- **Term Extraction**: The `_extract_search_term` method normalizes the query by removing specific triggers, normalizing whitespace, and ensuring ASCII characters only.
- **Ontology Search**: The `_search_ontology` method queries Neo4j for ontology terms that contain the search term.
- **Node Search**: The `_search_nodes` method queries Neo4j for nodes with specific labels that contain the search term.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos skill system.
- **Neo4j**: Uses the Neo4j driver to connect and query the Neo4j database.
- **FastAPI**: Likely integrates with FastAPI for handling HTTP requests and responses.

### Detailed Documentation

#### Class: `Neo4jGraphSearchSkill`
- **Inheritance**: Extends `SkillBase`.
- **Attributes**:
  - `name`: The name of the skill (`neo4j_graph_search`).
  - `triggers`: List of keywords that trigger this skill.
  - `cache_ttl`: Time-to-live for caching results (600 seconds).
- **Methods**:
  - `execute`: Processes the user query, extracts the search term, and performs searches in the ontology and nodes.
  - `_extract_search_term`: Normalizes the query to extract the search term.
  - `_search_ontology`: Queries Neo4j for ontology terms matching the search term.
  - `_search_nodes`: Queries Neo4j for nodes matching the search term.

#### Top-level Functions
- **`_get_driver`**: Returns a Neo4j driver instance using environment variables for connection details.
- **`execute`**: A top-level function that processes a request and returns a response, likely used for testing or standalone execution.

#### Database Interactions
- **Neo4j Queries**:
  - **Ontology Search**: Uses a Cypher query to find ontology terms containing the search term.
  - **Node Search**: Uses a Cypher query to find nodes with specific labels containing the search term.

#### Configuration and Environment
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` are used to configure the Neo4j driver.
- **.env File**: Loaded using `dotenv` to provide environment variables.

#### Integration with Mythos
- **SkillBase**: Integrates with the Mythos skill system by extending `SkillBase` and providing a `execute` method.
- **FastAPI**: Likely integrated with FastAPI for handling HTTP requests and responses, though not explicitly shown in the code.

This file is a critical component of the Mythos system, enabling users to search the Neo4j database for ontology terms and graph nodes based on user queries.
