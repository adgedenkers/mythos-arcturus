# Mythos Orchestration System

## Overview

Parallel LLM task decomposition and synthesis framework. Breaks complex tasks into independent stages, executes them (potentially across multiple models), and reassembles outputs into coherent deliverables.

Core principle: **MapReduce for LLM work.** Each worker gets a focused slice of the problem with explicit input/output contracts, eliminating context window limitations.

## Architecture

```
orchestration/
├── orchestrator.py          # Core engine: load, gather, execute, synthesize
├── pattern_schema.json      # JSON Schema defining pattern structure
├── patterns/                # Pattern definitions (one JSON per pattern)
│   └── crud-update.json     # First pattern: Mythos CRUD operations
├── logs/                    # Execution logs (one per run)
└── cache/                   # Context gathering cache (future)
```

## Pattern Structure

Every pattern defines:

| Component          | Purpose                                                |
|--------------------|--------------------------------------------------------|
| trigger            | Keywords, intent types, preconditions for activation   |
| context_gathering  | Shell commands and files to pre-fetch before LLM work  |
| stages             | Ordered execution steps with dependency graph          |
| synthesis          | How to merge stage outputs into final deliverable      |
| feedback_loop      | Metrics tracking and pattern refinement rules          |

## Execution Flow

```
1. MATCH     → Identify which pattern fits the request
2. GATHER    → Pre-fetch all context (schema, code, docs) before any LLM call
3. DISPATCH  → Run stages respecting dependency graph (parallel where possible)
4. SYNTHESIZE → Merge stage outputs via template or LLM pass
5. VALIDATE  → Run checks on final output
6. LOG       → Record execution metrics for pattern refinement
```

## Stage Dependency Model

Stages declare dependencies. The engine resolves execution order into "waves":

```
Wave 1 (parallel): recon         ← no dependencies, runs first
Wave 2 (sequential): plan        ← depends on recon
Wave 3 (parallel): build_sql, build_code, build_bot  ← all depend on plan only
Wave 4 (sequential): synthesis   ← depends on all build stages
```

## Model Routing

| Preference | Model                          | Use For                        |
|------------|--------------------------------|--------------------------------|
| fast       | claude-haiku-4-5               | Recon, parsing, classification |
| balanced   | claude-sonnet-4-5              | Planning, code generation      |
| deep       | claude-opus-4-6                | Complex synthesis, review      |

## CLI Usage

```bash
# List available patterns
python3 orchestrator.py --list-patterns

# Dry run (show execution plan)
python3 orchestrator.py -p crud-update -r "Add mood tracking to journals" --dry-run

# Execute with variables
python3 orchestrator.py -p crud-update -r "Add mood tracking" -v TARGET_MODULE=journal

# Full execution
python3 orchestrator.py -p crud-update -r "Add mood tracking to journals"
```

## Current Patterns

### crud-update (v1.0.0)
Standard Mythos database feature changes. 5 stages: recon → plan → build_sql + build_code + build_bot → synthesis. Outputs a deployment-ready patch zip.

## Integration Points

- **Patch System**: Synthesis outputs are formatted as Mythos patches
- **Telegram Bot**: Future `/orchestrate` command for triggering from chat
- **Iris**: Future integration for automated pattern matching and execution
- **Neo4j**: Patterns stored as graph nodes for traversal-based matching

## Status

- [x] Pattern schema defined
- [x] CRUD Update pattern defined
- [x] Core orchestrator engine (gather, execute, synthesize)
- [x] CLI interface with dry-run support
- [ ] Anthropic API integration (placeholder in place)
- [ ] Async/parallel stage execution
- [ ] Pattern matching engine (auto-detect which pattern fits)
- [ ] Telegram bot integration
- [ ] Execution metrics dashboard
- [ ] Pattern self-refinement from execution logs
