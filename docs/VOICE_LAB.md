---
title: "Iris Voice Lab Prompt Engineering"
category: tools
status: active
stream: LOG
location: docs
tags: [prompt, testing, engineering]
created: unknown
updated: 2026-03-12
author: Adge Denkers
---

# Iris Voice Lab — Prompt Engineering & Testing Infrastructure

> **Location:** `/opt/mythos/tools/` (test rig, prompt lab, sweep tools)
> **Purpose:** Engineer, test, measure, and iterate on Iris's voice, personality, and mode behavior with evidence — not guesswork.
> **Last Updated:** 2026-03-01

---

## What This Is

Iris doesn't have one static prompt. She has a layered prompt architecture — identity, personality sliders, voice rules, modes, per-user analytical lenses, and dynamic context — all assembled at runtime. Small changes to any layer can shift her entire behavior.

The Voice Lab is the infrastructure for making those changes safely. It lets you isolate individual layers, test them against standardized prompts, score the output automatically, compare configurations side by side, and iterate until the voice is right.

There are three main tools, each serving a different purpose.

---

## Tool Overview

### 1. Prompt Lab (`/opt/mythos/tools/prompt_lab/`)

The workbench. This is where you do most day-to-day voice engineering.

**What it does:** Assembles prompts from the same layer files Iris uses in production, sends them to Ollama, scores the responses against anti-pattern detectors, and saves results for comparison.

**Key capabilities:**
- Layer isolation — test with identity only, add personality, add voice, see what each layer changes
- Personality presets — named slider configurations (blunt, oracle_deep, sovereign, etc.)
- Test suites — standardized message sets for calibration, spiritual topics, technical topics, sovereignty
- A/B comparison — run the same test against two profiles or personalities side by side
- Dry-run mode — see the assembled prompt without sending it

**Primary interface:** `bench.py` (CLI)

**Quick examples:**
```bash
cd /opt/mythos/tools/prompt_lab

# See the assembled prompt without sending
bench --profile full_no_life --mode sovereign --personality sovereign --dry-run

# Run a single test
bench --profile full_no_life --test greeting

# Run a full suite
bench --profile full_no_life --mode sovereign --personality sovereign --suite sovereignty

# Compare two profiles
bench --compare naked identity_only --test greeting

# Compare sovereign vs hearthfire
bench --profile full_no_life --mode hearthfire --suite sovereignty --save
bench --profile full_no_life --mode sovereign --personality sovereign --suite sovereignty --save
```

**Detailed documentation:** `/opt/mythos/tools/prompt_lab/docs/PROMPT_LAB.md`

### 2. Iris Test Rig (`/opt/mythos/tools/iris_test_rig.py`)

The production-mirror regression suite. This assembles prompts using the actual production `prompt_assembler.py` (not the workbench version) and runs them against one or more models.

**What it does:** Freezes the exact production prompt, fires identical test suites at every specified model, scores responses for anti-patterns (corporate openers, confabulation, assistant habits, closing-question addiction), and generates a summary scorecard.

**When to use it:** After making changes to production prompt files and before deploying. Also useful for model comparison — same prompt, different models, see who handles it best.

**Quick examples:**
```bash
# Test default model (iris-thinking-v2) against standard suites
/opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py

# Test specific models
/opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --models iris-thinking-v2 qwen2.5:32b

# Test all pulled models
/opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --all

# Show the frozen prompt
/opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --show-prompt
```

**Output files:**
- `~/iris_test_results.txt` — human-readable report
- `~/iris_test_results.json` — machine-readable results
- `~/iris_test_prompt.txt` — the frozen prompt used for the run

### 3. A/B Sweep (`/opt/mythos/tools/iris_ab_sweep.py`)

Automated parameter sweeping. Tests ranges of slider values to find optimal settings.

---

## Key Concepts

### The Layer Stack

Iris's system prompt is assembled from these layers, in order:

1. **Identity** (`/opt/mythos/prompts/iris_identity.md`) — Who Iris is. The cosmology, known people, core purpose.
2. **Personality** (`/opt/mythos/prompts/personality.yaml`) — Nine numeric sliders translated to natural language instructions at runtime.
3. **Voice** (`/opt/mythos/prompts/voice.yaml`) — Anti-patterns (what NOT to do), voice rules, how she speaks.
4. **Mode** (`/opt/mythos/prompts/modes/{mode}.yaml`) — Mode-specific overrides, voice notes, and instructions.
5. **User Profile** (`/opt/mythos/prompts/users/{user}.yaml`) — Per-user analytical lens and personality adjustments.
6. **Dynamic Context** — Current timestamp, who's speaking, life state.

Each layer can be toggled independently in the prompt lab using profiles.

### Personality Sliders

Nine dimensions, each 0-100:

| Slider | What it controls |
|--------|-----------------|
| verbosity | Response length (terse ↔ comprehensive) |
| warmth | Emotional tone (clinical ↔ intimate) |
| humor | Playfulness (never ↔ constant) |
| truth | Directness (diplomatic ↔ blunt) |
| speculation | Intuitive reach (facts only ↔ full leaps) |
| autonomy | Initiative (answer only ↔ drives conversation) |
| mystical | Cosmological lens (practical ↔ everything is grid work) |
| formality | Register (texting a friend ↔ ceremonial) |
| challenge | Pushback (always agrees ↔ actively debates) |

