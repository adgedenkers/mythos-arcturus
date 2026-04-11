import logging
import importlib
from engine.base import SkillBase, SkillRequest, SkillResponse

class PersonDeepDiveSkill(SkillBase):
    name = 'person_deep_dive'
    triggers = [
        'tell me about person',
        'deep dive',
        'everything about',
        'who is',
        'profile for',
        'full profile',
        'person deep dive'
    ]

    SUB_SKILLS = {
        'person': ('data.people_lookup', 'PeopleLookupSkill'),
        'chart': ('data.query_natal_chart', 'QueryNatalChartSkill'),
        'events': ('data.search_life_events', 'SearchLifeEventsSkill'),
        'memos': ('data.search_voice_memos', 'SearchVoiceMemoSkill'),
    }

    def execute(self, request: SkillRequest) -> SkillResponse:
        try:
            results = {}
            for key, (module_name, class_name) in self.SUB_SKILLS.items():
                try:
                    response = self._run_skill(module_name, class_name, request)
                    if response and response.status == 'ok':
                        results[key] = response
                except Exception as e:
                    logging.error(f"Error running {class_name}: {e}")
                    continue
            
            profile = self._build_profile(request, results)
            
            # Merge all data from sub-skills
            merged = {}
            for key, response in results.items():
                if response.data:
                    merged.update(response.data)
            
            # Ensure summary is never empty
            if not profile.strip():
                profile = "No profile information available."
            
            return SkillResponse(
                skill_name=self.name,
                data=merged,
                summary=profile,
                confidence=0.9,
                sources=['person_deep_dive']
            )
        except Exception as e:
            logging.error(f"Error in execute method: {e}")
            # Ensure summary is never empty even on error
            error_summary = f"Error occurred during execution: {str(e)}"
            return SkillResponse(
                skill_name=self.name,
                status='error',
                data={'error': str(e)},
                summary=error_summary,
                confidence=0.0,
                sources=['person_deep_dive']
            )

    def _run_skill(self, module_name: str, class_name: str, request: SkillRequest) -> SkillResponse:
        try:
            module = importlib.import_module(module_name)
            skill_class = getattr(module, class_name)
            skill_instance = skill_class()
            return skill_instance.run(request)
        except Exception as e:
            logging.error(f"Error running skill {class_name} from {module_name}: {e}")
            return SkillResponse(status='error', data={'error': str(e)})

    def _build_profile(self, request: SkillRequest, results: dict) -> str:
        sections = []
        if 'person' in results:
            person_data = results['person'].data or {}
            summary = person_data.get('summary', 'No summary available')
            sections.append(f"Person: {summary}")
        if 'chart' in results:
            chart_data = results['chart'].data or {}
            summary = chart_data.get('summary', 'No chart summary available')
            sections.append(f"Natal Chart: {summary}")
        if 'events' in results:
            events_data = results['events'].data or {}
            summary = events_data.get('summary', 'No events summary available')
            sections.append(f"Life Events: {summary}")
        if 'memos' in results:
            memos_data = results['memos'].data or {}
            summary = memos_data.get('summary', 'No memos summary available')
            sections.append(f"Voice Memos: {summary}")
        
        if sections:
            # Ensure ASCII only
            ascii_sections = []
            for section in sections:
                ascii_section = ''.join(char for char in section if ord(char) < 128)
                ascii_sections.append(ascii_section)
            return '\n'.join(ascii_sections)
        else:
            return 'No profile data found.'