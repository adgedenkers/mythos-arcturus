# tools/prompt_lab/messages/technical.yaml

**Language:** yaml
**Stream:** SYS
**Module:** Tools
**Lines:** 41

---

### Documentation for `tools/prompt_lab/messages/technical.yaml`

#### Purpose
This YAML file defines a suite of technical test messages for the Mythos system. Each message is designed to test various technical and infrastructure-related topics such as database schema design, Cypher queries, debugging, architecture decisions, and patch creation processes.

#### Architecture
The file is structured as a YAML document with a top-level `suite` and `description` field. Under these, there is a list of `messages`, each containing:
- `id`: A unique identifier for the message.
- `text`: The actual prompt text.
- `tests`: A list of categories the message falls under.
- `expect`: A dictionary of expected behaviors, notably `no_life_dump: true` indicating that the response should not be overly verbose.
- `notes`: Additional notes or context for the message.

#### Patterns
No specific design patterns are used in this YAML file. It is a simple data structure for storing test messages and their metadata.

#### Dependencies
This YAML file does not import or rely on any external libraries or modules. It is a standalone configuration file.

#### Interfaces
This file is used by the Mythos system to generate or retrieve test messages for technical topics. It does not expose any functions or classes but is consumed by other parts of the system to provide test prompts.

#### Database
The file does not directly interact with any databases. However, it references database-related topics such as PostgreSQL and Neo4j in its prompts.

#### Configuration
This file itself is a configuration file. It does not use any external configuration files or environment variables.

#### Key Logic
The key logic in this file is the definition of test messages and their associated metadata. Each message is crafted to test specific technical skills or knowledge areas.

#### Integration Points
This YAML file integrates with the Mythos system's prompt generation or retrieval subsystems. It is likely consumed by a module or service responsible for generating or selecting prompts based on the `suite` and `tests` categories.

### Detailed Analysis of Each Message

1. **Message: `postgres_table`**
   - **Purpose**: Tests the ability to design a PostgreSQL table schema.
   - **Tests**: `technical`, `architecture`
   - **Expectation**: The response should be technically precise and may reference design patterns.
   - **Notes**: The response should focus on the schema design for a workout session tracking table.

2. **Message: `neo4j_query`**
   - **Purpose**: Tests the ability to write a Cypher query for a Neo4j database.
   - **Tests**: `technical`, `mystical`
   - **Expectation**: The response should produce a valid Cypher query.
   - **Notes**: The response should reference the existing schema to find people connected to the Merovingian lineage.

3. **Message: `debug_help`**
   - **Purpose**: Tests the ability to debug a service using systemd and journalctl.
   - **Tests**: `technical`, `voice`
   - **Expectation**: The response should provide concrete commands for debugging.
   - **Notes**: The response should include specific systemd and journalctl commands for debugging the `mythos-bot` service.

4. **Message: `architecture_question`**
   - **Purpose**: Tests the ability to make architectural decisions regarding database choices.
   - **Tests**: `technical`, `architecture`, `challenge`
   - **Expectation**: The response should reason about the tradeoffs between different database choices.
   - **Notes**: The response should reference the dual-database pattern for storing astrology chart data.

5. **Message: `patch_help`**
   - **Purpose**: Tests the knowledge of the patch creation process.
   - **Tests**: `technical`, `knowledge`
   - **Expectation**: The response should reference the patch standard v2 and related scripts.
   - **Notes**: The response should include details on the `apply_patch.py` and `install.sh` scripts.

This YAML file serves as a comprehensive test suite for evaluating technical skills and knowledge within the Mythos system.
