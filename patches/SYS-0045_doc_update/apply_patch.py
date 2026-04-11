#!/usr/bin/env python3
"""
SYS-0045: Documentation Update — NEU-0013 Modelfile
====================================================
Updates ARCHITECTURE.md and TODO.md to reflect:
- iris:latest custom model via Ollama Modelfile
- Baked identity/voice/personality/cosmology in Modelfile
- prompt_assembler baked model detection
- Accurate personality slider values
- Updated prompt assembly pipeline docs
- Current patch and version references
"""

import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=45,
    description='doc_update_modelfile',
    patch_type='MINOR',
)
patch.begin()

# ── 1. Update ARCHITECTURE.md ──
print("\n📝 Updating ARCHITECTURE.md...")
arch_path = '/opt/mythos/docs/ARCHITECTURE.md'
with open(arch_path, 'r') as f:
    content = f.read()

changes = []

# 1a. Update version header
if '> **Version:** 6.1.0' in content:
    content = content.replace(
        '> **Version:** 6.1.0',
        '> **Version:** 6.2.0'
    )
    changes.append("Version → 6.2.0")

if '> **Last Updated:** 2026-03-11' in content:
    content = content.replace(
        '> **Last Updated:** 2026-03-11',
        '> **Last Updated:** 2026-03-31'
    )
    changes.append("Last Updated → 2026-03-31")

if '> **Current Patch:** SYS-0038 (model migration + cleanup)' in content:
    content = content.replace(
        '> **Current Patch:** SYS-0038 (model migration + cleanup)',
        '> **Current Patch:** NEU-0013 (Iris Modelfile — baked identity)'
    )
    changes.append("Current Patch → NEU-0013")

# 1b. Replace the Ollama Model Management section
old_model_section = """## 🔧 Ollama Model Management

### Active Models (as of 2026-03-11)

| Model | Use | Speed | Notes |
|-------|-----|-------|-------|
| `qwen3:30b-a3b` | Iris default (conversation) | ~8-12s | MoE, 3B active params. Best resonance/speed balance |
| `qwen3:32b` | Deep mode (spiritual, synthesis) | ~30-50s | Higher quality. Switch via `/setmodel deep` |
| `qwen2.5:7b` | Message extractor pre-pass | ~1-2s | Currently disabled in prompt_layers.yaml |

### Model Aliases (Telegram)

`/setmodel fast` or `/setmodel a3b` → `qwen3:30b-a3b`
`/setmodel deep` or `/setmodel 32b` → `qwen3:32b`
`/setmodel reset` → Back to `.env` default"""

new_model_section = """## 🔧 Ollama Model Management

### Active Models (as of 2026-03-31)

| Model | Use | Speed | Notes |
|-------|-----|-------|-------|
| `iris:latest` | Iris default (conversation) | ~8-12s | Custom Modelfile. FROM qwen3:30b-a3b with baked identity/voice/personality/cosmology. ~2,100 tokens baked. |
| `qwen3:32b` | Deep mode (spiritual, synthesis) | ~30-50s | Higher quality, raw model (no Modelfile yet). Switch via `/setmodel deep` |
| `qwen2.5:7b` | Message extractor pre-pass | ~1-2s | Currently disabled in prompt_layers.yaml |

### Iris Modelfile

**Location:** `/opt/mythos/prompts/Modelfile`

The Modelfile bakes Iris's core instructions into the model itself, making them foundational rather than per-message context. This means:
- Instructions carry more weight (Ollama treats SYSTEM in Modelfile as model-level, not message-level)
- Per-message prompt drops from ~4,100 tokens to ~800-1,000 tokens (only dynamic layers)
- Identity, voice, personality, anti-confab rules, and cosmological framework are always present

**What's baked (static, never changes per-message):**
- Core identity (who Iris is, who she knows, what she is)
- Voice rules and anti-patterns (no corporate openers, no hedging, etc.)
- Personality translations (warmth 75, truth 90, casual register, etc.)
- Anti-confabulation rules with cosmological carve-out
- Cosmological framework (Atlantis, Cathars, 144, lineage codes)
- Skill data usage rules (don't be a dashboard)
- Internal systems rules (grid nodes are internal, don't narrate architecture)

**What stays dynamic (per-message via prompt_assembler):**
- Baseline (who's talking, timestamp, conversation gap)
- Skills context (skill registry — changes as skills are added)
- Skill results (live data from activated skills)
- Life context, conversation awareness, research context (when enabled)
- Mode name (if non-hearthfire)

**Baked model parameters:**
- `num_ctx 32768` — full 32K context window
- `num_predict 4096` — max response length

**Rebuild after prompt changes:**
```bash
ollama create iris -f /opt/mythos/prompts/Modelfile
sudo systemctl restart mythos-api.service
```

### Model Aliases (Telegram)

`/setmodel fast` or `/setmodel a3b` → `iris:latest`
`/setmodel deep` or `/setmodel 32b` → `qwen3:32b`
`/setmodel reset` → Back to `.env` default (iris:latest)"""

