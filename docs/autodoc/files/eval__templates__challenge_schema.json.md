# eval/templates/challenge_schema.json

**Language:** json
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 130

---

### Purpose
The `challenge_schema.json` file defines a JSON schema for specifying challenges for the Ollama chunk factory eval harness. This schema ensures that all challenges include necessary details for building valid Mythos SkillBase skills.

### Architecture
The schema is structured as a JSON object with various properties, each defining specific aspects of a challenge. It includes required fields and nested objects to describe the challenge's requirements, context, expected behavior, and validation criteria.

### Patterns
No specific design patterns are used in this JSON schema. It is a straightforward definition of the structure and constraints for a challenge specification.

### Dependencies
This JSON schema does not have direct dependencies. It relies on the JSON Schema specification (draft/2020-12) for its structure and validation rules.

### Interfaces
This schema defines the structure for challenge specifications, which are used by the Ollama chunk factory eval harness. It does not expose any functions or classes but serves as a blueprint for JSON objects representing challenges.

### Database
This schema does not directly interact with any databases. However, it includes properties like `database`, `database_name`, and `table` to describe the target environment, which may be used to interact with PostgreSQL or Neo4j in the broader Mythos system.

### Configuration
The schema itself does not use any configuration files or environment variables. It is a static definition used to validate challenge specifications.

### Key Logic
The key logic in this schema is the definition of required and optional properties for a challenge, including:
- **Challenge Metadata**: `challenge_id`, `version`, `created_by`, `created_at`
- **Challenge Description**: `description`, `difficulty`, `category`, `stream`
- **Requirements**: `natural_language`, `skill_name`, `class_name`, `filename`
- **System Context**: Details about the target environment, including database and table information
- **Expected Behavior**: Test cases to validate the skill's behavior
- **Validation Criteria**: Structural and behavioral checks

### Integration Points
This schema integrates with the Ollama chunk factory eval harness by defining the structure of challenge specifications. It is used to validate and structure the input data for the eval harness, ensuring consistency and completeness of challenge definitions.

### Detailed Breakdown of Properties

1. **Challenge Metadata**:
   - `challenge_id`: Unique identifier for the challenge.
   - `version`: Version of the challenge specification.
   - `created_by`: Creator of the challenge.
   - `created_at`: Date when the challenge was created.

2. **Challenge Description**:
   - `description`: Summary of the challenge.
   - `difficulty`: Level of difficulty.
   - `category`: Type of skill (data, action, composite, meta).
   - `stream`: Stream type (SYS, NEU, LOG, MNE, SEN).

3. **Requirements**:
   - `natural_language`: Plain English description of the task.
   - `skill_name`: Name of the skill to be built.
   - `class_name`: Class name for the skill.
   - `filename`: Filename for the skill.
   - `category`: Category of the skill.
   - `cache_ttl`: Time-to-live for caching.
   - `triggers`: Triggers for the skill.

4. **System Context**:
   - `database`: Type of database.
   - `database_name`: Name of the database.
   - `connection_pattern`: Connection pattern.
   - `table`: Details about the table, including name, schema, columns, and indexes.
   - `engine_import`: Import for the database engine.
   - `venv_python`: Python version for the virtual environment.
   - `skill_directory`: Directory for the skill.

5. **Expected Behavior**:
   - `test_cases`: Array of test cases with expected behavior and notes.

6. **Validation Criteria**:
   - `structural`: Array of structural checks.
   - `behavioral`: Array of behavioral checks.

7. **Gold Path**:
   - `gold_path`: Path to the gold standard implementation.

This schema ensures that all challenges are well-defined and consistent, facilitating the evaluation and validation of skills in the Mythos system.
