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
        results = {}
        for skill_name, (module_path, class_name) in self.SUB_SKILLS.items():
            try:
                response = await self._run_skill(module_path, class_name, request)
                results[skill_name] = response
            except Exception as e:
                return SkillResponse(skill_name=self.name, error=str(e))

        plan_summary = self._build_plan(results)

        merged_data = {}
        for skill_name, response in results.items():
            if response.ok:
                merged_data.update(response.data)

        return SkillResponse(skill_name=self.name, data={'tasks': merged_data, 'calendar': results.get('calendar', {}).data if results.get('calendar') and results['calendar'].ok else {}, 'routines': results.get('routines', {}).data if results.get('routines') and results['routines'].ok else {}, 'bills': results.get('bills', {}).data if results.get('bills') and results['bills'].ok else {}}, summary=plan_summary.response, confidence=0.9, sources=['daily_task_planner'])

    async def _run_skill(self, module_path, class_name, request: SkillRequest) -> SkillResponse:
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            response = await cls().run(request)
            return response
        except Exception as e:
            return SkillResponse(skill_name=class_name, error=str(e))

    def _build_plan(self, results: dict) -> SkillResponse:
        plan = []
        task_count = 0
        completed_routines = 0
        upcoming_events = 0

        # Calendar Events
        if 'calendar' in results and results['calendar'].data:
            for event in results['calendar'].data:
                plan.append(f"1. [HIGH] Event: {event['title']} at {event['time']}")
                task_count += 1
                upcoming_events += 1

        # Routines
        if 'routines' in results and results['routines'].data:
            for routine in results['routines'].data:
                if routine.get('completed', False):
                    completed_routines += 1
                else:
                    plan.append(f"2. [MED] Routine: {routine['title']}")
                    task_count += 1

        # Bills Due Today/Tomorrow
        if 'bills' in results and results['bills'].data:
            bills_today_tomorrow = [bill for bill in results['bills'].data if bill['due_date'] <= 2]
            for bill in bills_today_tomorrow:
                plan.append(f"3. [MED] Bill: {bill['merchant']} ${bill['amount']} due day {bill['due_date']}")
                task_count += 1

        # Bills Due This Week
        bills_this_week = [bill for bill in results['bills'].data if 3 <= bill['due_date'] <= 7]
        for bill in bills_this_week:
            plan.append(f"4. [LOW] Bill: {bill['merchant']} ${bill['amount']} due day {bill['due_date']}")
            task_count += 1

        summary = "\n".join(plan)
        summary += f"\n\nTotal Tasks: {task_count}\nCompleted Routines: {completed_routines}\nUpcoming Events: {upcoming_events}"

        return SkillResponse(skill_name='daily_task_planner', response=summary)