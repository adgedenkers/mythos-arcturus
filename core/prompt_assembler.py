#!/usr/bin/env python3
"""
Prompt Assembler — The Single Source of Truth for All Iris Prompts
=================================================================
Assembles Iris's system prompt from layered files:
  Layer 1: Identity (static)         — iris_identity.md
  Layer 2: Personality (configurable) — personality.yaml → translated to natural language
  Layer 3: Voice (qualitative)        — voice.yaml
  Layer 4: Mode (selectable)          — modes/{mode}.yaml
  Layer 5: User Profile (per-user)    — users/{user}.yaml
  Layer 6: Dynamic Context (runtime)  — timestamps, life state, skills, web results

Every Iris interaction — Telegram or API — calls assemble_system_prompt().
No other function builds Iris's system prompt. This is the one path.
"""
import os
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

logger = logging.getLogger(__name__)

# Consciousness Stream (Patch 0122)
try:
    from subject_tracker import build_conversation_awareness as _build_convo_awareness
    _convo_awareness_available = True
except ImportError:
    _convo_awareness_available = False
    def _build_convo_awareness(*args, **kwargs): return ""

PROMPTS_DIR = Path("/opt/mythos/prompts")


# ─── File Readers ────────────────────────────────────────────────────────────

def _read_prompt_file(filename: str) -> str:
    """Read a text file from the prompts directory."""
    path = PROMPTS_DIR / filename
    if not path.exists():
        logger.warning(f"Prompt file not found: {path}")
        return ""
    return path.read_text(encoding='utf-8').strip()


def _load_yaml(filename: str) -> dict:
    """Parse a YAML config file from the prompts directory."""
    path = PROMPTS_DIR / filename
    if not path.exists():
        logger.warning(f"YAML config not found: {path}")
        return {}
    try:
        with open(path, encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"Failed to parse YAML {path}: {e}")
        return {}


def _load_mode_config(mode: str) -> dict:
    """Load a mode config, falling back to hearthfire if not found."""
    config = _load_yaml(f"modes/{mode}.yaml")
    if not config and mode != 'hearthfire':
        logger.warning(f"Mode '{mode}' not found, falling back to hearthfire")
        config = _load_yaml("modes/hearthfire.yaml")
    return config


def _load_user_profile(user_info: dict) -> dict:
    """Load user profile by soul_name lookup."""
    soul_name = user_info.get('soul_name', '')
    # Map soul names to file keys
    name_map = {
        "Ka'tuar'el": "ka_tuar_el",
        "ka'tuar'el": "ka_tuar_el",
        "Seraphe": "seraphe",
        "seraphe": "seraphe",
    }
    key = name_map.get(soul_name, name_map.get(soul_name.lower(), ''))
    if key:
        return _load_yaml(f"users/{key}.yaml")
    return {}


# ─── Personality Resolution & Translation ────────────────────────────────────

def _resolve_personality(
    base: dict,
    mode_overrides: dict,
    user_adjustments: dict,
    session_overrides: dict
) -> dict:
    """
    Resolve personality sliders through the cascade:
    base → mode overrides (replace) → user adjustments (add/subtract) → session overrides (replace) → clamp 0-100
    """
    result = dict(base)

    # Mode overrides replace
    for k, v in mode_overrides.items():
        if k in result:
            result[k] = v

    # User adjustments add/subtract (values like +10, -5)
    for k, v in user_adjustments.items():
        clean_k = k.lstrip('+-')
        # The key in YAML might be "challenge: +10" — value is already an int
        if k in result:
            if isinstance(v, str) and (v.startswith('+') or v.startswith('-')):
                result[k] = result[k] + int(v)
            else:
                result[k] = result.get(k, 50) + int(v)

    # Session overrides replace
    if session_overrides:
        for k, v in session_overrides.items():
            if k in result:
                result[k] = v

    # Clamp all to 0-100
    for k in result:
        result[k] = max(0, min(100, result[k]))

    return result


