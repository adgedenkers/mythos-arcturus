---
title: "Mythos Orchestrator Architecture"
category: orchestrator
status: active
stream: LOG
location: docs
tags: [orchestrator, architecture, benchmarking]
created: unknown
updated: 2026-03-12
author: Adge Denkers
---

# Mythos Orchestrator - Architecture

**Version:** 1.15.1  
**Phase:** 1.1 (Core Infrastructure)  
**Last Updated:** 2026-02-16

---

## System Overview

Mythos Orchestrator is a multi-model AI orchestration system built on three core principles:

1. **Sovereignty** - All models run locally on your hardware
2. **Specialization** - Use the best model for each specific task
3. **Orchestration** - Intelligently coordinate multiple models

**Goal:** Superior AI results at zero marginal cost through intelligent model selection and orchestration.

---

## High-Level Architecture

```
                    ┌─────────────────────────┐
                    │   User Query            │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Intent Classifier      │
                    │  (Phase 2)              │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Multi-Dimensional      │
                    │  Analyzer (Phase 3)     │
                    │  • Task Decomposition   │
                    │  • Entity Detection     │
                    │  • Code Detection       │
                    │  • Context Analysis     │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Model Router           │
                    │  (Phase 2)              │
                    │  Uses benchmark data ─┐ │
                    └───────────┬───────────┼─┘
                                │           │
                                │     ┌─────▼──────┐
                                │     │ Model Bench│
                                │     │ (Phase 1)  │
                                │     └────────────┘
                    ┌───────────▼─────────────┐
                    │  Execution Engine       │
                    │  (Phase 4)              │
                    │  • Parallel             │
                    │  • Sequential           │
                    │  • Consensus            │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │  Synthesis Engine       │
                    │  (Phase 5)              │
                    └───────────┬─────────────┘
                                │
                    ┌───────────▼─────────────┐
                    │   Final Response        │
                    └─────────────────────────┘
```

---

## Phase 1: Model Bench (v1.15.1 - v1.16.0)

**Purpose:** Create testing infrastructure to measure model performance across different task types.

**Why This Matters:** The router needs data to make intelligent decisions. Model Bench provides that data.

### Phase 1.1: Core Infrastructure ✅ (v1.15.1)

**Status:** Complete  
**Provides:**
- Project structure at `/opt/mythos/orchestrator`
- Database schema (7 `orch_*` tables)
- Configuration system (pydantic-settings)
- Core utilities (ID generation, formatting, JSON)

**Key Files:**
- `src/config.py` - Settings management
- `src/database.py` - PostgreSQL connection
- `src/utils.py` - Helper functions

### Upcoming Phases

- **1.2** (v1.15.2): Ollama Integration
- **1.3** (v1.15.3): Test Framework
- **1.4** (v1.15.4): Grading System
- **1.5** (v1.15.5): Test Runner
- **1.6** (v1.15.6): Test Suites (1,500+ questions)
- **1.7** (v1.15.7): Benchmarking & Reporting

---

## Database Schema (Phase 1.1)

### Tables Created

All tables use `orch_` prefix to avoid conflicts with existing Mythos tables.

#### orch_models
Registry of available LLM models.