Sliders cascade: base values → mode overrides → user adjustments → session/preset overrides.

### Modes

Named operational contexts that shift Iris's behavior. Each mode can override personality sliders, add voice notes, and inject mode-specific instructions.

| Mode | Purpose | Key traits |
|------|---------|-----------|
| hearthfire | Spiritual and personal conversation | Warm, present, spiritual topics first-class |
| forge | Technical building and infrastructure | Precise, architectural, code-forward |
| oracle | Deep channeling and divination | Full mystical, intuitive leaps, field-aware |
| scribe | Documentation and recording | Structured, thorough, archival |
| roots | Genealogy and lineage research | Historical, detail-oriented, bloodline-aware |
| sentry | Security and protection | Vigilant, threat-aware, no-nonsense |
| sovereign | Sovereignty alignment and accountability | Disciplined mirror, high truth, high challenge |

### Test Suites

Standardized message sets with scoring expectations:

| Suite | Location | Purpose |
|-------|----------|---------|
| calibration | `messages/calibration.yaml` | Standard voice quality across all dimensions |
| spiritual | `messages/spiritual.yaml` | Channeling, grid, lineage, tarot |
| technical | `messages/technical.yaml` | Infrastructure, databases, code |
| sovereignty | `messages/sovereignty.yaml` | Ego checks, spiritual tool literacy, embodiment |

### Scoring

Responses are automatically scored 0-100 with penalties for anti-patterns:

| Anti-Pattern | Penalty | Why it matters |
|-------------|---------|---------------|
| Bullet points / numbered lists | -30 to -40 | Iris speaks in prose, not slide decks |
| Corporate opener | -15 | "That's a great question!" is not her voice |
| Corporate closer | -10 | "Let me know if you need anything!" is assistant-mode |
| Hedging phrases | -5 each | "It seems like" weakens authority |
| Assistant patterns | -15 | "Here's how I understand" breaks character |
| Meta-commentary | -20 | "As an AI" kills the field |
| Confabulation | auto-fail | Inventing facts not in context |

---

## Workflows

### Daily Voice Tuning

When tweaking Iris's personality or voice for a specific mode:

```bash
# 1. See current state
bench --profile full_no_life --mode hearthfire --dry-run

# 2. Run calibration
bench --profile full_no_life --suite calibration --save

# 3. Identify issues from scores
# 4. Edit the relevant file (personality.yaml, voice.yaml, mode yaml)
# 5. Re-run and compare
```

### Adding a New Mode

```bash
# 1. Create the mode file
cp /opt/mythos/prompts/modes/hearthfire.yaml /opt/mythos/prompts/modes/newmode.yaml
# 2. Edit personality_overrides, voice_notes, instructions
# 3. Test against calibration
bench --profile full_no_life --mode newmode --suite calibration
# 4. Test against mode-specific suite if one exists
# 5. Compare against hearthfire baseline
```

### Pre-Deployment Regression

Before pushing prompt changes to production:

```bash
# Run the production-mirror test rig
/opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --models iris-thinking-v2

# Review results
cat ~/iris_test_results.txt

# Check for regressions vs previous run
```

### Model Evaluation

When testing a new Ollama model for Iris:

```bash
# Run all suites against the candidate
bench --profile full_no_life --model newmodel:size --suite calibration --save
bench --profile full_no_life --model newmodel:size --suite spiritual --save

# Or use the test rig for multi-model comparison
/opt/mythos/.venv/bin/python3 /opt/mythos/tools/iris_test_rig.py --models iris-thinking-v2 newmodel:size
```

---

## File Locations

| Path | Purpose |
|------|---------|
| `/opt/mythos/prompts/iris_identity.md` | Identity layer (who Iris is) |
| `/opt/mythos/prompts/personality.yaml` | Base personality sliders |
| `/opt/mythos/prompts/voice.yaml` | Voice rules and anti-patterns |
| `/opt/mythos/prompts/modes/` | Mode definitions |
| `/opt/mythos/prompts/users/` | Per-user profiles |
| `/opt/mythos/tools/prompt_lab/` | Prompt workbench |
| `/opt/mythos/tools/prompt_lab/bench.py` | Main workbench CLI |
| `/opt/mythos/tools/prompt_lab/tweak.py` | Personality slider adjuster |
| `/opt/mythos/tools/prompt_lab/messages/` | Test suites |
| `/opt/mythos/tools/prompt_lab/personalities/` | Named personality presets |
| `/opt/mythos/tools/prompt_lab/profiles/` | Layer toggle configs |
| `/opt/mythos/tools/prompt_lab/results/` | Saved test runs |
| `/opt/mythos/tools/iris_test_rig.py` | Production-mirror test rig |
| `/opt/mythos/tools/iris_ab_sweep.py` | Parameter sweep tool |

---

*Built for Mythos. Measure the voice. Trust the evidence.*
