# iris/core/src/agency.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 651

---

### Documentation for `iris/core/src/agency.py`

#### Purpose
The `agency.py` file contains the core logic for the Iris Agency System, which is responsible for executing tasks and actions in a sandboxed environment, managing container lifecycles, and proposing changes for human review.

#### Architecture
The file defines two main classes:
1. **`TaskResult`**: A data class that holds the result of a task execution.
2. **`AgencySystem`**: The main class that implements the agency system's capabilities, including executing code in sandboxed containers, building and testing prototypes, managing container lifecycles, and proposing changes for human review.

The `AgencySystem` class contains several methods:
- **Initialization and Setup**: `__init__`, `initialize`, `_ensure_sandbox_image`
- **Action Execution**: `consider_actions`, `execute`, `execute_task`
- **Code Generation and Execution**: `_generate_code`, `_execute_in_sandbox`, `_evaluate_result`, `_save_to_workshop`
- **Utility Methods**: `_build_code_generation_prompt`, `_extract_code_from_response`, `_update_goal_context`, `_execute_notify`, `_execute_analyze`, `_execute_build`, `run_code`, `shutdown`

#### Patterns
- **Singleton**: The `AgencySystem` class can be considered a singleton as it is designed to be instantiated once and reused throughout the system.
- **Factory Method**: `_generate_code` and `_execute_in_sandbox` can be seen as factory methods that generate and execute code respectively.

#### Dependencies
- **Imports**: `asyncio`, `os`, `uuid`, `aiodocker`, `structlog`, `shutil`
- **External Libraries**: `aiodocker` for Docker container management, `structlog` for logging
- **Internal Modules**: `Config` from `iris/core/config`

#### Interfaces
- **Public Methods**: `initialize`, `consider_actions`, `execute`, `execute_task`, `run_code`, `shutdown`
- **Internal Methods**: `_ensure_sandbox_image`, `_generate_code`, `_execute_in_sandbox`, `_evaluate_result`, `_save_to_workshop`, `_build_code_generation_prompt`, `_extract_code_from_response`, `_update_goal_context`, `_execute_notify`, `_execute_analyze`, `_execute_build`

#### Database
- **PostgreSQL Tables**: `datetime`, `typing`, `dataclasses`, `environment`, `task`, `goal`, `LLM`
- **Neo4j Labels**: Not explicitly mentioned in the code, but the environment variables suggest interaction with Neo4j.

#### Configuration
- **Environment Variables**: `SANDBOX_IMAGE`, `SANDBOX_NETWORK`, `SANDBOX_TIMEOUT`, `WORKSHOP_PATH`, `SANDBOX_PATH`, `SANDBOX_HOST_PATH`, `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`, `REDIS_HOST`, `REDIS_PORT`

#### Key Logic
- **Task Execution Loop**: The `execute_task` method implements a loop where code is generated, executed in a sandbox, and evaluated. If the result does not meet the goal, the process iterates until the maximum number of attempts is reached.
- **Code Generation and Execution**: The `_generate_code` method generates code based on a goal and previous attempts, and the `_execute_in_sandbox` method executes this code in a sandboxed Docker container.
- **Result Evaluation**: The `_evaluate_result` method checks if the generated code achieves the goal and decides whether to continue iterating or to save the successful code.

#### Integration Points
- **Task Queue**: The `execute_task` method is designed to handle tasks from a task queue, indicating integration with a task management system.
- **LLM Integration**: The `AgencySystem` class uses an LLM (Language Model) to generate code, suggesting integration with an AI model for code generation.
- **Notification System**: The `_execute_notify` method is used to send notifications, indicating integration with a notification system (e.g., Telegram).
- **Analysis System**: The `_execute_analyze` method is used to run analysis, indicating integration with an analysis system.
- **Build System**: The `_execute_build` method is used to build prototypes, indicating integration with a build system.

### Summary
The `agency.py` file is a critical component of the Iris Agency System, responsible for executing tasks and actions in a sandboxed environment, managing container lifecycles, and proposing changes for human review. It integrates with various subsystems, including task queues, AI models, notification systems, analysis systems, and build systems, to provide a comprehensive autonomous execution capability.
