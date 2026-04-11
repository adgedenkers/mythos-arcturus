# eval/results/neo4j_graph_search/20260305_111100/pass06_attempt03.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 101

---

### Documentation for `eval/results/neo4j_graph_search/20260305_111100/pass06_attempt03.py`

#### Purpose
This file implements a Neo4j-based graph search skill (`Neo4jGraphSearchSkill`) that extracts search terms from user requests, searches for ontology terms and graph nodes in a Neo4j database, and builds a summary of the results.

#### Architecture
The file contains a single class `Neo4jGraphSearchSkill` that inherits from `SkillBase`. It includes methods for executing the search, extracting search terms, searching the ontology, searching nodes, and building a summary. Additionally, there are top-level functions for getting the Neo4j driver and extracting search terms.

#### Patterns
- **Factory Method**: The `_get_driver` function acts as a factory method to create and return a Neo4j driver instance.
- **Singleton**: The `_get_driver` function ensures a single instance of the Neo4j driver is used throughout the execution.

#### Dependencies
- **Imports**: `os`, `logging`, `dotenv`, `engine.base` (for `SkillBase`, `SkillRequest`, `SkillResponse`), `neo4j` (for `GraphDatabase`).
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.

#### Interfaces
- **Public Methods**:
  - `execute`: Asynchronous method to execute the search and return a `SkillResponse`.
  - `_extract_search_term`: Extracts the search term from the request.
  - `_search_ontology`: Searches for ontology terms in Neo4j.
  - `_search_nodes`: Searches for nodes in Neo4j.
  - `_build_summary`: Builds a summary of the search results.

#### Database
- **Neo4j Labels**: `OntologyTerm` for ontology terms.
- **Neo4j Nodes**: Nodes with labels `Person`, `Soul`, `SpiritualConcept`.

#### Configuration
- **Environment Variables**: Configured through `.env` file using `dotenv` for Neo4j connection details.
- **Class Attributes**: `name`, `triggers`, `cache_ttl` are defined in `Neo4jGraphSearchSkill`.

#### Key Logic
1. **Term Extraction**: `_extract_search_term` removes common triggers and filters out short words to form a meaningful search term.
2. **Ontology Search**: `_search_ontology` queries Neo4j to find ontology terms that match the search term.
3. **Node Search**: `_search_nodes` queries Neo4j to find nodes with specific labels that match the search term.
4. **Result Summary**: `_build_summary` constructs a summary of the search results, though it is currently a placeholder method.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos skill execution framework.
- **Neo4j**: Uses the `neo4j` driver to interact with the Neo4j database.
- **Environment Configuration**: Loads environment variables from `.env` for Neo4j connection details.

### Detailed Breakdown

#### Class: `Neo4jGraphSearchSkill`
- **Inheritance**: Inherits from `SkillBase`.
- **Attributes**:
  - `name`: Name of the skill (`neo4j_graph_search`).
  - `triggers`: List of keywords that trigger this skill.
  - `cache_ttl`: Time-to-live for caching results (600 seconds).
- **Methods**:
  - `execute`: Main method to execute the search and return a `SkillResponse`.
  - `_extract_search_term`: Extracts the search term from the `SkillRequest`.
  - `_search_ontology`: Queries Neo4j for ontology terms.
  - `_search_nodes`: Queries Neo4j for nodes with specific labels.
  - `_build_summary`: Placeholder method to build a summary of the results.

#### Top-level Functions
- **_get_driver**: Returns a Neo4j driver instance using environment variables for connection details.
- **execute**: Asynchronous function to execute the search and return a `SkillResponse`.

#### Database Interactions
- **Ontology Search**: Queries the `OntologyTerm` label in Neo4j.
- **Node Search**: Queries nodes with labels `Person`, `Soul`, `SpiritualConcept` in Neo4j.

#### Configuration and Environment
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` are loaded from `.env`.
- **Logging**: Uses `logging` to log exceptions during execution.

This file integrates with the Mythos system by providing a Neo4j-based graph search skill that can be triggered by specific keywords and returns a structured response with search results.
