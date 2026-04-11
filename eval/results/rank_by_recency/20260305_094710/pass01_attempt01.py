import logging
from datetime import datetime, timedelta, timezone

from engine.base import SkillBase, SkillRequest, SkillResponse

class RankByRecencySkill(SkillBase):
    name = 'rank_by_recency'
    version = '1.0'
    category = 'meta'
    description = 'Sort results by date, newest first, with relative timestamps'
    triggers = ['recent', 'latest', 'newest', 'sort by date']
    cache_ttl = 0

    async def execute(self, request) -> SkillResponse:
        # Expects request.parameters['results'] as list of dicts with 'created_at' key
        # Sorts newest first, adds relative_time field
        pass

    def _relative_time(self, dt_str) -> str:
        # Convert ISO date string to 'X minutes/hours/days ago'
        pass