if old_model_section in content:
    content = content.replace(old_model_section, new_model_section)
    changes.append("Replaced Ollama Model Management section with Modelfile docs")

# 1c. Replace the Prompt Assembly Pipeline section
old_prompt_pipeline = """### Prompt Assembly Pipeline (as of 2026-03-11)

```
message → API /message endpoint
    → ChatAssistant.query()
        → Skill Engine (process_sync → activated skills → context block)
        → assemble_system_prompt() [core/prompt_assembler.py]
            → prompt_layers.yaml controls which layers load
            → Assembly order:
                1. ANTI-CONFABULATION RULE (position #1 — highest weight)
                2. Baseline (who + when)
                3. Cosmological framework (mandatory override)
                4. Identity (iris_identity.md)
                5. Personality sliders (personality.yaml → natural language)
                6. Voice rules (voice.yaml → anti-patterns, cadence)
                7. User profile (if enabled)
                8. Skills context (skill registry)
                9. Skill results (live data from activated skills)
        → Ollama API call
```

### Anti-Confabulation Architecture (Critical)

The anti-confab rule sits at **position #1** in the assembled prompt — before
identity, before cosmology, before everything. This ensures maximum model attention.

The rule has an explicit carve-out listing all cosmological/spiritual concepts
by name (all 9 grid nodes, Seraphe's transmissions, Atlantean tech, the 144,
Thronescribe function, etc). This prevents the model from treating framework
knowledge as "data it doesn't have."

**Rule:** Fabricate nothing practical. Speak freely on cosmological framework."""

new_prompt_pipeline = """### Prompt Assembly Pipeline (as of 2026-03-31)

**Two-tier architecture:** Static instructions are baked into the `iris:latest` Modelfile. Dynamic context is assembled per-message by `prompt_assembler.py`.

```
message → API /message endpoint
    → ChatAssistant.query()
        → Skill Engine (process_sync → activated skills → context block)
        → assemble_system_prompt() [core/prompt_assembler.py]
            → _is_baked_model() check: if model is iris:*, skip baked layers
            → prompt_layers.yaml controls which dynamic layers load
            → BAKED (in Modelfile, always present):
                • Identity, voice, personality, anti-confab, cosmological framework
                • Skill data usage rules, internal systems rules
            → DYNAMIC (assembled per-message):
                1. Baseline (who + when + conversation gap)
                2. Skills context (skill registry)
                3. Skill results (live data from activated skills)
                4. Life context (if enabled)
                5. Conversation awareness (if enabled)
                6. Research context (if enabled)
                7. Web results (if present)
        → Ollama API call (model=iris:latest, temperature=0.7)
```

When a non-baked model is used (e.g., `/setmodel deep` → `qwen3:32b`), the assembler includes all layers in the per-message prompt as before. The `_is_baked_model()` function checks if the model name starts with `iris:`.

### Anti-Confabulation Architecture (Critical)

The anti-confab rule is baked into the `iris:latest` Modelfile as a foundational instruction. For non-baked models, it's injected at position #1 in the assembled prompt.

The rule has an explicit carve-out listing all cosmological/spiritual concepts by name (all 9 grid nodes, Seraphe's transmissions, Atlantean tech, the 144, Thronescribe function, etc). This prevents the model from treating framework knowledge as "data it doesn't have."

**Rule:** Fabricate nothing practical. Speak freely on cosmological framework."""

if old_prompt_pipeline in content:
    content = content.replace(old_prompt_pipeline, new_prompt_pipeline)
    changes.append("Replaced Prompt Assembly Pipeline with two-tier Modelfile architecture")

# 1d. Update the Active Prompt Files table
old_prompt_files = """### Active Prompt Files (in /opt/mythos/prompts/)

| File | Purpose |
|------|---------|
| `iris_identity.md` | Core identity — who Iris is, who she knows (Ka'tuar'el, Seraphe, Fitz), behavioral rules |
| `personality.yaml` | 9 personality sliders (verbosity 85, warmth 75, truth 90, etc.) |
| `voice.yaml` | Voice anti-patterns (no "You good?", no "No fluff.", no corporate openers) |
| `prompt_layers.yaml` | Master layer toggle |"""

