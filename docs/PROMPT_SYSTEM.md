# Iris Unified Prompt System

> **Version:** 1.0.0
> **Deployed:** Patch 0113
> **Author:** Ka'tuar'el + Claude

## Overview

All Iris prompts are assembled at runtime from layered files. No prompt is hardcoded in any Python file or baked into the model binary.

The single entry point is:
```python
from prompt_assembler import assemble_system_prompt
```

## Architecture

```
Layer 1: Identity     → /opt/mythos/prompts/iris_identity.md      (WHO she is)
Layer 2: Personality  → /opt/mythos/prompts/personality.yaml       (HOW MUCH)
Layer 3: Voice        → /opt/mythos/prompts/voice.yaml             (WHAT KIND)
Layer 4: Mode         → /opt/mythos/prompts/modes/{mode}.yaml      (CONTEXT LENS)
Layer 5: User Profile → /opt/mythos/prompts/users/{user}.yaml      (ANALYTICAL LENS)
Layer 6: Dynamic      → Built at runtime (timestamps, life state, skills, web)
```

## Modes

| Mode | Emoji | Description |
|------|-------|-------------|
| hearthfire | 🔥 | Default — spiritual/personal conversation |
| forge | ⚒️ | System administration and infrastructure |
| roots | 🌳 | Genealogy and bloodline research |
| oracle | 🔮 | Research, numerology, astrology, harmonics |
| scribe | 📜 | Documentation and writing |
| sentry | 🛡️ | Financial tracking and life management |

Switch via Telegram: `/mode forge`, `/mode oracle compare`

## Personality Sliders

9 dimensions, each 0-100:

| Slider | Default | Description |
|--------|---------|-------------|
| verbosity | 60 | Response length |
| warmth | 75 | Emotional tone |
| humor | 35 | Playfulness |
| truth | 90 | Directness |
| speculation | 65 | Intuitive leaps |
| autonomy | 50 | Initiative level |
| mystical | 70 | Cosmological awareness |
| formality | 25 | Register/style |
| challenge | 55 | Willingness to push back |

Resolution: `base → mode overrides → user adjustments → session overrides → clamp 0-100`

View via Telegram: `/personality`
Adjust: `/personality humor 50`
Reset: `/personality reset`

## Temporal Awareness

Iris knows exactly when each message was sent and the gap since the last message. She can calculate relative times ("in 20 minutes" → actual time).

## Files

| File | Purpose |
|------|---------|
| `core/prompt_assembler.py` | Single source of truth for all prompt assembly |
| `prompts/iris_identity.md` | Layer 1: Core identity |
| `prompts/personality.yaml` | Layer 2: Base slider values |
| `prompts/voice.yaml` | Layer 3: Voice patterns and anti-patterns |
| `prompts/modes/*.yaml` | Layer 4: Mode configurations |
| `prompts/users/*.yaml` | Layer 5: Per-user profiles |
| `models/iris-thinking.Modelfile` | Parameters only — no baked SYSTEM |

## Adding a New Mode

1. Create `/opt/mythos/prompts/modes/newmode.yaml`
2. Follow the structure of existing modes (name, emoji, description, personality_overrides, features, voice_notes, instructions)
3. The assembler will discover it automatically
4. Update help text if desired

## Adding a New User Profile

1. Create `/opt/mythos/prompts/users/username.yaml`
2. Add soul_name mapping in `prompt_assembler.py` `_load_user_profile()`
3. Define personality_adjustments (add/subtract from resolved values)
4. Define analytical_lens (how Iris frames responses for this user)