```sql
CREATE TABLE orch_models (
    model_id TEXT PRIMARY KEY,           -- llama3_70b, qwen2_5_32b
    name TEXT NOT NULL,                  -- llama3.1:70b, qwen2.5:32b
    provider TEXT DEFAULT 'ollama',      -- ollama, openai, anthropic
    size_params TEXT,                    -- 70B, 32B, 7B
    quantization TEXT,                   -- q4_0, q5_0, q8_0
    context_window INTEGER,              -- 32000, 128000
    installed BOOLEAN DEFAULT false,
    installed_at TIMESTAMP,
    last_used TIMESTAMP,
    metadata JSONB,                      -- Additional info
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### orch_model_capabilities
Task-specific performance for each model.

```sql
CREATE TABLE orch_model_capabilities (
    capability_id TEXT PRIMARY KEY,
    model_id TEXT REFERENCES orch_models(model_id),
    task_type TEXT NOT NULL,            -- math, code, dates, etc.
    quality_score REAL,                 -- 0.0-1.0
    speed_tier TEXT,                    -- fast, medium, slow
    cost_per_1k_tokens REAL DEFAULT 0,  -- $0 for local models
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### orch_test_suites
Test suite definitions.

```sql
CREATE TABLE orch_test_suites (
    suite_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,             -- math, dates, code, etc.
    description TEXT,
    question_count INTEGER,
    difficulty TEXT,                    -- easy, medium, hard, expert
    version TEXT DEFAULT '1.0',
    public BOOLEAN DEFAULT true,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### orch_test_questions
Individual test questions.

```sql
CREATE TABLE orch_test_questions (
    question_id TEXT PRIMARY KEY,
    suite_id TEXT REFERENCES orch_test_suites(suite_id),
    question_text TEXT NOT NULL,
    correct_answer TEXT,
    answer_type TEXT,                   -- exact, numeric, semantic, code
    grading_criteria JSONB,             -- Validation rules
    difficulty TEXT,
    tags TEXT[],                        -- Categorization
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### orch_test_runs
Test execution history.

```sql
CREATE TABLE orch_test_runs (
    run_id TEXT PRIMARY KEY,
    suite_id TEXT REFERENCES orch_test_suites(suite_id),
    model_id TEXT REFERENCES orch_models(model_id),
    model_params JSONB,                 -- Temperature, etc.
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    total_questions INTEGER,
    correct_answers INTEGER,
    accuracy REAL,                      -- 0.0-1.0
    avg_response_time REAL,             -- Seconds
    total_cost REAL DEFAULT 0,
    status TEXT,                        -- running, completed, failed
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### orch_test_results
Individual question results.

```sql
CREATE TABLE orch_test_results (
    result_id TEXT PRIMARY KEY,
    run_id TEXT REFERENCES orch_test_runs(run_id),
    question_id TEXT REFERENCES orch_test_questions(question_id),
    model_response TEXT,
    is_correct BOOLEAN,
    partial_credit REAL,                -- 0.0-1.0
    response_time REAL,                 -- Seconds
    grading_details JSONB,              -- Detailed grading info
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### orch_model_benchmarks
Aggregated performance metrics.

```sql
CREATE TABLE orch_model_benchmarks (
    benchmark_id TEXT PRIMARY KEY,
    model_id TEXT REFERENCES orch_models(model_id),
    task_type TEXT,
    test_suite TEXT,
    accuracy REAL,
    hallucination_rate REAL,
    avg_response_time REAL,
    sample_size INTEGER,
    tested_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Configuration System

Settings are managed via pydantic-settings, loaded from environment variables and `.env` file.

**File:** `/opt/mythos/orchestrator/.env`

**Key Settings:**

```python
from config import settings

# Database
settings.DATABASE_URL  # "postgresql://adge@localhost:5432/mythos"

# Ollama
settings.OLLAMA_HOST   # "http://localhost:11434"

# Paths
settings.DATA_DIR      # "/opt/mythos/orchestrator/data"
settings.TEST_SUITES_DIR
settings.RESULTS_DIR
settings.LOGS_DIR

# Model defaults
settings.DEFAULT_TEMPERATURE  # 0.7
settings.DEFAULT_TOP_P        # 0.9
settings.DEFAULT_MODEL        # "qwen2.5:32b"
```

---

## Development Principles

1. **Modular Design** - Each phase builds on previous without breaking existing functionality
2. **Async First** - All I/O operations use asyncio for performance
3. **Type Safety** - Pydantic models for data validation
4. **Namespace Isolation** - `orch_` prefix prevents conflicts
5. **Error Handling** - Graceful degradation with detailed logging
6. **Testability** - Each component is independently testable
7. **Documentation** - Comprehensive docstrings and examples

---

## Future Phases

### Phase 2: Model Router (Weeks 5-6)
Simple intelligent routing based on task type and benchmark data.

### Phase 3: Multi-Dimensional Analyzer (Weeks 7-9)
Parallel specialist analyzers:
- Task decomposition
- Entity detection
- Code detection
- Image analysis
- Context analysis

### Phase 4: Execution Engine (Weeks 10-11)
Multi-model orchestration:
- Parallel execution
- Sequential execution
- Consensus patterns

### Phase 5: Synthesis Engine (Weeks 12-13)
Result compilation and presentation.

### Phase 6: Integration & Polish (Weeks 14-16)
End-to-end testing, optimization, documentation.

---

## Performance Considerations

**Phase 1.1 Benchmarks:**
- Database connection pool: 2-10 connections
- Config loading: <1ms
- ID generation: ~0.1ms per ID
- JSON operations: Safe with fallbacks

**Expected Phase 1 Complete Performance:**
- Test 1 model on 100 questions: ~10-15 minutes
- Parallel testing (5 models): ~15-20 minutes
- Database insert rate: >1000 results/second

---

## Security & Privacy

1. **Local Execution** - All models run on Arcturus, no external API calls
2. **Database Security** - PostgreSQL with user permissions
3. **No Data Leakage** - Test questions and results stay local
4. **Audit Trail** - All test runs logged with timestamps
5. **Configurable** - Sensitive settings in .env (gitignored)

---

## Next Steps

1. **Phase 1.1 Complete** ✅ - Core infrastructure ready
2. **Install Phase 1.2** - Ollama integration
3. **Continue through Phase 1.7** - Complete Model Bench
4. **Move to Phase 2** - Begin Router implementation

---

**Status:** Phase 1.1 Complete  
**Version:** 1.15.1  
**Next:** Phase 1.2 (v1.15.2) - Ollama Integration
