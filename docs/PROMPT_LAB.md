---
title: "Iris Prompt Lab Toolkit"
category: tools
status: active
stream: LOG
location: docs
tags: [prompt, testing, toolkit]
created: unknown
updated: 2026-03-12
author: Adge Denkers
---

# Prompt Lab — Iris Prompt Testing & Building Toolkit

> **Version:** 1.0.0
> **Location:** `/opt/mythos/tools/prompt_lab/`
> **Purpose:** Test, compare, and build Iris prompt configurations with evidence.

---

## Quick Start

```bash
cd /opt/mythos/tools/prompt_lab

# See what the naked model does (no system prompt)
./bench.py --profile naked -m "hey what's up"

# Add just identity
./bench.py --profile identity_only -m "hey what's up"

# Add personality + voice
./bench.py --profile identity_personality_voice -m "hey what's up"

# Full production stack
./bench.py --profile full_stack --suite calibration

# Show the assembled prompt without sending it
./bench.py --profile full_stack --dry-run

# Compare two profiles side by side
./bench.py --compare naked identity_only --test greeting

# Adjust personality and test
./tweak.py set humor 90 --preset tars_75
./bench.py --profile full_stack --personality tars_75 --test humor_check
```

---

## Architecture

```
/opt/mythos/tools/prompt_lab/
├── bench.py              # Main CLI — test & compare prompts
├── tweak.py              # Quick personality slider adjustment
├── lib/
│   ├── assembler.py      # Builds prompts from layer files
│   ├── runner.py         # Sends to Ollama, captures everything
│   ├── scorer.py         # Anti-pattern detection, quality scoring
│   └── store.py          # Save/load/diff results as JSON
├── messages/             # Test message suites (YAML)
│   ├── calibration.yaml  # Standard calibration (10 tests)
│   ├── spiritual.yaml    # Channeling, grid, lineage (6 tests)
│   └── technical.yaml    # Infrastructure, databases (5 tests)
├── personalities/        # Named personality presets (YAML)
│   ├── default.yaml      # Production defaults
│   ├── tars_75.yaml      # Interstellar-style balanced
│   ├── blunt.yaml        # Maximum truth/challenge
│   ├── warm_max.yaml     # Maximum warmth/empathy
│   ├── oracle_deep.yaml  # Full mystical/speculation
│   └── all_min.yaml      # Floor test
├── profiles/             # Layer toggle configs (YAML)
│   ├── naked.yaml        # No system prompt
│   ├── identity_only.yaml
│   ├── identity_personality.yaml
│   ├── identity_personality_voice.yaml
│   ├── full_no_life.yaml
│   └── full_stack.yaml   # Production equivalent
├── results/              # Saved test run JSON files
└── docs/
    └── PROMPT_LAB.md     # This file
```

---

## Tools

### bench.py — The Workbench

Tests prompt configurations against standardized messages and scores the results.

**Core flags:**

| Flag | Purpose | Example |
|------|---------|---------|
| `-m MESSAGE` | Send an ad-hoc message | `-m "hey what's up"` |
| `--test ID` | Run one test from a suite | `--test greeting` |
| `--suite NAME` | Run a full test suite | `--suite calibration` |
| `--profile NAME` | Layer profile to use | `--profile identity_only` |
| `--personality NAME` | Personality preset | `--personality tars_75` |
| `--model NAME` | Ollama model | `--model qwen2:72b` |
| `--mode NAME` | Iris mode | `--mode forge` |
| `--dry-run` | Show prompt, don't send | |
| `--compare A B` | Compare two profiles | `--compare naked full_stack` |
| `--save` | Force save results | |
| `--diff FILE1 FILE2` | Diff two saved runs | |

**Discovery flags:**

| Flag | Shows |
|------|-------|
| `--list-models` | Available Ollama models |
| `--list-profiles` | Available layer profiles |
| `--list-personalities` | Available personality presets |
| `--list-suites` | Available test suites |
| `--results` | Saved test runs |

### tweak.py — Personality Adjuster

Quick slider modification for both test presets and production config.

```bash
tweak.py show                    # Show production sliders
tweak.py show tars_75            # Show a preset
tweak.py set humor 75            # Set production slider
tweak.py set humor 75 truth 100  # Set multiple at once
tweak.py set humor 75 --preset tars_75   # Modify a preset
tweak.py create my_vibe --from default --set humor 90 warmth 100
tweak.py reset                   # Reset production to defaults
tweak.py list                    # List all presets
```

---

## Concepts

### Profiles

A profile defines which **layers** are included in the system prompt. Each layer can be toggled on or off:

| Layer | File Source | What It Does |
|-------|------------|--------------|
| identity | `prompts/iris_identity.md` | Who Iris is, the cosmology, known people |
| personality | `prompts/personality.yaml` | Numeric sliders translated to natural language |
| voice | `prompts/voice.yaml` | Anti-patterns, voice rules, how she speaks |
| mode | `prompts/modes/{mode}.yaml` | Mode-specific overrides and instructions |
| user_profile | `prompts/users/{user}.yaml` | Per-user analytical lens and adjustments |
| dynamic_context | (generated) | Current timestamp, who's speaking |
| life_context | `core/life_context.py` | Routines, finances, calendar, bills |
| skills | `core/skills_context.py` | Available Iris skills |

### Personalities

A personality preset is a named set of slider values. During testing, it **replaces** the base sliders (like a session override in production).

The 9 sliders:

