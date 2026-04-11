import logging
from engine.base import SkillBase, SkillRequest, SkillResponse

class FormatPersonSummarySkill(SkillBase):
    name = 'format_person_summary'
    version = '1.0'
    category = 'meta'
    description = 'Format person data into a standard readable summary'
    triggers = ['format person', 'person summary', 'who is']
    cache_ttl = 0

    async def execute(self, request) -> SkillResponse:
        # Expects request.parameters['person'] as a dict with people table fields
        pass

    def _format(self, person) -> str:
        # Build: 'Name (aka Nickname), born DATE in CITY, STATE'
        pass