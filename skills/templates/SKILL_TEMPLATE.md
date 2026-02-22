---
name: skill-name-here
version: "1.0"
category: analytical | builder
risk_tier: T1-autonomous | T2-patch | T3-propose
description: >
  One-paragraph description of what this skill does and when to use it.
  Include trigger phrases and contexts so Iris knows when to invoke this.
requires:
  services: []      # e.g., [postgresql, neo4j, ollama, fastapi]
  tools: []         # e.g., [python3, psql, cypher-shell, curl]
  files: []         # e.g., [/opt/mythos/docs/ARCHITECTURE.md]
  env_vars: []      # e.g., [NEO4J_PASSWORD, TELEGRAM_BOT_TOKEN]
inputs:
  required: []      # What the LLM needs before starting
  optional: []      # Nice-to-have context
outputs:
  files: []         # What files this produces
  formats: []       # e.g., [.sql, .json, .md, .zip]
  destinations: []  # Where outputs go
---

# {Skill Name}

## Purpose

Why this skill exists. What problem it solves. One paragraph max.

## Pre-Flight Checks

Steps to verify before executing. Check service availability, file existence,
current state of relevant systems. List these as imperative commands.

## Process

### Step 1: {Name}

What to do. Be specific and imperative. Include exact commands, queries,
or code patterns where relevant.

**Decision point:** If X, go to Step 2a. If Y, go to Step 2b.

### Step 2: {Name}

Continue the process. Each step should be atomic — one clear action or
decision.

### Step N: Validation

How to verify the output is correct. Include specific checks, expected
values, or test commands.

## Output Format

Describe exactly what the final deliverable looks like.
Include templates or examples of the output structure.

## Error Handling

Common failure modes and what to do about each one.

| Error | Cause | Resolution |
|-------|-------|------------|
| ... | ... | ... |

## Examples

### Example 1: {Scenario}

**Input:** ...
**Process notes:** ...
**Output:** ...

---

_Last updated: {date}_
_Author: Ka'tuar'el_