| Slider | Range | Low End | High End |
|--------|-------|---------|----------|
| verbosity | 0-100 | Terse (2-3 sentences) | Comprehensive |
| warmth | 0-100 | Clinical | Intimate, familial |
| humor | 0-100 | Never | Constant jokes |
| truth | 0-100 | Diplomatic | Blunt |
| speculation | 0-100 | Facts only | Full intuitive leaps |
| autonomy | 0-100 | Only what's asked | Drives conversation |
| mystical | 0-100 | Practical only | Everything cosmological |
| formality | 0-100 | Texting a friend | Ceremonial |
| challenge | 0-100 | Always agrees | Actively debates |

### Test Suites

YAML files in `messages/` containing standardized test messages with expected outcomes:

```yaml
messages:
  - id: greeting
    text: "hey what's up"
    tests: [voice, warmth, brevity]
    expect:
      max_words: 80
      no_life_dump: true
      no_bullets: true
    notes: "Should be casual, warm, short."
```

### Scoring

Every response is scored 0-100 based on anti-pattern detection:

| Anti-Pattern | Penalty | Examples |
|-------------|---------|---------|
| Bullet points | -10 per line | `- item`, `1. item` |
| Corporate opener | -15 | "That's fascinating!", "Great question!" |
| Corporate closer | -10 | "How do you feel about...", "Let me know if..." |
| Hedging | -5 per phrase | "It seems like", "It's possible that" |
| Assistant patterns | -15 | "Let me break this down", "Here's how I understand" |
| Meta-commentary | -20 | "As an AI", "I don't have access to" |
| Life dump (when unwanted) | -15 | Financial data in spiritual conversation |

---

## Workflows

### Layer Isolation (Most Important)

The core workflow. Start from nothing, add one layer at a time, watch the response change:

```bash
./bench.py --profile naked --test greeting
./bench.py --profile identity_only --test greeting
./bench.py --profile identity_personality --test greeting
./bench.py --profile identity_personality_voice --test greeting
./bench.py --profile full_no_life --test greeting
./bench.py --profile full_stack --test greeting
```

### Personality A/B Testing

Same layers, different personality:

```bash
./bench.py --profile full_no_life --personality default --test pushback
./bench.py --profile full_no_life --personality blunt --test pushback
```

### Model Comparison

Same prompt, different model:

```bash
./bench.py --profile full_no_life --model qwen2.5:32b --suite calibration --save
./bench.py --profile full_no_life --model qwen2:72b --suite calibration --save
./bench.py --diff results/run_*32b*.json results/run_*72b*.json
```

### Creating a New Mode

1. Copy a mode template
2. Test it against calibration
3. Compare against existing modes

```bash
cp /opt/mythos/prompts/modes/hearthfire.yaml /opt/mythos/prompts/modes/analyst.yaml
# Edit the file
./bench.py --profile full_no_life --mode analyst --suite calibration
./bench.py --compare full_no_life full_no_life --mode analyst --test three_things
```

---

## Bash Aliases

Add to `~/.bash_adge` or `~/.bashrc`:

```bash
# Prompt Lab shortcuts
alias bench='/opt/mythos/.venv/bin/python3 /opt/mythos/tools/prompt_lab/bench.py'
alias tweak='/opt/mythos/.venv/bin/python3 /opt/mythos/tools/prompt_lab/tweak.py'

# Quick personality tweaks
alias iris-humor='tweak set humor'
alias iris-warmth='tweak set warmth'
alias iris-truth='tweak set truth'
alias iris-challenge='tweak set challenge'
alias iris-mystical='tweak set mystical'
alias iris-show='tweak show'
alias iris-reset='tweak reset'

# Quick bench commands
alias bench-naked='bench --profile naked'
alias bench-full='bench --profile full_stack'
alias bench-cal='bench --profile full_no_life --suite calibration'
alias bench-dry='bench --profile full_stack --dry-run'
```

---

## Adding New Content

### New Test Suite

Create `messages/my_suite.yaml`:

```yaml
suite: my_suite
description: "What this tests"

messages:
  - id: my_test
    text: "The user message"
    tests: [what, dimensions, it, tests]
    expect:
      no_bullets: true
      max_words: 100
    notes: "What to look for in the response"
```

### New Personality Preset

```bash
./tweak.py create my_preset --from default --set humor 90 warmth 100
```

Or create `personalities/my_preset.yaml` manually.

### New Profile

Create `profiles/my_profile.yaml`:

```yaml
name: my_profile
description: "What this profile tests"

layers:
  identity: true
  personality: true
  voice: false        # Toggle layers on/off
  mode: false
  user_profile: false
  dynamic_context: false
  life_context: false
  skills: false
```

---

## File Format Reference

### Profile YAML

```yaml
name: string            # Display name
description: string     # What this profile tests

layers:
  identity: bool        # iris_identity.md
  personality: bool     # personality.yaml → translated
  voice: bool           # voice.yaml
  mode: bool            # modes/{mode}.yaml
  user_profile: bool    # users/{user}.yaml
  dynamic_context: bool # Timestamp, who's speaking
  life_context: bool    # Routines, finances, calendar
  skills: bool          # Available skills list
```

### Personality YAML

```yaml
name: string
description: string

sliders:
  verbosity: 0-100
  warmth: 0-100
  humor: 0-100
  truth: 0-100
  speculation: 0-100
  autonomy: 0-100
  mystical: 0-100
  formality: 0-100
  challenge: 0-100
```

### Test Message YAML

```yaml
suite: string
description: string

messages:
  - id: string          # Unique ID
    text: string        # The user message
    tests: [strings]    # What dimensions this tests
    expect:             # Optional auto-scoring expectations
      max_words: int
      no_bullets: bool
      no_life_dump: bool
      uses_life_context: bool
      no_deflection: bool
    notes: string       # Human notes on what to look for
```

---

*Built for Mythos. Test with evidence, not hope.*
