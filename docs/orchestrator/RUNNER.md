# Test Runner

**Phase 1.5** - Test Execution Engine

---

## Overview

Phase 1.5 adds the TestRunner - the execution engine that brings everything together.

**What it does:**
1. Loads test suites
2. Executes questions against models
3. Grades responses
4. Stores results in database
5. Tracks performance metrics

**Components:**
- **TestRun** - Container for run results and statistics
- **TestRunner** - Main execution engine

---

## Quick Start

```python
import asyncio
from bench import TestRunner, TestSuite, TestQuestion

async def main():
    # Create a simple suite
    suite = TestSuite("Quick Test", "test")
    suite.add_question(TestQuestion("What is 2+2?", "4", "exact"))
    suite.add_question(TestQuestion("What is 10*5?", "50", "numeric"))
    
    # Run it
    runner = TestRunner()
    run = await runner.run_suite(
        suite=suite,
        model_name="qwen2.5:32b"
    )
    
    # Check results
    stats = run.get_statistics()
    print(f"Accuracy: {stats['accuracy']:.1%}")
    print(f"Avg time: {stats['avg_response_time']:.2f}s")

asyncio.run(main())
```

---

## TestRun

Container for test run results.

### Creating a Run

```python
from bench import TestRun

run = TestRun(
    run_id="run_abc123",
    suite_id="suite_xyz789",
    model_id="qwen2_5_32b",
    model_params={"temperature": 0.7}
)

run.start()
# ... execute tests ...
run.complete()
```

### Adding Results

```python
from bench import GradingResult

result = GradingResult(
    is_correct=True,
    score=1.0,
    explanation="Correct"
)

run.add_result(
    question_id="q_123",
    model_response="Paris",
    grading_result=result,
    response_time=1.5
)
```

### Statistics

```python
stats = run.get_statistics()
# {
#     "total_questions": 10,
#     "correct_answers": 8,
#     "accuracy": 0.8,
#     "avg_score": 0.82,
#     "avg_response_time": 2.3,
#     "total_time": 25.4,
#     "status": "completed"
# }
```

---

## TestRunner

Main test execution engine.

### Basic Usage

```python
import asyncio
from bench import TestRunner

async def run_test():
    runner = TestRunner()
    
    # Run from database
    run = await runner.run_suite(
        suite_id="suite_abc",
        model_name="qwen2.5:32b"
    )
    
    print(f"Accuracy: {run.get_statistics()['accuracy']:.1%}")

asyncio.run(run_test())
```

### With Progress Tracking

```python
def progress(current, total, question_id):
    print(f"[{current}/{total}] Testing {question_id}...")

run = await runner.run_suite(
    suite_id="suite_abc",
    model_name="qwen2.5:32b",
    progress_callback=progress
)
```

### Custom Model Parameters

```python
run = await runner.run_suite(
    suite_id="suite_abc",
    model_name="llama3.1:70b",
    model_params={
        "temperature": 0.3,
        "top_p": 0.9,
        "max_tokens": 1000
    }
)
```

### Without Database Storage

```python
# For testing/debugging - don't save to DB
run = await runner.run_suite(
    suite=my_suite,
    model_name="qwen2.5:32b",
    save_to_db=False
)
```

---

## Loading Past Runs

### Get Specific Run

```python
runner = TestRunner()

# Load by ID
run = await runner.get_run("run_abc123")

# Access results
stats = run.get_statistics()
for result in run.results:
    print(f"{result.question_id}: {'✓' if result.grading_result.is_correct else '✗'}")
```

### List Recent Runs

```python
# All runs
runs = await runner.list_runs(limit=20)

# Filter by suite
runs = await runner.list_runs(suite_id="suite_abc")

# Filter by model
runs = await runner.list_runs(model_id="qwen2_5_32b")

# Both
runs = await runner.list_runs(
    suite_id="suite_abc",
    model_id="qwen2_5_32b",
    limit=5
)

for run_info in runs:
    print(f"{run_info['run_id']}: {run_info['accuracy']:.1%}")
```

---

## Complete Example

