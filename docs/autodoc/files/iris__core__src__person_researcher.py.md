# iris/core/src/person_researcher.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 1269

---

### Documentation for `person_researcher.py`

#### Purpose
The `person_researcher.py` file is responsible for managing the research pipeline for individuals in the Mythos system. It handles both local database lookups and external web research (Wikipedia and Wikidata) to gather comprehensive information about a person. It also orchestrates the storage of this information in PostgreSQL and Neo4j, and queues deep research tasks for background processing.

#### Architecture
The file is structured around two primary classes: `PersonRecord` and `ResearchResult`. The `PersonRecord` class encapsulates the information known about a person, while `ResearchResult` provides a summary of the research process and outcomes. The file also contains several top-level functions that handle specific tasks such as HTTP requests, database connections, and data parsing.

#### Patterns
- **Factory Pattern**: The `PersonRecord` and `ResearchResult` classes act as factories for creating structured records and research summaries.
- **Singleton Pattern**: The database connection `_get_db` function can be considered a singleton, as it ensures a single connection is used throughout the module.
- **Observer Pattern**: The `ResearchResult` class can be seen as an observer that collects and summarizes the results of various research tasks.

#### Dependencies
The file imports several modules:
- `json`, `logging`, `os`, `re`, `time`, `urllib.parse`, `urllib.request`, `httpx`, `psycopg2`, `psycopg2.extras`, `redis`, `sys`

#### Interfaces
The file exposes the following functions to other parts of the system:
- `research_person(db_config, name, requested_by)`: Main entry point for initiating research on a person.
- `quick_research(name)`: Performs a quick Wikipedia lookup to create a minimal `PersonRecord`.
- `store_person(db_config, record)`: Inserts a person into the PostgreSQL `people` table.
- `update_person_notes(db_config, person_id, notes)`: Updates the notes field for an existing person.
- `store_neo4j_person(record)`: Creates or updates a `Person` node in Neo4j.
- `queue_deep_research(record, requested_by)`: Queues a deep research task for background processing.
- `run_deep_research(db_config, person_id)`: Executes a full dossier build for a person.

#### Database
The file interacts with the following PostgreSQL tables:
- `people`: Stores basic person information.
- `person_dates`: Stores date-related information for a person.
- `astrotheme`: Stores astrology-related data.
- `astrology`: Stores astrology-related data.
- `soul_stratigraphy`: Stores soul stratigraphy data.
- `harmonic`: Stores harmonic data.

It also interacts with Neo4j:
- `Person`: A label for person nodes.

#### Configuration
The file uses the following configuration:
- `WIKI_SEARCH_URL`, `WIKI_SUMMARY_URL`, `WIKIDATA_URL`, `WIKIDATA_SPARQL`: URLs for Wikipedia and Wikidata APIs.
- `REDIS_STREAM`: Redis stream for queuing deep research tasks.
- `OLLAMA_HOST`: Host for the Ollama LLM service.
- `DEFAULT_MODEL`: Default model for the Ollama service.
- `REQUEST_TIMEOUT`: Timeout for HTTP requests.

#### Key Logic
- **Local Lookup**: The `lookup_local` function searches the `people` table for a person by name, known_as, or fuzzy match.
- **Web Research**: The `wiki_search`, `wiki_summary`, and `wikidata_birth_info` functions perform full-text Wikipedia searches, fetch Wikipedia summaries, and fetch structured birth data from Wikidata, respectively.
- **Deep Research**: The `run_deep_research` function performs a comprehensive dossier build, including astrology, numerology, and resonance mapping.
- **Storage**: The `store_person` and `store_neo4j_person` functions insert or update person records in PostgreSQL and Neo4j, respectively.
- **Background Processing**: The `queue_deep_research` function queues deep research tasks for background processing via Redis.

#### Integration Points
- **Database**: Interacts with PostgreSQL for storing person records and related data.
- **Neo4j**: Interacts with Neo4j for storing person nodes and relationships.
- **Redis**: Uses Redis to queue deep research tasks for background processing.
- **Wikipedia/Wikidata**: Uses HTTP requests to fetch information from Wikipedia and Wikidata.
- **Ollama**: Uses HTTP requests to interact with the Ollama LLM service for synthesizing biographies and resonance mappings.

### Summary
The `person_researcher.py` file is a critical component of the Mythos system, handling the research, storage, and background processing of person records. It integrates with multiple data sources and storage systems to provide comprehensive information about individuals encountered by the system.