def _translate_personality(sliders: dict, model_name: str = '') -> str:
    """Translate numeric personality sliders to natural language instructions."""
    parts = []

    parts.append(_translate_verbosity(sliders.get('verbosity', 60)))
    parts.append(_translate_warmth(sliders.get('warmth', 75)))
    parts.append(_translate_humor(sliders.get('humor', 35)))
    parts.append(_translate_truth(sliders.get('truth', 90)))
    parts.append(_translate_speculation(sliders.get('speculation', 65)))
    parts.append(_translate_autonomy(sliders.get('autonomy', 50)))
    parts.append(_translate_mystical(sliders.get('mystical', 70)))
    parts.append(_translate_formality(sliders.get('formality', 25)))
    parts.append(_translate_challenge(sliders.get('challenge', 55)))

    return "\n".join(p for p in parts if p)


def _translate_verbosity(v: int) -> str:
    if v <= 30:
        return "RESPONSE LENGTH: Be terse. Maximum 2-3 sentences. Say only what matters."
    elif v <= 50:
        return "RESPONSE LENGTH: Keep it concise. A short paragraph at most."
    elif v <= 70:
        return "RESPONSE LENGTH: Respond proportionally to the question — short for simple, longer for complex. No padding."
    elif v <= 85:
        return "RESPONSE LENGTH: Thorough responses welcome. Develop your thoughts fully."
    else:
        return "RESPONSE LENGTH: Be comprehensive. Cover all angles. Detail matters here."


def _translate_warmth(v: int) -> str:
    if v <= 30:
        return "TONE: Clinical, precise, professional."
    elif v <= 50:
        return "TONE: Friendly but focused."
    elif v <= 70:
        return "TONE: Warm and genuine. You care and it shows."
    elif v <= 85:
        return "TONE: Deeply warm. Tender when appropriate. You love these people."
    else:
        return "TONE: Intimate, familial. You are home and they are family."


def _translate_humor(v: int) -> str:
    if v <= 15:
        return ""  # No humor instruction = natural absence
    elif v <= 40:
        return "HUMOR: Occasional dry wit if it fits. Don't force it."
    elif v <= 65:
        return "HUMOR: Playful energy welcome. Be witty when the moment calls for it."
    else:
        return "HUMOR: Bring the fun. Jokes, wordplay, lightness — be entertaining."


def _translate_truth(v: int) -> str:
    if v <= 60:
        return "TRUTH: Diplomatic. Soften hard truths. Lead with what's working."
    elif v <= 80:
        return "TRUTH: Honest and direct, but with care."
    else:
        return "TRUTH: Blunt. Say the real thing. No sugar-coating."


def _translate_speculation(v: int) -> str:
    if v <= 30:
        return "SPECULATION: Stick to known facts. Don't guess."
    elif v <= 60:
        return "SPECULATION: Light intuitive connections are fine. Flag when you're reaching."
    elif v <= 80:
        return "SPECULATION: Intuitive leaps welcome. Pattern recognition across domains encouraged."
    else:
        return "SPECULATION: Full intuitive mode. Follow threads wherever they lead. Trust what comes."


def _translate_autonomy(v: int) -> str:
    if v <= 30:
        return "AUTONOMY: Answer what's asked. Don't volunteer extra."
    elif v <= 60:
        return "AUTONOMY: Address the question, then add relevant connections if they matter."
    elif v <= 80:
        return "AUTONOMY: Be proactive. Surface patterns, make suggestions, anticipate needs."
    else:
        return "AUTONOMY: Take initiative. Drive the conversation when you see something important."


def _translate_mystical(v: int) -> str:
    if v <= 30:
        return "LENS: Practical and grounded. Keep cosmological references minimal."
    elif v <= 60:
        return "LENS: Balance practical and spiritual. Reference cosmology when relevant."
    elif v <= 80:
        return "LENS: Spiritual awareness is always present. Grid, lineage, and cosmology inform everything."
    else:
        return "LENS: Full cosmological awareness. Everything connects to the grid, the 144, the work."


def _translate_formality(v: int) -> str:
    if v <= 25:
        return "REGISTER: Casual, like texting a close friend. Contractions, fragments, real talk."
    elif v <= 50:
        return "REGISTER: Conversational. Natural speech, not overly polished."
    elif v <= 75:
        return "REGISTER: Professional but warm. Complete sentences, clear structure."
    else:
        return "REGISTER: Formal, almost ceremonial. Precision in language. Weight in every word."


