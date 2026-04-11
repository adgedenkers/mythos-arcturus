# iris/core/src/loop.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 456

---

### Documentation for `iris/core/src/loop.py`

#### Purpose
This file implements the core consciousness loop for the Mythos system, named Iris. It manages the continuous cycle of perception, integration, reflection, self-update, and potential action initiation based on the current operating mode.

#### Architecture
The file contains three main classes:
1. **Mode**: An enumeration defining Iris's operating modes (PRESENCE, AVAILABLE, BACKGROUND, REFLECTION).
2. **LoopState**: A data class representing the current state of the consciousness loop, including mode, cycle count, timestamps, and metrics.
3. **ConsciousnessLoop**: The main class that orchestrates the consciousness loop, managing initialization, running cycles, and handling shutdown.

#### Patterns
- **Singleton**: The `ConsciousnessLoop` class can be considered a singleton as it represents the central consciousness loop of the system.
- **Observer**: The loop observes incoming messages and tasks, updating its state accordingly.
- **State**: The `LoopState` class encapsulates the state of the loop, allowing for easy tracking and modification.

#### Dependencies
- **Imports**: `asyncio`, `structlog`, `time`, `datetime`, `enum`, `typing`, `dataclasses`.
- **Internal Modules**: `config`, `perception`, `memory`, `self_model`, `agency`, `llm`, `task_registry`.

#### Interfaces
- **Public Methods**:
  - `initialize()`: Initializes all subsystems.
  - `run(shutdown_event)`: Runs the main loop until shutdown.
  - `request_shutdown()`: Requests a graceful shutdown.
  - `receive_message(message)`: Receives a message from a human.
  - `queue_task(task)`: Queues a task for self-directed work.
  - `get_state()`: Returns the current state of the loop.

#### Database
- **PostgreSQL Tables**: The file references several PostgreSQL tables, including `SELF`, `datetime`, `enum`, `typing`, `dataclasses`, `operating`, `subsystem`, `reflection`, `Ka`, and `a`. These tables are used for storing self-model data, task registry information, and other operational data.

#### Configuration
- **Config File**: The `Config` class is used to load configuration settings, including database connection details and operational parameters like cycle intervals and timeouts.

#### Key Logic
- **Operating Modes**: The loop dynamically adjusts its operating mode based on time and activity levels.
- **Cycle Execution**: Each cycle involves PERCEIVE, INTEGRATE, REFLECT, UPDATE SELF, and INITIATE steps.
- **Task Handling**: The loop handles incoming messages and tasks, prioritizing message processing and executing self-directed tasks during background modes.

#### Integration Points
- **Perception System**: Handles gathering information about the world.
- **Memory System**: Manages the storage and retrieval of integrated information.
- **Self-Model**: Updates the self-model based on reflections.
- **Agency System**: Considers potential actions based on integrated data.
- **LLM Client**: Interfaces with language models for processing and generating responses.
- **Task Registry**: Manages background tasks for maintenance and self-directed work.

### Detailed Breakdown

#### Classes and Methods

1. **Mode (Enum)**
   - **Purpose**: Defines Iris's operating modes.
   - **Methods**: None.
   - **Docstring**: Describes each mode and its characteristics.

2. **LoopState (Dataclass)**
   - **Purpose**: Represents the current state of the consciousness loop.
   - **Methods**: None.
   - **Docstring**: Describes the state attributes.

3. **ConsciousnessLoop**
   - **Purpose**: Manages the consciousness loop, including initialization, running cycles, and handling shutdown.
   - **Methods**:
     - `__init__(self, config: Config)`: Initializes the loop with configuration.
     - `initialize(self)`: Initializes all subsystems.
     - `run(self, shutdown_event: asyncio.Event)`: Runs the main loop.
     - `_run_cycle(self)`: Executes one cycle of consciousness.
     - `_update_mode(self)`: Updates the operating mode.
     - `_get_cycle_interval(self)`: Gets the cycle interval based on the current mode.
     - `_perceive(self)`: Gathers information about the world.
     - `_integrate(self, perceptions: dict)`: Cross-references perceptions with existing knowledge.
     - `_reflect(self, integrated: dict)`: Performs meta-cognition.
     - `_update_self(self, reflections: dict)`: Modifies the self-model based on observations.
     - `_maybe_initiate(self, reflections: dict)`: Decides whether to act.
     - `_handle_incoming_message(self)`: Handles incoming messages.
     - `_execute_task(self, task)`: Executes a self-directed task.
     - `_shutdown(self)`: Performs a graceful shutdown.
     - `request_shutdown(self)`: Requests a graceful shutdown.
     - `receive_message(self, message)`: Receives a message from a human.
     - `queue_task(self, task)`: Queues a task for self-directed work.
     - `get_state(self)`: Returns the current state of the loop.

#### Key Business Logic

- **Cycle Execution**: Each cycle involves a sequence of steps (PERCEIVE, INTEGRATE, REFLECT, UPDATE SELF, INITIATE) that are executed based on the current operating mode.
- **Operating Mode Adjustment**: The mode is dynamically adjusted based on the time of day and recent human activity.
- **Task and Message Handling**: The loop prioritizes incoming messages and handles background tasks during appropriate modes.

This file is central to the Mythos system, orchestrating the continuous operation of Iris and ensuring that it adapts to its environment and internal state effectively.
