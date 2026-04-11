import os
import logging
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from engine.base import SkillBase, SkillRequest, SkillResponse

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
        # 2. Detect domain
        # 3. INSERT into idea_inbox
        # 4. Return confirmation
        pass

    def _extract_idea(self, message) -> str:
        pass

    def _detect_domain(self, message) -> str:
        pass

    def _insert_idea(self, idea_text, domain, source_message) -> str:
        # INSERT and return the new uuid as string
        pass