import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=18,
    description='Control plane unification — prompt_assembler + prompt_layers fixes (chat_assistant already patched)',
    patch_type='MINOR',
)
patch.begin()

# ═══════════════════════════════════════════════════════════════════════════════
# 1. prompt_assembler.py — Deprecate include_life_context/include_skills params,
#    fix voice_notes injection from base voice config
# ═══════════════════════════════════════════════════════════════════════════════

PA_PATH = '/opt/mythos/core/prompt_assembler.py'

with open(PA_PATH, 'r') as f:
    pa = f.read()

# --- 1a. Deprecate include_life_context and include_skills in signature ---
old_sig = """    include_life_context: bool = True,
    include_skills: bool = True,"""

new_sig = """    include_life_context: bool = True,   # DEPRECATED by SYS-0018: ignored, reads prompt_layers.yaml
    include_skills: bool = True,          # DEPRECATED by SYS-0018: ignored, reads prompt_layers.yaml"""

assert old_sig in pa, f"assemble_system_prompt signature params not found in prompt_assembler.py"
pa = pa.replace(old_sig, new_sig)

# --- 1b. Life context gate: remove `and include_life_context` ---
old_lc_gate = "    if is_layer_enabled('life_context') and include_life_context:"
new_lc_gate = "    if is_layer_enabled('life_context'):"

assert old_lc_gate in pa, "life_context gate with include_life_context not found"
pa = pa.replace(old_lc_gate, new_lc_gate)

# --- 1c. Skills context gate: remove `and include_skills` ---
old_sk_gate = "    if is_layer_enabled('skills_context') and include_skills:"
new_sk_gate = "    if is_layer_enabled('skills_context'):"

assert old_sk_gate in pa, "skills_context gate with include_skills not found"
pa = pa.replace(old_sk_gate, new_sk_gate)

# --- 1d. Fix voice_notes injection from base voice config ---
# _build_voice_section reads mode_config.get('voice_notes') but NOT base_voice.get('voice_notes').
# The 6 voice_notes lines in voice.yaml are never injected.

old_voice_notes = """    mode_notes = mode_config.get('voice_notes', [])
    if mode_notes:
        parts.append("\\n".join(mode_notes))"""

new_voice_notes = """    # Base voice notes (from voice.yaml top-level voice_notes list)
    base_notes = base_voice.get('voice_notes', [])
    if base_notes:
        parts.append("\\n".join(base_notes))

    # Mode-specific voice notes (from modes/*.yaml)
    mode_notes = mode_config.get('voice_notes', [])
    if mode_notes:
        parts.append("\\n".join(mode_notes))"""

assert old_voice_notes in pa, "voice_notes injection block not found in prompt_assembler.py"
pa = pa.replace(old_voice_notes, new_voice_notes)

with open(PA_PATH, 'w') as f:
    f.write(pa)

patch.logger.log("prompt_assembler.py: Deprecated include_life_context/include_skills, fixed voice_notes injection")

# ═══════════════════════════════════════════════════════════════════════════════
# 2. prompt_layers.yaml — Fix skill_results typo
# ═══════════════════════════════════════════════════════════════════════════════

PL_PATH = '/opt/mythos/prompts/prompt_layers.yaml'

with open(PL_PATH, 'r') as f:
    pl = f.read()

old_typo = "    enabled: tfalse"
new_typo = "    enabled: true"

assert old_typo in pl, "skill_results 'tfalse' typo not found in prompt_layers.yaml"
pl = pl.replace(old_typo, new_typo, 1)  # only replace the first occurrence

with open(PL_PATH, 'w') as f:
    f.write(pl)

patch.logger.log("prompt_layers.yaml: Fixed skill_results 'tfalse' -> true")

# ═══════════════════════════════════════════════════════════════════════════════
# 3. Verify compilation
# ═══════════════════════════════════════════════════════════════════════════════

import py_compile
py_compile.compile(PA_PATH, doraise=True)
patch.logger.log("prompt_assembler.py compiles OK")

CA_PATH = '/opt/mythos/assistants/chat_assistant.py'
py_compile.compile(CA_PATH, doraise=True)
patch.logger.log("chat_assistant.py compiles OK (pre-patched state verified)")

# ═══════════════════════════════════════════════════════════════════════════════
# 4. Restart services
# ═══════════════════════════════════════════════════════════════════════════════

patch.restart_service('mythos-bot.service')
patch.restart_service('mythos-api.service')

patch.finish()
