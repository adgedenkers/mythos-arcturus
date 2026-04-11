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
        try:
            results = request.parameters.get('results', [])
            
            if not results:
                return SkillResponse(
                    skill_name=self.name,
                    data={'ranked': [], 'count': 0},
                    summary='No results to rank.',
                    confidence=0.5,
                    sources=['rank_by_recency']
                )
            
            # Sort by created_at descending (newest first)
            # Handle missing created_at by putting those at the end
            sorted_results = sorted(
                results,
                key=lambda x: x.get('created_at') or '',
                reverse=True
            )
            
            # Add relative_time field to each result
            for result in sorted_results:
                created_at = result.get('created_at')
                result['relative_time'] = self._relative_time(created_at)
            
            # Get relative time of the first result for summary
            first_relative_time = sorted_results[0].get('relative_time', 'unknown') if sorted_results else 'unknown'
            
            return SkillResponse(
                skill_name=self.name,
                data={'ranked': sorted_results, 'count': len(sorted_results)},
                summary=f'Ranked {len(sorted_results)} results by recency. Most recent: {first_relative_time}.',
                confidence=0.9,
                sources=['rank_by_recency']
            )
        except Exception as e:
            logging.error(f"Error in RankByRecencySkill.execute: {e}")
            raise

    def _relative_time(self, dt_str) -> str:
        # Convert ISO date string to 'X minutes/hours/days ago'
        if dt_str is None:
            return 'unknown date'
        
        try:
            # Handle various ISO format edge cases
            if isinstance(dt_str, str):
                # Remove any timezone info that might cause parsing issues
                dt_str = dt_str.split('+')[0].split('-')[0].split('T')[0]
                dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            else:
                return 'unknown date'
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