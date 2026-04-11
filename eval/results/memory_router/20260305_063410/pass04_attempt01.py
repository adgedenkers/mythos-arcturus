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
        try:
            # 1. Extract search terms using _extract_search_terms()
            # 2. Score each store using _score_stores()
            # 3. Return ranked list of stores to search, plus extracted terms
            message = request.message
            terms = self._extract_search_terms(message)
            targets = self._score_stores(message)
            
            # Build summary
            if terms:
                if len(targets) > 0 and any(score > 0 for _, score in targets):
                    store_names = [name for name, score in targets]
                    summary = f"Routing to {len(store_names)} store(s): {', '.join(store_names)}. Search terms: {terms}."
                else:
                    summary = f"No specific store identified -- searching all memory stores for: {terms}."
            else:
                summary = "No searchable content found in message."
            
            return SkillResponse(
                skill_name=self.name,
                data={
                    'targets': [name for name, score in targets],
                    'scores': {name: score for name, score in targets},
                    'search_terms': terms
                },
                summary=summary,
                confidence=max([score for _, score in targets]) if targets else 0.5,
                sources=['memory_router']
            )
        except Exception as e:
            logging.error(f"Error in MemoryRouterSkill.execute: {e}")
            return SkillResponse(
                skill_name=self.name,
                data={},
                summary=f"Error processing request: {str(e)}",
                confidence=0.0,
                sources=['memory_router'],
                success=False
            )

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

    def _score_stores(self, message: str) -> list:
        # Lowercase the message
        message = message.lower()
        
        # Count keyword matches for each store
        store_scores = {}
        for store_name, keywords in self.STORE_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in message:
                    score += 1
            store_scores[store_name] = score
        
        # Check if any store has a score > 0
        total_score = sum(store_scores.values())
        
        # If no specific keywords matched, return all stores with score 1.0
        if total_score == 0:
            return [(store, 1.0) for store in store_scores.keys()]
        
        # Otherwise, filter out stores with score 0 and normalize scores
        scored_stores = [(store, score) for store, score in store_scores.items() if score > 0]
        
        # Normalize scores so max is 1.0
        max_score = max(score for _, score in scored_stores)
        if max_score > 0:
            normalized_stores = [(store, score / max_score) for store, score in scored_stores]
        else:
            normalized_stores = scored_stores
        
        # Sort by score descending
        normalized_stores.sort(key=lambda x: x[1], reverse=True)
        
        return normalized_stores