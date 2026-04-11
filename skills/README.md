# Mythos Skills System

## Overview

Skills are structured instruction files that tell an LLM how to execute a
repeatable process. They are the executable knowledge base of the Mythos system.
Iris reads the **REGISTRY.yaml** to discover available skills, matches trigger
conditions against the current task, loads the relevant skill file, and follows
its instructions.

## Directory Structure

```
/opt/mythos/skills/
├── REGISTRY.yaml              # Master index (Iris reads this first)
├── README.md                  # This file
├── analytical/                # Process data, produce analysis
│   ├── soul_stratigraphy.md         # Tri-field astro (Hellenistic+Vedic+Western) — v2.0
│   ├── western_tropical_natal_chart.md  # Standard Western natal chart — v2.0
│   └── tools/                       # Shared computation engines
│       └── ephemeris.py             # Swiss Ephemeris engine (pyswisseph)
├── builder/                   # Create/deploy infrastructure
│   ├── build_patch.md               # Standard Mythos patch creation
│   ├── build_feature_api.md         # FastAPI endpoint builder
│   ├── build_feature_telegram_mode.md   # Telegram bot mode builder
│   ├── build_feature_telegram_tool.md   # Telegram bot command builder
│   └── build_feature_self.md        # Iris self-build (T3 — needs approval)
├── meta/                      # Skills about skills
│   └── humandoc_to_skill.md         # Convert human docs to skill format
└── templates/
    └── SKILL_TEMPLATE.md            # Canonical skill format template
```

## Skills Inventory

### Analytical Skills

| Skill | Version | File | Engine | What It Does |
|-------|---------|------|--------|-------------|
| **soul_stratigraphy** | 2.0 | `analytical/soul_stratigraphy.md` | ephemeris.py | Full tri-field astrological analysis. Hellenistic (sect, dignities, Whole Sign) + Vedic (sidereal, nakshatras, dashas) + Western Tropical (Placidus, aspects, psychology) + synthesis layer. The deepest chart reading available. |
| **western_tropical_natal_chart** | 2.0 | `analytical/western_tropical_natal_chart.md` | ephemeris.py | Standard Western natal chart. Placidus houses, tropical positions, aspects, dignities. Layer 1 of Soul Stratigraphy as a standalone. Also handles chart rectification. |

### Builder Skills

| Skill | File | Risk | What It Does |
|-------|------|------|-------------|
| **build_patch** | `builder/build_patch.md` | T2-patch | Creates numbered Mythos patches with install.sh. The standard deployment mechanism. |
| **build_feature_api** | `builder/build_feature_api.md` | T2-patch | Designs and deploys FastAPI endpoints within the Mythos gateway. |
| **build_feature_telegram_mode** | `builder/build_feature_telegram_mode.md` | T2-patch | Creates Telegram bot operating modes (/life-log, /finance, etc.) with state management. |
| **build_feature_telegram_tool** | `builder/build_feature_telegram_tool.md` | T2-patch | Builds discrete Telegram bot commands and inline tools. |
| **build_feature_self** | `builder/build_feature_self.md` | T3-propose | For when Iris identifies her own capability gaps. Always requires Ka'tuar'el's approval. |

### Meta Skills

| Skill | File | What It Does |
|-------|------|-------------|
| **humandoc_to_skill** | `meta/humandoc_to_skill.md` | Transforms human-written documents into properly formatted Mythos skill files. |

## Shared Tools

Tools are computation engines that live alongside skills but serve multiple
skills. They're registered in REGISTRY.yaml under the `tools` section.

| Tool | Path | Runtime | Dependencies | Used By |
|------|------|---------|-------------|---------|
| **ephemeris_engine** | `analytical/tools/ephemeris.py` | `/opt/mythos/.venv/bin/python3` | pyswisseph | soul_stratigraphy, western_tropical_natal_chart |

### Ephemeris Engine

The ephemeris engine (`analytical/tools/ephemeris.py`) is a Swiss Ephemeris
wrapper that computes real planetary positions, house cusps, aspects, Vedic
sidereal positions, nakshatras, and Vimshottari Dasha timelines.

**CLI usage:**
```bash
/opt/mythos/.venv/bin/python3 /opt/mythos/skills/analytical/tools/ephemeris.py natal \
  --year 1985 --month 3 --day 15 --hour 10 --minute 30 \
  --lat 40.7128 --lon -74.0060 --tz -5 \
  --name "Person Name" --output /tmp/chart.json
```

**Library usage:**
```python
import sys
sys.path.insert(0, '/opt/mythos/skills/analytical/tools')
from ephemeris import calculate_natal, calculate_transits, calculate_synastry
```

Three calculation modes: `calculate_natal()`, `calculate_transits()`,
`calculate_synastry()`. All return structured dictionaries with positions
across Western Tropical, Hellenistic, and Vedic frameworks.

## Skill File Format

Each skill is a Markdown file with YAML frontmatter:
- **Frontmatter**: Structured metadata (name, category, risk tier, requirements)
- **Body**: Imperative instructions optimized for LLM execution

See `templates/SKILL_TEMPLATE.md` for the canonical format.

## Risk Tiers

| Tier | Execution Model | When |
|------|----------------|------|
| **T1 — Autonomous** | Execute directly, notify after | Analysis, reports, safe reads |
| **T2 — Patch** | Build patch, deploy via monitor | Code changes, new features |
| **T3 — Propose** | Propose plan, wait for approval | Schema changes, security, self-modification |

## Adding New Skills

1. Write the skill using `humandoc_to_skill` or from `SKILL_TEMPLATE.md`
2. Place in the appropriate category directory
3. Add entry to `REGISTRY.yaml`
4. Deploy via patch

## Conventions

- Skill names use snake_case
- One skill per file
- All file paths are absolute (Arcturus paths)
- Diagnostic dumps use the standard `~/diag.txt` pattern
- Builder skills always terminate through `build_patch`
- Every skill includes validation criteria and error handling
- Skills that need computation reference shared tools, not inline code
- Tool scripts live in `{category}/tools/` subdirectories

---
_System designed by Ka'tuar'el_
_Last updated: 2026-03-01_
