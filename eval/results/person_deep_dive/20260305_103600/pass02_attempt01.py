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
        return SkillResponse(status='ok', data={'profile': profile})

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
            sections.append(f"Person: {results['person'].data.get('summary', 'No summary available')}")
        if 'chart' in results:
            sections.append(f"Natal Chart: {results['chart'].data.get('summary', 'No chart summary available')}")
        if 'events' in results:
            sections.append(f"Life Events: {results['events'].data.get('summary', 'No events summary available')}")
        if 'memos' in results:
            sections.append(f"Voice Memos: {results['memos'].data.get('summary', 'No memos summary available')}")
        
        if sections:
            return '\n'.join(sections)
        else:
            return 'No profile data found.'