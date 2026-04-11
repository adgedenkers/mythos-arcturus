# eval/results/neo4j_graph_search/20260305_110247/pass06_attempt03.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 173

---

### Documentation for `eval/results/neo4j_graph_search/20260305_110247/pass06_attempt03.py`

#### Purpose
This file contains a class `Neo4jGraphSearchSkill` that implements a skill for searching the Neo4j graph database for ontology terms and nodes based on a given query. It extracts a search term from the query, performs searches in the ontology and graph nodes, and builds a summary of the results.

#### Architecture
- **Class**: `Neo4jGraphSearchSkill` extends `SkillBase` and contains methods for executing the search, extracting the search term, searching the ontology, searching the nodes, and building a summary.
- **Top-level Functions**: `_get_driver` initializes the Neo4j driver, and `execute` is an asynchronous function that orchestrates the search process.
- **Data Flow**: The query is processed to extract a search term, which is then used to search the ontology and nodes. The results are summarized and returned as a `SkillResponse`.

#### Patterns
- **Singleton**: The `_get_driver` function can be considered a singleton pattern as it ensures a single instance of the Neo4j driver is used.
- **Factory**: The `execute` method acts as a factory for creating `SkillResponse` objects based on the search results.

#### Dependencies
- **Imports**: `os`, `logging`, `re`, `dotenv`, `engine.base`, `neo4j`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

#### Interfaces
- **Public Methods**: `execute` (asynchronous)
- **Private Methods**: `_extract_search_term`, `_search_ontology`, `_search_nodes`, `_build_summary`

#### Database
- **Neo4j**: 
  - **Label**: `OntologyTerm`
  - **Nodes**: `Person`, `Soul`, `SpiritualConcept`

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- **Config Files**: `.env` file loaded using `dotenv`

#### Key Logic
- **_extract_search_term**: Cleans and normalizes the query to extract a meaningful search term.
- **_search_ontology**: Queries Neo4j for ontology terms matching the search term.
- **_search_nodes**: Queries Neo4j for nodes matching the search term.
- **_build_summary**: Constructs a summary of the search results.

#### Integration Points
- **SkillBase**: Inherits from `SkillBase` and integrates with the Mythos skill framework.
- **Neo4j**: Uses the Neo4j driver to interact with the graph database.
- **SkillRequest/SkillResponse**: Uses `SkillRequest` and `SkillResponse` classes for request and response handling.

### Detailed Breakdown

#### Class: `Neo4jGraphSearchSkill`
- **Attributes**:
  - `name`: Name of the skill (`neo4j_graph_search`).
  - `triggers`: List of keywords that trigger this skill.
  - `cache_ttl`: Time-to-live for cache (600 seconds).

- **Methods**:
  - `execute`: Asynchronous method that processes the query, extracts the search term, searches the ontology and nodes, and builds a summary.
  - `_extract_search_term`: Cleans and normalizes the query to extract a meaningful search term.
  - `_search_ontology`: Queries Neo4j for ontology terms matching the search term.
  - `_search_nodes`: Queries Neo4j for nodes matching the search term.
  - `_build_summary`: Constructs a summary of the search results.

#### Top-level Functions
- **_get_driver**: Initializes and returns the Neo4j driver using environment variables for connection details.
- **execute**: Asynchronous function that orchestrates the search process and returns a `SkillResponse`.

#### Database Interactions
- **Neo4j Queries**:
  - **_search_ontology**: 
    ```cypher
    MATCH (t:OntologyTerm)
    WHERE toLower(t.name) CONTAINS toLower($term)
    RETURN t.name as name, t.definition as definition, t.category as category
    LIMIT 10
    ```
  - **_search_nodes**: 
    ```cypher
    MATCH (n)
    WHERE any(label IN labels(n) WHERE label IN ['Person', 'Soul', 'SpiritualConcept'])
    AND toLower(n.name) CONTAINS toLower($term)
    RETURN labels(n) as labels, n.name as name, n.canonical_id as canonical_id
    LIMIT 10
    ```

#### Configuration and Environment Variables
- **.env File**: Loaded using `dotenv` to provide environment variables for Neo4j connection details.
- **Environment Variables**:
  - `NEO4J_URI`: URI for Neo4j server.
  - `NEO4J_USER`: Username for Neo4j.
  - `NEO4J_PASSWORD`: Password for Neo4j.

#### Integration with Mythos System
- **SkillBase**: The class extends `SkillBase`, integrating with the Mythos skill framework.
- **SkillRequest/SkillResponse**: The `execute` method processes `SkillRequest` and returns `SkillResponse` objects, facilitating integration with the Mythos system's request-response model.
