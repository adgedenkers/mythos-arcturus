# orchestrator/src/bench/grader.py

**Language:** python
**Stream:** LOG
**Module:** LLM Orchestrator
**Lines:** 355

---

### File: orchestrator/src/bench/grader.py

#### Purpose
This file contains the `Grader` class and several top-level functions for grading model answers against correct answers using different strategies: exact string matching, numeric comparison, semantic similarity, and code comparison.

#### Architecture
The file is structured around the `Grader` class, which contains methods for various grading strategies. The `grade` method acts as a dispatcher to route to the appropriate grading method based on the specified `answer_type`. Each grading method (`grade_exact`, `grade_numeric`, `grade_semantic`, `grade_code`) performs the specific grading logic and returns a `GradingResult` object.

#### Patterns
- **Strategy Pattern**: The `grade` method uses a strategy pattern to delegate to the appropriate grading method based on the `answer_type`.
- **Helper Methods**: Private methods (`_extract_number`, `_normalize_code`) are used to perform common tasks like extracting numbers and normalizing code.

#### Dependencies
- **Imports**: `re`, `logging`, `typing` (for type hints), and `bench.grading_result` (for `GradingResult` class).
- **Database References**: References to PostgreSQL tables (`bench`, `answers`, `model`, `correct`, `text`, `typing`).

#### Interfaces
- **Public Methods**:
  - `grade`: Main method to grade a model's answer.
  - `grade_exact`: Grades using exact string matching.
  - `grade_numeric`: Grades using numeric comparison.
  - `grade_semantic`: Grades using semantic similarity.
  - `grade_code`: Grades using code comparison.
- **Private Methods**:
  - `_extract_number`: Extracts a number from text.
  - `_normalize_code`: Normalizes code for comparison.

#### Database
- **References**: The file references several PostgreSQL tables (`bench`, `answers`, `model`, `correct`, `text`, `typing`), but does not directly interact with them. The references are likely used for configuration or data retrieval in other parts of the system.

#### Configuration
- **Environment Variables**: No explicit environment variables are used.
- **Configuration Files**: No explicit configuration files are used.

#### Key Logic
- **Exact Matching (`grade_exact`)**: Compares model and correct answers with options for case sensitivity, stripping whitespace, and normalizing whitespace.
- **Numeric Comparison (`grade_numeric`)**: Compares numeric values with absolute and relative tolerances.
- **Semantic Similarity (`grade_semantic`)**: Uses Jaccard similarity based on word overlap.
- **Code Comparison (`grade_code`)**: Normalizes and compares code based on line-by-line similarity.

#### Integration Points
- **GradingResult**: The `GradingResult` class is used to encapsulate the grading results and is returned by all grading methods.
- **Logging**: Uses the `logging` module to log errors and information.
- **Regex**: Uses regular expressions (`re`) for number extraction.
- **Type Hints**: Uses `typing` for type hints in method signatures.

### Detailed Documentation

#### Class: `Grader`
- **Purpose**: Provides a framework for grading model answers against correct answers using various strategies.
- **Methods**:
  - `grade`: Main method to grade a model's answer. It routes to the appropriate grading method based on the `answer_type`.
  - `grade_exact`: Grades using exact string matching with configurable options for case sensitivity, whitespace stripping, and normalization.
  - `grade_numeric`: Grades using numeric comparison with configurable absolute and relative tolerances.
  - `grade_semantic`: Grades using semantic similarity based on word overlap.
  - `grade_code`: Grades using code comparison with normalization.
  - `_extract_number`: Helper method to extract numbers from text.
  - `_normalize_code`: Helper method to normalize code for comparison.

#### Top-Level Functions
- **grade**: A top-level function that acts as a convenience wrapper around the `Grader` class's `grade` method.

#### Example Usage
```python
grader = Grader()
result = grader.grade(
    model_answer="4",
    correct_answer="4",
    answer_type="exact"
)
if result.is_correct:
    print("Correct!")
```

#### Logging
- **Usage**: The `logging` module is used to log errors during numeric grading.

#### Database References
- **Tables**: The file references several PostgreSQL tables (`bench`, `answers`, `model`, `correct`, `text`, `typing`), but does not directly interact with them.

#### Configuration and Environment Variables
- **Configuration**: No explicit configuration files or environment variables are used.

#### Integration Points
- **GradingResult**: The `GradingResult` class is used to encapsulate the grading results and is returned by all grading methods.
- **Logging**: Uses the `logging` module to log errors and information.
- **Regex**: Uses regular expressions (`re`) for number extraction.
- **Type Hints**: Uses `typing` for type hints in method signatures.

This documentation provides a comprehensive overview of the `grader.py` file, detailing its purpose, architecture, dependencies, interfaces, and key logic.
