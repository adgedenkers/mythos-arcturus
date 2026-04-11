from engine.base import SkillBase, SkillRequest, SkillResponse
import logging
import importlib

class DailyTaskPlannerSkill(SkillBase):
    name = 'daily_task_planner'
    triggers = ['task planner', 'plan my day', 'what should i do', 'daily plan', 'prioritize my day', 'to do list', 'todo list', 'whats on my plate']

    SUB_SKILLS = {
        'calendar': ('data.query_calendar', 'QueryCalendarSkill'),
        'routines': ('data.query_routines', 'QueryRoutinesSkill'),
        'bills': ('data.query_bills_due', 'QueryBillsDueSkill'),
    }

    async def execute(self, request: SkillRequest) -> SkillResponse:
        pass

    async def _run_skill(self, module_path, class_name, request: SkillRequest) -> SkillResponse:
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            response = await cls().run(request)
            return response
        except Exception as e:
            return SkillResponse(skill_name=class_name, error=str(e))

    def _build_plan(self, request: SkillRequest) -> SkillResponse:
        pass