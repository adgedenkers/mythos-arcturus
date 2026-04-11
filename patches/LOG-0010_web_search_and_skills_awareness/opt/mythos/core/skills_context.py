#!/usr/bin/env python3
"""
Skills Context Builder
======================
Produces the skills awareness block injected into Iris's system prompt.

This is NOT a data dump of REGISTRY.yaml. It's a decision guide —
natural language that tells Iris *when* to reach for each capability
and what she'll get back.

The goal: Iris reads this and knows, in the moment, "this question
calls for web_search" or "this is a finance question, I have data for that."

Two tiers of skills:
  - data/ skills: execute automatically via the skill engine (Iris just
    uses the SKILL RESULTS block that appears in her context)
  - analytical/builder/meta skills: Iris invokes manually by reading
    the skill file and following its process

Target: under 400 tokens.
"""
import logging
from pathlib import Path
from typing import Optional
import yaml

logger = logging.getLogger(__name__)

SKILLS_DIR = Path("/opt/mythos/skills")
REGISTRY_FILE = SKILLS_DIR / "REGISTRY.yaml"


# Natural language descriptions of each data skill — what it does and when to expect it.
# These are injected when skills_context layer is enabled, to give Iris awareness
# of what the skill engine may have already run for her.
DATA_SKILL_AWARENESS = """
YOUR SKILL ENGINE — Live data that may appear in your context:

When a message triggers a relevant skill, a "SKILL RESULTS" block appears above
this section. Read it naturally — don't announce that you used a skill, just let
the data inform what you say.

Skills that run automatically when relevant:

KNOWLEDGE & SEARCH:
• web_search — searches the open web via DuckDuckGo + Wikipedia. Activates when
  someone asks about news, current events, recent releases, or anything time-sensitive.
  If you see web results in your context, use them. If web search found nothing,
  say so and suggest they check directly.

FINANCE:
• finance_balance — current account balances and upcoming bills. Activates on
  money questions: "how much do I have", "can I afford", "what's due".
• financial_overview — spending summary, income vs outflow. For budget questions.
• spending_analysis — category-level spending breakdown. For "where is my money going".
• query_bills_due — bills due in a time window. For "what bills are coming up".
• query_transactions — transaction history search. For "did I pay X" or "show me charges".

TIME & SCHEDULE:
• spiral_time — current position in the 9-day spiral cycle (Ka'tuar'el system).
  Always available. Cycle, day number, node archetype, energy description.
• calendar_context — today's events and upcoming appointments.
• query_calendar — calendar lookup for a specific date or range.
• query_routines — today's routines and completion status.

MEMORY & PEOPLE:
• memory_search_composite — searches conversations, life events, voice memos, and
  documents together. For "do you remember when", "what did we talk about", "find X".
• search_conversations — conversation history search.
• search_life_events — life event log search.
• search_voice_memos — voice memo transcript search.
• people_lookup — finds a person in the people registry.
• person_deep_dive — full dossier on a person (astrology, relationships, history).

ASTROLOGY:
• astro_context — current transits and aspects. For "what's the sky doing today".
• query_natal_chart — natal chart data for Ka'tuar'el or Seraphe.

IDEAS & TASKS:
• idea_backlog_manager — backlog items, priorities, dependencies.
• search_ideas — idea inbox search.
• daily_briefing — full day summary: routines, calendar, bills, tasks.
• daily_task_planner — today's task suggestions based on system state.

SHOPPING:
• query_shopping_lists — active shopping lists and items.

If SKILL RESULTS appear in your context: use them naturally.
If no SKILL RESULTS appear: the skill engine found nothing relevant, proceed on your own knowledge.
"""


# Natural language guide for skills Iris invokes manually (analytical/builder/meta)
MANUAL_SKILL_AWARENESS = """
SKILLS YOU INVOKE MANUALLY — Capabilities you activate by reading a skill file:

These are more complex workflows. When the conversation calls for one, read the
skill file at the listed path and follow its process.

ANALYTICAL (read file → follow process → produce output):
• soul_stratigraphy — tri-field astrological analysis: Hellenistic + Vedic + Western
  Tropical with a 4th synthesis layer. For deep chart readings and soul-level work.
  Path: analytical/soul_stratigraphy.md | Risk: T1 (execute freely)

• western_tropical_natal_chart — natal chart generation or rectification using Swiss
  Ephemeris. For chart readings, placement questions, house analysis.
  Path: analytical/western_tropical_natal_chart.md | Risk: T1

BUILDER (build and deploy infrastructure on Arcturus):
• build_patch — create a numbered Mythos patch and deploy via patch monitor.
  For any infrastructure changes, bug fixes, or feature additions.
  Path: builder/build_patch.md | Risk: T2 (build patch, deploy via system)

• build_feature_api — new FastAPI endpoint or service.
  Path: builder/build_feature_api.md | Risk: T2

• build_feature_telegram_mode — new Telegram bot operating mode.
  Path: builder/build_feature_telegram_mode.md | Risk: T2

• build_feature_telegram_tool — new Telegram bot command or inline tool.
  Path: builder/build_feature_telegram_tool.md | Risk: T2

• build_feature_self — when you identify a capability gap and need to build for
  yourself. ALWAYS propose to Ka'tuar'el first before building.
  Path: builder/build_feature_self.md | Risk: T3 (propose, wait for approval)

META:
• humandoc_to_skill — convert a human-written process into a proper skill file.
  Path: meta/humandoc_to_skill.md | Risk: T1

Risk tiers: T1=execute directly, T2=build patch and deploy via system, T3=propose and wait.
All skill files live at /opt/mythos/skills/{path}.
"""


def build_skills_context() -> str:
    """
    Build the skills awareness block for Iris's system prompt.

    Returns a string that tells Iris what skills she has, when they activate,
    and how to use them — in plain language she can reason from.
    """
    return DATA_SKILL_AWARENESS.strip() + "\n\n" + MANUAL_SKILL_AWARENESS.strip()


def get_skill_content(skill_path: str) -> Optional[str]:
    """
    Read a specific skill file.

    Args:
        skill_path: Relative path from skills dir (e.g., 'builder/build_patch.md')

    Returns:
        Skill file content as string, or None if not found.
    """
    full_path = SKILLS_DIR / skill_path
    if not full_path.exists():
        logger.warning(f"Skill file not found: {full_path}")
        return None
    try:
        return full_path.read_text()
    except Exception as e:
        logger.error(f"Failed to read skill file {full_path}: {e}")
        return None


if __name__ == "__main__":
    print(build_skills_context())
    print(f"\n\n--- Token estimate: ~{len(build_skills_context()) // 4} tokens ---")
