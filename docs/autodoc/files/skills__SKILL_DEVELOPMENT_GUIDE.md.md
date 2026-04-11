# skills/SKILL_DEVELOPMENT_GUIDE.md

**Language:** markdown
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 371

---

### Purpose
The `SKILL_DEVELOPMENT_GUIDE.md` file serves as a comprehensive guide for developers to create and integrate new skills into the Mythos system. It provides detailed instructions, examples, and best practices for developing skills that interact with various subsystems and databases.

### Architecture
The guide is structured into several sections, each covering different aspects of skill development:
- **Introduction**: Defines what a skill is and how it integrates into the system.
- **Quick Start**: Provides a minimal example of a skill implementation.
- **Core Files**: Describes the key files involved in the skill engine.
- **Skill Types**: Explains different types of skills (data, action, composite) with examples.
- **SkillRequest and SkillResponse**: Details the structure and use of these objects.
- **Triggers**: Explains how skills are activated based on user input.
- **Caching**: Describes how to implement caching for skill results.
- **Database Access**: Provides patterns for accessing PostgreSQL and Neo4j.
- **Error Handling**: Guidelines for handling exceptions within skills.
- **Testing**: Instructions for testing skills from the command line.
- **Checklist**: A list of tasks to complete before deploying a new skill.
- **Current Skills**: Lists existing skills and their types.

### Patterns
- **Factory Pattern**: Skills are instantiated and managed by the skill engine, which acts as a factory.
- **Observer Pattern**: The router observes user input and activates relevant skills based on triggers.

### Dependencies
- **Python Standard Library**: `os`, `asyncio`, `datetime`, `sys`
- **External Libraries**: `psycopg2`, `neo4j`, `dotenv`
- **Mythos Internal Modules**: `engine.base`, `engine.router`, `engine.engine`

### Interfaces
- **SkillBase Class**: Abstract base class for all skills.
- **SkillRequest Class**: Represents the request object passed to skills.
- **SkillResponse Class**: Represents the response object returned by skills.

### Database
- **PostgreSQL**: Used for data retrieval and storage in data and action skills.
- **Neo4j**: Used for graph database interactions.

### Configuration
- **Environment Variables**: Used for database connection details (e.g., `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_PORT`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`).
- **.env File**: Located at `/opt/mythos/.env`.

### Key Logic
- **Skill Execution**: The `execute` method is the core logic where skills perform their tasks and return structured results.
- **Caching**: Skills can cache results using a TTL (Time To Live) mechanism.
- **Error Handling**: Skills should handle exceptions gracefully and return meaningful error messages.

### Integration Points
- **Skill Engine**: Loads and manages skills, routing user requests to appropriate skills.
- **API**: Skills are integrated into the FastAPI-based API, which handles user requests and responses.
- **Database**: Skills interact with PostgreSQL and Neo4j to retrieve and store data.
- **Command Line**: Skills can be tested and debugged from the command line using the provided scripts.

### Summary
The `SKILL_DEVELOPMENT_GUIDE.md` is a critical document for developers working on the Mythos system. It provides detailed instructions and examples for creating, testing, and deploying skills, ensuring they integrate seamlessly with the system's architecture and subsystems.
