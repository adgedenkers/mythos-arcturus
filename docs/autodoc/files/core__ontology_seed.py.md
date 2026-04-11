# core/ontology_seed.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 644

---

### File: core/ontology_seed.py

#### Purpose
The `ontology_seed.py` file is responsible for seeding the Neo4j database with predefined ontology terms and their relationships, specifically for categories such as Astrology, Numerology, Tarot, and Mythos Core.

#### Architecture
The file consists of a single top-level function `seed_ontology` which is responsible for populating the Neo4j database with ontology terms. The file imports necessary modules and defines constants for Neo4j connection details. The ontology terms are defined as a list of dictionaries, each containing details such as name, definition, category, and aliases.

#### Patterns
- **Singleton**: The Neo4j driver connection is established once and reused, adhering to the Singleton pattern to ensure a single connection instance.
- **Configuration Management**: Environment variables and a `.env` file are used to manage configuration settings, which is a common pattern for handling sensitive information and configuration settings.

#### Dependencies
- **os**: Used for interacting with the operating system, specifically for reading environment variables and file paths.
- **sys**: Standard Python library for system-specific parameters and functions.
- **datetime**: Used for handling date and time operations.
- **neo4j**: Neo4j Python driver for interacting with the Neo4j database.

#### Interfaces
- **seed_ontology**: This function is the primary interface exposed by the file. It is responsible for seeding the Neo4j database with ontology terms and their relationships.

#### Database
- **Neo4j**: The file interacts with Neo4j to create `OntologyTerm` nodes and `RELATED_TO` relationships. It reads from a predefined list of ontology terms and writes them into the Neo4j database.

#### Configuration
- **Environment Variables**: The file reads `NEO4J_URI`, `NEO4J_USER`, and `NEO4J_PASSWORD` from environment variables. If `NEO4J_PASSWORD` is not set, it attempts to load it from a `.env` file located at `/opt/mythos/.env`.

#### Key Logic
- **Neo4j Connection Setup**: Establishes a connection to the Neo4j database using the `GraphDatabase.driver` method.
- **Ontology Term Insertion**: Iterates over the predefined list of ontology terms and inserts each term as a node in the Neo4j database with the label `OntologyTerm`. It also creates relationships between terms using the `RELATED_TO` relationship type.
- **Error Handling**: The file does not explicitly handle errors, but the Neo4j driver manages connection and transaction errors internally.

#### Integration Points
- **Mythos Core**: This file integrates with the Mythos Core subsystem by seeding the ontology terms that are foundational to the Mythos system's knowledge graph.
- **Neo4j Database**: Directly interacts with the Neo4j database to store and manage ontology terms and relationships, which are used by other subsystems for querying and analysis.

### Example Code Snippet
```python
import os
import sys
from datetime import datetime
from neo4j import GraphDatabase

NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', '')

# Load from .env if not set
if not NEO4J_PASSWORD:
    env_path = '/opt/mythos/.env'
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                if line.startswith('NEO4J_PASSWORD='):
                    NEO4J_PASSWORD = line.strip().split('=', 1)[1]

TERMS = [
    {
        "name": "Natal Chart",
        "definition": "A map of the sky at the exact moment and location of birth, showing the positions of all planets, the ascendant, midheaven, and house cusps. The foundational document of a person's astrological identity.",
        "category": "Astrology",
        "aliases": ["birth chart", "nativity", "radix chart"],
    },
    # ... more terms ...
]

def seed_ontology():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        for term in TERMS:
            session.run(
                """
                MERGE (t:OntologyTerm {name: $name, definition: $definition, category: $category})
                """,
                name=term["name"],
                definition=term["definition"],
                category=term["category"],
            )
            for alias in term.get("aliases", []):
                session.run(
                    """
                    MATCH (t:OntologyTerm {name: $name})
                    MERGE (a:OntologyTerm {name: $alias})
                    MERGE (t)-[:RELATED_TO]->(a)
                    """,
                    name=term["name"],
                    alias=alias,
                )
    driver.close()

if __name__ == "__main__":
    seed_ontology()
```

This file ensures that the Neo4j database is populated with the necessary ontology terms and relationships, providing a foundational knowledge graph for the Mythos system.
