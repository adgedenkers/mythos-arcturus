---
title: "Test Suite Management"
category: tools
status: active
stream: LOG
location: docs
tags: [test, framework, suite, question]
created: unknown
updated: 2026-03-12
author: Adge Denkers
---

# Test Framework

**Phase 1.3** - Test Suite Management

---

## Overview

Phase 1.3 adds the core test framework for creating, managing, and loading test suites.

**Components:**
- **TestQuestion** - Individual test question with grading criteria
- **TestSuite** - Collection of related questions
- **TestLoader** - Load/save suites from JSON and database

---

## Quick Start

### Create a Test Suite

```python
import asyncio
from bench import TestQuestion, TestSuite, TestLoader

# Create questions
q1 = TestQuestion(
    text="What is 2+2?",
    correct_answer="4",
    answer_type="exact",
    difficulty="easy",
    tags=["math", "arithmetic"]
)

q2 = TestQuestion(
    text="What is 15 * 7?",
    correct_answer="105",
    answer_type="numeric",
    difficulty="medium",
    tags=["math", "multiplication"]
)

# Create suite
suite = TestSuite(
    name="Basic Math",
    category="math",
    description="Simple arithmetic questions"
)

suite.add_question(q1)
suite.add_question(q2)

# Save to JSON
loader = TestLoader()
path = loader.save_to_json(suite, "math/basic.json")
print(f"Saved to: {path}")

# Save to database
async def save():
    suite_id = await loader.save_to_database(suite)
    print(f"Saved to database: {suite_id}")

asyncio.run(save())
```

---

## TestQuestion

Individual test question with validation.

### Creating Questions

```python
from bench import TestQuestion

# Simple exact match
question = TestQuestion(
    text="What is the capital of France?",
    correct_answer="Paris",
    answer_type="exact"
)

# Numeric answer
question = TestQuestion(
    text="What is 15% of 200?",
    correct_answer="30",
    answer_type="numeric",
    grading_criteria={"tolerance": 0.1}
)

# With metadata
question = TestQuestion(
    text="Implement a binary search",
    correct_answer="def binary_search(arr, target): ...",
    answer_type="code",
    difficulty="hard",
    tags=["algorithms", "search", "binary-search"],
    grading_criteria={"must_handle_edge_cases": True},
    metadata={"time_limit": 60, "hints_allowed": False}
)
```

### Answer Types

- **exact**: Exact string match (case-sensitive)
- **numeric**: Numeric comparison with tolerance
- **semantic**: Semantic similarity (Phase 1.4+)
- **code**: Code execution match (Phase 1.4+)

### Difficulty Levels

- **easy**: Simple, straightforward
- **medium**: Requires some thought
- **hard**: Complex, multi-step
- **expert**: Advanced, specialized knowledge

### Methods

```python
# Validate
is_valid, error = question.validate()

# Convert to/from dict
data = question.to_dict()
question = TestQuestion.from_dict(data)
```

---

## TestSuite

Collection of test questions.

### Creating Suites

```python
from bench import TestSuite, TestQuestion

suite = TestSuite(
    name="Python Basics",
    category="code",
    description="Fundamental Python concepts",
    version="1.0"
)

# Add questions
suite.add_question(question1)
suite.add_question(question2)

# Remove question
suite.remove_question("q_abc123")

# Get question
question = suite.get_question("q_abc123")
```

### Statistics

```python
stats = suite.get_statistics()
# {
#     "total_questions": 10,
#     "difficulty_distribution": {"easy": 3, "medium": 5, "hard": 2},
#     "answer_type_distribution": {"exact": 4, "numeric": 3, "code": 3},
#     "tags": ["algorithms", "data-structures", "python"]
# }
```

### Validation

```python
is_valid, error = suite.validate()
if not is_valid:
    print(f"Suite invalid: {error}")
```

---

## TestLoader

Load and save test suites.

### JSON Files

```python
from bench import TestLoader

loader = TestLoader()

# Load from JSON
suite = loader.load_from_json("math/arithmetic.json")

# Save to JSON
path = loader.save_to_json(suite, "math/new_suite.json")

# Auto-generate filename
path = loader.save_to_json(suite)  # Saves as category_suiteid.json

# List JSON files
files = loader.list_json_files(category="math")
```

### Database

```python
import asyncio

async def main():
    loader = TestLoader()
    
    # Save to database
    suite_id = await loader.save_to_database(suite)
    
    # Load from database
    suite = await loader.load_from_database(suite_id)
    
    # List suites
    suites = await loader.list_suites(category="math", public_only=True)
    for s in suites:
        print(f"{s['name']}: {s['question_count']} questions")

asyncio.run(main())
```

---

## File Format

JSON test suite format:

```json
{
  "suite_id": "suite_abc123",
  "name": "Basic Arithmetic",
  "category": "math",
  "description": "Simple math questions",
  "version": "1.0",
  "public": true,
  "created_by": "user_123",
  "question_count": 2,
  "questions": [
    {
      "question_id": "q_xyz789",
      "text": "What is 2+2?",
      "correct_answer": "4",
      "answer_type": "exact",
      "difficulty": "easy",
      "tags": ["math", "addition"],
      "grading_criteria": {},
      "metadata": {}
    },
    {
      "question_id": "q_def456",
      "text": "What is 15 * 7?",
      "correct_answer": "105",
      "answer_type": "numeric",
      "difficulty": "medium",
      "tags": ["math", "multiplication"],
      "grading_criteria": {"tolerance": 0},
      "metadata": {}
    }
  ]
}
```

---

## Directory Structure

```
test_suites/
├── standard/          # Standard test suites
│   ├── math/
│   │   ├── arithmetic.json
│   │   └── algebra.json
│   ├── code/
│   │   ├── python_basics.json
│   │   └── algorithms.json
│   └── dates/
│       └── date_reasoning.json
└── custom/            # Custom user suites
    └── my_suite.json
```

---

## Examples

### Complete Example

```python
import asyncio
from bench import TestQuestion, TestSuite, TestLoader

async def create_math_suite():
    # Create suite
    suite = TestSuite(
        name="Mental Math",
        category="math",
        description="Quick mental calculations"
    )
    
    # Add questions
    questions = [
        TestQuestion("7 + 8", "15", "exact", difficulty="easy"),
        TestQuestion("12 * 11", "132", "numeric", difficulty="medium"),
        TestQuestion("144 / 12", "12", "exact", difficulty="easy"),
    ]
    
    for q in questions:
        suite.add_question(q)
    
    # Validate
    is_valid, error = suite.validate()
    if not is_valid:
        print(f"Error: {error}")
        return
    
    # Save
    loader = TestLoader()
    
    # To JSON
    json_path = loader.save_to_json(suite, "math/mental_math.json")
    print(f"Saved to: {json_path}")
    
    # To database
    suite_id = await loader.save_to_database(suite)
    print(f"Saved to database: {suite_id}")
    
    # Load back
    loaded = await loader.load_from_database(suite_id)
    stats = loaded.get_statistics()
    print(f"Loaded: {loaded.name} with {stats['total_questions']} questions")

asyncio.run(create_math_suite())
```

---

## Next Steps

**Phase 1.4: Grading System**
- Grader class
- Answer validation
- Scoring logic
- Partial credit

**Phase 1.5: Test Runner**
- Execute tests against models
- Track results
- Performance metrics

---

**Version:** 1.15.3  
**Phase:** 1.3 Complete  
**Next:** Phase 1.4 - Grading System
