# orchestrator/benchmark/run_deepseek_solo.sh

**Language:** bash
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 33

---

### File: `orchestrator/benchmark/run_deepseek_solo.sh`

#### Purpose
This script is designed to run a solo benchmark for the `deepseek-r1:32b` model once it has been downloaded and is available. It dynamically generates a configuration file and executes the benchmark using the specified model.

#### Architecture
The script follows a linear flow:
1. Changes directory to `/opt/mythos/orchestrator/benchmark`.
2. Checks if the `deepseek-r1:32b` model is available using `ollama list`.
3. Generates a configuration file (`bench_config_deepseek.json`) using Python.
4. Executes the benchmark using `run_benchmark.py` with the generated configuration.

#### Patterns
- **Scripting**: The script uses bash scripting to orchestrate the benchmark process.
- **Dynamic Configuration**: Uses Python to dynamically generate a configuration file based on an existing template.

#### Dependencies
- **External Commands**: `ollama list`, `cd`, `echo`, `grep`.
- **Python**: `/opt/mythos/.venv/bin/python3` for dynamic configuration generation.
- **Files**: `bench_config_round2.json` for the base configuration.

#### Interfaces
- **Command Line Arguments**: The script accepts command line arguments and passes them to `run_benchmark.py`.

#### Database
- **No Direct Database Interaction**: This script does not directly interact with PostgreSQL, Neo4j, or Redis. However, the benchmark results might be stored in one of these databases by `run_benchmark.py`.

#### Configuration
- **Environment Variables**: None used directly.
- **Config Files**: `bench_config_round2.json` is used as a base template for generating the benchmark configuration.

#### Key Logic
1. **Model Availability Check**: Ensures the `deepseek-r1:32b` model is available before proceeding.
2. **Dynamic Configuration Generation**: Modifies the base configuration to include only the `deepseek-r1:32b` model and sets specific parameters for the solo run.
3. **Benchmark Execution**: Invokes `run_benchmark.py` with the generated configuration.

#### Integration Points
- **Ollama**: Uses `ollama list` to check model availability.
- **Python Script**: Uses `/opt/mythos/.venv/bin/python3` to dynamically generate the configuration file.
- **Benchmark Runner**: Executes `run_benchmark.py` to run the benchmark with the generated configuration.

### Detailed Breakdown

1. **Model Availability Check**:
   ```bash
   if ! ollama list | grep -q "deepseek-r1:32b"; then
       echo "❌ deepseek-r1:32b not yet available — still downloading?"
       echo "   Check with: ollama list"
       exit 1
   fi
   ```
   - This block checks if the `deepseek-r1:32b` model is available using `ollama list`. If not, it prints an error message and exits.

2. **Dynamic Configuration Generation**:
   ```bash
   /opt/mythos/.venv/bin/python3 -c "
   import json, pathlib
   cfg = json.loads(pathlib.Path("bench_config_round2.json").read_text())
   cfg["models"] = ["deepseek-r1:32b"]
   cfg["run_id_prefix"] = "deepseek_solo"
   cfg["notes"] = "DeepSeek-R1:32b solo run for comparison against Round 2"
   pathlib.Path("bench_config_deepseek.json").write_text(json.dumps(cfg, indent=2))
   print("Config written")
   "
   ```
   - This block uses Python to read `bench_config_round2.json`, modifies it to include only the `deepseek-r1:32b` model, sets a run ID prefix, and adds notes. The modified configuration is then written to `bench_config_deepseek.json`.

3. **Benchmark Execution**:
   ```bash
   /opt/mythos/.venv/bin/python3 run_benchmark.py --config bench_config_deepseek.json "$@"
   ```
   - This line executes the benchmark using `run_benchmark.py` with the generated configuration file and any additional command line arguments passed to the script.

This script is a crucial part of the benchmarking process for the `deepseek-r1:32b` model, ensuring that the model is available and dynamically configuring the benchmark to run with the specified model.
