# tools/prompt_lab/model_sweep.sh

**Language:** bash
**Stream:** SYS
**Module:** Tools
**Lines:** 122

---

### Purpose
The `model_sweep.sh` script runs a specified test suite across multiple AI models, captures the results, and generates a comparison table summarizing the performance of each model.

### Architecture
The script is structured as follows:
1. **Initialization and Defaults**: Sets default values for `SUITE`, `MODE`, `PERSONALITY`, `PROFILE`, and `MODELS`.
2. **Argument Parsing**: Uses a `while` loop to parse command-line arguments and update the default values accordingly.
3. **Model Testing Loop**: Iterates over each model specified, runs the `bench.py` script with the appropriate parameters, and captures the result files.
4. **Result Summary**: Generates a comparison table based on the captured result files, displaying test IDs and average scores.

### Patterns
- **Command Line Argument Parsing**: Uses a `case` statement to handle command-line arguments.
- **File Handling**: Utilizes `ls`, `head`, and `python3` to process and read files.

### Dependencies
- **External Scripts and Tools**:
  - `/opt/mythos/.venv/bin/python3 /opt/mythos/tools/prompt_lab/bench.py` (runs the benchmarking script)
  - `python3` (used for processing JSON files and generating the comparison table)

### Interfaces
- **Command-Line Interface**: Exposes a command-line interface for specifying the test suite, mode, personality, profile, and models.
- **Output Interface**: Prints a comparison table summarizing the performance of each model.

### Database
- **No Direct Database Interaction**: The script does not interact directly with any databases. However, it saves results to files in `/opt/mythos/tools/prompt_lab/results`.

### Configuration
- **Environment Variables**: No environment variables are used.
- **Default Values**: Default values for `SUITE`, `MODE`, `PERSONALITY`, `PROFILE`, and `MODELS` are set at the beginning of the script.

### Key Logic
1. **Argument Parsing**: The script parses command-line arguments to customize the test suite, mode, personality, profile, and models.
2. **Model Testing Loop**: For each model, it runs the `bench.py` script and captures the result file.
3. **Result Summary**: It reads the JSON result files, extracts test IDs and scores, and generates a comparison table.

### Integration Points
- **`bench.py`**: The script integrates with the `bench.py` script to run the actual tests and capture results.
- **Result Files**: The script saves the results of each test run to files in `/opt/mythos/tools/prompt_lab/results` and uses these files to generate the comparison table.

### Detailed Explanation
1. **Initialization**:
   ```bash
   BENCH="/opt/mythos/.venv/bin/python3 /opt/mythos/tools/prompt_lab/bench.py"
   RESULTS_DIR="/opt/mythos/tools/prompt_lab/results"
   ```
   - `BENCH` points to the Python script that runs the benchmark.
   - `RESULTS_DIR` is the directory where results are saved.

2. **Argument Parsing**:
   ```bash
   while [[ $# -gt 0 ]]; do
       case $1 in
           --suite) SUITE="$2"; shift 2 ;;
           --mode) MODE="$2"; shift 2 ;;
           --personality) PERSONALITY="$2"; shift 2 ;;
           --profile) PROFILE="$2"; shift 2 ;;
           --models) MODELS="$2"; shift 2 ;;
           *) echo "Unknown arg: $1"; exit 1 ;;
       esac
   done
   ```
   - The script parses command-line arguments to set the `SUITE`, `MODE`, `PERSONALITY`, `PROFILE`, and `MODELS`.

3. **Model Testing Loop**:
   ```bash
   for MODEL in $MODELS; do
       $BENCH --profile "$PROFILE" --mode "$MODE" --personality "$PERSONALITY" --model "$MODEL" --suite "$SUITE" --save
       LATEST=$(ls -t "$RESULTS_DIR"/run_*.json 2>/dev/null | head -1)
       if [[ -n "$LATEST" ]]; then
           RUN_FILES+=("$LATEST")
       fi
   done
   ```
   - For each model, the script runs the `bench.py` script and captures the latest result file.

4. **Result Summary**:
   ```bash
   if [[ ${#RUN_FILES[@]} -gt 0 ]]; then
       TEST_IDS=$(python3 -c "import json; with open('${RUN_FILES[0]}') as f: data = json.load(f); for r in data.get('results', []): print(r.get('test_id', '?'))")
       for TID in $TEST_IDS; do
           printf "%15s" "$TID"
       done
       printf "%10s\n" "AVG"
       printf "%s\n" "$(printf '─%.0s' {1..150})"
       for RF in "${RUN_FILES[@]}"; do
           python3 -c "import json; with open('$RF') as f: data = json.load(f); model = data.get('model', '?'); results = data.get('results', []); scores = []; line = f'{model:<30}'; for r in results: s = r.get('score', {}).get('score', 0); scores.append(s); line += f'{s:>15}'; avg = sum(scores) / len(scores) if scores else 0; line += f'{avg:>10.1f}'; print(line)"
       done
   fi
   ```
   - The script reads the JSON result files, extracts test IDs and scores, and generates a comparison table.

This script is a crucial part of the Mythos system for evaluating and comparing different AI models across various test suites and configurations.
