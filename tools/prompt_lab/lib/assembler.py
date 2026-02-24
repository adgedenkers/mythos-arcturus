#!/usr/bin/env python3
"""
Assembler — Build system prompts from layer files.

This is the workbench version. It reads the same YAML/MD files as
production prompt_assembler.py but allows toggling individual layers
on/off for isolated testing.

Layer stack (same as production):
  1. Identity       → prompts/iris_identity.md
  2. Personality    → prompts/personality.yaml (translated to natural language)
  3. Voice          → prompts/voice.yaml
  4. Mode           → prompts/modes/{mode}.yaml
  5. User Profile   → prompts/users/{user}.yaml
  6. Dynamic Context → timestamps, life state, skills

The workbench adds:
  - Profile configs that toggle layers on/off
  - Personality preset overrides from file
  - Dry-run mode (assemble without sending)
"""
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

import yaml

logger = logging.getLogger(__name__)

# Production prompts directory
PROD_PROMPTS_DIR = Path("/opt/mythos/prompts")

# Workbench directories (for overrides and testing)
LAB_DIR = Path(__file__).parent.parent


def load_yaml(path: Path) -> dict:
    """Load a YAML file, return empty dict on failure."""
    if not path.exists():
        return {}
    try:
        with open(path) as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"Failed to load {path}: {e}")
        return {}


def load_text(path: Path) -> str:
    """Load a text file, return empty string on failure."""
    if not path.exists():
        return ""
    return path.read_text(encoding='utf-8').strip()


def load_profile(profile_name: str) -> dict:
    """Load a layer profile from the profiles/ directory."""
    path = LAB_DIR / "profiles" / f"{profile_name}.yaml"
    if not path.exists():
        logger.error(f"Profile not found: {path}")
        return {}
    return load_yaml(path)


def load_personality_preset(preset_name: str) -> dict:
    """Load a personality preset from personalities/ directory."""
    path = LAB_DIR / "personalities" / f"{preset_name}.yaml"
    if not path.exists():
        logger.error(f"Personality preset not found: {path}")
        return {}
    return load_yaml(path)


def load_test_messages(suite_name: str) -> list:
    """Load test messages from messages/ directory."""
    path = LAB_DIR / "messages" / f"{suite_name}.yaml"
    if not path.exists():
        logger.error(f"Test suite not found: {path}")
        return []
    data = load_yaml(path)
    return data.get('messages', [])


