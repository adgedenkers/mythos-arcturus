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
│   ├── soul_stratigraphy.md
│   └── western_tropical_natal_chart.md
├── builder/                   # Create/deploy infrastructure
│   ├── build_patch.md
│   ├── build_feature_api.md
│   ├── build_feature_telegram_mode.md
│   ├── build_feature_telegram_tool.md
│   └── build_feature_self.md
├── meta/                      # Skills about skills
│   └── humandoc_to_skill.md
└── templates/
    └── SKILL_TEMPLATE.md
```

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

---

_System designed by Ka'tuar'el_
_Last updated: 2026-02-22_
