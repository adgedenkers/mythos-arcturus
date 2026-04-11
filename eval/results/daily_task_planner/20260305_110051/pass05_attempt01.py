import logging
import importlib
from engine.base import SkillBase, SkillRequest, SkillResponse

class DailyTaskPlannerSkill(SkillBase):
    name = 'daily_task_planner'
    triggers = [
        'task planner', 'plan my day', 'what should i do', 'daily plan',
        'prioritize my day', 'to do list', 'todo list', 'whats on my plate'
    ]

    SUB_SKILLS = {
        'calendar': ('data.query_calendar', 'QueryCalendarSkill'),
        'routines': ('data.query_routines', 'QueryRoutinesSkill'),
        'bills': ('data.query_bills_due', 'QueryBillsDueSkill'),
    }

    async def execute(self, request: SkillRequest) -> SkillResponse:
        results = {}
        for skill_name, (module_path, class_name) in self.SUB_SKILLS.items():
            response = await self._run_skill(module_path, class_name, request)
            results[skill_name] = response

        plan = self._build_plan(results)
        
        # Merge data from successful responses
        merged_data = []
        calendar_data = results.get('calendar', {}).data if results.get('calendar') and results['calendar'].ok else {}
        routines_data = results.get('routines', {}).data if results.get('routines') and results['routines'].ok else {}
        bills_data = results.get('bills', {}).data if results.get('bills') and results['bills'].ok else {}
        
        if calendar_data:
            merged_data.extend(calendar_data)
        if routines_data:
            merged_data.extend(routines_data)
        if bills_data:
            merged_data.extend(bills_data)

        try:
            if not merged_data:
                plan = "No tasks for today - enjoy your free time!"
            return SkillResponse(
                skill_name=self.name,
                data={
                    'tasks': merged_data,
                    'calendar': calendar_data,
                    'routines': routines_data,
                    'bills': bills_data
                },
                summary=plan,
                confidence=0.9,
                sources=['daily_task_planner']
            )
        except Exception as e:
            logging.error(f"Error in daily task planner: {e}")
            return SkillResponse(skill_name=self.name, error=str(e))

    async def _run_skill(self, module_path: str, class_name: str, request: SkillRequest) -> dict:
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            response = await cls().run(request)
            return response
        except Exception as e:
            return SkillResponse(skill_name=class_name, error=str(e))

    def _build_plan(self, results: dict) -> str:
        plan_lines = []
        total_tasks = 0
        completed_routines = 0
        upcoming_events = 0

        # Process calendar events
        if 'calendar' in results and results['calendar'].data:
            calendar_data = results['calendar'].data
            for event in calendar_data:
                if 'time' in event:
                    plan_lines.append(f"1. [HIGH] Event: {event.get('title', 'Untitled')} at {event.get('time')}")
                    total_tasks += 1
                    upcoming_events += 1

        # Process routines
        if 'routines' in results and results['routines'].data:
            routines_data = results['routines'].data
            for routine in routines_data:
                if routine.get('completed'):
                    completed_routines += 1
                else:
                    plan_lines.append(f"{len(plan_lines) + 1}. [MED] Routine: {routine.get('title', 'Untitled')}")
                    total_tasks += 1

        # Process bills due today or tomorrow
        if 'bills' in results and results['bills'].data:
            bills_data = results['bills'].data
            for bill in bills_data:
                due_date = bill.get('due_date')
                if due_date:
                    if 'today' in due_date.lower() or 'tomorrow' in due_date.lower():
                        plan_lines.append(f"{len(plan_lines) + 1}. [MED-HIGH] Bill: {bill.get('merchant', 'Unknown')} ${bill.get('amount', '0.00')} due {due_date}")
                        total_tasks += 1
                    elif 'this week' in due_date.lower():
                        plan_lines.append(f"{len(plan_lines) + 1}. [LOW] Bill: {bill.get('merchant', 'Unknown')} ${bill.get('amount', '0.00')} due {due_date}")
                        total_tasks += 1

        # Build summary
        summary = f"Total tasks: {total_tasks}\nCompleted routines: {completed_routines}\nUpcoming events: {upcoming_events}\n\n"
        if not plan_lines:
            return "No tasks for today - enjoy your free time!"
        return summary + "\n".join(plan_lines)