# eval/chunk-grind.sh

**Language:** bash
**Stream:** SYS
**Module:** Root / Miscellaneous
**Lines:** 44

---

### File: `eval/chunk-grind.sh`

#### Purpose
This script runs a multi-pass grinder on a specified build plan using a specified AI model and maximum number of retries. It is used to process and evaluate build plans in the Mythos system.

#### Architecture
The script is a simple bash script that:
1. Sets up environment variables for Python interpreter and grinder script paths.
2. Parses command-line arguments for the build plan ID, model, and maximum retries.
3. Checks if the build plan file exists.
4. Prints a header with the plan details.
5. Executes the grinder script with the provided parameters.

#### Patterns
No specific design patterns are used in this script. It is a straightforward procedural script.

#### Dependencies
- `/opt/mythos/.venv/bin/python3` (Python interpreter)
- `/opt/mythos/eval/ollama_grinder.py` (Python script for the grinder)
- `/opt/mythos/eval/challenges/<plan_id>/build_plan.json` (Build plan JSON file)

#### Interfaces
- **Command-line arguments**:
  - `PLAN`: The build plan ID (required).
  - `MODEL`: The AI model to use (optional, default is `qwen3-coder:30b`).
  - `MAX_RETRIES`: Maximum number of retries (optional, default is `5`).

#### Database
No direct database interactions are performed in this script.

#### Configuration
- Environment variables are not used directly in this script.
- The script relies on the existence of certain files and directories, which are expected to be configured in the system.

#### Key Logic
1. **Argument Parsing**: The script parses the command-line arguments to determine the build plan ID, model, and maximum retries.
2. **File Existence Check**: It checks if the build plan file exists and provides a list of available plans if the specified plan is not found.
3. **Execution**: It executes the grinder script with the specified parameters.

#### Integration Points
- **Build Plan**: The script reads the build plan from a JSON file located in `/opt/mythos/eval/challenges/<plan_id>/build_plan.json`.
- **Grinder Script**: The script invokes the Python script `/opt/mythos/eval/ollama_grinder.py` with the specified parameters to process the build plan.

### Detailed Breakdown

1. **Environment Setup**:
   ```bash
   PYTHON="/opt/mythos/.venv/bin/python3"
   GRINDER="/opt/mythos/eval/ollama_grinder.py"
   EVAL_DIR="/opt/mythos/eval"
   ```

2. **Argument Parsing**:
   ```bash
   PLAN="${1:?Usage: chunk-grind <plan_id> [model] [max_retries]}"
   MODEL="${2:-qwen3-coder:30b}"
   MAX_RETRIES="${3:-5}"
   ```

3. **File Existence Check**:
   ```bash
   PLAN_FILE="$EVAL_DIR/challenges/$PLAN/build_plan.json"
   if [ ! -f "$PLAN_FILE" ]; then
       echo "Build plan not found: $PLAN_FILE"
       echo ""
       echo "Available plans:"
       find "$EVAL_DIR/challenges" -name "build_plan.json" -type f 2>/dev/null | while read f; do
           DIR=$(dirname "$f")
           echo "  $(basename "$DIR")"
       done
       exit 1
   fi
   ```

4. **Header Printing**:
   ```bash
   echo ""
   echo "╔══════════════════════════════════════════════╗"
   echo "║         CHUNK GRINDER — Build Run            ║"
   echo "╠══════════════════════════════════════════════╣"
   echo "║  Plan:      $PLAN"
   echo "║  Model:     $MODEL"
   echo "║  Retries:   $MAX_RETRIES"
   echo "╚══════════════════════════════════════════════╝"
   echo ""
   ```

5. **Execution**:
   ```bash
   $PYTHON "$GRINDER" \
       --plan "$PLAN_FILE" \
       --model "$MODEL" \
       --max-retries "$MAX_RETRIES" \
       --verbose
   ```

This script serves as a command-line interface to the `ollama_grinder.py` script, allowing users to specify the build plan, AI model, and retry settings for processing and evaluation.
