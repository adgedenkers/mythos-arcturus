#!/usr/bin/env python3
"""
Skill Router — Tier 1 Heuristic Classification
================================================
Decides which skills to activate for a given message.

Current implementation: keyword matching against skill triggers from REGISTRY.yaml
and from registered skill objects themselves.

Designed to be swappable: the SkillRouter class has a single method `route()` that
returns an activation set. Replace the internals with a 7b LLM classifier later
without changing any calling code.

The router interface:
    Input:  message (str) + context (dict)
    Output: list of (skill_name, relevance_score) tuples, sorted by score descending
"""
import logging
from typing import Any, Dict, List, Tuple

from .base import SkillBase

logger = logging.getLogger(__name__)

# Minimum relevance score for a skill to be activated
DEFAULT_THRESHOLD = 0.3

# Maximum skills to activate per message (prevent prompt bloat)
DEFAULT_MAX_SKILLS = 5


class SkillRouter:
    """Routes messages to relevant skills.
    
    Current: Heuristic keyword matching.
    Future: Swap internals for 7b LLM classification. Interface stays the same.
    """

    def __init__(self, threshold: float = DEFAULT_THRESHOLD,
                 max_skills: int = DEFAULT_MAX_SKILLS):
        self.threshold = threshold
        self.max_skills = max_skills

    def route(self, message: str, skills: Dict[str, SkillBase],
              context: Dict[str, Any] = None) -> List[Tuple[str, float]]:
        """Determine which skills should be activated for this message.
        
        Args:
            message: The user's message text
            skills: Dict of skill_name → SkillBase instance (all registered skills)
            context: Optional context (user info, conversation state, etc.)
        
        Returns:
            List of (skill_name, relevance_score) tuples, sorted by score desc.
            Only skills above self.threshold are included.
            Capped at self.max_skills.
        """
        if not message or not skills:
            return []

        scored = []
        for name, skill in skills.items():
            try:
                score = skill.relevance(message, context)
                if score >= self.threshold:
                    scored.append((name, score))
            except Exception as e:
                logger.warning(f"Router: relevance check failed for {name}: {e}")

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        # Cap at max
        activated = scored[:self.max_skills]

        if activated:
            names = ", ".join(f"{n}({s:.2f})" for n, s in activated)
            logger.info(f"Router: activated {len(activated)} skills: {names}")
        else:
            logger.debug(f"Router: no skills activated for message: {message[:80]}...")

        return activated


class AlwaysOnRouter(SkillRouter):
    """A router variant that always activates specific skills.
    
    Useful for skills like spiral_time that should run on every message.
    Combines always-on skills with heuristic routing for the rest.
    """

    def __init__(self, always_on: List[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.always_on = set(always_on or [])

    def route(self, message: str, skills: Dict[str, SkillBase],
              context: Dict[str, Any] = None) -> List[Tuple[str, float]]:
        """Route with always-on skills guaranteed."""
        # Get heuristic results
        heuristic = super().route(message, skills, context)
        heuristic_names = {name for name, _ in heuristic}

        # Add always-on skills that weren't already activated
        result = list(heuristic)
        for name in self.always_on:
            if name in skills and name not in heuristic_names:
                result.append((name, 1.0))  # Always-on gets max score

        # Re-sort and cap
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:self.max_skills]
