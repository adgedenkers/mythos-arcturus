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
        try:
            results = request.parameters.get('results', [])
            keywords = request.parameters.get('keywords', [])
            
            if not keywords:
                # Try splitting the message into words as fallback
                keywords = re.findall(r'\b\w+\b', request.message.lower())
            
            if not results:
                return SkillResponse(
                    skill_name=self.name,
                    data={'ranked': [], 'count': 0, 'keywords_used': keywords},
                    summary='No results to rank.',
                    confidence=0.0,
                    sources=['rank_by_relevance']
                )
            
            # Score each result
            scored_results = []
            for result in results:
                score = self._score(result, keywords)
                result_with_score = result.copy()
                result_with_score['relevance_score'] = score
                scored_results.append(result_with_score)
            
            # Sort by score descending
            sorted_list = sorted(scored_results, key=lambda x: x['relevance_score'], reverse=True)
            
            # Get top score for summary
            top_score = sorted_list[0]['relevance_score'] if sorted_list else 0.0
            
            return SkillResponse(
                skill_name=self.name,
                data={
                    'ranked': sorted_list,
                    'count': len(sorted_list),
                    'keywords_used': keywords
                },
                summary=f'Ranked {len(sorted_list)} results by relevance for keywords: {keywords}. Top score: {top_score:.0%}.',
                confidence=0.9,
                sources=['rank_by_relevance']
            )
        except Exception as e:
            logging.error(f"Error in rank_by_relevance skill: {e}")
            return SkillResponse(
                skill_name=self.name,
                data={'ranked': [], 'count': 0, 'keywords_used': keywords},
                summary=f'Error processing results: {str(e)}',
                confidence=0.0,
                sources=['rank_by_relevance']
            )

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