import logging
import importlib
from engine.base import SkillBase, SkillRequest, SkillResponse

class DailyBriefingSkill(SkillBase):
    name = 'daily_briefing'
    version = '1.0'
    category = 'composite'
    description = 'Daily briefing combining spiral time, calendar, routines, and bills'
    triggers = ['good morning', 'daily briefing', 'brief me', 'start my day', 'morning report', 'whats today look like', 'what do i have today']
    cache_ttl = 300

    SUB_SKILLS = {
        'spiral_time': ('data.spiral_time', 'SpiralTimeSkill'),
        'calendar': ('data.query_calendar', 'QueryCalendarSkill'),
        'routines': ('data.query_routines', 'QueryRoutinesSkill'),
        'bills': ('data.query_bills_due', 'QueryBillsDueSkill'),
    }

    def execute(self, request: SkillRequest) -> SkillResponse:
        pass

    def _run_skill(self, module_path: str, class_name: str, request: SkillRequest) -> SkillResponse:
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            response = cls().run(request)
            return response
        except Exception as e:
            return SkillResponse(skill_name=class_name, error=str(e))

    def _build_briefing(self, responses: list) -> str:
        pass