# Mythos Mission Specification

> The mission file is the contract between Claude (architect) and Iris/Ollama (executor).
> Claude generates it. The executor on Arcturus runs it.

## Overview

A mission file is a YAML document that describes:
1. **What** needs to be accomplished (goal, success criteria)
2. **Where** to look (files, directories, tables, graph queries)
3. **How** to approach it (phases, with instructions per phase)
4. **When it's done** (validation checks)

The executor reads the mission, runs each phase sequentially, injects system context
into Ollama prompts, and produces outputs. If a phase fails, the executor can retry
with adjusted context or halt with a diagnostic report.

## Context Sources

| Source | YAML Key | Description |
|--------|----------|-------------|
| Files | `context.files` | Read file contents, optional truncation |
| Directories | `context.directories` | List directory contents with depth/pattern |
| PostgreSQL | `context.postgres` | Run SQL queries against `mythos` database |
| Neo4j | `context.graph` | Run Cypher queries against the graph |
| Shell | `context.shell` | Run shell commands, capture output |

## Phase Types

| Type | Description | Required Fields |
|------|-------------|-----------------|
| Prompt | Send context + instructions to Ollama | `prompt`, optionally `output_format` |
| Validation | Check conditions without calling Ollama | `validate` (no `prompt`) |

## Output Formats

| Format | Description |
|--------|-------------|
| `json` | Parse response as JSON, fail if invalid |
| `code` | Strip markdown fences, return raw code |
| `text` | Return raw text (default) |

## Validation Types

| Type | Description | Fields |
|------|-------------|--------|
| `python_syntax` | py_compile check | `file` |
| `contains` | Check strings exist in file | `file`, `strings` |
| `not_contains` | Check strings do NOT exist | `file`, `strings` |
| `file_exists` | Check file exists | `file` |
| `shell` | Run command, check exit code | `command` |

## Template Variables

In prompt text, use `{path.to.value}` for substitution:
- `{mission.description}` — the mission description
- `{context.files.alias_name}` — file contents
- `{context.graph.alias_name}` — graph query results
- `{context.postgres.alias_name}` — SQL query results
- `{context.shell.alias_name}` — shell command output
- `{phases.alias_name}` — output from a prior phase
- `{validation.errors}` — validation error text (in retry prompts)
- `{dynamic_context.files.alias}` — dynamically loaded files

Use double braces `{{like this}}` for literal braces in prompts (e.g., JSON examples).

## CLI Usage

```bash
# Execute a mission
mythos-mission run mission.yaml

# Validate without executing
mythos-mission validate mission.yaml

# Gather context and render prompts without calling Ollama
mythos-mission dry-run mission.yaml

# List recent mission runs
mythos-mission list
```

## Graph Bridge CLI

```bash
# Query functions in a file
graph-bridge functions /opt/mythos/assistants/chat_assistant.py

# Query file dependencies
graph-bridge deps /opt/mythos/assistants/chat_assistant.py

# Find what imports a file
graph-bridge dependents /opt/mythos/core/life_context.py

# Search functions by name
graph-bridge search-func query

# Search files by path
graph-bridge search-file chat_assistant

# List all tables
graph-bridge tables

# List columns for a table
graph-bridge columns transactions

# List all services
graph-bridge services

# Export full snapshot for Claude
graph-bridge snapshot [output_path]
```
