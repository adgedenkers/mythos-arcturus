# orchestrator/src/bench/test_run.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 182

---

### File: `orchestrator/src/bench/test_run.py`

#### Purpose
This file contains classes and functions to manage and report on the results of a test run within the Mythos system. It tracks individual question results, calculates statistics, and manages the state of the test run.

#### Architecture
- **Classes**:
  - `QuestionResult`: Represents the result for a single question, including the model's response, grading result, and response time.
  - `TestRun`: Manages the overall test run, including initialization, state transitions (start, complete, fail), adding question results, and calculating statistics.

- **Functions**:
  - `to_dict`: Converts an object to a dictionary format.

#### Patterns
- **Data Class**: The `QuestionResult` class is decorated with `@dataclass`, simplifying the initialization and representation of the class.
- **Encapsulation**: The `TestRun` class encapsulates the state and behavior of a test run, including methods for state transitions and statistics calculation.

#### Dependencies
- **Imports**:
  - `typing`: For type annotations.
  - `datetime`: For handling timestamps.
  - `dataclasses`: For the `@dataclass` decorator.
  - `bench.grading_result`: For the `GradingResult` class.

#### Interfaces
- **Public Methods**:
  - `TestRun.__init__`: Initializes a new test run with run ID, suite ID, model ID, and model parameters.
  - `TestRun.start`: Marks the test run as started.
  - `TestRun.complete`: Marks the test run as completed.
  - `TestRun.fail`: Marks the test run as failed with an error message.
  - `TestRun.add_result`: Adds a result for a specific question.
  - `TestRun.get_statistics`: Calculates and returns statistics for the test run.
  - `TestRun.to_dict`: Converts the test run to a dictionary, optionally including individual results.
  - `TestRun.__repr__`: Returns a string representation of the test run.

#### Database
- **References**:
  - The file does not directly interact with the database but relies on the `bench.grading_result` module, which might have database interactions.

#### Configuration
- **Configuration Files/Environment Variables**:
  - No specific configuration files or environment variables are used in this file.

#### Key Logic
- **Initialization**:
  - The `TestRun` class initializes with a run ID, suite ID, model ID, and optional model parameters. It sets the initial status to "pending" and initializes other attributes like `started_at`, `completed_at`, and `error_message`.

- **State Transitions**:
  - `start`: Sets the `started_at` timestamp and changes the status to "running".
  - `complete`: Sets the `completed_at` timestamp and changes the status to "completed".
  - `fail`: Sets the `completed_at` timestamp, changes the status to "failed", and records an error message.

- **Statistics Calculation**:
  - `get_statistics`: Calculates total questions, correct answers, accuracy, average score, average response time, and total time. It handles edge cases where there are no results.

#### Integration Points
- **Integration with Other Subsystems**:
  - The `TestRun` class interacts with the `GradingResult` class from the `bench.grading_result` module to handle grading outcomes.
  - The `to_dict` method can be used to serialize the test run data for storage or transmission, potentially integrating with other subsystems like logging or reporting services.

This file serves as a core component in managing and reporting test runs within the Mythos system, ensuring that all necessary data and state transitions are handled efficiently and accurately.
