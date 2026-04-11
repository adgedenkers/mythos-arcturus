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
        results = {}
        merged_data = {}
        
        try:
            for label, (module_path, class_name) in self.SUB_SKILLS.items():
                response = self._run_skill(module_path, class_name, request)
                results[label] = response
                
                if response.ok and response.data:
                    merged_data[label] = response.data
            
            briefing = self._build_briefing(results)
            
            return SkillResponse(
                skill_name=self.name,
                data=merged_data,
                summary=briefing,
                confidence=0.9,
                sources=['daily_briefing']
            )
        except Exception as e:
            logging.error(f"Error in daily briefing execution: {e}")
            return SkillResponse(
                skill_name=self.name,
                error=str(e),
                confidence=0.0
            )

    def _run_skill(self, module_path: str, class_name: str, request: SkillRequest) -> SkillResponse:
        try:
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            instance = cls()
            response = instance.run(request)
            return response
        except Exception as e:
            return SkillResponse(skill_name=class_name, error=str(e), ok=False)

    def _build_briefing(self, results: dict) -> str:
        sections = []
        order = ['spiral_time', 'calendar', 'routines', 'bills']
        
        for label in order:
            if label in results:
                response = results[label]
                if response.ok and response.summary:
                    sections.append(response.summary)
                elif response.ok and response.data:
                    # Fallback to data if summary is missing
                    if label == 'routines':
                        sections.append(f"Routine: {response.data}")
                    else:
                        sections.append(f"{label.capitalize()}: {response.data}")
        
        if not sections:
            return 'Good morning. No briefing data available today.'
        
        return ' | '.join(sections)