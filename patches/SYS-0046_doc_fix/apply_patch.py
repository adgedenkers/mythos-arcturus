#!/usr/bin/env python3
"""
SYS-0046: Doc Fix — Sections SYS-0045 Missed
==============================================
SYS-0045 updated some sections but missed others due to whitespace mismatches.
This patch fixes: Active Models table, Model Aliases, Changing the Default Model,
Prompt Assembly Pipeline, Anti-Confab section, and Active Prompt Files table.

All old strings are copied EXACTLY from the current file on disk (verified via diagnostic).
"""

import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=46,
    description='doc_fix_modelfile',
    patch_type='PATCH',
)
patch.begin()

arch_path = '/opt/mythos/docs/ARCHITECTURE.md'
with open(arch_path, 'r') as f:
    content = f.read()

changes = []

# ── 1. Active Models table ──
old = """### Active Models (as of 2026-03-11)
| Model | Use | Speed | Notes |
|-------|-----|-------|-------|
| `qwen3:30b-a3b` | Iris default (conversation) | ~8-12s | MoE, 3B active params. Best resonance/speed balance |
| `qwen3:32b` | Deep mode (spiritual, synthesis) | ~30-50s | Higher quality. Switch via `/setmodel deep` |
| `qwen2.5:7b` | Message extractor pre-pass | ~1-2s | Currently disabled in prompt_layers.yaml |"""

new = """### Active Models (as of 2026-03-31)
| Model | Use | Speed | Notes |
|-------|-----|-------|-------|
| `iris:latest` | Iris default (conversation) | ~8-12s | Custom Modelfile FROM qwen3:30b-a3b. Identity/voice/personality/cosmology baked (~2,100 tokens). |
| `qwen3:32b` | Deep mode (spiritual, synthesis) | ~30-50s | Raw model, no Modelfile. Switch via `/setmodel deep` |
| `qwen2.5:7b` | Message extractor pre-pass | ~1-2s | Currently disabled in prompt_layers.yaml |"""

if old in content:
    content = content.replace(old, new)
    changes.append("Active Models table → iris:latest")
else:
    print("   ⚠️  Active Models table not found — already updated?")

# ── 2. Model Aliases ──
old = """`/setmodel fast` or `/setmodel a3b` → `qwen3:30b-a3b`
`/setmodel deep` or `/setmodel 32b` → `qwen3:32b`
`/setmodel reset` → Back to `.env` default"""

new = """`/setmodel fast` or `/setmodel a3b` → `iris:latest`
`/setmodel deep` or `/setmodel 32b` → `qwen3:32b`
`/setmodel reset` → Back to `.env` default (`iris:latest`)"""

if old in content:
    content = content.replace(old, new)
    changes.append("Model Aliases → iris:latest")
else:
    print("   ⚠️  Model Aliases not found — already updated?")

# ── 3. Changing the Default Model ──
old = """### Changing the Default Model
```bash
sed -i 's/^OLLAMA_MODEL=.*/OLLAMA_MODEL=new_model:tag/' /opt/mythos/.env
sudo systemctl restart mythos-api.service
sudo systemctl restart mythos-worker-grid.service
echo '{}' > /opt/mythos/.model_overrides.json
curl -s http://localhost:11434/api/generate -d '{"model":"old_model","keep_alive":0}'
iris-test --set quick
```"""

new = """### Changing the Default Model

The default model is `iris:latest` (custom Modelfile with baked identity). To update:

```bash
# After editing the Modelfile:
ollama create iris -f /opt/mythos/prompts/Modelfile
sudo systemctl restart mythos-api.service

# To switch to a different base model entirely:
sed -i 's/^OLLAMA_MODEL=.*/OLLAMA_MODEL=new_model:tag/' /opt/mythos/.env
sudo systemctl restart mythos-api.service
sudo systemctl restart mythos-worker-grid.service
echo '{}' > /opt/mythos/.model_overrides.json
iris-test --set quick
```

**Note:** Non-iris models get all layers in the per-message prompt automatically (the assembler detects baked vs. unbaked)."""

if old in content:
    content = content.replace(old, new)
    changes.append("Changing the Default Model → Modelfile instructions")
else:
    print("   ⚠️  Changing the Default Model not found — already updated?")

# ── 4. Prompt Assembly Pipeline ──
old = """### Prompt Assembly Pipeline (as of 2026-03-11)
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

new = """### Prompt Assembly Pipeline (as of 2026-03-31)

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

When a non-baked model is used (e.g., `/setmodel deep` → `qwen3:32b`), the assembler includes all layers in the per-message prompt as before.

### Anti-Confabulation Architecture (Critical)
The anti-confab rule is baked into the `iris:latest` Modelfile as a foundational instruction. For non-baked models, it's injected at position #1 in the assembled prompt.

The rule has an explicit carve-out listing all cosmological/spiritual concepts
by name (all 9 grid nodes, Seraphe's transmissions, Atlantean tech, the 144,
Thronescribe function, etc). This prevents the model from treating framework
knowledge as "data it doesn't have."

**Rule:** Fabricate nothing practical. Speak freely on cosmological framework."""

if old in content:
    content = content.replace(old, new)
    changes.append("Prompt Assembly Pipeline → two-tier Modelfile architecture")
else:
    print("   ⚠️  Prompt Assembly Pipeline not found — already updated?")

# ── 5. Active Prompt Files table ──
old = """### Active Prompt Files (in /opt/mythos/prompts/)
| File | Purpose |
|------|---------|
| `iris_identity.md` | Core identity — who Iris is, who she knows (Ka'tuar'el, Seraphe, Fitz), behavioral rules |
| `personality.yaml` | 9 personality sliders (verbosity 85, warmth 75, truth 90, etc.) |
| `voice.yaml` | Voice anti-patterns (no "You good?", no "No fluff.", no corporate openers) |
| `prompt_layers.yaml` | Master layer toggle |"""

new = """### Active Prompt Files (in /opt/mythos/prompts/)
| File | Purpose |
|------|---------|
| `Modelfile` | **Ollama Modelfile** — baked identity, voice, personality, cosmology, anti-confab (~2,100 tokens). Rebuild: `ollama create iris -f Modelfile` |
| `iris_identity.md` | Core identity source — used by non-baked models and as canonical reference |
| `personality.yaml` | 9 personality sliders (verbosity 65, warmth 75, truth 90, etc.) — translations baked into Modelfile |
| `voice.yaml` | Voice anti-patterns — rules baked into Modelfile |
| `prompt_layers.yaml` | Master layer toggle — controls dynamic layers for all models |"""

if old in content:
    content = content.replace(old, new)
    changes.append("Active Prompt Files → added Modelfile, fixed verbosity 85→65")
else:
    print("   ⚠️  Active Prompt Files table not found — already updated?")

# ── Write ──
if changes:
    with open(arch_path, 'w') as f:
        f.write(content)
    print(f"\n📝 ARCHITECTURE.md: {len(changes)} sections updated")
    for c in changes:
        print(f"   ✅ {c}")
else:
    print("\n   ⏭️  All sections already current")

patch.finish()

print("\n" + "="*60)
print("SYS-0046 COMPLETE — Doc sections fixed")
print("="*60)
