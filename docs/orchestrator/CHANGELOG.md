# Changelog

All notable changes to Mythos Orchestrator will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.15.1] - 2026-02-16

### Added
- **Phase 1.1: Core Infrastructure**
- Project structure at `/opt/mythos/orchestrator`
- Database schema with 7 tables (all prefixed with `orch_`)
  - `orch_models` - Model registry
  - `orch_model_capabilities` - Task-specific capabilities
  - `orch_test_suites` - Test suite definitions
  - `orch_test_questions` - Individual test questions
  - `orch_test_runs` - Test execution history
  - `orch_test_results` - Individual question results
  - `orch_model_benchmarks` - Aggregated performance metrics
- Configuration system using pydantic-settings
  - Environment variable loading from `.env`
  - Type-safe settings validation
  - Path management utilities
- Core utility functions
  - ID generation (`generate_id`)
  - String hashing (`hash_string`)
  - Duration formatting (`format_duration`)
  - Timestamp utilities (`format_timestamp`, `parse_timestamp`)
  - JSON handling (`safe_json_loads`, `safe_json_dumps`)
  - String operations (`truncate_string`, `clean_whitespace`)
  - Math utilities (`calculate_percentage`)
- Database connection management
  - Async connection pooling with asyncpg
  - Connection context managers
  - Query methods (`execute`, `fetch`, `fetchrow`, `fetchval`)
- Documentation
  - Architecture overview
  - Installation guide
  - Configuration reference
  - This changelog

### Changed
- System version: 1.0.0 → 1.15.1

### Fixed
- N/A (initial release)

### Security
- All database credentials stored in gitignored `.env` file
- Database permissions restricted to `adge` user
- No external API calls (fully local)

---

## [Unreleased]

### Planned for 1.15.2 (Phase 1.2)
- Ollama client wrapper
- Model registry implementation
- Model manager for installed models
- Performance tracking

### Planned for 1.15.3 (Phase 1.3)
- TestSuite and TestQuestion classes
- Test loader/saver
- Question categorization

### Planned for 1.15.4 (Phase 1.4)
- Grader with multiple methods (exact, numeric, semantic, code)
- Answer validation
- Partial credit scoring

### Planned for 1.15.5 (Phase 1.5)
- Async test execution engine
- Progress tracking
- Result persistence

### Planned for 1.15.6 (Phase 1.6)
- Math test suite (100 questions)
- Date reasoning suite (500 questions)
- Code generation suite (200 questions)
- Hallucination detection suite (300 questions)
- General reasoning suite (400 questions)

### Planned for 1.15.7 (Phase 1.7)
- Automated benchmarking system
- Report generation
- Model comparison tools

### Planned for 1.16.0 (Phase 1 Complete)
- Full Model Bench operational
- Complete testing infrastructure
- Performance data for routing decisions

---

## Version History

- **1.0.0** - Base Mythos system (patch_0081)
- **1.15.1** - Phase 1.1: Core Infrastructure (patch_0082) ← Current
- **1.15.2** - Phase 1.2: Ollama Integration (patch_0083) - Planned
- **1.16.0** - Phase 1 Complete: Model Bench - Planned

---

## Notes

### Versioning Strategy

Starting with patch_0082, Mythos uses semantic versioning:

- **MAJOR** version: Breaking changes, major refactors
- **MINOR** version: New features, backward compatible
- **PATCH** version: Bug fixes, small improvements

Phase 1 versions (1.15.x → 1.16.0):
- Each sub-phase increments PATCH (1.15.1, 1.15.2, etc.)
- Phase completion increments MINOR (1.16.0)

### Database Changes

All database tables use the `orch_` prefix to avoid conflicts with existing Mythos tables. This allows the orchestrator to coexist with the main Mythos system without interference.

### Rollback Support

Phase 1.1 includes a rollback script at `/opt/mythos/orchestrator/scripts/rollback.sh` that can safely remove all changes if needed.

---

**Maintainer:** Ka'tuar'el  
**Repository:** https://github.com/your-repo/mythos  
**Documentation:** /opt/mythos/docs/orchestrator/


---

## [1.15.2] - 2026-02-16

### Added
- **Phase 1.2: Ollama Integration**
- Ollama API client wrapper (`OllamaClient`)
  - Async operations with automatic retries
  - Model listing, pulling, deletion
  - Text generation with streaming support
  - Embeddings support
  - Health checking
- Model registry (`ModelRegistry`)
  - Database-backed model tracking
  - Model normalization and ID management
  - Capability tracking per model
  - Best model selection for task types
- Model manager (`ModelManager`)
  - High-level model operations
  - Automatic model synchronization
  - Model selection strategies
  - Usage tracking
- Model registration script (`register_models.sh`)
  - Automatic sync of installed Ollama models
  - Called during installation
- Documentation (`OLLAMA.md`)
  - Complete API reference
  - Usage examples
  - Troubleshooting guide

### Changed
- Updated `pydantic` to >=2.9.0 for ollama compatibility
- System version: 1.15.1 → 1.15.2

### Fixed
- N/A

---


---

## [1.15.2] - 2026-02-16

### Added
- **Phase 1.2: Ollama Integration**
- Ollama API client wrapper (`OllamaClient`)
  - Async operations with automatic retries
  - Model listing, pulling, deletion
  - Text generation with streaming support
  - Embeddings support
  - Health checking
