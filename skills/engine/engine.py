#!/usr/bin/env python3
"""
Skill Engine — The Orchestrator
================================
Loads skills from the registry, routes messages, executes activated skills,
and assembles results into a context block for Iris's prompt.

This is the single integration point. ChatAssistant calls:
    engine = SkillEngine()
    context_block = await engine.process(message, user_context)

And gets back a string ready to inject into the system prompt.

The engine:
1. Loads all registered skill classes from /opt/mythos/skills/data/
2. On each message, runs the router to determine activation set
3. Executes activated skills (currently sequential, async-ready for parallel later)
4. Assembles all summaries into a single context block
5. Returns the block (or empty string if no skills activated)
"""
import asyncio
import importlib
import importlib.util
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import SkillBase, SkillRequest, SkillResponse
from .router import SkillRouter

logger = logging.getLogger(__name__)

SKILLS_DATA_DIR = Path("/opt/mythos/skills/data")


class SkillEngine:
    """Central skill orchestration engine.
    
    Usage:
        engine = SkillEngine()
        context_block = engine.process_sync(message, context)
        # inject context_block into system prompt
    """

    def __init__(self, router: SkillRouter = None):
        self.router = router or SkillRouter()
        self.skills: Dict[str, SkillBase] = {}
        self._loaded = False

    def load_skills(self):
        """Discover and load all skill classes from the data directory."""
        if self._loaded:
            return

        if not SKILLS_DATA_DIR.exists():
            logger.warning(f"Skills data directory not found: {SKILLS_DATA_DIR}")
            self._loaded = True
            return

        for py_file in sorted(SKILLS_DATA_DIR.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            try:
                self._load_skill_module(py_file)
            except Exception as e:
                logger.error(f"Failed to load skill from {py_file.name}: {e}", exc_info=True)

        self._loaded = True
        logger.info(f"SkillEngine: loaded {len(self.skills)} skills: {', '.join(self.skills.keys())}")

    def _load_skill_module(self, path: Path):
        """Load a single skill module and register any SkillBase subclasses."""
        module_name = f"mythos_skill_{path.stem}"

        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            logger.warning(f"Could not load spec for {path}")
            return

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Find all SkillBase subclasses in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (isinstance(attr, type)
                    and issubclass(attr, SkillBase)
                    and attr is not SkillBase
                    and not getattr(attr, '__abstractmethods__', None)):
                instance = attr()
                self.skills[instance.name] = instance
                logger.debug(f"Registered skill: {instance.name} from {path.name}")

    def register_skill(self, skill: SkillBase):
        """Manually register a skill instance."""
        self.skills[skill.name] = skill
        logger.info(f"Manually registered skill: {skill.name}")

    async def process(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process a message through the skill pipeline.
        
        1. Ensure skills are loaded
        2. Route message to determine activation set
        3. Execute activated skills
        4. Assemble context block from results
        
        Returns:
            A formatted context block string for prompt injection.
            Empty string if no skills activated or all failed.
        """
        self.load_skills()

        if not self.skills:
            return ""

        context = context or {}
        start = time.time()

        # Route
        activation_set = self.router.route(message, self.skills, context)
        if not activation_set:
            return ""

        # Execute activated skills
        request = SkillRequest(message=message, context=context)
        results: List[SkillResponse] = []

        for skill_name, score in activation_set:
            skill = self.skills.get(skill_name)
            if not skill:
                continue
            response = await skill.run(request)
            if response.ok:
                results.append(response)

        if not results:
            return ""

        # Assemble context block
        total_ms = int((time.time() - start) * 1000)
        # ── Mutual exclusion: web_browser supersedes web_search ──
        skill_names_in_results = [r.skill_name for r in results]
        if 'web_browser' in skill_names_in_results and 'web_search' in skill_names_in_results:
            results = [r for r in results if r.skill_name != 'web_search']

        context_block = self._assemble_context(results, total_ms)

        logger.info(
            f"SkillEngine: {len(results)}/{len(activation_set)} skills returned data, "
            f"total {total_ms}ms, context {len(context_block)} chars"
        )

        return context_block

    def process_sync(self, message: str, context: Dict[str, Any] = None) -> str:
        """Synchronous wrapper for process(). Use from non-async code.

        Uses threading.Thread instead of ThreadPoolExecutor to avoid
        interference from the parent event loop's I/O machinery when
        called from within a running event loop (e.g. telegram bot).

        ThreadPoolExecutor shares the parent loop's context and causes
        urllib/socket calls to silently fail inside the worker thread.
        threading.Thread gives a completely clean execution context.
        """
        import threading

        result_holder = []
        error_holder = []

        def run_in_thread():
            try:
                result_holder.append(asyncio.run(self.process(message, context)))
            except Exception as e:
                error_holder.append(e)
                result_holder.append("")

        try:
            loop = asyncio.get_running_loop()
            # Running inside an active event loop — use a clean thread
            t = threading.Thread(target=run_in_thread, daemon=True)
            t.start()
            t.join(timeout=15)
            if t.is_alive():
                logger.warning("process_sync: thread timed out after 15s")
                return ""
            if error_holder:
                logger.error(f"process_sync thread error: {error_holder[0]}")
            return result_holder[0] if result_holder else ""
        except RuntimeError:
            # No running event loop — call directly
            return asyncio.run(self.process(message, context))

    def _assemble_context(self, results: List[SkillResponse], total_ms: int) -> str:
        """Assemble skill results into a prompt-ready context block."""
        lines = []
        lines.append("SKILL RESULTS — Data retrieved to answer this message. USE this data in your response. Do NOT ignore it or redirect to other topics:")

        for r in results:
            source_str = f" [{', '.join(r.sources)}]" if r.sources else ""
            lines.append(f"• {r.skill_name}{source_str}: {r.summary}")

        lines.append(f"(Retrieved in {total_ms}ms from {len(results)} skill{'s' if len(results) != 1 else ''})")
        lines.append("Use this data naturally in your response. Don't recite it — let it inform what you say.")

        return "\n".join(lines)

    def get_status(self) -> Dict[str, Any]:
        """Return engine status for diagnostics."""
        self.load_skills()
        return {
            "loaded": self._loaded,
            "skill_count": len(self.skills),
            "skills": {
                name: {
                    "version": s.version,
                    "category": s.category,
                    "triggers": s.triggers,
                    "cache_ttl": s.cache_ttl,
                }
                for name, s in self.skills.items()
            },
            "router": type(self.router).__name__,
        }
