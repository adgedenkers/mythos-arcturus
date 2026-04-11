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
        pass

    def _run_skill(self, module_name: str, class_name: str, request: SkillRequest) -> SkillResponse:
        pass

    def _build_profile(self, request: SkillRequest, results: dict) -> str:
        pass