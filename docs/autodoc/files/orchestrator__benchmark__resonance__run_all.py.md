# orchestrator/benchmark/resonance/run_all.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 97

---

### File: `orchestrator/benchmark/resonance/run_all.py`

#### Purpose
This file serves as the master runner for the Iris Resonance Benchmark, orchestrating the execution of four distinct phases of a benchmarking process. It provides command-line options to control which phases are executed.

#### Architecture
The file is structured around a single `main` function that handles command-line arguments and orchestrates the execution of different phases based on these arguments. The phases are executed sequentially, with options to skip or run specific phases.

#### Patterns
- **Command-line Argument Parsing**: Uses `argparse` to handle command-line arguments.
- **Logging**: Uses Python's `logging` module to log information to both the console and a file.

#### Dependencies
- **Standard Libraries**: `sys`, `argparse`, `logging`, `datetime`
- **Custom Modules**: `run_phase1`, `resonance_report`, `run_phase3`, `run_phase4`

#### Interfaces
- **Command-line Interface**: Exposes a command-line interface with options to control the execution of phases.
- **Logging**: Exposes logging information to both the console and a log file.

#### Database
- **PostgreSQL Tables**: `resonant`, `datetime`, `run_phase1`, `resonance_report`, `run_phase3`, `run_phase4`

#### Configuration
- **Environment Variables**: None.
- **Configuration Files**: None.

#### Key Logic
1. **Command-line Argument Parsing**: The `main` function parses command-line arguments to control which phases are executed.
2. **Phase Execution**:
   - **Phase 1**: Resonance screening, executed unless `--skip-phase1` is specified.
   - **Phase 2**: Automatically generates a report and groups models into resonant/non-resonant categories.
   - **Phase 3**: Position testing for resonant models, skipped if `--skip-phase3` is specified.
   - **Phase 4**: Padding experiment for top 3 resonant models, skipped if `--skip-phase4` is specified.
3. **Logging**: Logs the start and end of each phase, as well as the overall benchmark run.

#### Integration Points
- **Phase 1**: Integrates with `run_phase1` module to execute the resonance screening.
- **Phase 2**: Integrates with `resonance_report` module to generate a report and group models.
- **Phase 3**: Integrates with `run_phase3` module to execute position testing.
- **Phase 4**: Integrates with `run_phase4` module to execute padding experiments.

### Detailed Breakdown

#### `main` Function
- **Purpose**: Orchestrates the execution of the benchmark phases based on command-line arguments.
- **Arguments**:
  - `--phase1-only`: Runs only Phase 1.
  - `--skip-phase1`: Skips Phase 1.
  - `--skip-phase3`: Skips Phase 3.
  - `--skip-phase4`: Skips Phase 4.
  - `--models`: Overrides the model list for all phases.
- **Flow**:
  1. Parses command-line arguments.
  2. Logs the start of the benchmark.
  3. Executes Phase 1 if not skipped.
  4. Generates a report and groups models after Phase 1.
  5. Executes Phase 3 if not skipped.
  6. Executes Phase 4 if not skipped.
  7. Logs the completion of the benchmark.

#### Logging
- **Configuration**: Configures logging to output to both the console and a file (`/opt/mythos/orchestrator/benchmark/resonance/benchmark.log`).
- **Usage**: Logs the start and end of each phase, as well as the overall benchmark run.

#### Database Interactions
- **PostgreSQL**: Interacts with multiple tables (`resonant`, `datetime`, `run_phase1`, `resonance_report`, `run_phase3`, `run_phase4`) to store and retrieve data related to the benchmark phases.

#### Custom Modules
- **`run_phase1`**: Contains the logic for Phase 1 (resonance screening).
- **`resonance_report`**: Contains the logic for generating reports and grouping models.
- **`run_phase3`**: Contains the logic for Phase 3 (position testing).
- **`run_phase4`**: Contains the logic for Phase 4 (padding experiments).

This file serves as the central orchestrator for the Iris Resonance Benchmark, providing a flexible and configurable way to execute the benchmark phases.
