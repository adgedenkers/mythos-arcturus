import logging
import re
from engine.base import SkillBase, SkillRequest, SkillResponse

class ExtractSearchTermsSkill(SkillBase):
    name = 'extract_search_terms'
    version = '1.0'
    category = 'meta'
    description = 'Extract meaningful search keywords from natural language'
    triggers = ['extract', 'keywords', 'search terms']
    cache_ttl = 0

    # Master list of filler words and common phrases to strip
    FILLER_WORDS = {
        'the', 'a', 'an', 'is', 'was', 'are', 'were', 'do', 'does', 'did',
        'have', 'has', 'had', 'been', 'be', 'will', 'would', 'could',
        'should', 'can', 'may', 'might', 'my', 'your', 'our', 'me', 'you',
        'we', 'i', 'it', 'its', 'that', 'this', 'what', 'when', 'where',
        'which', 'who', 'how', 'any', 'some', 'all', 'about', 'for', 'from',
        'with', 'at', 'of', 'in', 'on', 'to', 'and', 'or', 'but', 'not',
        'if', 'so', 'up', 'out', 'just', 'also', 'very', 'really', 'please'
    }

    # Comprehensive list of phrases users prefix queries with
    TRIGGER_PHRASES = [
        'do you remember anything about',
        'what did we talk about',
        'find anything about',
        'search everything for',
        'can you find',
        'show me',
        'look up',
        'search for',
        'tell me about',
        'what do you know about',
        'have we ever discussed',
        'i want to find',
        'search through',
        'look for',
        'find information about',
        'what is',
        'who is',
        'what are',
        'who are',
        'where is',
        'when is',
        'how is',
        'why is',
        'what was',
        'who was',
        'what were',
        'who were',
        'where was',
        'when was',
        'how was',
        'why was',
        'what are we talking about',
        'what have we discussed',
        'what information do you have about',
        'what do you recall about',
        'what do you know',
        'what do you remember',
        'search the database for',
        'find in the records',
        'look in the archives for',
        'search our files for',
        'find anything in the system about'
    ]

    async def execute(self, request) -> SkillResponse:
        try:
            cleaned = self._clean(request.message)
            return SkillResponse(
                skill_name=self.name,
                data={
                    'original': request.message,
                    'cleaned': cleaned,
                    'keywords': cleaned.split() if cleaned else []
                },
                summary=f'Extracted search terms: "{cleaned}"' if cleaned else 'No meaningful search terms found.',
                confidence=0.9 if cleaned else 0.3,
                sources=['extract_search_terms']
            )
        except Exception as e:
            logging.error(f"Error in extract_search_terms skill: {e}")
            raise

    def _clean(self, message) -> str:
        if not message:
            return ''
        
        # Lowercase
        message = message.lower()
        
        # Remove trigger phrases
        for phrase in self.TRIGGER_PHRASES:
            message = message.replace(phrase, '')
        
        # Normalize whitespace
        message = ' '.join(message.split())
        
        # Split into words
        words = message.split()
        
        # Filter out filler words and short words
        filtered_words = [word for word in words if word not in self.FILLER_WORDS and len(word) >= 2]
        
        # Rejoin
        message = ' '.join(filtered_words)
        
        # Strip punctuation except hyphens
        message = re.sub(r'[^\w\s-]', '', message)
        
        # Final whitespace normalize
        message = ' '.join(message.split())
        
        # Ensure ASCII only
        message = re.sub(r'[^\x00-\x7F]+', '', message)
        
        return message or ''