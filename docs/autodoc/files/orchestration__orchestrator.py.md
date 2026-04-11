# orchestration/orchestrator.py

**Language:** python
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 712

---

### Documentation for `orchestration/orchestrator.py`

#### Purpose
This file contains the core orchestration logic for the Mythos system, including loading patterns, gathering context, executing stages, and synthesizing final outputs. It serves as the main entry point for orchestrating tasks based on predefined patterns.

#### Architecture
The file is structured around several key classes and functions:
- **Classes**:
  - `StageStatus`: An enumeration representing the status of a stage (e.g., PENDING, RUNNING, COMPLETED).
  - `StageResult`: A dataclass holding the results of a stage execution.
  - `ExecutionContext`: A dataclass that holds all context and stage outputs for an orchestration run.
- **Functions**:
  - Top-level functions handle various orchestration tasks such as loading patterns, rendering templates, gathering context, executing stages, and synthesizing outputs.

#### Patterns
- **Factory Pattern**: The `load_pattern` function can be seen as a factory method that loads and returns pattern definitions.
- **Singleton Pattern**: The `ExecutionContext` class can be used as a singleton to maintain state across different stages of an orchestration run.
- **Observer Pattern**: The `ExecutionContext` class observes and updates context and stage results throughout the orchestration process.

#### Dependencies
- **Imports**: The file imports modules such as `json`, `os`, `sys`, `time`, `subprocess`, `asyncio`, `logging`, `re`, `argparse`, `pathlib`, `datetime`, `typing`, and `dataclasses`.
- **External Libraries**: Uses `anthropic` for LLM API calls (though currently placeholder).

#### Interfaces
- **Public Functions**:
  - `load_pattern(pattern_id: str) -> dict`: Loads a pattern definition from the patterns directory.
  - `list_patterns() -> list[dict]`: Lists all available patterns with basic info.
  - `render_template(template: str, ctx: ExecutionContext) -> str`: Replaces placeholders in a template with values from the context.
  - `gather_context(pattern: dict, ctx: ExecutionContext) -> None`: Runs context-gathering commands and loads files.
  - `call_llm(prompt: str, model_pref: str, max_tokens: int = 4096, temperature: float = 0.2) -> dict`: Calls an LLM via the Anthropic API.
  - `can_run_stage(stage: dict, ctx: ExecutionContext) -> bool`: Checks if all dependencies for a stage are satisfied.
  - `execute_stage(stage: dict, ctx: ExecutionContext) -> StageResult`: Executes a single stage.
  - `should_skip_stage(stage: dict, ctx: ExecutionContext) -> bool`: Evaluates skip conditions for a stage.
  - `execute_stages(pattern: dict, ctx: ExecutionContext) -> None`: Executes all stages respecting dependency ordering and skip conditions.
  - `synthesize(pattern: dict, ctx: ExecutionContext) -> None`: Runs the synthesis step to combine all stage outputs.
  - `save_execution_log(ctx: ExecutionContext, synthesis_result: Any) -> None`: Saves a complete execution log for the run.
  - `dry_run(pattern: dict, ctx: ExecutionContext) -> None`: Shows what would happen without executing anything.
  - `run_orchestration(pattern_id: str, user_request: str, variables: dict, dry: bool) -> None`: Main orchestration entry point.

#### Database
- **References**: The file does not directly interact with PostgreSQL or Neo4j databases. However, it references `pathlib` and `datetime` which might be used in database interactions elsewhere in the system.

#### Configuration
- **Environment Variables**: No direct use of environment variables.
- **Config Files**: Uses predefined directories and paths like `PATTERNS_DIR`, `EXECUTION_LOG_DIR`, and `CONTEXT_CACHE_DIR`.

#### Key Logic
- **Pattern Loading**: Loads and parses JSON pattern definitions.
- **Context Gathering**: Runs commands and loads files to gather context.
- **Stage Execution**: Executes stages based on their defined execution mode (LLM, script, hybrid).
- **Dependency Checking**: Ensures stages are executed only when their dependencies are satisfied.
- **Synthesis**: Combines outputs from all stages to produce the final output.

#### Integration Points
- **Pattern Definitions**: Integrates with pattern definitions stored in JSON files.
- **LLM API**: Placeholder for calling the Anthropic API or a local model via Ollama.
- **Subprocesses**: Uses `subprocess` to run external scripts and commands.
- **Logging**: Uses Python's `logging` module to log orchestration progress and errors.

This file serves as the core orchestration engine for the Mythos system, handling the entire lifecycle from pattern loading to final output synthesis.
