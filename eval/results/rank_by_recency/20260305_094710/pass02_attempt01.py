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
        if dt_str is None:
            return 'unknown date'
        
        try:
            dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return 'unknown date'
        
        now = datetime.now(timezone.utc)
        delta = now - dt
        
        if delta < timedelta(minutes=1):
            return 'just now'
        elif delta < timedelta(hours=1):
            minutes = int(delta.total_seconds() / 60)
            return f'{minutes} minutes ago'
        elif delta < timedelta(days=1):
            hours = int(delta.total_seconds() / 3600)
            return f'{hours} hours ago'
        elif delta < timedelta(days=7):
            days = int(delta.total_seconds() / 86400)
            return f'{days} days ago'
        elif delta < timedelta(days=30):
            weeks = int(delta.total_seconds() / 604800)
            return f'{weeks} weeks ago'
        else:
            months = int(delta.total_seconds() / 2592000)
            return f'{months} months ago'