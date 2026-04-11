#!/usr/bin/env python3
"""
Memory Router Skill for Mythos System.
Analyzes messages to determine which memory stores to search.
"""

import logging
import re
from engine.base import SkillBase, SkillRequest, SkillResponse

class MemoryRouterSkill(SkillBase):
    name = 'memory_router'
    version = '1.0'
    category = 'meta'
    description = 'Analyzes a message and determines which memory stores to search'
    triggers = ['remember', 'recall', 'what did', 'when did', 'did we', 'did I', 'have I', 'have we', 'memory', 'search everything', 'find anything about', 'look up']
    cache_ttl = 0

    STORE_KEYWORDS = {
        'voice_memos': ['voice', 'memo', 'memos', 'recording', 'said', 'talked', 'spoke', 'heard', 'audio', 'transcri'],
        'conversations': ['chat', 'conversation', 'discuss', 'discussed', 'asked', 'told', 'replied', 'message', 'thread'],
        'life_events': ['happened', 'event', 'occurred', 'milestone', 'experience', 'went', 'did', 'felt', 'mood'],
        'ideas': ['idea', 'thought', 'brainstorm', 'suggestion', 'concept', 'proposal', 'plan', 'backlog'],
        'documents': ['document', 'doc', 'file', 'scroll', 'written', 'notes', 'readme', 'architecture'],
    }

    async def execute(self, request: SkillRequest) -> SkillResponse:
        # 1. Extract search terms using _extract_search_terms()
        # 2. Score each store using _score_stores()
        # 3. Return ranked list of stores to search, plus extracted terms
        pass

    def _extract_search_terms(self, message: str) -> str:
        # Lowercase the message
        message = message.lower()
        
        # Define trigger phrases to remove, longest first
        trigger_phrases = [
            'find anything about',
            'search everything',
            'what did we',
            'what did i',
            'when did we',
            'when did i',
            'did we',
            'did i',
            'have we',
            'have i',
            'remember',
            'recall',
            'look up',
            'memory',
            'search for',
            'search about',
            'search',
            'find',
            'about'
        ]
        
        # Remove each trigger phrase
        for phrase in trigger_phrases:
            message = message.replace(phrase, '')
        
        # Clean up extra spaces
        message = ' '.join(message.split())
        
        # Strip punctuation, keep only alphanumeric and spaces
        message = re.sub(r'[^a-z0-9\s]', '', message)
        
        # Return if length >= 2, else empty string
        return message if len(message) >= 2 else ''