- Model registry (`ModelRegistry`)
  - Database-backed model tracking
  - Model normalization and ID management
  - Capability tracking per model
  - Best model selection for task types
- Model manager (`ModelManager`)
  - High-level model operations
  - Automatic model synchronization
  - Model selection strategies
  - Usage tracking
- Model registration script (`register_models.sh`)
  - Automatic sync of installed Ollama models
  - Called during installation
- Documentation (`OLLAMA.md`)
  - Complete API reference
  - Usage examples
  - Troubleshooting guide

### Changed
- Updated `pydantic` to >=2.9.0 for ollama compatibility
- System version: 1.15.1 → 1.15.2

### Fixed
- N/A

---


---

## [1.15.3] - 2026-02-17

### Added
- **Phase 1.3: Test Framework**
- TestQuestion class
  - Question text and correct answer
  - Answer types: exact, numeric, semantic, code
  - Difficulty levels: easy, medium, hard, expert
  - Tags and grading criteria
  - Validation methods
  - Dict serialization
- TestSuite class
  - Collection of test questions
  - Add/remove questions
  - Suite statistics (difficulty distribution, answer types, tags)
  - Validation methods
  - Dict serialization
- TestLoader class
  - Load test suites from JSON files
  - Save test suites to JSON files
  - Load test suites from database
  - Save test suites to database
  - List available suites
  - Auto-generated filenames
- Documentation (`TESTING.md`)
  - Complete API reference
  - Usage examples
  - File format specification

### Changed
- System version: 1.15.2 → 1.15.3

### Fixed
- N/A

---


---

## [1.15.3] - 2026-02-17

### Added
- **Phase 1.3: Test Framework**
- TestQuestion class
  - Question text and correct answer
  - Answer types: exact, numeric, semantic, code
  - Difficulty levels: easy, medium, hard, expert
  - Tags and grading criteria
  - Validation methods
  - Dict serialization
- TestSuite class
  - Collection of test questions
  - Add/remove questions
  - Suite statistics (difficulty distribution, answer types, tags)
  - Validation methods
  - Dict serialization
- TestLoader class
  - Load test suites from JSON files
  - Save test suites to JSON files
  - Load test suites from database
  - Save test suites to database
  - List available suites
  - Auto-generated filenames
- Documentation (`TESTING.md`)
  - Complete API reference
  - Usage examples
  - File format specification

### Changed
- System version: 1.15.2 → 1.15.3

### Fixed
- N/A

---


---

## [1.15.4] - 2026-02-17

### Added
- **Phase 1.4: Grading System**
- GradingResult class
  - Correctness flag (is_correct)
  - Score (0.0-1.0)
  - Partial credit support
  - Explanation and details
  - Dict serialization
- Grader class
  - Exact matching (case-sensitive/insensitive options)
  - Numeric comparison (with tolerance and partial credit)
  - Semantic similarity (word overlap based)
  - Code validation (normalized comparison)
  - Automatic routing based on answer_type
- Grading criteria support
  - Customizable tolerance for numeric
  - Case sensitivity for exact
  - Similarity threshold for semantic
- Partial credit calculation
  - Numeric answers: credit for being close
  - Semantic answers: similarity score as credit
  - Code answers: line overlap as credit
- Documentation (`GRADING.md`)
  - Complete API reference
  - Usage examples for all grading types
  - Customization guide

### Changed
- System version: 1.15.3 → 1.15.4
- Updated bench package exports

### Fixed
- N/A

---


---

## [1.15.4] - 2026-02-17

### Added
- **Phase 1.4: Grading System**
- GradingResult class
  - Correctness flag (is_correct)
  - Score (0.0-1.0)
  - Partial credit support
  - Explanation and details
  - Dict serialization
- Grader class
  - Exact matching (case-sensitive/insensitive options)
  - Numeric comparison (with tolerance and partial credit)
  - Semantic similarity (word overlap based)
  - Code validation (normalized comparison)
  - Automatic routing based on answer_type
- Grading criteria support
  - Customizable tolerance for numeric
  - Case sensitivity for exact
  - Similarity threshold for semantic
- Partial credit calculation
  - Numeric answers: credit for being close
  - Semantic answers: similarity score as credit
  - Code answers: line overlap as credit
- Documentation (`GRADING.md`)
  - Complete API reference
  - Usage examples for all grading types
  - Customization guide

### Changed
- System version: 1.15.3 → 1.15.4
- Updated bench package exports

### Fixed
- N/A

---


---

## [1.15.5] - 2026-02-17

### Added
- **Phase 1.5: Test Runner**
- TestRun class
  - Container for test run results
  - Individual question results tracking
  - Run statistics calculation
  - Status tracking (pending, running, completed, failed)
  - Export to dictionary/JSON
- QuestionResult class
  - Question ID, model response, grading result
  - Response time tracking
- TestRunner class
  - Main test execution engine
  - Run test suites against models
  - Automatic grading of responses
  - Database persistence of runs and results
  - Progress callback support
  - Error handling (continue on failure)
  - Load past runs from database
  - List runs with filtering
- Complete test workflow integration
  - TestLoader → OllamaClient → Grader → Database
  - Async execution
  - Performance metrics
- Documentation (`RUNNER.md`)
  - Complete API reference
  - Usage examples
  - Integration patterns
  - Performance tips

### Changed
- System version: 1.15.4 → 1.15.5
- Updated bench package exports
- Database: Stores runs in orch_test_runs, results in orch_test_results

### Fixed
- N/A

---
