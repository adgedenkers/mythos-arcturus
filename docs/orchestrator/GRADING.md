# Grading System

**Phase 1.4** - Answer Validation and Scoring

---

## Overview

Phase 1.4 adds the grading infrastructure for validating model answers and assigning scores.

**Components:**
- **GradingResult** - Result of grading with score and explanation
- **Grader** - Answer validation engine

**Grading Methods:**
- Exact matching (case-sensitive/insensitive)
- Numeric comparison (with tolerance)
- Semantic similarity (word overlap)
- Code validation (normalized comparison)

---

## Quick Start

```python
from bench import Grader

grader = Grader()

# Exact match
result = grader.grade(
    model_answer="Paris",
    correct_answer="Paris",
    answer_type="exact"
)

print(result.is_correct)  # True
print(result.score)       # 1.0
```

---

## GradingResult

Result object containing grading outcome.

### Fields

```python
@dataclass
class GradingResult:
    is_correct: bool          # True if answer is correct
    score: float             # 0.0 to 1.0
    partial_credit: float    # 0.0 to 1.0 (for partial correctness)
    explanation: str         # Human-readable explanation
    details: Dict[str, Any]  # Additional details
```

### Example

```python
result = GradingResult(
    is_correct=True,
    score=1.0,
    partial_credit=0.0,
    explanation="Exact match",
    details={"method": "exact"}
)

# Convert to dict
data = result.to_dict()

# Create from dict
result = GradingResult.from_dict(data)
```

---

## Grader

Main grading engine.

### Exact Matching

Exact string comparison with options.

```python
grader = Grader()

# Case-sensitive (default)
result = grader.grade("Paris", "Paris", "exact")
# is_correct=True

# Case-insensitive
result = grader.grade(
    "paris",
    "Paris",
    "exact",
    grading_criteria={"case_sensitive": False}
)
# is_correct=True

# With whitespace normalization
result = grader.grade(
    "Hello    World",
    "Hello World",
    "exact",
    grading_criteria={"normalize_whitespace": True}
)
# is_correct=True
```

**Criteria Options:**
- `case_sensitive` (bool): Match case (default: True)
- `strip_whitespace` (bool): Strip leading/trailing (default: True)
- `normalize_whitespace` (bool): Normalize internal whitespace (default: False)

---

### Numeric Comparison

Compare numbers with tolerance.

```python
grader = Grader()

# Exact match
result = grader.grade("42", "42", "numeric")
# is_correct=True, score=1.0

# Within tolerance
result = grader.grade(
    "42.01",
    "42",
    "numeric",
    grading_criteria={"tolerance": 0.05}
)
# is_correct=True

# With partial credit
result = grader.grade(
    "45",
    "42",
    "numeric",
    grading_criteria={"tolerance": 0.01}
)
# is_correct=False, partial_credit=0.93 (close but not within tolerance)

# Extract numbers from text
result = grader.grade(
    "The answer is $42.50",
    "42.50",
    "numeric"
)
# is_correct=True
```

**Criteria Options:**
- `tolerance` (float): Absolute tolerance (default: 0.01)
- `relative_tolerance` (float): Relative tolerance (default: 0.0)

**Partial Credit:**
- If within 50% of correct answer, partial credit awarded
- Credit decreases linearly with distance from correct

---

### Semantic Similarity

Word overlap similarity (basic implementation).

```python
grader = Grader()

result = grader.grade(
    "The capital of France is Paris",
    "Paris is the capital of France",
    "semantic"
)
# High similarity score

result = grader.grade(
    "Paris",
    "The capital city of France",
    "semantic",
    grading_criteria={"threshold": 0.3}
)
# May pass with lower threshold
```

**Criteria Options:**
- `threshold` (float): Similarity threshold (default: 0.6)

**Method:**
- Jaccard similarity: |intersection| / |union| of words
- Case-insensitive word matching
- Simple but effective for many use cases

**Future Enhancements:**
- Embeddings-based similarity
- Transformer models
- Contextual understanding

---

### Code Validation

Normalized code comparison (basic implementation).

```python
grader = Grader()

result = grader.grade(
    """
    def hello():
        return "Hello"
    """,
    """
    def hello():
        return "Hello"
    """,
    "code"
)
# is_correct=True

# Handles whitespace differences
result = grader.grade(
    "def hello():\n    return 'Hello'",
    "def hello():\n        return 'Hello'",
    "code"
)
# Normalized comparison
```

**Method:**
- Normalizes whitespace
- Removes empty lines
- Compares structure

**Future Enhancements:**
- Code execution
- Test case validation
- AST-based comparison
- Linting and style checks

---

## Complete Example

```python
from bench import Grader, TestQuestion

# Create grader
grader = Grader()

# Define question
question = TestQuestion(
    text="What is 15% of 200?",
    correct_answer="30",
    answer_type="numeric",
    grading_criteria={"tolerance": 0.1}
)

# Model's answer
model_answer = "30.0"

# Grade it
result = grader.grade(
    model_answer=model_answer,
    correct_answer=question.correct_answer,
    answer_type=question.answer_type,
    grading_criteria=question.grading_criteria
)

# Check result
if result.is_correct:
    print(f"✓ Correct! Score: {result.score}")
else:
    print(f"✗ Incorrect. {result.explanation}")
    if result.partial_credit > 0:
        print(f"  Partial credit: {result.partial_credit:.2f}")

# Access details
print(f"Details: {result.details}")
```

---

## Integration with Test Framework

```python
from bench import TestQuestion, Grader

# Create question
question = TestQuestion(
    text="What is 2+2?",
    correct_answer="4",
    answer_type="exact"
)

# Grade answer
grader = Grader()
result = grader.grade(
    model_answer="4",
    correct_answer=question.correct_answer,
    answer_type=question.answer_type,
    grading_criteria=question.grading_criteria
)

print(f"Correct: {result.is_correct}")
print(f"Score: {result.score}")
```

---

## Grading Strategies

### When to Use Each Type

**exact:**
- Factual answers (names, places, dates)
- Short answers with clear correct form
- Multiple choice (single word answers)

**numeric:**
- Math problems
- Calculations
- Measurements
- Percentages

**semantic:**
- Explanations
- Descriptions
- Open-ended questions
- Paraphrased answers

**code:**
- Programming challenges
- Function implementations
- Algorithm questions

---

## Customizing Grading

### Custom Grading Criteria

```python
# Strict exact matching
criteria = {
    "case_sensitive": True,
    "strip_whitespace": True,
    "normalize_whitespace": False
}

# Lenient numeric matching
criteria = {
    "tolerance": 1.0,
    "relative_tolerance": 0.05
}

# Loose semantic matching
criteria = {
    "threshold": 0.4
}
```

### Interpreting Results

```python
result = grader.grade(...)

# Perfect answer
if result.is_correct and result.score == 1.0:
    print("Perfect!")

# Partial credit
elif result.partial_credit > 0:
    print(f"Partially correct: {result.partial_credit:.1%}")

# Incorrect
else:
    print(f"Incorrect: {result.explanation}")
```

---

## Next Steps

**Phase 1.5: Test Runner**
- Execute full test suites
- Track results in database
- Performance metrics
- Batch testing

---

**Version:** 1.15.4  
**Phase:** 1.4 Complete  
**Next:** Phase 1.5 - Test Runner