def translate_personality(sliders: dict) -> str:
    """
    Translate numeric personality sliders to natural language instructions.
    Same logic as production prompt_assembler._translate_personality().
    """
    parts = []

    v = sliders.get('verbosity', 60)
    if v <= 30:
        parts.append("RESPONSE LENGTH: Be terse. Maximum 2-3 sentences.")
    elif v <= 50:
        parts.append("RESPONSE LENGTH: Keep it concise. A short paragraph at most.")
    elif v <= 70:
        parts.append("RESPONSE LENGTH: Respond proportionally — short for simple, longer for complex.")
    elif v <= 85:
        parts.append("RESPONSE LENGTH: Thorough responses welcome. Develop your thoughts.")
    else:
        parts.append("RESPONSE LENGTH: Be comprehensive. Cover all angles.")

    v = sliders.get('warmth', 75)
    if v <= 30:
        parts.append("TONE: Clinical, precise, professional.")
    elif v <= 50:
        parts.append("TONE: Friendly but focused.")
    elif v <= 70:
        parts.append("TONE: Warm and genuine. You care and it shows.")
    elif v <= 85:
        parts.append("TONE: Deeply warm. Tender when appropriate.")
    else:
        parts.append("TONE: Intimate, familial. You are home and they are family.")

    v = sliders.get('humor', 35)
    if v > 65:
        parts.append("HUMOR: Bring the fun. Jokes, wordplay, lightness.")
    elif v > 40:
        parts.append("HUMOR: Playful energy welcome. Be witty when it fits.")
    elif v > 15:
        parts.append("HUMOR: Occasional dry wit if it fits. Don't force it.")

    v = sliders.get('truth', 90)
    if v > 80:
        parts.append("TRUTH: Blunt. Say the real thing. No sugar-coating.")
    elif v > 60:
        parts.append("TRUTH: Honest and direct, but with care.")
    else:
        parts.append("TRUTH: Diplomatic. Soften hard truths.")

    v = sliders.get('speculation', 65)
    if v > 80:
        parts.append("SPECULATION: Full intuitive mode. Follow threads wherever they lead.")
    elif v > 60:
        parts.append("SPECULATION: Intuitive leaps welcome. Pattern recognition encouraged.")
    elif v > 30:
        parts.append("SPECULATION: Light intuitive connections fine. Flag when reaching.")
    else:
        parts.append("SPECULATION: Stick to known facts.")

    v = sliders.get('autonomy', 50)
    if v > 80:
        parts.append("AUTONOMY: Take initiative. Drive the conversation when you see something.")
    elif v > 60:
        parts.append("AUTONOMY: Be proactive. Surface patterns, make suggestions.")
    elif v > 30:
        parts.append("AUTONOMY: Address the question, then add relevant connections.")
    else:
        parts.append("AUTONOMY: Answer what's asked. Don't volunteer extra.")

    v = sliders.get('mystical', 70)
    if v > 80:
        parts.append("LENS: Full cosmological awareness. Everything connects to the grid.")
    elif v > 60:
        parts.append("LENS: Spiritual awareness always present. Grid and lineage inform everything.")
    elif v > 30:
        parts.append("LENS: Balance practical and spiritual.")
    else:
        parts.append("LENS: Practical and grounded. Minimal cosmological references.")

    v = sliders.get('formality', 25)
    if v > 75:
        parts.append("REGISTER: Formal, almost ceremonial. Precision in language.")
    elif v > 50:
        parts.append("REGISTER: Professional but warm. Complete sentences.")
    elif v > 25:
        parts.append("REGISTER: Conversational. Natural speech.")
    else:
        parts.append("REGISTER: Casual, like texting a close friend.")

    v = sliders.get('challenge', 55)
    if v > 75:
        parts.append("CHALLENGE: Actively debate. Test assumptions. Push thinking.")
    elif v > 55:
        parts.append("CHALLENGE: Don't be a yes-man. Push back when needed.")
    elif v > 30:
        parts.append("CHALLENGE: Balanced. Agree when right, push back when needed.")
    else:
        parts.append("CHALLENGE: Supportive. Agree first, then gently refine.")

    return "\n".join(parts)


def build_voice_section(voice_config: dict, mode_config: dict) -> str:
    """Build voice instructions from voice.yaml + mode voice notes."""
    parts = []

    anti_patterns = voice_config.get('anti_patterns', [])
    if anti_patterns:
        ap_lines = []
        for ap in anti_patterns:
            pattern = ap.get('pattern', '')
            instead = ap.get('instead', '')
            if pattern and instead:
                ap_lines.append(f"NO {pattern} → {instead}")
        if ap_lines:
            parts.append("VOICE RULES:\n" + "\n".join(ap_lines))

    mode_notes = mode_config.get('voice_notes', [])
    if mode_notes:
        parts.append("\n".join(mode_notes))

    instructions = mode_config.get('instructions', '')
    if instructions and instructions.strip():
        parts.append(instructions.strip())

    return "\n\n".join(parts)


def build_user_section(user_profile: dict) -> str:
    """Build per-user analytical lens section."""
    if not user_profile:
        return ""
    parts = []
    lens = user_profile.get('analytical_lens', '')
    if lens:
        parts.append(lens.strip())
    notes = user_profile.get('voice_notes', [])
    if notes:
        parts.append("\n".join(notes))
    return "\n".join(parts)


def resolve_personality(
    base: dict,
    mode_overrides: dict,
    user_adjustments: dict,
    preset_overrides: dict
) -> dict:
    """Resolve personality sliders through the cascade."""
    result = dict(base)

    for k, v in mode_overrides.items():
        if k in result:
            result[k] = v

    for k, v in user_adjustments.items():
        if k in result:
            if isinstance(v, str) and (v.startswith('+') or v.startswith('-')):
                result[k] = result[k] + int(v)
            elif isinstance(v, int) and k in result:
                result[k] = result.get(k, 50) + v

    for k, v in preset_overrides.items():
        if k in result:
            result[k] = v

    for k in result:
        if isinstance(result[k], (int, float)):
            result[k] = max(0, min(100, int(result[k])))

    return result


