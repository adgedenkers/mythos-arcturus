# eval/skill_reference/SKILL.md

**Language:** markdown
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 287

---

### Documentation for `eval/skill_reference/SKILL.md`

#### Purpose
This markdown file serves as a comprehensive guide for creating and deploying self-contained Python skills (referred to as "radioactive chunks") that integrate with the Mythos skill engine on the Arcturus server. It outlines the structure, requirements, and best practices for developing these skills.

#### Architecture
The file is structured as a markdown document with sections detailing:
- **What a Chunk Is**: Definition and key characteristics.
- **Required Contract**: Mandatory class attributes and methods.
- **File Template**: Suggested Python file structure.
- **System Context**: Environment details and dependencies.
- **Process**: Steps to create, validate, and deploy a skill.
- **Category-Specific Patterns**: Guidelines for different types of skills.
- **Anti-Patterns**: Common mistakes to avoid.
- **Examples**: Sample implementations.

#### Patterns
- **Template Method Pattern**: The file template provides a structure that developers must follow, ensuring consistency across skills.
- **Singleton Pattern**: The skill engine autodiscovers and manages instances of skills.

#### Dependencies
- **Python Libraries**: `psycopg2`, `neo4j`, `redis`, `dotenv`, `typing`.
- **Environment Variables**: Loaded from `/opt/mythos/.env`.
- **Base Classes**: `SkillBase`, `SkillRequest`, `SkillResponse` from `engine.base`.

#### Interfaces
- **SkillBase Class**: Developers must subclass `SkillBase` and implement the `execute` method.
- **SkillRequest and SkillResponse**: These classes define the input and output of the `execute` method.

#### Database
- **PostgreSQL**: Skills can interact with the `mythos` database, using `_get_conn()` to establish connections.
- **Neo4j**: Skills can interact with the Neo4j graph database using `GraphDatabase`.

#### Configuration
- **Environment Variables**: Secrets and configuration details are stored in `/opt/mythos/.env` and loaded using `dotenv`.

#### Key Logic
- **Skill Execution**: The `execute` method must handle database interactions, build structured data, and generate a human-readable summary.
- **Error Handling**: The `execute` method must gracefully handle exceptions and return appropriate error messages.

#### Integration Points
- **Skill Engine**: Skills are autodiscovered and managed by the Mythos skill engine.
- **API Restart**: Skills are reloaded when the API service restarts.
- **Other Skills**: Composite skills can call other skills using `await OtherSkill().run(request)`.

### Detailed Breakdown

#### What Is a Chunk?
- **Definition**: A single Python file that subclasses `SkillBase`, lives in `/opt/mythos/skills/data/`, and is autodiscovered on API restart.
- **Characteristics**: Self-contained, self-describing, self-testing, and composable.

#### Required Contract
- **Attributes**: `name`, `version`, `category`, `description`, `triggers`, `cache_ttl`.
- **Method**: `async def execute(self, request: SkillRequest) -> SkillResponse`.

#### File Template
- **Structure**: Includes imports, logging setup, connection function, and class definition.
- **Execution**: Handles database connections, queries, and summary generation.

#### System Context
- **Python Environment**: `/opt/mythos/.venv/bin/python3`.
- **Skill Directory**: `/opt/mythos/skills/data/`.
- **Database Connections**: PostgreSQL and Neo4j.
- **Redis and Ollama**: For caching and LLM-powered skills.

#### Process
- **Step 1**: Understand the requirement.
- **Step 2**: Check the schema.
- **Step 3**: Write the skill.
- **Step 4**: Validate the skill.
- **Step 5**: Deploy the skill.

#### Category-Specific Patterns
- **Data Skills**: Query databases, return structured results.
- **Action Skills**: Perform write operations, return confirmation.
- **Composite Skills**: Chain multiple skills, combine summaries.

#### Anti-Patterns
- **Hardcoding Credentials**: Avoid hardcoding database credentials.
- **Empty Summary**: Ensure the summary is non-empty.
- **Open Connections**: Always close database connections.
- **Multiple Classes**: Keep one class per file.
- **Print Statements**: Use logging instead of `print`.

#### Examples
- **Simple Data Skill**: Example of a skill that looks up a person by name from the `people` table.
- **Composite Skill**: Example of a skill that combines multiple skills for a daily briefing.

This markdown file provides a detailed guide for developers to create, validate, and deploy skills within the Mythos system, ensuring consistency and adherence to best practices.
