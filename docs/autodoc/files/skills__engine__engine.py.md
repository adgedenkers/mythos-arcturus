# skills/engine/engine.py

**Language:** python
**Stream:** LOG
**Module:** Skill Engine
**Lines:** 227

---

### File: skills/engine/engine.py

#### Purpose
The `SkillEngine` class is the central orchestrator for the Mythos system's skills. It loads skill modules, routes messages to appropriate skills, executes them, and assembles their results into a context block for prompt injection.

#### Architecture
The `SkillEngine` class contains methods for loading skills, processing messages, and assembling context blocks. The class is initialized with an optional `SkillRouter` instance. The primary methods include:
- `__init__`: Initializes the engine with a router and an empty dictionary for skills.
- `load_skills`: Discovers and loads all skill classes from the specified data directory.
- `_load_skill_module`: Loads a single skill module and registers any `SkillBase` subclasses.
- `register_skill`: Manually registers a skill instance.
- `process`: Processes a message through the skill pipeline asynchronously.
- `process_sync`: Provides a synchronous wrapper for the `process` method.
- `_assemble_context`: Assembles skill results into a prompt-ready context block.
- `get_status`: Returns the engine status for diagnostics.

#### Patterns
- **Factory Method**: `_load_skill_module` dynamically loads and registers skill modules.
- **Singleton**: The `SkillEngine` can be considered a singleton if only one instance is intended to be used throughout the system.

#### Dependencies
- `asyncio`: For asynchronous operations.
- `importlib`, `importlib.util`: For dynamic module loading.
- `logging`: For logging messages.
- `sys`: For managing the module namespace.
- `time`: For timing operations.
- `threading`: For running asynchronous tasks in a synchronous context.
- `pathlib`: For handling file paths.
- `typing`: For type hints.

#### Interfaces
- `load_skills`: Discovers and loads all skill classes.
- `register_skill`: Manually registers a skill instance.
- `process`: Processes a message through the skill pipeline asynchronously.
- `process_sync`: Provides a synchronous wrapper for the `process` method.
- `_assemble_context`: Assembles skill results into a prompt-ready context block.
- `get_status`: Returns the engine status for diagnostics.

#### Database
The file does not directly interact with any specific PostgreSQL tables or Neo4j labels. However, it may indirectly interact with the database through skill modules that it loads and executes.

#### Configuration
- `SKILLS_DATA_DIR`: Path to the directory containing skill modules (`/opt/mythos/skills/data`).

#### Key Logic
- **Skill Loading**: The `load_skills` method discovers and loads all skill classes from the specified data directory.
- **Message Processing**: The `process` method routes messages to determine the activation set, executes activated skills, and assembles results into a context block.
- **Context Block Assembly**: The `_assemble_context` method constructs a prompt-ready context block from the results of executed skills.

#### Integration Points
- **Skill Modules**: The `SkillEngine` loads and executes skill modules that inherit from `SkillBase`.
- **SkillRouter**: The `SkillEngine` uses an instance of `SkillRouter` to route messages and determine the activation set.
- **SkillRequest and SkillResponse**: The `process` method uses `SkillRequest` and `SkillResponse` objects to communicate with skills.
- **ChatAssistant**: The `SkillEngine` is used by `ChatAssistant` to process messages and generate context blocks for prompt injection.

### Summary
The `SkillEngine` class is the core component of the Mythos system's skill orchestration. It dynamically loads and manages skill modules, processes messages, and generates context blocks for prompt injection. The class is designed to be flexible and extensible, allowing for easy integration with various skill modules and routing mechanisms.
