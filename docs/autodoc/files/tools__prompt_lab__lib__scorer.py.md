# tools/prompt_lab/lib/scorer.py

**Language:** python
**Stream:** SYS
**Module:** Tools
**Lines:** 234

---

### File: tools/prompt_lab/lib/scorer.py

#### Purpose
This file contains functions to score and analyze responses from an AI system (Iris) for quality and anti-patterns. It provides a detailed scorecard and flags for various anti-patterns and quality metrics.

#### Architecture
The file consists of several top-level functions:
- `score_response`: The main function that processes the response text and returns a detailed scorecard.
- `_detect_bullets`: Helper function to detect bullet points and numbered lists.
- `_find_matches`: Helper function to find specific phrases in the text.
- `format_scorecard`: Formats the scorecard into a human-readable string.

The file uses dictionaries and lists to store anti-pattern phrases and to compile the results.

#### Patterns
- **Helper Functions**: `_detect_bullets` and `_find_matches` are helper functions used by `score_response`.
- **Configuration Handling**: The `score_response` function accepts a `test_config` dictionary to handle test-specific expectations.

#### Dependencies
- `typing` module for type hints.
- No direct database interactions are present in this file.

#### Interfaces
- **`score_response`**: Exposes a function to score a response text and return a detailed dictionary with various flags, counts, and a quality score.
- **`format_scorecard`**: Exposes a function to format the scorecard into a human-readable string.

#### Database
- No direct database interactions are present in this file. The DB references mentioned (`typing` and `what`) are likely placeholders or misinterpretations.

#### Configuration
- The `score_response` function accepts a `test_config` dictionary which can be used to specify test-specific expectations.

#### Key Logic
1. **Anti-pattern Detection**:
   - Detects corporate openers and closers.
   - Identifies hedge phrases and assistant patterns.
   - Detects meta-commentary and life dump signals.
2. **Quality Scoring**:
   - Computes a quality score based on the presence of anti-patterns.
   - Applies penalties for specific anti-patterns.
3. **Test-specific Expectations**:
   - Handles test-specific expectations like no bullets, no life dump, and maximum word count.
4. **Formatting**:
   - `format_scorecard` formats the scorecard into a human-readable string.

#### Integration Points
- This file is likely integrated into the Mythos system to analyze and score responses from the AI system (Iris). It could be used in testing and monitoring the quality of AI-generated responses.
- The `score_response` function can be called from other parts of the system to evaluate responses.
- The `format_scorecard` function can be used to present the results in a readable format for users or logging purposes.

### Detailed Analysis

#### `score_response`
- **Purpose**: Scores a response for quality signals and anti-patterns, returning a detailed dictionary.
- **Parameters**:
  - `response_text`: The text of the response to be scored.
  - `test_config`: Optional dictionary for test-specific expectations.
- **Returns**: A dictionary with flags, counts, score, penalties, and detailed information.
- **Logic**:
  - Converts the response text to lowercase for case-insensitive matching.
  - Detects bullet points and numbered lists.
  - Identifies various anti-patterns (corporate openers/closers, hedge phrases, assistant patterns, meta-commentary).
  - Computes a quality score with penalties for anti-patterns.
  - Handles test-specific expectations and applies penalties accordingly.

#### `_detect_bullets`
- **Purpose**: Detects bullet points and numbered lists in the response text.
- **Parameters**: `lines` — a list of lines from the response text.
- **Returns**: A list of detected bullet lines.
- **Logic**: Checks each line for bullet characters and numbered list patterns.

#### `_find_matches`
- **Purpose**: Finds specific phrases in the text.
- **Parameters**:
  - `text_lower`: The lowercase text to search.
  - `phrases`: A list of phrases to find.
- **Returns**: A list of phrases found in the text.

#### `format_scorecard`
- **Purpose**: Formats the scorecard into a human-readable string.
- **Parameters**:
  - `result`: A dictionary containing the result data.
  - `score_data`: A dictionary containing the score and detailed information.
- **Returns**: A formatted string representing the scorecard.
- **Logic**: Constructs a formatted string with model information, time, score, penalties, flags, and test-specific expectations.

This file plays a crucial role in ensuring the quality and adherence to standards of AI-generated responses in the Mythos system.
