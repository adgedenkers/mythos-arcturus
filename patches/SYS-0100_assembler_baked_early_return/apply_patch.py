"""
SYS-0100: Prompt assembler early return for baked models

What this patch changes:
- Modifies /opt/mythos/core/prompt_assembler.py
- After building baseline, baked models get an immediate return
- No identity, personality, voice, skills_context, or cosmological framework
- Skill results and research context still flow through chat_assistant.py
- Eliminates context contamination where 800+ tokens of skill registry
  and spiritual identity overwrote the baked Modelfile SYSTEM prompt

Services restarted: mythos-bot.service
Tables touched: none
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SYS',
    number=100,
    description='prompt assembler early return for baked models',
    patch_type='MINOR',
)
patch.begin()

# The edit: insert an early return right after baseline is built,
# before any other layers are assembled.
#
# Anchor: the line "sections.append(baseline)" followed by the
# anti-confabulation section. We insert between them.

patch.str_replace(
    '/opt/mythos/core/prompt_assembler.py',
    old=(
        '    sections.append(baseline)\n'
        '\n'
        '    # ── ANTI-CONFABULATION (highest priority — before everything) ──'
    ),
    new=(
        '    sections.append(baseline)\n'
        '\n'
        '    # ── BAKED MODEL EARLY RETURN ──────────────────────────────────────\n'
        '    # SYS-0100: Baked models (iris:*) have identity, personality, voice,\n'
        '    # and capability awareness in their Modelfile SYSTEM prompt.\n'
        '    # The assembler only provides the temporal/relational baseline.\n'
        '    # Dynamic data (skill results, research context) flows separately\n'
        '    # through chat_assistant.py into the [Context] preamble.\n'
        '    if _is_baked_model(model_name):\n'
        '        logger.info(\n'
        '            f"Baked model early return: {len(baseline)} chars baseline only, "\n'
        '            f"model={model_name}, user={user_info.get(\'soul_name\', \'?\')}"\n'
        '        )\n'
        '        return baseline\n'
        '\n'
        '    # ── ANTI-CONFABULATION (highest priority — before everything) ──'
    ),
    label='assembler baked model early return',
)

patch.py_compile_check(
    '/opt/mythos/core/prompt_assembler.py',
    label='prompt_assembler.py syntax',
)

patch.restart_service('mythos-bot.service')

patch.finish()
