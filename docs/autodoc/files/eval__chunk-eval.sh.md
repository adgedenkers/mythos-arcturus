# eval/chunk-eval.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 76

---

### File: `eval/chunk-eval.sh`

#### Purpose
This script serves as a convenience wrapper for running evaluation tasks using the Ollama chunk builder. It supports listing available challenges, listing available models, comparing results for a specific challenge, and running a specific challenge with optional model and iteration parameters.

#### Architecture
The script is structured as a series of conditional checks and commands. It uses environment variables and command-line arguments to determine the action to take. The core logic involves invoking a Python script (`ollama_builder.py`) with different arguments based on the user input.

#### Patterns
- **Command Pattern**: The script acts as a command dispatcher, routing different command-line arguments to specific actions.
- **Guard Clause**: Early exits are used to handle invalid commands or missing files.

#### Dependencies
- **Environment Variables**: `EVAL_DIR`, `PYTHON`, `BUILDER`
- **External Scripts**: `ollama_builder.py`
- **System Commands**: `python3`, `find`, `basename`, `dirname`, `bc`

#### Interfaces
- **Command-Line Arguments**:
  - `--list`: List available challenges.
  - `--models`: List available models.
  - `--compare <challenge_id>`: Compare results for a specific challenge.
  - `<challenge_id> [model] [max_iterations]`: Run a specific challenge with optional model and iteration parameters.

#### Database
- **No direct database interaction**. However, it reads from and writes to files in the `results` directory, which could be considered a form of data storage.

#### Configuration
- **Environment Variables**:
  - `EVAL_DIR`: Directory path for evaluation files.
  - `PYTHON`: Path to the Python interpreter.
  - `BUILDER`: Path to the Python script (`ollama_builder.py`).

#### Key Logic
1. **List Challenges**: Invokes `ollama_builder.py` with `--list-challenges` to list available challenges.
2. **List Models**: Invokes `ollama_builder.py` with `--list-models` to list available models.
3. **Compare Results**: Iterates over JSON files in the results directory for a given challenge, extracting and formatting model results.
4. **Run Challenge**: Invokes `ollama_builder.py` with the specified challenge, model, and maximum iterations.

#### Integration Points
- **Python Script (`ollama_builder.py`)**: The script heavily relies on this Python script for performing the actual evaluation tasks.
- **File System**: Reads from and writes to files in the `EVAL_DIR` directory, particularly in the `challenges` and `results` subdirectories.

### Detailed Breakdown

1. **List Challenges**:
   ```bash
   if [ "$1" == "--list" ]; then
       $PYTHON "$BUILDER" --list-challenges
       exit 0
   fi
   ```
   - Invokes `ollama_builder.py` with `--list-challenges` to list available challenges.

2. **List Models**:
   ```bash
   if [ "$1" == "--models" ]; then
       $PYTHON "$BUILDER" --list-models
       exit 0
   fi
   ```
   - Invokes `ollama_builder.py` with `--list-models` to list available models.

3. **Compare Results**:
   ```bash
   if [ "$1" == "--compare" ]; then
       CHALLENGE="${2:?Usage: chunk-eval --compare <challenge_id>}"
       RESULTS_DIR="$EVAL_DIR/results/$CHALLENGE"
       if [ ! -d "$RESULTS_DIR" ]; then
           echo "No results found for challenge: $CHALLENGE"
           exit 1
       fi
       echo ""
       echo "=== Results for challenge: $CHALLENGE ==="
       echo ""
       for report in $(find "$RESULTS_DIR" -name "report.json" -type f | sort); do
           MODEL=$(python3 -c "import json; print(json.load(open('$report'))['model'])")
           SCORE=$(python3 -c "import json; print(json.load(open('$report'))['best_composite_score'])")
           PASS=$(python3 -c "import json; print('PASS' if json.load(open('$report'))['final_pass'] else 'FAIL')")
           ITERS=$(python3 -c "import json; print(json.load(open('$report'))['iterations_used'])")
           TIMESTAMP=$(basename "$(dirname "$report")")
           printf "  %-25s  Score: %.1f%%  %s  Iters: %s  (%s)\n" "$MODEL" "$(echo "$SCORE * 100" | bc)" "$PASS" "$ITERS" "$TIMESTAMP"
       done
       echo ""
       exit 0
   fi
   ```
   - Checks if the challenge directory exists.
   - Iterates over JSON report files in the results directory, extracting and formatting model results.

4. **Run Challenge**:
   ```bash
   CHALLENGE="${1:?Usage: chunk-eval <challenge_id> [model] [max_iterations]}"
   MODEL="${2:-qwen3-coder:30b}"
   MAX_ITER="${3:-5}"
   SPEC="$EVAL_DIR/challenges/$CHALLENGE/challenge_spec.json"
   if [ ! -f "$SPEC" ]; then
       echo "Challenge not found: $SPEC"
       echo "Available challenges:"
       $PYTHON "$BUILDER" --list-challenges
       exit 1
   fi
   echo ""
   echo "╔══════════════════════════════════════════════╗"
   echo "║         CHUNK FACTORY — Eval Run             ║"
   echo "╠══════════════════════════════════════════════╣"
   echo "║  Challenge: $CHALLENGE"
   echo "║  Model:     $MODEL"
   echo "║  Max iter:  $MAX_ITER"
   echo "╚══════════════════════════════════════════════╝"
   echo ""
   $PYTHON "$BUILDER" \
       --challenge "$SPEC" \
       --model "$MODEL" \
       --max-iterations "$MAX_ITER" \
       --verbose
   ```
   - Validates the challenge specification file.
   - Invokes `ollama_builder.py` with the specified challenge, model, and maximum iterations.

This script acts as a high-level interface for managing and executing evaluation tasks within the Mythos system, leveraging a Python script for the heavy lifting.
