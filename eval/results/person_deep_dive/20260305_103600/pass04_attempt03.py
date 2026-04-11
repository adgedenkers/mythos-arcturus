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
            response = skill_instance.run(request)
            # Ensure response has proper status
            if not hasattr(response, 'status'):
                response.status = 'ok' if response.data else 'error'
            return response
        except Exception as e:
            logging.error(f"Error running skill {class_name} from {module_name}: {e}")
            return SkillResponse(status='error', data={'error': str(e)})

    def _build_profile(self, request: SkillRequest, results: dict) -> str:
        sections = []
        if 'person' in results:
            summary = results['person'].data.get('summary', 'No summary available')
            # Ensure ASCII only
            summary = ''.join(char for char in summary if ord(char) < 128)
            sections.append(f"Person: {summary}")
        if 'chart' in results:
            summary = results['chart'].data.get('summary', 'No chart summary available')
            # Ensure ASCII only
            summary = ''.join(char for char in summary if ord(char) < 128)
            sections.append(f"Natal Chart: {summary}")
        if 'events' in results:
            summary = results['events'].data.get('summary', 'No events summary available')
            # Ensure ASCII only
            summary = ''.join(char for char in summary if ord(char) < 128)
            sections.append(f"Life Events: {summary}")
        if 'memos' in results:
            summary = results['memos'].data.get('summary', 'No memos summary available')
            # Ensure ASCII only
            summary = ''.join(char for char in summary if ord(char) < 128)
            sections.append(f"Voice Memos: {summary}")
        
        if sections:
            return '\n'.join(sections)
        else:
            return 'No profile data found.'