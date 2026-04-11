import os
import logging
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from engine.base import SkillBase, SkillRequest, SkillResponse
import re
import unicodedata

load_dotenv()

class AddIdeaSkill(SkillBase):
    name = 'add_idea'
    version = '1.0'
    category = 'action'
    description = 'Capture a new idea into the inbox'
    triggers = ['idea', 'i have an idea', 'new idea', 'add idea', 'capture idea', 'thought about', 'what if we', 'we should', 'we could']
    cache_ttl = 0

    async def execute(self, request) -> SkillResponse:
        # 1. Extract the idea text
        idea_text = self._extract_idea(request.message)
        
        # Check if idea text is empty or less than 3 characters
        if not idea_text or len(idea_text) < 3:
            return SkillResponse(
                skill_name=self.name,
                data={},
                summary='Could not capture an idea. Please describe your thought.',
                confidence=0.3,
                sources=[]
            )
        
        # 2. Detect domain
        domain = self._detect_domain(request.message)
        
        # 3. INSERT into idea_inbox
        try:
            idea_id = self._insert_idea(idea_text, domain, request.message)
        except Exception as e:
            logging.error(f"Error inserting idea: {e}")
            raise
        
        # 4. Return confirmation
        return SkillResponse(
            skill_name=self.name,
            data={'idea_id': idea_id, 'idea': idea_text, 'domain': domain},
            summary=f'Captured idea: "{idea_text}"' + (f' (domain: {domain})' if domain else ''),
            confidence=0.95,
            sources=['mythos.idea_inbox']
        )

    def _extract_idea(self, message) -> str:
        # Convert to lowercase
        message = message.lower()
        
        # Remove triggers LONGEST FIRST
        triggers_to_remove = [
            'i have an idea',
            'capture idea',
            'thought about',
            'what if we',
            'we should',
            'we could',
            'new idea',
            'add idea',
            'idea',
            'capture'
        ]
        
        for trigger in triggers_to_remove:
            if trigger in message:
                message = message.replace(trigger, '', 1)
                break  # Only remove the first occurrence (longest match)
        
        # Normalize whitespace
        message = re.sub(r'\s+', ' ', message)
        
        # Strip punctuation except basic ones (letters, numbers, spaces, periods, commas, exclamation, question marks)
        message = re.sub(r'[^\w\s.,!?]', '', message)
        
        # Strip leading/trailing whitespace
        message = message.strip()
        
        # Normalize to ASCII
        message = unicodedata.normalize('NFKD', message)
        message = ''.join(c for c in message if ord(c) < 128)
        
        return message

    def _detect_domain(self, message) -> str:
        message = message.lower()
        
        domains = {
            'technical': ['technical', 'code', 'programming', 'software', 'development', 'engineer', 'coding'],
            'spiritual': ['spiritual', 'spirit', 'god', 'divine', 'soul', 'consciousness', 'enlightenment', 'meditation'],
            'personal': ['personal', 'self', 'me', 'myself', 'i', 'we', 'our', 'you', 'your'],
            'financial': ['financial', 'money', 'finance', 'economy', 'investment', 'wealth', 'budget', 'cash', 'loan', 'credit'],
            'mythos': ['mythos', 'myth', 'legend', 'tale', 'story', 'narrative', 'archetype', 'symbol', 'sacred', 'mythical']
        }
        
        for domain, keywords in domains.items():
            for keyword in keywords:
                if keyword in message:
                    return domain
        
        return None

    def _insert_idea(self, idea_text, domain, source_message) -> str:
        # INSERT and return the new uuid as string
        conn = None
        try:
            conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST'),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                port=os.getenv('DB_PORT')
            )
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Insert the idea
            insert_query = """
            INSERT INTO idea_inbox (
                conversation_context,
                items,
                item_count,
                disposition,
                domain,
                tags
            ) VALUES (%s, %s, 1, 'pending', %s, %s) RETURNING id
            """
            
            items_json = json.dumps([idea_text])
            tags_json = json.dumps([domain]) if domain else json.dumps([])
            
            cursor.execute(insert_query, (
                source_message,
                items_json,
                domain,
                tags_json
            ))
            
            result = cursor.fetchone()
            idea_id = result['id']
            
            conn.commit()
            return str(idea_id)
            
        except Exception as e:
            logging.error(f"Error inserting idea: {e}")
            raise
        finally:
            if conn:
                conn.close()