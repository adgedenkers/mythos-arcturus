#!/usr/bin/env python3
"""
Skill Engine — Base Classes
============================
The universal interface that every Mythos skill implements.

SkillBase: Abstract base class for all skills.
SkillRequest: What a skill receives.
SkillResponse: What a skill returns. The `summary` field is MANDATORY —
               Iris never reads raw data, only natural language summaries.

Design: JSON in, JSON out. Skills chain but don't nest.
Cache by cadence: natal charts = forever, transits = hourly, balances = 5 min.
"""
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SkillRequest:
    """What a skill receives when activated."""
    message: str                           # Original user message
    context: Dict[str, Any] = field(default_factory=dict)   # User info, conversation context
    parameters: Dict[str, Any] = field(default_factory=dict) # Skill-specific params from router
    calling_skill: Optional[str] = None    # If chained from another skill
    timestamp: Optional[datetime] = None   # When the request was made

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class SkillResponse:
    """What a skill returns after execution.
    
    The `summary` field is MANDATORY. This is the natural-language text
    that gets injected into Iris's prompt. She never sees raw data.
    """
    skill_name: str                        # Which skill produced this
    data: Dict[str, Any] = field(default_factory=dict)  # Structured results
    summary: str = ""                      # MANDATORY: natural language for prompt
    confidence: float = 1.0                # 0.0–1.0
    sources: List[str] = field(default_factory=list)     # Data provenance
    execution_ms: int = 0                  # How long it took
    error: Optional[str] = None            # If something went wrong
    suggest_skills: Optional[List[str]] = None  # "You should also ask..."

    @property
    def ok(self) -> bool:
        return self.error is None and bool(self.summary)


class SkillBase(ABC):
    """Abstract base class for all Mythos skills.
    
    Every skill implements two methods:
    - relevance(): Given a message, how relevant is this skill? (0.0–1.0)
    - execute(): Do the work, return a SkillResponse.
    
    Subclasses set class-level attributes for metadata:
        name, version, category, description, triggers, cache_ttl
    """

    # ── Subclass must set these ──────────────────────────────────────
    name: str = "unnamed_skill"
    version: str = "1.0"
    category: str = "data"                 # data | action | composite | meta
    description: str = ""
    triggers: List[str] = []               # Keywords/phrases that activate this skill
    cache_ttl: int = 0                     # Seconds. 0 = no cache.

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._cache_time: Dict[str, float] = {}

    def relevance(self, message: str, context: Dict[str, Any] = None) -> float:
        """Score how relevant this skill is to the given message.
        
        Default implementation: keyword matching against self.triggers.
        Override for smarter matching.
        
        Returns 0.0–1.0
        """
        if not self.triggers:
            return 0.0

        msg_lower = message.lower()
        matches = 0
        for trigger in self.triggers:
            trigger_lower = trigger.lower()
            if trigger_lower in msg_lower:
                matches += 1

        if matches == 0:
            return 0.0

        # Score: more trigger matches = higher relevance, capped at 1.0
        return min(1.0, matches * 0.4 + 0.3)

    @abstractmethod
    async def execute(self, request: SkillRequest) -> SkillResponse:
        """Execute the skill and return results.
        
        Must return a SkillResponse with at minimum a non-empty `summary`.
        """
        ...

    def _cache_key(self, request: SkillRequest) -> str:
        """Generate a cache key for this request. Override for custom keys."""
        return f"{self.name}:{hash(request.message)}"

    def _check_cache(self, request: SkillRequest) -> Optional[SkillResponse]:
        """Check if we have a cached response."""
        if self.cache_ttl <= 0:
            return None
        key = self._cache_key(request)
        if key in self._cache:
            age = time.time() - self._cache_time.get(key, 0)
            if age < self.cache_ttl:
                logger.debug(f"Skill {self.name}: cache hit (age={age:.0f}s)")
                return self._cache[key]
            else:
                del self._cache[key]
                del self._cache_time[key]
        return None

    def _set_cache(self, request: SkillRequest, response: SkillResponse):
        """Cache a response."""
        if self.cache_ttl <= 0:
            return
        key = self._cache_key(request)
        self._cache[key] = response
        self._cache_time[key] = time.time()

    async def run(self, request: SkillRequest) -> SkillResponse:
        """Run the skill with caching and timing. Don't override this — override execute()."""
        # Check cache first
        cached = self._check_cache(request)
        if cached:
            return cached

        start = time.time()
        try:
            response = await self.execute(request)
            response.execution_ms = int((time.time() - start) * 1000)
            response.skill_name = self.name

            if response.ok:
                self._set_cache(request, response)

            logger.info(
                f"Skill {self.name}: executed in {response.execution_ms}ms, "
                f"confidence={response.confidence:.2f}, "
                f"summary_len={len(response.summary)}"
            )
            return response

        except Exception as e:
            elapsed = int((time.time() - start) * 1000)
            logger.error(f"Skill {self.name} failed after {elapsed}ms: {e}", exc_info=True)
            return SkillResponse(
                skill_name=self.name,
                error=str(e),
                execution_ms=elapsed,
            )

    def __repr__(self):
        return f"<Skill:{self.name} v{self.version} ({self.category})>"