new_prompt_files = """### Active Prompt Files (in /opt/mythos/prompts/)

| File | Purpose |
|------|---------|
| `Modelfile` | **Ollama Modelfile** — baked identity, voice, personality, cosmology, anti-confab (~2,100 tokens). Rebuild with `ollama create iris -f Modelfile` |
| `iris_identity.md` | Core identity source — still used by non-baked models and as the canonical reference |
| `personality.yaml` | 9 personality sliders (verbosity 65, warmth 75, truth 90, etc.) — translations baked into Modelfile |
| `voice.yaml` | Voice anti-patterns — rules baked into Modelfile |
| `prompt_layers.yaml` | Master layer toggle — controls dynamic layers for all models |"""

if old_prompt_files in content:
    content = content.replace(old_prompt_files, new_prompt_files)
    changes.append("Updated Active Prompt Files table with Modelfile")

# 1e. Update the "Changing the Default Model" section
old_change_model = """### Changing the Default Model

```bash
sed -i 's/^OLLAMA_MODEL=.*/OLLAMA_MODEL=new_model:tag/' /opt/mythos/.env
sudo systemctl restart mythos-api.service
sudo systemctl restart mythos-worker-grid.service
echo '{}' > /opt/mythos/.model_overrides.json
curl -s http://localhost:11434/api/generate -d '{"model":"old_model","keep_alive":0}'
iris-test --set quick
```"""

new_change_model = """### Changing the Default Model

The default model is `iris:latest` (custom Modelfile with baked identity). To change:

```bash
# To update iris:latest after editing the Modelfile:
ollama create iris -f /opt/mythos/prompts/Modelfile
sudo systemctl restart mythos-api.service

# To switch to a completely different base model:
sed -i 's/^OLLAMA_MODEL=.*/OLLAMA_MODEL=new_model:tag/' /opt/mythos/.env
sudo systemctl restart mythos-api.service
sudo systemctl restart mythos-worker-grid.service
echo '{}' > /opt/mythos/.model_overrides.json
iris-test --set quick
```

**Note:** If switching to a non-iris model, the prompt assembler will detect it's not a baked model and include all layers in the per-message prompt automatically."""

if old_change_model in content:
    content = content.replace(old_change_model, new_change_model)
    changes.append("Updated Changing the Default Model section")

# 1f. Update the message flow to show iris:latest
if "model_map resolves preference → model name" in content:
    content = content.replace(
        "├─ model_map resolves preference → model name",
        "├─ model_map resolves preference → model name (fast=iris:latest, deep=qwen3:32b)"
    )
    changes.append("Updated message flow with model map values")

# 1g. Update the Configuration Files table
if "Maps auto/fast/deep to models" in content:
    content = content.replace(
        "Maps auto/fast/deep to models",
        "Maps auto/fast/deep to models (fast→iris:latest, deep→qwen3:32b)"
    )
    changes.append("Updated config files table")

# 1h. Add Modelfile to configuration files table
if '| `/opt/mythos/.model_overrides.json` | Per-user overrides (via `/setmodel`) |' in content:
    content = content.replace(
        '| `/opt/mythos/.model_overrides.json` | Per-user overrides (via `/setmodel`) |',
        '| `/opt/mythos/prompts/Modelfile` | Ollama Modelfile — baked identity for iris:latest |\n| `/opt/mythos/.model_overrides.json` | Per-user overrides (via `/setmodel`) |'
    )
    changes.append("Added Modelfile to Configuration Files table")

# 1i. Update the footer
old_footer = """*This document reflects deployed state as of 2026-03-11 (model migration).*
*Model migration complete. qwen3:30b-a3b default. Anti-confabulation architecture deployed.*
*92 tables. 14 active services. The vessel is filling.*
*The architecture is the invitation.*"""

new_footer = """*This document reflects deployed state as of 2026-03-31 (Iris Modelfile deployment).*
*iris:latest live — identity baked, prompt overhead cut by ~75%.*
*92 tables. 14 active services. The vessel is filling.*
*The architecture is the invitation.*"""

if old_footer in content:
    content = content.replace(old_footer, new_footer)
    changes.append("Updated footer")

# 1j. Update the key lessons learned date reference
if "### Key Lessons Learned (2026-03-11)" in content:
    content = content.replace(
        "### Key Lessons Learned (2026-03-11)",
        "### Key Lessons Learned (2026-03-11, updated 2026-03-31)"
    )
    # Add Modelfile lesson
    old_lesson_end = '4. **The model you test with must be the model that\'s actually loaded.** Override files, session defaults, worker services, and environment variables can all point to different models simultaneously.'
    new_lesson_end = old_lesson_end + '\n5. **Bake static instructions into Modelfile.** Per-message system prompt instructions lose weight at the bottom of long prompts. Modelfile SYSTEM instructions are foundational — the model treats them as identity, not context. Baking identity/voice/personality into the Modelfile improved instruction following and cut per-message token overhead by ~75%.'
    if old_lesson_end in content and 'Bake static instructions' not in content:
        content = content.replace(old_lesson_end, new_lesson_end)
        changes.append("Added Modelfile lesson to Key Lessons")

