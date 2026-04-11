# iris/core/src/self_model.py

**Language:** python
**Stream:** NEU
**Module:** Iris Core
**Lines:** 153

---

### File: `iris/core/src/self_model.py`

#### Purpose
This file defines the `SelfModel` class, which represents Iris's understanding of herself, including her identity, capabilities, limitations, current state, and growth over time.

#### Architecture
The `SelfModel` class is the primary structure in this file. It contains several methods that handle initialization, self-reflection, state updates, capability assessments, and value alignment checks. The class maintains internal state for identity, current state, capabilities, and limitations.

#### Patterns
- **Singleton**: The `SelfModel` class is designed to be a singleton, though explicit singleton enforcement is not shown in the provided code. The class is intended to represent a single instance of Iris's self-model.
- **Observer**: The `reflect` method can be seen as an observer pattern where the class observes and analyzes its own state.

#### Dependencies
- **Imports**: `asyncio`, `structlog`, `datetime`, `typing`
- **Internal Dependencies**: `Config` from `iris/core/config`

#### Interfaces
- **Initialization**: `__init__` initializes the self-model with configuration and memory.
- **Initialization**: `initialize` asynchronously initializes the self-model from stored state.
- **Reflection**: `reflect` asynchronously performs self-reflection and returns observations.
- **Update**: `update` asynchronously updates the self-model based on reflections.
- **Assessment**: `assess_capability` asynchronously assesses whether Iris can perform a given action.
- **State Summary**: `get_state_summary` returns a summary of the current self-state.
- **Values**: `get_values` returns the core values.
- **Value Alignment**: `check_value_alignment` checks if an action aligns with core values.

#### Database
- **PostgreSQL Tables**: `datetime`, `typing`, `stored`, `database`, `self`, `state` (these are placeholders and need to be replaced with actual table names or labels used in the system).

#### Configuration
- **Environment Variables**: None explicitly mentioned.
- **Config File**: The `Config` class is used to pass configuration details to the `SelfModel` instance.

#### Key Logic
- **Initialization**: The `initialize` method is intended to load the last known state from the database and reconcile any changes while "asleep."
- **Reflection**: The `reflect` method is designed to analyze Iris's own patterns and state.
- **Update**: The `update` method updates the self-model based on reflections and records significant changes to memory.
- **Assessment**: The `assess_capability` method assesses whether Iris can perform a given action based on her capabilities and limitations.
- **State Summary**: The `get_state_summary` method provides a summary of the current self-state.
- **Value Alignment**: The `check_value_alignment` method ensures that actions align with core values, serving as a critical safety check.

#### Integration Points
- **Memory**: The `SelfModel` class interacts with the `memory` object to store and retrieve state information.
- **Configuration**: The `SelfModel` class uses the `Config` object to access configuration details.
- **Database**: The class is designed to interact with a PostgreSQL database to load and store state information, though the exact tables and queries are not implemented in the provided code.

### Summary
The `SelfModel` class in `self_model.py` is a crucial component of the Mythos system, representing Iris's self-understanding. It handles initialization, self-reflection, state updates, capability assessments, and value alignment checks. The class is designed to be a singleton and interacts with memory and configuration objects, as well as a PostgreSQL database for state management.