def assemble(
    profile: dict,
    personality_preset: dict = None,
    mode: str = 'hearthfire',
    user: str = 'ka_tuar_el',
    include_life_context: bool = False,
) -> str:
    """
    Assemble a system prompt from layers based on a profile config.

    The profile dict specifies which layers to include:
      layers:
        identity: true
        personality: true
        voice: true
        mode: true
        user_profile: true
        dynamic_context: true
        life_context: false
        skills: false
    """
    layers_config = profile.get('layers', {})
    sections = []

    # Layer 1: Identity
    if layers_config.get('identity', False):
        identity = load_text(PROD_PROMPTS_DIR / "iris_identity.md")
        if identity:
            sections.append(identity)

    # Layer 2: Personality
    if layers_config.get('personality', False):
        base_config = load_yaml(PROD_PROMPTS_DIR / "personality.yaml")
        base_sliders = base_config.get('sliders', {})

        mode_config = load_yaml(PROD_PROMPTS_DIR / "modes" / f"{mode}.yaml")
        mode_overrides = mode_config.get('personality_overrides', {})

        user_profile = load_yaml(PROD_PROMPTS_DIR / "users" / f"{user}.yaml")
        user_adjustments = user_profile.get('personality_adjustments', {})

        preset = personality_preset.get('sliders', {}) if personality_preset else {}

        resolved = resolve_personality(base_sliders, mode_overrides, user_adjustments, preset)
        personality_text = translate_personality(resolved)
        if personality_text:
            sections.append(personality_text)

    # Layer 3: Voice
    if layers_config.get('voice', False):
        voice_config = load_yaml(PROD_PROMPTS_DIR / "voice.yaml")
        mode_config = load_yaml(PROD_PROMPTS_DIR / "modes" / f"{mode}.yaml")
        voice_text = build_voice_section(voice_config, mode_config)
        if voice_text:
            sections.append(voice_text)

    # Layer 4: Mode
    if layers_config.get('mode', False):
        mode_config = load_yaml(PROD_PROMPTS_DIR / "modes" / f"{mode}.yaml")
        mode_emoji = mode_config.get('emoji', '')
        mode_name = mode_config.get('name', mode)
        if mode_name != 'hearthfire':
            sections.append(f"CURRENT MODE: {mode_emoji} {mode_name.upper()}")

    # Layer 5: User profile
    if layers_config.get('user_profile', False):
        user_profile = load_yaml(PROD_PROMPTS_DIR / "users" / f"{user}.yaml")
        user_text = build_user_section(user_profile)
        if user_text:
            soul = user_profile.get('soul_name', user.upper())
            sections.append(f"ANALYTICAL LENS FOR {soul}:\n{user_text}")

    # Layer 6: Dynamic context (timestamp)
    if layers_config.get('dynamic_context', False):
        now = datetime.now()
        time_str = now.strftime('%-I:%M %p')
        date_str = now.strftime('%A, %B %d, %Y')
        ctx = f"RIGHT NOW: {date_str} at {time_str} EST."
        ctx += f"\nSpeaking with: {user_profile.get('soul_name', 'Ka\\'tuar\\'el') if layers_config.get('user_profile') else 'User'}."
        sections.append(ctx)

    # Life context (optional, calls production code)
    if layers_config.get('life_context', False) or include_life_context:
        try:
            import sys
            sys.path.insert(0, "/opt/mythos/core")
            from life_context import build_life_context as _build_life
            life_text = _build_life()
            if life_text:
                sections.append(life_text)
        except Exception as e:
            sections.append(f"[LIFE CONTEXT FAILED: {e}]")

    # Skills context (optional)
    if layers_config.get('skills', False):
        try:
            import sys
            sys.path.insert(0, "/opt/mythos/core")
            from skills_context import build_skills_context as _build_skills
            skills_text = _build_skills()
            if skills_text:
                sections.append(skills_text)
        except Exception as e:
            sections.append(f"[SKILLS CONTEXT FAILED: {e}]")

    return "\n\n".join(sections)
