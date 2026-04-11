from engine.base import SkillBase, SkillRequest, SkillResponse
import logging

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

    async def _run_skill(self, request: SkillRequest) -> SkillResponse:
        pass

    def _build_plan(self, request: SkillRequest) -> SkillResponse:
        pass