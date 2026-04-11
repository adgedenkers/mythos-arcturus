# tools/prompt_lab/layer_test.sh

**Language:** bash
**Stream:** SYS
**Module:** Tools
**Lines:** 48

---

### Purpose
The `layer_test.sh` script runs a given message through multiple profiles and collects the results, saving them to a temporary file and copying the output to the clipboard.

### Architecture
The script is a simple bash script that:
1. Sets up environment variables and initializes a temporary file.
2. Defines an array of profiles.
3. Iterates over each profile, running a Python script (`bench.py`) with the specified profile and message.
4. Appends the results to the temporary file.
5. Copies the final output to the clipboard and prints a summary.

### Patterns
- **Sequential Execution**: The script sequentially processes each profile in the `PROFILES` array.
- **Temporary File Handling**: Uses `mktemp` to create a temporary file for storing results.

### Dependencies
- **Environment Variables**: Uses `$1` to get the message from the command line.
- **Python Script**: Depends on `/opt/mythos/.venv/bin/python3 /opt/mythos/tools/prompt_lab/bench.py` to process each profile.
- **External Tools**: Uses `xclip` to copy the results to the clipboard.

### Interfaces
- **Command Line Interface**: Accepts a message as a command-line argument.
- **Output**: Writes results to a temporary file and copies them to the clipboard.

### Database
- **No Direct Database Interaction**: The script does not interact directly with any database. However, `bench.py` might interact with databases indirectly.

### Configuration
- **Environment Variables**: Uses `$1` for the message.
- **Hardcoded Paths**: Uses hardcoded paths for the Python script and temporary file.

### Key Logic
1. **Initialization**:
   - Sets up the Python script path (`$BENCH`).
   - Sets the message (`$MSG`), defaulting to "hey whats up" if no argument is provided.
   - Creates a temporary file for results (`$OUT`).

2. **Profile Iteration**:
   - Iterates over each profile in the `PROFILES` array.
   - Runs the `bench.py` script with the current profile and message.
   - Appends the results to the temporary file.

3. **Finalization**:
   - Copies the results to the clipboard.
   - Prints a summary of the completed profiles.

### Integration Points
- **Python Script**: Integrates with the `bench.py` script to process each profile.
- **Clipboard**: Integrates with `xclip` to copy the results to the clipboard.
- **Command Line**: Integrates with the command line to accept a message as input.

### Detailed Breakdown
1. **Initialization**:
   ```bash
   set -e
   BENCH="/opt/mythos/.venv/bin/python3 /opt/mythos/tools/prompt_lab/bench.py"
   MSG="${1:-hey whats up}"
   OUT=$(mktemp /tmp/bench_results_XXXX.txt)
   ```

2. **Profile Array**:
   ```bash
   PROFILES=(
       naked
       identity_only
       identity_personality
       identity_personality_voice
       full_no_life
       full_stack
   )
   ```

3. **Header Writing**:
   ```bash
   echo "=== LAYER ISOLATION TEST ===" > "$OUT"
   echo "Message: $MSG" >> "$OUT"
   echo "Model: qwen2.5:32b" >> "$OUT"
   echo "Date: $(date)" >> "$OUT"
   echo "Profiles: ${#PROFILES[@]}" >> "$OUT"
   ```

4. **Profile Iteration**:
   ```bash
   for i in "${!PROFILES[@]}"; do
       p="${PROFILES[$i]}"
       n=$((i + 1))
       echo -n "[$n/${#PROFILES[@]}] $p..."
       echo "" >> "$OUT"
       echo "================================================================" >> "$OUT"
       echo "PROFILE: $p ($n/${#PROFILES[@]})" >> "$OUT"
       echo "================================================================" >> "$OUT"
       $BENCH --profile "$p" -m "$MSG" >> "$OUT" 2>&1
       echo " done"
   done
   ```

5. **Finalization**:
   ```bash
   echo "" >> "$OUT"
   echo "================================================================" >> "$OUT"
   echo "END OF LAYER ISOLATION TEST" >> "$OUT"
   echo "================================================================" >> "$OUT"

   cat "$OUT" | xclip -selection clipboard
   echo ""
   echo "✓ All ${#PROFILES[@]} profiles complete"
   echo "✓ Results copied to clipboard"
   echo "✓ Also saved: $OUT"
   ```

This script provides a systematic way to test and compare different profiles by running a message through each and collecting the results for analysis.