```python
import asyncio
from bench import TestRunner, TestLoader

async def benchmark_models():
    runner = TestRunner()
    loader = TestLoader()
    
    # Load suite
    suite = await loader.load_from_database("math_suite")
    
    # Test multiple models
    models = ["qwen2.5:32b", "llama3.1:70b", "codellama:70b"]
    
    results = {}
    for model in models:
        print(f"\nTesting {model}...")
        
        run = await runner.run_suite(
            suite=suite,
            model_name=model,
            progress_callback=lambda c, t, q: print(f"  [{c}/{t}]", end="\r")
        )
        
        stats = run.get_statistics()
        results[model] = stats
        
        print(f"\n{model}: {stats['accuracy']:.1%} accuracy")
        print(f"  Avg time: {stats['avg_response_time']:.2f}s")
    
    # Compare
    print("\n=== Comparison ===")
    for model, stats in sorted(results.items(), key=lambda x: x[1]['accuracy'], reverse=True):
        print(f"{model:20s} {stats['accuracy']:5.1%}  {stats['avg_response_time']:5.2f}s")

asyncio.run(benchmark_models())
```

---

## Database Schema

Test runs are stored in `orch_test_runs`:

```sql
SELECT 
    run_id,
    suite_id,
    model_id,
    accuracy,
    avg_response_time,
    started_at
FROM orch_test_runs
ORDER BY started_at DESC
LIMIT 10;
```

Individual results in `orch_test_results`:

```sql
SELECT 
    r.question_id,
    r.model_response,
    r.is_correct,
    r.response_time
FROM orch_test_results r
WHERE r.run_id = 'run_abc123'
ORDER BY r.created_at;
```

---

## Error Handling

### Graceful Degradation

TestRunner continues even if individual questions fail:

```python
run = await runner.run_suite(
    suite_id="suite_abc",
    model_name="qwen2.5:32b"
)

# Even if some questions error out, run completes
stats = run.get_statistics()
print(f"Completed: {stats['total_questions']} questions")
```

### Full Failure

```python
try:
    run = await runner.run_suite(
        suite_id="nonexistent",
        model_name="qwen2.5:32b"
    )
except ValueError as e:
    print(f"Suite not found: {e}")
```

---

## Performance Tips

### Parallel Testing

For testing multiple models, run them in parallel:

```python
async def test_models(suite_id, models):
    runner = TestRunner()
    
    tasks = [
        runner.run_suite(suite_id=suite_id, model_name=model)
        for model in models
    ]
    
    runs = await asyncio.gather(*tasks)
    return runs
```

### Batch Processing

For large test suites, consider splitting into chunks:

```python
# Split suite into smaller batches
# Run each batch
# Aggregate results
```

---

## Integration Example

### Full Workflow

```python
import asyncio
from bench import TestQuestion, TestSuite, TestLoader, TestRunner

async def full_workflow():
    # 1. Create suite
    suite = TestSuite("Math Basics", "math")
    suite.add_question(TestQuestion("2+2?", "4", "exact"))
    suite.add_question(TestQuestion("5*6?", "30", "numeric"))
    
    # 2. Save to database
    loader = TestLoader()
    suite_id = await loader.save_to_database(suite)
    print(f"Saved suite: {suite_id}")
    
    # 3. Run test
    runner = TestRunner()
    run = await runner.run_suite(
        suite_id=suite_id,
        model_name="qwen2.5:32b"
    )
    
    # 4. View results
    stats = run.get_statistics()
    print(f"\nResults:")
    print(f"  Accuracy: {stats['accuracy']:.1%}")
    print(f"  Avg time: {stats['avg_response_time']:.2f}s")
    
    # 5. Export
    export = run.to_dict(include_results=True)
    print(f"\nExport available with {len(export['results'])} results")

asyncio.run(full_workflow())
```

---

## Next Steps

**Phase 1.6: Test Suites**
- Pre-built test suites (math, code, dates)
- 1,500+ questions
- Comprehensive coverage

**Phase 1.7: Benchmarking**
- Automated benchmarking
- Model comparison reports
- Performance tracking

---

**Version:** 1.15.5  
**Phase:** 1.5 Complete  
**Next:** Phase 1.6 - Test Suites
