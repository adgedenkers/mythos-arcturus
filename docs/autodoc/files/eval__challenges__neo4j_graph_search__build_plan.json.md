# eval/challenges/neo4j_graph_search/build_plan.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 34

---

### File: eval/challenges/neo4j_graph_search/build_plan.json

#### Purpose
This JSON file serves as a blueprint for developing a Neo4j graph search skill within the Mythos system. It outlines the steps, logic, and requirements for creating a Python class that interacts with a Neo4j database to search for ontology terms, souls, spiritual concepts, and relationships.

#### Architecture
The file is structured as a JSON object with several key sections:
- **plan_id**: Identifier for the plan.
- **version**: Version of the plan.
- **description**: Description of the plan's purpose.
- **pattern**: Pattern identifier for the skill.
- **model_hint**: Model hint for the skill.
- **context**: Contextual information including system context, table schema, and mandatory patterns.
- **build_plan**: A list of steps (passes) detailing the implementation of the skill.
- **test_cases**: Test cases to validate the functionality of the skill.

#### Patterns
- **Factory Pattern**: Not explicitly used in this JSON file, but the skill class can be seen as a factory for creating search responses.
- **Singleton Pattern**: Not explicitly used, but the Neo4j driver could be implemented as a singleton to ensure a single connection throughout the application.
- **Observer Pattern**: Not explicitly used, but the skill class could be designed to observe changes in the Neo4j database.

#### Dependencies
- **Imports**: `os`, `logging`, `dotenv`, `engine.base`, `neo4j.GraphDatabase`.
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`.
- **Configuration Files**: `.env` file for loading environment variables.

#### Interfaces
- **SkillBase Class**: The skill class `Neo4jGraphSearchSkill` inherits from `SkillBase` and implements methods like `execute`, `_extract_search_term`, `_search_ontology`, `_search_nodes`, and `_build_summary`.
- **SkillRequest/SkillResponse**: The skill class processes `SkillRequest` objects and returns `SkillResponse` objects.

#### Database
- **Neo4j Labels**: The Neo4j database contains nodes with labels `OntologyTerm`, `Person`, `Soul`, and `SpiritualConcept`.
- **Cypher Queries**: The skill uses Cypher queries to search for nodes and relationships based on the search term.

#### Configuration
- **Environment Variables**: `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` are used to connect to the Neo4j database.
- **.env File**: The `.env` file is loaded using `dotenv.load_dotenv` to set environment variables.

#### Key Logic
1. **_get_driver**: Establishes a connection to the Neo4j database using the `neo4j.GraphDatabase.driver` method.
2. **_extract_search_term**: Processes the input message to extract the search term by removing specific triggers and normalizing whitespace.
3. **_search_ontology**: Executes a Cypher query to search for ontology terms that match the search term.
4. **_search_nodes**: Executes a Cypher query to search for nodes (Person, Soul, SpiritualConcept) that match the search term.
5. **execute**: The main method that orchestrates the search process, extracts the search term, calls `_search_ontology` and `_search_nodes`, and builds a summary response.

#### Integration Points
- **engine.base**: The skill class inherits from `SkillBase` and uses `SkillRequest` and `SkillResponse` classes.
- **neo4j**: The skill uses the `neo4j.GraphDatabase` driver to connect to and query the Neo4j database.
- **dotenv**: The skill loads environment variables from a `.env` file using `dotenv.load_dotenv`.

### Detailed Breakdown of Passes

1. **Pass 1**: Define the file skeleton, import necessary modules, and create the `Neo4jGraphSearchSkill` class with placeholder methods.
2. **Pass 2**: Implement the `_extract_search_term` method to process the input message and extract the search term.
3. **Pass 3**: Implement the `_search_ontology` method to search for ontology terms in the Neo4j database.
4. **Pass 4**: Implement the `_search_nodes` method to search for nodes (Person, Soul, SpiritualConcept) in the Neo4j database.
5. **Pass 5**: Implement the `execute` method to orchestrate the search process, combine results, and build a summary response.
6. **Pass 6**: Review the implementation to ensure it meets the specified requirements, including closing the Neo4j driver in a `finally` block and using ASCII-only characters.

### Test Cases
- **Test Case 1**: Search ontology for "tarot" and expect ontology results.
- **Test Case 2**: Search for "emerald flame" and expect a response.
- **Test Case 3**: Search using the term "graph search" and expect a response.

This JSON file provides a comprehensive guide for developing a Neo4j graph search skill, ensuring that all necessary components and logic are implemented correctly.
