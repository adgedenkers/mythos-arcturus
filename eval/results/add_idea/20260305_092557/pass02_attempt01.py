import os
import logging
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from engine.base import SkillBase, SkillRequest, SkillResponse
import re

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
        
        # 2. Detect domain
        domain = self._detect_domain(request.message)
        
        # 3. INSERT into idea_inbox
        idea_id = self._insert_idea(idea_text, domain, request.message)
        
        # 4. Return confirmation
        return SkillResponse(
            message=f"Idea captured successfully with ID: {idea_id}",
            success=True
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
                host=os.getenv('DB_HOST'),
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
                domain
            ) VALUES (%s, %s, %s, %s) RETURNING id
            """
            
            items = [idea_text]
            item_count = len(items)
            
            cursor.execute(insert_query, (
                source_message,
                json.dumps(items),
                item_count,
                domain
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