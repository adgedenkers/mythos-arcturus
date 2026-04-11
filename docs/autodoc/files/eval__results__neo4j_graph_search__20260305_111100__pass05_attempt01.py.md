# eval/results/neo4j_graph_search/20260305_111100/pass05_attempt01.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 98

---

### Documentation for `pass05_attempt01.py`

#### Purpose
This file implements a skill (`Neo4jGraphSearchSkill`) for searching a Neo4j graph database to find ontology terms and graph nodes based on a given search term. The skill is part of the Mythos system and is designed to handle requests to search for specific terms or concepts within the knowledge graph.

#### Architecture
The file contains a single class `Neo4jGraphSearchSkill` which inherits from `SkillBase`. The class has several methods:
- `execute`: The main method that processes the request and returns a response.
- `_extract_search_term`: Extracts the search term from the request message.
- `_search_ontology`: Queries the Neo4j database for ontology terms.
- `_search_nodes`: Queries the Neo4j database for graph nodes.
- `_build_summary`: Builds a summary of the search results (currently empty).

Additionally, there are top-level functions:
- `_get_driver`: Returns a Neo4j driver instance.
- `execute`: A top-level function that wraps the class method `execute`.

#### Patterns
- **Singleton**: The `_get_driver` function acts as a singleton by returning a single instance of the Neo4j driver.
- **Factory**: The `_get_driver` function can be considered a factory method for creating the Neo4j driver.

#### Dependencies
- `os`: For environment variable handling.
- `logging`: For logging exceptions.
- `dotenv`: For loading environment variables from a `.env` file.
- `engine.base`: For `SkillBase`, `SkillRequest`, and `SkillResponse`.
- `neo4j`: For interacting with the Neo4j database.

#### Interfaces
- **Public Methods**:
  - `execute`: Processes a request and returns a response.
- **Private Methods**:
  - `_extract_search_term`: Extracts the search term from the request.
  - `_search_ontology`: Queries the ontology terms.
  - `_search_nodes`: Queries the graph nodes.
  - `_build_summary`: Builds a summary of the results (currently empty).

#### Database
- **Neo4j**:
  - **Labels**:
    - `OntologyTerm`: Used in `_search_ontology`.
    - `Person`, `Soul`, `SpiritualConcept`: Used in `_search_nodes`.

#### Configuration
- **Environment Variables**:
  - `NEO4J_URI`: URI for the Neo4j database.
  - `NEO4J_USER`: Username for the Neo4j database.
  - `NEO4J_PASSWORD`: Password for the Neo4j database.

#### Key Logic
1. **Term Extraction**: The `_extract_search_term` method processes the request message to extract a meaningful search term by removing predefined trigger words.
2. **Ontology Search**: The `_search_ontology` method queries the Neo4j database for ontology terms that contain the search term.
3. **Node Search**: The `_search_nodes` method queries the Neo4j database for nodes of specific labels (`Person`, `Soul`, `SpiritualConcept`) that contain the search term.
4. **Response Construction**: The `execute` method constructs a `SkillResponse` object with the search results and a summary.

#### Integration Points
- **Mythos System**: The `Neo4jGraphSearchSkill` class integrates with the Mythos system through the `SkillBase` interface, allowing it to be invoked as a skill within the system.
- **Neo4j Database**: The skill interacts with the Neo4j database to perform searches and retrieve results.
- **Environment Configuration**: The skill loads environment variables from a `.env` file to configure the Neo4j connection.

This file is a critical component of the Mythos system, providing a robust mechanism for searching and retrieving information from a Neo4j graph database based on user requests.
