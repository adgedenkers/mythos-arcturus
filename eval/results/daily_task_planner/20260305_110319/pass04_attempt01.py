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
        responses = {}
        for label, (module_path, class_name) in self.SUB_SKILLS.items():
            response = await self._run_skill(module_path, class_name, request)
            responses[label] = response

        plan_summary = self._build_plan(responses)
        
        # Merge data from successful responses
        merged_data = []
        for label, response in responses.items():
            if response and hasattr(response, 'data') and response.data:
                if isinstance(response.data, list):
                    merged_data.extend(response.data)
                else:
                    merged_data.append(response.data)
        
        try:
            return SkillResponse(
                skill_name=self.name,
                data={
                    'tasks': merged_data,
                    'calendar': responses.get('calendar', {}).data if responses.get('calendar') and responses['calendar'].ok else {},
                    'routines': responses.get('routines', {}).data if responses.get('routines') and responses['routines'].ok else {},
                    'bills': responses.get('bills', {}).data if responses.get('bills') and responses['bills'].ok else {}
                },
                summary=plan_summary,
                confidence=0.9,
                sources=['daily_task_planner']
            )
        except Exception as e:
            return SkillResponse(skill_name=self.name, error=str(e))

    async def _run_skill(self, module_path: str, class_name: str, request: SkillRequest) -> SkillResponse:
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            response = await cls().run(request)
            return response
        except Exception as e:
            return SkillResponse(skill_name=class_name, error=str(e))

    def _build_plan(self, results) -> str:
        calendar_response = results.get('calendar', None)
        routines_response = results.get('routines', None)
        bills_response = results.get('bills', None)

        tasks = []
        completed_routines = 0
        upcoming_events = 0
        total_tasks = 0

        # 1. Calendar events with times (highest priority)
        if calendar_response and calendar_response.data:
            for event in calendar_response.data:
                if event.get('time'):
                    tasks.append(f"1. [HIGH] Event: {event['title']} at {event['time']}")
                    upcoming_events += 1
                    total_tasks += 1

        # 2. Incomplete routines (medium priority)
        if routines_response and routines_response.data:
            for routine in routines_response.data:
                if not routine.get('completed', False):
                    tasks.append(f"2. [MED] Routine: {routine['title']}")
                    total_tasks += 1
                else:
                    completed_routines += 1

        # 3. Bills due today or tomorrow (medium-high priority)
        if bills_response and bills_response.data:
            for bill in bills_response.data:
                due_date = bill.get('due_date')
                if due_date:
                    # Assuming due_date is a string like "today" or "tomorrow"
                    if due_date.lower() in ['today', 'tomorrow']:
                        tasks.append(f"3. [MED] Bill: {bill['merchant']} ${bill['amount']} due {due_date}")
                        total_tasks += 1

        # 4. Bills due this week (lower priority)
        if bills_response and bills_response.data:
            for bill in bills_response.data:
                due_date = bill.get('due_date')
                if due_date and due_date.lower() not in ['today', 'tomorrow']:
                    tasks.append(f"4. [LOW] Bill: {bill['merchant']} ${bill['amount']} due {due_date}")
                    total_tasks += 1

        # Build summary
        summary = f"Total tasks: {total_tasks}\n"
        summary += f"Completed routines: {completed_routines}\n"
        summary += f"Upcoming events: {upcoming_events}\n\n"

        # Combine tasks with numbering
        numbered_tasks = []
        task_counter = 1
        for task in tasks:
            if task.startswith("1."):
                numbered_tasks.append(f"{task_counter}. {task[3:]}")
            elif task.startswith("2."):
                numbered_tasks.append(f"{task_counter}. {task[3:]}")
            elif task.startswith("3."):
                numbered_tasks.append(f"{task_counter}. {task[3:]}")
            elif task.startswith("4."):
                numbered_tasks.append(f"{task_counter}. {task[3:]}")
            task_counter += 1

        return summary + "\n".join(numbered_tasks)