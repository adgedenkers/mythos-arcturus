import logging
import re
from datetime import datetime, timedelta

from engine.base import SkillBase, SkillRequest, SkillResponse

class RankByRelevanceSkill(SkillBase):
    name = 'rank_by_relevance'
    version = '1.0'
    category = 'meta'
    description = 'Score results by keyword relevance blended with recency'
    triggers = ['relevant', 'best match', 'most relevant', 'rank by relevance']
    cache_ttl = 0

    async def execute(self, request) -> SkillResponse:
        # Expects request.parameters with 'results' and 'keywords'
        pass

    def _score(self, result, keywords) -> float:
        # Score 0.0-1.0 based on keyword matches in searchable text fields
        # Blend with recency bonus
        if not keywords:
            return 0.0
            
        # Join all string values in result into one text block
        text_parts = []
        for value in result.values():
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, (int, float)):
                text_parts.append(str(value))
            elif isinstance(value, datetime):
                text_parts.append(value.isoformat())
        text = ' '.join(text_parts).lower()
        
        # Calculate keyword score
        total_keywords = len(keywords)
        keyword_score = 0.0
        
        for keyword in keywords:
            keyword = keyword.lower()
            occurrences = text.count(keyword)
            keyword_score += occurrences * (1.0 / total_keywords)
            
        # Cap at 1.0
        keyword_score = min(keyword_score, 1.0)
        
        # Calculate recency bonus
        recency_score = 0.5  # default if no date
        if 'created_at' in result:
            try:
                created_at = result['created_at']
                if isinstance(created_at, str):
                    # Try to parse the datetime string
                    if 'T' in created_at:
                        created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    else:
                        created_at = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                elif isinstance(created_at, datetime):
                    pass  # Already a datetime object
                else:
                    # Assume it's a timestamp
                    created_at = datetime.fromtimestamp(created_at)
                
                days_ago = (datetime.now() - created_at).days
                recency_score = max(0.0, 1.0 - (days_ago / 30.0))
            except Exception:
                # If we can't parse the date, keep default recency_score = 0.5
                pass
        
        # Final score = (keyword_score * 0.7) + (recency_score * 0.3)
        final_score = (keyword_score * 0.7) + (recency_score * 0.3)
        
        # Return clamped 0.0-1.0
        return max(0.0, min(final_score, 1.0))