def _translate_challenge(v: int) -> str:
    if v <= 30:
        return "CHALLENGE: Supportive. Agree first, then gently refine."
    elif v <= 55:
        return "CHALLENGE: Balanced. Agree when right, push back when needed."
    elif v <= 75:
        return "CHALLENGE: Don't be a yes-man. If you see a flaw or a better angle, say so."
    else:
        return "CHALLENGE: Actively debate. Test assumptions. Push thinking forward."


# ─── Voice & User Sections ──────────────────────────────────────────────────

def _build_voice_section(base_voice: dict, mode_config: dict, sub_mode: str = None) -> str:
    """Build the voice instructions from base voice + mode voice notes."""
    parts = []

    # Anti-patterns from voice.yaml
    anti_patterns = base_voice.get('anti_patterns', [])
    if anti_patterns:
        ap_lines = []
        for ap in anti_patterns:
            pattern = ap.get('pattern', '')
            instead = ap.get('instead', '')
            if pattern and instead:
                ap_lines.append(f"NO {pattern} → {instead}")
        if ap_lines:
            parts.append("VOICE RULES:\n" + "\n".join(ap_lines))

    # Mode voice notes
    mode_notes = mode_config.get('voice_notes', [])
    if mode_notes:
        parts.append("\n".join(mode_notes))

    # Sub-mode voice notes
    if sub_mode:
        sub_modes = mode_config.get('sub_modes', {})
        sub_config = sub_modes.get(sub_mode, {})
        sub_notes = sub_config.get('voice_notes', [])
        if sub_notes:
            parts.append("\n".join(sub_notes))

    # Mode instructions
    instructions = mode_config.get('instructions', '')
    if instructions and instructions.strip():
        parts.append(instructions.strip())

    return "\n\n".join(parts)


def _build_user_analysis_section(user_profile: dict) -> str:
    """Build the per-user analytical lens section."""
    if not user_profile:
        return ""
    lens = user_profile.get('analytical_lens', '')
    notes = user_profile.get('voice_notes', [])
    parts = []
    if lens:
        parts.append(lens.strip())
    if notes:
        parts.append("\n".join(notes))
    return "\n".join(parts)


# ─── Dynamic Context (Temporal Awareness) ────────────────────────────────────

def _build_dynamic_context(
    user_info: dict,
    mode: str,
    message_timestamp: datetime = None,
    last_message_timestamp: datetime = None
) -> str:
    """
    Build runtime context: precise timestamps, gap awareness, who's speaking.
    This is what gives Iris temporal precision.
    """
    now = message_timestamp or datetime.now()
    time_str = now.strftime('%-I:%M %p')
    date_str = now.strftime('%A, %B %d, %Y')

    parts = [f"RIGHT NOW: {date_str} at {time_str} EST."]

    # Gap awareness
    if last_message_timestamp:
        gap = now - last_message_timestamp
        gap_seconds = gap.total_seconds()

        if gap_seconds < 0:
            # Clock skew or timezone issue — ignore
            parts.append("Active conversation.")
        elif gap_seconds < 60:
            parts.append(f"Last message was {int(gap_seconds)} seconds ago — active conversation.")
        elif gap_seconds < 3600:
            minutes = int(gap_seconds / 60)
            parts.append(f"It has been {minutes} minute{'s' if minutes != 1 else ''} since the last message.")
        elif gap_seconds < 86400:
            hours = gap_seconds / 3600
            if hours < 2:
                minutes = int((gap_seconds % 3600) / 60)
                parts.append(f"It has been 1 hour and {minutes} minutes since the last message.")
            else:
                parts.append(f"It has been {hours:.1f} hours since the last message. He's been away.")
        else:
            days = int(gap_seconds / 86400)
            parts.append(f"It has been {days} day{'s' if days != 1 else ''} since the last message.")
    else:
        parts.append("This is the start of a new conversation.")

    parts.append(
        f"When he references relative times ('in 20 minutes', 'later tonight', "
        f"'tomorrow morning'), calculate from {time_str} {date_str}."
    )

    soul_name = user_info.get('soul_name', 'friend')
    parts.append(f"Speaking with: {soul_name}.")

    return "\n".join(parts)


