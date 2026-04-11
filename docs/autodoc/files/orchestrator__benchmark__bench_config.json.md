# orchestrator/benchmark/bench_config.json

**Language:** json
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 23

---

### File: orchestrator/benchmark/bench_config.json

#### Purpose
This JSON file contains configuration settings for the benchmarking process within the Mythos system, specifying models to be used, timeout values, output directory, and other parameters necessary for running and evaluating benchmarks.

#### Architecture
The file is structured as a JSON object with several key-value pairs, each representing a specific configuration setting. The settings include lists, strings, and nested objects to define various parameters.

#### Patterns
No design patterns are applicable as this is a configuration file, not a code file.

#### Dependencies
This file is imported and read by the benchmarking subsystem of the Mythos system. It does not import or rely on any external libraries or files directly.

#### Interfaces
The file exposes configuration settings to the benchmarking subsystem, which reads these settings to configure the benchmarking process.

#### Database
This configuration file does not interact directly with any database tables or Neo4j labels. It is purely a configuration file.

#### Configuration
The file itself is a configuration file. It does not use any external config files or environment variables directly, but the values within it can be influenced by environment variables or other configuration mechanisms in the broader system.

#### Key Logic
The key logic involves setting up the environment for benchmarking by defining which models to use, the judge model, timeout values for different tasks, the maximum number of threads for models, and whether to enable the judge and retry on timeout.

#### Integration Points
This configuration file integrates with the benchmarking subsystem of the Mythos system. The benchmarking subsystem reads this file to configure itself and then uses the specified settings to run and evaluate benchmarks.

### Detailed Breakdown of Configuration Settings

1. **models**: A list of models to be used for benchmarking.
   - Example: `"gemma3:27b", "qwen2.5:32b", "deepseek-r1:32b"`

2. **judge_model**: The model used to judge the performance of the other models.
   - Example: `"gemma3:27b"`

3. **ollama_host**: The host and port for the Ollama service.
   - Example: `"http://localhost:11434"`

4. **output_dir**: The directory where benchmark results will be stored.
   - Example: `"/opt/mythos/orchestrator/benchmark/runs"`

5. **timeouts**: A nested object defining timeout values for different tasks.
   - Example:
     ```json
     {
       "reasoning": 120,
       "code": 180,
       "mythos": 120,
       "narrative": 180,
       "tool_use": 120,
       "voice": 120,
       "default": 120
     }
     ```

6. **max_model_threads**: The maximum number of threads that can be used by a model.
   - Example: `3`

7. **judge_enabled**: A boolean indicating whether the judge model is enabled.
   - Example: `true`

8. **skip_task_ids**: A list of task IDs to skip during benchmarking.
   - Example: `[]`

9. **retry_on_timeout**: A boolean indicating whether to retry a task if it times out.
   - Example: `false`

This configuration file is critical for setting up the benchmarking environment and ensuring that the benchmarking process is properly configured according to the specified parameters.
