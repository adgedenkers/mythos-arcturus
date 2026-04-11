import sys
import re
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=48,
    description='Fix remaining alias refs (chat_mode, help_handler) + ARCHITECTURE.md update',
    patch_type='PATCH',
)
patch.begin()

# ── 1. Fix chat_mode.py ──────────────────────────────────────────────────
target = '/opt/mythos/telegram_bot/handlers/chat_mode.py'
with open(target, 'r') as f:
    content = f.read()

# Replace the whole block including the blank line using regex to be whitespace-tolerant
old_pattern = (
    r"OLLAMA_MODEL = os\.getenv\('OLLAMA_MODEL', 'qwen3:30b-a3b'\)\s*\n"
    r"\s*\n"
    r"# Model mapping for /model command\s*\n"
    r"MODEL_MAP = \{\s*\n"
    r"\s*'auto': 'qwen3:30b-a3b',\s*\n"
    r"\s*'fast': 'qwen3:30b-a3b',\s*\n"
    r"\s*'deep': 'qwen3:32b',\s*\n"
    r"\s*'thinking': 'qwen3:32b',\s*\n"
    r"\}"
)

new_block = (
    "from core.model_aliases import MODEL_ALIASES as MODEL_MAP, DEFAULT_MODEL\n"
    "OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', DEFAULT_MODEL)"
)

result = re.sub(old_pattern, new_block, content)
if result != content:
    with open(target, 'w') as f:
        f.write(result)
    print(f"✅ Fixed {target} — MODEL_MAP now imports from core.model_aliases")
else:
    print(f"⚠ {target} — pattern not found (may already be fixed)")

# ── 2. Fix help_handler.py first block ───────────────────────────────────
target = '/opt/mythos/telegram_bot/handlers/help_handler.py'
with open(target, 'r') as f:
    lines = f.readlines()

# Find and replace the model selection block by looking for the marker lines
in_model_block = False
block_start = None
block_end = None
for i, line in enumerate(lines):
    if '**MODEL SELECTION**' in line:
        in_model_block = True
        # The separator line is one line before
        block_start = i - 1
    if in_model_block and '**Advanced:**' in line:
        # Find the end: after `/models` line
        for j in range(i, min(i + 5, len(lines))):
            if '/models' in lines[j] and 'List all' in lines[j]:
                block_end = j + 1
                break
        break

if block_start is not None and block_end is not None:
    # Build replacement lines
    # Need to figure out the unicode separator character
    sep_line = lines[block_start]  # reuse the existing separator line as-is
    new_lines = [
        sep_line,
        '**MODEL SELECTION**\n',
        sep_line,
        '`/model deep` \u2014 iris-deep:latest (qwen3:32b, deeper reasoning)\n',
        '`/model fast` \u2014 iris:latest (qwen3:30b-a3b, quick conversational)\n',
        '`/model auto` \u2014 default model\n',
        '\n',
        '**Advanced:**\n',
        '`/setmodel <exact_name>` \u2014 Use any installed model\n',
        '`/models` \u2014 List all installed Ollama models\n',
    ]
    lines[block_start:block_end] = new_lines
    with open(target, 'w') as f:
        f.writelines(lines)
    print(f"✅ Fixed {target} — first MODEL SELECTION block updated")
else:
    print(f"⚠ {target} — MODEL SELECTION block boundaries not found")

# ── 3. Update ARCHITECTURE.md ────────────────────────────────────────────
target = '/opt/mythos/docs/ARCHITECTURE.md'
with open(target, 'r') as f:
    content = f.read()

# Fix the non-baked model line
old_nonbaked = 'When a non-baked model is used (e.g., `/setmodel deep` \u2192 `qwen3:32b`), the assembler includes all layers in the per-message prompt as before.'
new_nonbaked = 'When a non-baked model is used (e.g., `/setmodel qwen3:32b`), the assembler includes all layers in the per-message prompt as before. The default baked models are `iris-deep:latest` (FROM qwen3:32b) and `iris:latest` (FROM qwen3:30b-a3b).'
content = content.replace(old_nonbaked, new_nonbaked)

