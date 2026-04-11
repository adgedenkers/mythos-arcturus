"""
Introspection Skill - SkillBase implementation for triggering
introspection via the Iris skills engine.
"""
import logging
from skills.base import SkillBase, SkillRequest, SkillResponse

logger = logging.getLogger("iris.skills.introspection")


class IntrospectionSkill(SkillBase):
    """Skill that triggers Iris self-introspection."""

    name = "introspection"
    description = "Scan and analyze the Mythos codebase, update manifest and graph"
    version = "0187.1"

    trigger_phrases = [
        "introspect", "scan yourself", "self scan", "analyze codebase",
        "system health", "check integrity", "run introspection",
        "what do you know about yourself",
    ]

    def relevance(self, request: SkillRequest) -> float:
        """Score relevance of this skill to the request."""
        text = request.text.lower()
        for phrase in self.trigger_phrases:
            if phrase in text:
                return 0.95
        if "scan" in text and ("system" in text or "code" in text):
            return 0.7
        return 0.0

    def execute(self, request: SkillRequest) -> SkillResponse:
        """Run introspection and return report."""
        from iris.introspection.run import run_introspection

        # Parse options from request
        quick = "quick" in request.text.lower()
        target = None
        if "path:" in request.text:
            target = request.text.split("path:")[1].strip().split()[0]

        try:
            report = run_introspection(quick=quick, target_path=target)
            from iris.introspection.report import format_report_text
            return SkillResponse(
                success=True,
                text=format_report_text(report),
                data=report,
            )
        except Exception as e:
            logger.error(f"Introspection skill failed: {e}")
            return SkillResponse(
                success=False,
                text=f"Introspection failed: {e}",
            )