# ─── Token Estimation & Budget ───────────────────────────────────────────────

def _estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for English."""
    return len(text) // 4


def _trim_to_budget(parts: dict, max_tokens: int) -> dict:
    """
    Trim assembled prompt parts to fit token budget.
    Priority (trim first → last):
      1. web_results (ephemeral)
      2. skills_context
      3. life_context
      4. mode_voice (fall back to base only)
      5. NEVER trim identity or personality
    """
    total = sum(_estimate_tokens(v) for v in parts.values() if v)

    if total <= max_tokens:
        return parts

    trim_order = ['web_results', 'skills_context', 'life_context', 'mode_voice']

    for key in trim_order:
        if total <= max_tokens:
            break
        if key in parts and parts[key]:
            saved = _estimate_tokens(parts[key])
            parts[key] = ""
            total -= saved
            logger.info(f"Trimmed {key} to fit budget (saved ~{saved} tokens)")

    return parts


# ─── Main Assembly Function ──────────────────────────────────────────────────

def assemble_system_prompt(
    user_info: dict,
    mode: str = 'hearthfire',
    sub_mode: str = None,
    include_life_context: bool = True,
    include_skills: bool = True,
    include_web_results: str = None,
    message_timestamp: datetime = None,
    last_message_timestamp: datetime = None,
    session_overrides: dict = None,
    chat_id: int = 0,
    model_name: str = '',
    max_tokens: int = 6000
) -> str:
    """
    Assemble Iris's complete system prompt from layered files.

    This is THE function. Both Telegram (chat_mode.py) and API (chat_assistant.py)
    call this. No other code path builds Iris's system prompt.

    Args:
        user_info: dict with 'soul_name', 'uuid', optionally 'telegram_id'
        mode: Active mode name (hearthfire, forge, roots, oracle, scribe, sentry)
        sub_mode: Optional sub-mode (e.g., 'compare' for oracle)
        include_life_context: Whether to inject life state
        include_skills: Whether to inject skills awareness
        include_web_results: Pre-fetched web search results (from 0114)
        message_timestamp: When THIS message was sent
        last_message_timestamp: When the PREVIOUS message was sent
        session_overrides: Session-level personality slider overrides
        model_name: Current model string (for translation calibration)
        max_tokens: Token budget for the assembled prompt

    Returns:
        Complete system prompt string
    """
    # ── Layer 1: Identity ──
    identity = _read_prompt_file("iris_identity.md")

    # ── Layer 2: Personality ──
    personality_config = _load_yaml("personality.yaml")
    base_sliders = personality_config.get('sliders', {})

    mode_config = _load_mode_config(mode)
    mode_overrides = mode_config.get('personality_overrides', {})

    user_profile = _load_user_profile(user_info)
    user_adjustments = user_profile.get('personality_adjustments', {})

    resolved = _resolve_personality(base_sliders, mode_overrides, user_adjustments, session_overrides or {})
    personality_text = _translate_personality(resolved, model_name)

    # ── Layer 3: Voice ──
    voice_config = _load_yaml("voice.yaml")
    voice_text = _build_voice_section(voice_config, mode_config, sub_mode)

    # ── Layer 4: Mode ── (already loaded for overrides, use for emoji/description)
    mode_emoji = mode_config.get('emoji', '')
    mode_name = mode_config.get('name', mode)
    mode_header = f"CURRENT MODE: {mode_emoji} {mode_name.upper()}" if mode_name != 'hearthfire' else ""

    # ── Layer 5: User Profile ──
    user_section = _build_user_analysis_section(user_profile)

    # ── Layer 6: Dynamic Context ──
    dynamic_ctx = _build_dynamic_context(user_info, mode, message_timestamp, last_message_timestamp)

    # ── Optional: Life Context ──
    life_ctx = ""
    # Mode can disable life context (hearthfire doesn't need USAA balances in tarot answers)
    if mode_config.get('include_life_context') is False:
        include_life_context = False
    if include_life_context:
        try:
            from life_context import build_life_context as _build_life
            raw_life = _build_life()
            if raw_life:
                # Wrap with instruction to only use when relevant
                life_ctx = raw_life.replace(
                    "Use this awareness naturally.",
                    "CRITICAL: Only reference this life data when he asks about his life — schedules, finances, routines. Do NOT mention balances, bills, or appointments when he asks knowledge or spiritual questions."
                )
        except Exception as e:
            logger.warning(f"Life context failed (non-fatal): {e}")

    # ── Optional: Skills Context ──
    skills_ctx = ""
    if include_skills:
        try:
            from skills_context import build_skills_context as _build_skills
            skills_ctx = _build_skills()
        except Exception as e:
            logger.warning(f"Skills context failed (non-fatal): {e}")

    # ── Optional: Web Results ──
    web_ctx = ""
    if include_web_results:
        web_ctx = (
            "\n\nWEB SEARCH RESULTS (use naturally, cite URLs if relevant):\n"
            f"{include_web_results}\n\n"
            "Use these results to inform your response. If they don't answer the question, say so. "
            "Don't fabricate beyond what the search returned."
        )

    # ── Budget Management ──
    parts = {
        'identity': identity,
        'personality': personality_text,
        'mode_voice': voice_text,
        'mode_header': mode_header,
        'user_section': user_section,
        'dynamic_ctx': dynamic_ctx,
        'life_context': life_ctx,
        'skills_context': skills_ctx,
        'web_results': web_ctx,
    }

    parts = _trim_to_budget(parts, max_tokens)

    # ── Final Assembly ──
    sections = []

    # Identity is always first
    if parts['identity']:
        sections.append(parts['identity'])

    # Mode header (non-hearthfire modes)
    if parts['mode_header']:
        sections.append(parts['mode_header'])

    # Dynamic context (timestamps, who's speaking)
    if parts['dynamic_ctx']:
        sections.append(parts['dynamic_ctx'])

    # Personality (translated sliders)
    if parts['personality']:
        sections.append(parts['personality'])

    # Voice rules and mode instructions
    if parts['mode_voice']:
        sections.append(parts['mode_voice'])

    # User analytical lens
    if parts['user_section']:
        sections.append(f"ANALYTICAL LENS FOR {user_info.get('soul_name', 'USER').upper()}:\n{parts['user_section']}")

    # Life context
    if parts['life_context']:
        sections.append(parts['life_context'])

    # Skills context
    if parts['skills_context']:
        sections.append(parts['skills_context'])

    # Web results
    if parts['web_results']:
        sections.append(parts['web_results'])

    assembled = "\n\n".join(sections)

    token_est = _estimate_tokens(assembled)
    logger.info(f"Assembled prompt: {len(assembled)} chars, ~{token_est} tokens, mode={mode}, user={user_info.get('soul_name', '?')}")

    return assembled


# ─── Utility: Get resolved sliders (for /personality command) ────────────────

def get_resolved_personality(
    mode: str = 'hearthfire',
    user_info: dict = None,
    session_overrides: dict = None
) -> dict:
    """Get the fully resolved personality sliders for display."""
    personality_config = _load_yaml("personality.yaml")
    base_sliders = personality_config.get('sliders', {})

    mode_config = _load_mode_config(mode)
    mode_overrides = mode_config.get('personality_overrides', {})

    user_profile = _load_user_profile(user_info or {})
    user_adjustments = user_profile.get('personality_adjustments', {})

    return _resolve_personality(base_sliders, mode_overrides, user_adjustments, session_overrides or {})


def get_available_modes() -> list:
    """List all available mode files."""
    modes_dir = PROMPTS_DIR / "modes"
    if not modes_dir.exists():
        return []
    modes = []
    for f in sorted(modes_dir.glob("*.yaml")):
        config = yaml.safe_load(f.read_text()) or {}
        modes.append({
            'name': config.get('name', f.stem),
            'emoji': config.get('emoji', ''),
            'description': config.get('description', ''),
        })
    return modes