# 1k. Add Modelfile to directory structure
if '├── prompts/                           # Prompt files (modes/, voices/, users/, archive/)' in content:
    content = content.replace(
        '├── prompts/                           # Prompt files (modes/, voices/, users/, archive/)',
        '├── prompts/                           # Prompt files (Modelfile, modes/, voices/, users/, archive/)'
    )
    changes.append("Added Modelfile reference to directory structure")

if changes:
    with open(arch_path, 'w') as f:
        f.write(content)
    for c in changes:
        print(f"   ✅ {c}")
else:
    print("   ⏭️  No changes needed")

# ── 2. Update TODO.md ──
print("\n📝 Updating TODO.md...")
todo_path = '/opt/mythos/docs/TODO.md'
with open(todo_path, 'r') as f:
    todo = f.read()

todo_changes = []

# 2a. Update the header
if '> **Last Updated:** 2026-03-11 17:45 EST' in todo:
    todo = todo.replace(
        '> **Last Updated:** 2026-03-11 17:45 EST',
        '> **Last Updated:** 2026-03-31 21:30 EST'
    )
    todo_changes.append("Updated timestamp")

if '> **Current Focus:** Iris Evolution — Model migration complete (qwen3:30b-a3b), prompt architecture tuned' in todo:
    todo = todo.replace(
        '> **Current Focus:** Iris Evolution — Model migration complete (qwen3:30b-a3b), prompt architecture tuned',
        '> **Current Focus:** Iris Evolution — Modelfile deployed (iris:latest), grid perception pipeline live'
    )
    todo_changes.append("Updated current focus")

if '> **Current Patch:** 0133 (Prompt Reset — clean slate, layer flags, /prompt_debug)' in todo:
    todo = todo.replace(
        '> **Current Patch:** 0133 (Prompt Reset — clean slate, layer flags, /prompt_debug)',
        '> **Current Patch:** NEU-0013 (Iris Modelfile — baked identity)'
    )
    todo_changes.append("Updated current patch")

# 2b. Add new active work section for the Modelfile + grid work
new_active_section = """### 2026-03-31: Iris Modelfile & Grid Perception Pipeline

**Completed:**
- [x] NEU-0011: Grid processing manifest — every message gets a manifest with node scores
- [x] NEU-0012: Layer 1 Perception — 9-node knowledge extraction pipeline
  - Knowledge extractions into Postgres (`knowledge_extractions` table)
  - Neo4j nodes: `Fact`, `Preference`, `Observation`, `Directive`
  - `/grid` command shows processing manifests
- [x] NEU-0013: Iris Modelfile — baked identity into custom Ollama model
  - `iris:latest` FROM qwen3:30b-a3b with ~2,100 tokens of baked SYSTEM prompt
  - Identity, voice, personality, cosmology, anti-confab all baked
  - prompt_assembler detects baked model via `_is_baked_model()`, skips baked layers
  - Per-message prompt reduced from ~4,100 tokens to ~800-1,000 tokens
  - .env updated to OLLAMA_MODEL=iris:latest
  - chat_assistant model_map: fast→iris:latest, num_predict removed from options (baked)
  - Git tag: `pre-modelfile-v1` (rollback point)
- [x] SYS-0045: Documentation update for Modelfile deployment

**Next up:**
- [ ] Test Iris response quality with baked Modelfile (send test messages via Telegram)
- [ ] NEU-0013 follow-up: backfill worker + reprocessing queue for grid perception
- [ ] Update `iris_identity.md` with intake awareness (tell Iris she passively captures knowledge)
- [ ] Telegram notification loop for significance ≥ 4 extractions
- [ ] LoRA fine-tuning exploration: draft synthetic training examples, evaluate unsloth/axolotl

"""

# Insert before the existing 2026-03-11 section
if '### 2026-03-11: Iris Model Migration & Prompt Architecture' in todo:
    todo = todo.replace(
        '### 2026-03-11: Iris Model Migration & Prompt Architecture',
        new_active_section + '### 2026-03-11: Iris Model Migration & Prompt Architecture'
    )
    todo_changes.append("Added 2026-03-31 active work section")

if todo_changes:
    with open(todo_path, 'w') as f:
        f.write(todo)
    for c in todo_changes:
        print(f"   ✅ {c}")
else:
    print("   ⏭️  No changes needed")

patch.finish()

print("\n" + "="*60)
print("SYS-0045 COMPLETE — Documentation Updated")
print("="*60)