# Fix anti-confab section
old_anticonfab = """### Anti-Confabulation Architecture (Critical)
The anti-confab rule is baked into the `iris:latest` Modelfile as a foundational instruction. For non-baked models, it's injected at position #1 in the assembled prompt.

The rule has an explicit carve-out listing all cosmological/spiritual concepts
by name (all 9 grid nodes, Seraphe's transmissions, Atlantean tech, the 144,
Thronescribe function, etc). This prevents the model from treating framework
knowledge as "data it doesn't have."

**Rule:** Fabricate nothing practical. Speak freely on cosmological framework."""

new_anticonfab = """### Anti-Confabulation Architecture (Critical)
Anti-confab rules are baked into both `iris:latest` and `iris-deep:latest` Modelfiles at position #1 (highest priority). Two categories:

1. **Data fabrication:** Never invent facts, states, events, amounts, or what people are doing. If no data, say "it's been quiet."
2. **Capability fabrication:** Never offer to do things Iris can't do (no external websites, emails, phone calls, legal lookups, price checks). Only: Telegram conversation, Mythos skills, and Postgres/Neo4j data.

The rules include an explicit carve-out for cosmological/spiritual concepts
(grid nodes, Seraphe's transmissions, Atlantean tech, the 144, Thronescribe
function, etc). The model speaks freely on framework knowledge.

**Rule:** Fabricate nothing \u2014 not data, not capabilities. Speak freely on cosmological framework."""

content = content.replace(old_anticonfab, new_anticonfab)

# Fix the Active Prompt Files table
old_prompt_table = '| `Modelfile` | **Ollama Modelfile** \u2014 baked identity, voice, personality, cosmology, anti-confab (~2,100 tokens). Rebuild: `ollama create iris -f Modelfile` |'
new_prompt_table = """| `Modelfile` | **Ollama Modelfile (fast)** \u2014 v4 baked prompt (~1,050 tokens), FROM qwen3:30b-a3b. Rebuild: `ollama create iris -f Modelfile` |
| `Modelfile.deep` | **Ollama Modelfile (deep)** \u2014 v4 baked prompt (~1,050 tokens), FROM qwen3:32b. Rebuild: `ollama create iris-deep -f Modelfile.deep` |
| `model_aliases.py` | **Not here** \u2014 lives at `core/model_aliases.py`. Single source of truth for all model short names (fast, deep, auto, etc.) |"""
content = content.replace(old_prompt_table, new_prompt_table)

# Add new lesson learned
old_lessons_end = "5. **Bake static instructions into Modelfile.** Per-message system prompt instructions lose weight at the bottom of long prompts. Modelfile SYSTEM instructions are foundational \u2014 the model treats them as identity, not context. Baking identity/voice/personality into the Modelfile improved instruction following and cut per-message token overhead by ~75%."
new_lessons_end = """5. **Bake static instructions into Modelfile.** Per-message system prompt instructions lose weight at the bottom of long prompts. Modelfile SYSTEM instructions are foundational \u2014 the model treats them as identity, not context. Baking identity/voice/personality into the Modelfile improved instruction following and cut per-message token overhead by ~75%.
6. **Ollama chat API system message REPLACES Modelfile SYSTEM.** They do not combine. For baked models (`iris:*`), `_build_messages()` sends no system message. Dynamic context goes as a `[Context]...[/Context]` preamble in the user message instead.
7. **~950 tokens is the sweet spot for qwen3:30b-a3b.** Calibration proved layers 1\u20138 (~940 tokens) produce the best results. The full 2,100-token v1 prompt caused blank responses and instruction loss.
8. **Skill output contaminates voice.** If a skill returns grid node names and emojis, the model parrots them. Skills must return clean, voice-compatible output.
9. **Centralize aliases.** Model aliases consolidated in `core/model_aliases.py` \u2014 all handlers import from there. One file to update when models change."""

content = content.replace(old_lessons_end, new_lessons_end)

with open(target, 'w') as f:
    f.write(content)
print(f"✅ Updated {target} — Ollama/model sections reflect current state")

# Restart bot to pick up chat_mode.py changes
patch.restart_service('mythos-bot.service')

patch.finish()
print("\n✅ SYS-0048 complete")
print("   Fixed: chat_mode.py MODEL_MAP import")
print("   Fixed: help_handler.py first MODEL SELECTION block")
print("   Updated: ARCHITECTURE.md (anti-confab, Modelfile table, lessons learned)")
