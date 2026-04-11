# orchestrator/benchmark/resonance/resonance_config.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 504

---

### File: orchestrator/benchmark/resonance/resonance_config.py

#### Purpose
This file contains configuration settings and definitions for the Iris Resonance Benchmark, which is designed to test model resonance, prompt depth, and padding effects across four phases. It includes lists of models to be tested, prompt configurations, and specific test prompts for Phase 1.

#### Architecture
The file is structured into several sections, each defining different aspects of the benchmark configuration:
- **Models**: Lists of models to be tested and a judge model.
- **Prompt Configurations**: Different configurations of prompt layers and personality overrides.
- **Test Prompts**: Specific prompts and rubrics for Phase 1.

#### Patterns
- **Singleton Pattern**: The configuration values are defined as constants, acting as a singleton for the benchmark configuration.
- **Configuration Pattern**: The file serves as a configuration file, providing settings that are used throughout the benchmark process.

#### Dependencies
- **Imports**: No explicit imports are required as the file is a configuration file.
- **External References**: The configuration relies on external systems like Ollama (via `OLLAMA_HOST`).

#### Interfaces
- **Exposed Constants**: The file exposes several constants such as `ALL_MODELS`, `JUDGE_MODEL`, `OLLAMA_HOST`, `PROMPT_CONFIGS`, and `RESONANCE_PROMPTS` which are used by other parts of the system.

#### Database
- **PostgreSQL Tables**: The file references several PostgreSQL tables (`resonant`, `personality`, `message`, `inside`, `the`, `two`, `Montségur`, `start`) but does not interact with them directly. These tables are likely used in other parts of the system to store data related to the benchmark.

#### Configuration
- **Environment Variables**: No environment variables are used directly in this file.
- **Config Files**: The file itself acts as a configuration file, defining the benchmark settings.

#### Key Logic
- **Model List**: Defines a list of models to be tested (`ALL_MODELS`) and a judge model (`JUDGE_MODEL`).
- **Prompt Configurations**: Defines different prompt configurations (`PROMPT_CONFIGS`) with varying layers and personality overrides.
- **Test Prompts**: Defines specific test prompts (`RESONANCE_PROMPTS`) with rubrics for evaluating model responses.

#### Integration Points
- **Orchestrator**: The configurations defined in this file are used by the orchestrator to manage and execute the benchmark phases.
- **Ollama**: The `OLLAMA_HOST` constant is used to connect to the Ollama service for model interactions.
- **Database**: The PostgreSQL tables referenced are likely used to store and retrieve data related to the benchmark, such as model responses and evaluation results.

### Summary
This configuration file sets up the parameters and test cases for the Iris Resonance Benchmark. It defines the models to be tested, different prompt configurations, and specific test prompts with evaluation rubrics. The file serves as a centralized configuration point for the benchmark, and its constants are used by other parts of the system to execute the benchmark phases.
