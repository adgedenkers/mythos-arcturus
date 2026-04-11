# eval/results/neo4j_graph_search/20260305_111100/pass06_attempt02.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 101

---

### File: `eval/results/neo4j_graph_search/20260305_111100/pass06_attempt02.py`

#### Purpose
This file implements a Neo4j graph search skill (`Neo4jGraphSearchSkill`) that processes user requests to search for ontology terms and graph nodes within a Neo4j database. It extracts search terms from user requests, performs searches, and builds a summary of the results.

#### Architecture
The file contains a single class `Neo4jGraphSearchSkill` which inherits from `SkillBase`. The class has several methods to handle different aspects of the search process:
- `_get_driver`: A top-level function to initialize the Neo4j driver.
- `execute`: The main method that orchestrates the search process.
- `_extract_search_term`: Extracts the search term from the user request.
- `_search_ontology`: Searches for ontology terms in the Neo4j database.
- `_search_nodes`: Searches for graph nodes in the Neo4j database.
- `_build_summary`: Builds a summary of the search results.

#### Patterns
- **Singleton**: The `_get_driver` function ensures that the Neo4j driver is initialized only once.
- **Factory**: The `execute` method acts as a factory to create `SkillResponse` objects based on the search results.

#### Dependencies
- **Imports**: `os`, `logging`, `dotenv`, `SkillBase`, `SkillRequest`, `SkillResponse`, `GraphDatabase`
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`

#### Interfaces
- **Public Methods**: `execute`
- **Exposed Objects**: `SkillResponse` objects are returned from the `execute` method.

#### Database
- **Neo4j Labels**: `OntologyTerm`
- **Neo4j Queries**:
  - `_search_ontology`: Queries for ontology terms.
  - `_search_nodes`: Queries for graph nodes with specific labels.

#### Configuration
- **Environment Variables**: The Neo4j connection details are loaded from environment variables.
- **Configuration File**: `.env` file is loaded to set environment variables.

#### Key Logic
- **Term Extraction**: The `_extract_search_term` method removes specific triggers from the user request and extracts a meaningful search term.
- **Ontology Search**: The `_search_ontology` method queries the Neo4j database for ontology terms that match the search term.
- **Node Search**: The `_search_nodes` method queries the Neo4j database for nodes with specific labels that match the search term.
- **Summary Building**: The `execute` method builds a summary of the search results and constructs a `SkillResponse` object.

#### Integration Points
- **SkillBase**: The `Neo4jGraphSearchSkill` class inherits from `SkillBase` and integrates with the Mythos system's skill framework.
- **Neo4j**: The `_get_driver` function initializes the Neo4j driver, and the `_search_ontology` and `_search_nodes` methods interact with the Neo4j database.
- **SkillRequest and SkillResponse**: The `execute` method processes `SkillRequest` objects and returns `SkillResponse` objects, integrating with the Mythos system's request-response mechanism.

### Detailed Documentation

#### Class: `Neo4jGraphSearchSkill`
- **Inherits**: `SkillBase`
- **Attributes**:
  - `name`: `'neo4j_graph_search'`
  - `triggers`: List of keywords that trigger this skill
  - `cache_ttl`: Cache time-to-live in seconds
- **Methods**:
  - `execute`: Main method to process the user request, extract the search term, perform searches, and build a summary.
  - `_extract_search_term`: Extracts the search term from the user request.
  - `_search_ontology`: Queries the Neo4j database for ontology terms.
  - `_search_nodes`: Queries the Neo4j database for graph nodes.
  - `_build_summary`: Placeholder method to build a summary of the search results.

#### Top-Level Functions
- **_get_driver**: Initializes and returns the Neo4j driver.
- **execute**: Placeholder for a top-level `execute` function (not used in the class).

#### Database Queries
- **Ontology Search**:
  ```cypher
  MATCH (t:OntologyTerm) WHERE toLower(t.name) CONTAINS toLower($term) RETURN t.name as name, t.definition as definition, t.category as category LIMIT 10
  ```
- **Node Search**:
  ```cypher
  MATCH (n) WHERE any(label IN labels(n) WHERE label IN ['Person', 'Soul', 'SpiritualConcept']) AND toLower(n.name) CONTAINS toLower($term) RETURN labels(n) as labels, n.name as name, n.canonical_id as canonical_id LIMIT 10
  ```

#### Configuration
- **Environment Variables**:
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for the Neo4j database.
  - `NEO4J_PASSWORD`: Password for the Neo4j database.
- **.env File**: Contains the environment variables for the Neo4j connection.

This file is a critical component of the Mythos system, enabling users to search for ontology terms and graph nodes within the Neo4j database, and providing a structured response to the user.
