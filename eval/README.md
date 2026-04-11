# Chunk Factory — Eval Harness & Local Model Benchmark

> **Location:** `/opt/mythos/eval/`
> **Author:** Ka'tuar'el
> **Since:** SYS-0011

## What Is This?

The Chunk Factory tests whether local Ollama models can build valid Mythos
skills (radioactive chunks) from a structured specification. Claude designs
a feature as a "gold standard," and the harness feeds the same spec to a
local model to see how close it gets — then loops with error feedback until
it passes or exhausts its iterations.

This is Iris's cell factory. Every successful chunk becomes a skill she can use.

## Quick Start

```bash
# Run a challenge with default model (qwen3-coder:30b)
chunk-eval people_lookup

# Specify model and max iterations
chunk-eval people_lookup llama3.3:70b 10

# List available challenges
chunk-eval --list

# List available Ollama models
chunk-eval --models

# Compare all results for a challenge across models
chunk-eval --compare people_lookup
```

## How It Works

### The Loop

```
┌─────────────────┐     ┌──────────────┐     ┌────────────────┐
│ Challenge Spec   │────▶│ Prompt       │────▶│ Ollama Model   │
│ (what to build)  │     │ Builder      │     │ (local LLM)    │
└─────────────────┘     └──────────────┘     └───────┬────────┘
                                                      │
┌─────────────────┐     ┌──────────────┐              ▼
│ SKILL.md        │────▶│ (merged into │     ┌────────────────┐
│ (how to build)  │     │  prompt)     │     │ Raw Response   │
└─────────────────┘     └──────────────┘     └───────┬────────┘
                                                      │
                                                      ▼
                                              ┌────────────────┐
                                              │ Code Extractor │
                                              └───────┬────────┘
                                                      │
                              ┌────────────────────────┤
                              ▼                        ▼
                     ┌────────────────┐     ┌────────────────┐
                     │ Structural     │     │ Gold Standard  │
                     │ Validator      │     │ Comparator     │
                     └───────┬────────┘     └───────┬────────┘
                              │                      │
                              ▼                      ▼
                     ┌─────────────────────────────────┐
                     │       Composite Score            │
                     │  (60% structural + 40% gold)    │
                     └───────┬─────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │  Score >= 85%?     │
                    │  All checks pass?  │
                    └─────────┬──────────┘
                       YES ──▶│◀── NO
                    ┌─────────┘    └──────────┐
                    ▼                          ▼
             ┌──────────┐            ┌──────────────────┐
             │  PASS    │            │ Feed errors back  │
             │  Done!   │            │ into prompt, loop │
             └──────────┘            └──────────────────┘
```

### Validation Checks

The structural validator checks:
1. Valid Python syntax (ast.parse)
2. Contains a class subclassing SkillBase
3. Has required attributes: name, version, category, description, triggers, cache_ttl
4. Has `async def execute()` method
5. Imports SkillBase, SkillRequest, SkillResponse
6. Uses database connection pattern (for data skills)
7. Has try/except error handling
8. Has finally block for connection cleanup

### Gold Comparison

If a gold standard file exists, the harness also:
- Calculates text similarity (SequenceMatcher ratio)
- Generates a unified diff
- Compares class structure (methods, attributes)

## Directory Structure

```
/opt/mythos/eval/
├── README.md                  ← This file
├── ollama_builder.py          ← The recursive eval harness
├── chunk-eval.sh              ← CLI wrapper (symlinked to /usr/local/bin/chunk-eval)
├── skill_reference/
│   └── SKILL.md               ← Chunk-building instructions (fed to model)
├── templates/
│   └── challenge_schema.json  ← JSON schema for challenge specs
├── challenges/
│   └── people_lookup/         ← First challenge
│       ├── challenge_spec.json
│       └── gold/
│           └── people_lookup.py
└── results/
    └── {challenge_id}/
        └── {timestamp}/
            ├── report.json    ← Full evaluation report
            ├── best.py        ← Best code produced
            ├── iter01_raw.txt ← Raw model response
            ├── iter01_code.py ← Extracted Python code
            └── ...
```

## Creating a New Challenge

### 1. Write the challenge spec

```json
{
  "challenge_id": "my_skill",
  "version": "1.0",
  "description": "What needs to be built",
  "difficulty": "beginner|intermediate|advanced",
  "category": "data|action|composite|meta",
  "stream": "SYS|NEU|LOG|MNE|SEN",
  "requirement": {
    "natural_language": "Plain English description of what to build",
    "skill_name": "my_skill",
    "class_name": "MySkill",
    "filename": "my_skill.py",
    "category": "data",
    "cache_ttl": 300,
    "triggers": ["keyword1", "keyword2"]
  },
  "system_context": {
    "database": "postgresql",
    "database_name": "mythos",
    "connection_pattern": "psycopg2 with RealDictCursor",
    "table": {
      "name": "table_name",
      "columns": [
        {"name": "id", "type": "integer", "nullable": false},
        {"name": "name", "type": "varchar(100)", "nullable": false}
      ]
    },
    "engine_import": "from engine.base import SkillBase, SkillRequest, SkillResponse"
  },
  "validation_criteria": {
    "structural": ["list of structural checks"],
    "behavioral": ["list of behavioral expectations"]
  },
  "gold_path": "challenges/my_skill/gold/my_skill.py"
}
```

### 2. Write the gold standard

Build the skill yourself (or have Claude build it) and save it as the gold
reference. This is what the local model's output gets compared against.

### 3. Place in challenges directory

```
challenges/
└── my_skill/
    ├── challenge_spec.json
    └── gold/
        └── my_skill.py
```

### 4. Run it

```bash
chunk-eval my_skill qwen3-coder:30b
```

## Recommended Models

Based on available models on Arcturus and the task (structured code generation):

| Model | Size | Best For |
|-------|------|----------|
| `qwen3-coder:30b` | 18 GB | Default choice, code-specialized |
| `llama3.3:70b` | 42 GB | Strongest general reasoning |
| `qwen3-next:80b` | 50 GB | Largest, highest capability |
| `mistral-small:24b` | 14 GB | Fast iteration, decent quality |
| `codellama:70b` | 38 GB | Code-focused alternative |

## Interpreting Results

### Composite Score

- **0.85+** = PASS (structurally valid + high gold similarity)
- **0.60-0.84** = Close, probably one or two issues
- **0.30-0.59** = Right idea, structural problems
- **0.00-0.29** = Major issues (usually syntax errors blocking all checks)

### Common Failure Patterns

| Pattern | Cause | Fix |
|---------|-------|-----|
| Syntax error on finally | Empty finally block | Harness now shows context lines |
| Score 0.0 all iterations | Same error repeated | Model can't self-correct from error message alone |
| High similarity, low structural | Correct logic, wrong format | Improve SKILL.md instructions |
| Low similarity, high structural | Valid code, different approach | Not a failure — different valid solution |

## Integration with Iris

Skills produced by the chunk factory (once validated) can be deployed
directly to `/opt/mythos/skills/data/`. The skill engine autodiscovers
them on API restart. The gold standard files serve double duty — they're
both the benchmark AND deployable skills.

---
_System designed by Ka'tuar'el_
_Last updated: 2026-03-04_
