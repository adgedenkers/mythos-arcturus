#!/usr/bin/env python3

"""
MemorySearchSkill - Unified memory search across all stores.
"""

import logging
import importlib
from engine.base import SkillBase, SkillRequest, SkillResponse

STORE_SKILLS = {
    'voice_memos': ('data.search_voice_memos', 'SearchVoiceMemoSkill'),
    'conversations': ('data.search_conversations', 'SearchConversationsSkill'),
    'life_events': ('data.search_life_events', 'SearchLifeEventsSkill'),
    'ideas': ('data.search_ideas', 'SearchIdeasSkill'),
    'documents': ('data.search_documents', 'SearchDocumentsSkill'),
}

class MemorySearchSkill(SkillBase):
    name = 'memory_search'
    version = '1.0'
    category = 'composite'
    description = 'Unified memory search across all stores - voice memos, conversations, life events, ideas, documents'
    triggers = ['remember', 'recall', 'what did', 'when did', 'search memory', 'search everything', 'find anything about', 'do you remember', 'have we ever', 'look through everything']
    cache_ttl = 0

    STORE_SKILLS = {
        'voice_memos': ('data.search_voice_memos', 'SearchVoiceMemoSkill'),
        'conversations': ('data.search_conversations', 'SearchConversationsSkill'),
        'life_events': ('data.search_life_events', 'SearchLifeEventsSkill'),
        'ideas': ('data.search_ideas', 'SearchIdeasSkill'),
        'documents': ('data.search_documents', 'SearchDocumentsSkill'),
    }

    async def execute(self, request: SkillRequest) -> SkillResponse:
        # 1. Run memory_router to determine which stores to search
        router_data = await self._run_router(request)
        targets = router_data.get('targets', list(self.STORE_SKILLS.keys()))
        
        # 2. For each targeted store, import and run the corresponding search skill
        results = {}
        for store_name in targets:
            try:
                response = await self._run_search_skill(store_name, request)
                if response.ok:
                    results[store_name] = response
            except Exception as e:
                logging.error(f"Error running search skill for {store_name}: {e}")
                continue
        
        # 3. Collect all results that returned ok
        # 4. Merge summaries into one unified response
        if results:
            merged_data, merged_summary = self._merge_results(results)
            return SkillResponse(
                ok=True,
                data=merged_data,
                summary=merged_summary
            )
        else:
            return SkillResponse(
                ok=False,
                data={},
                summary="No results found."
            )

    async def _run_router(self, request: SkillRequest) -> dict:
        try:
            module = importlib.import_module('data.memory_router')
            RouterClass = getattr(module, 'MemoryRouterSkill')
            router = RouterClass()
            response = await router.run(request)
            if response.ok:
                return response.data
        except Exception as e:
            logging.error(f"Error in memory router: {e}")
        # Return default dict on error or if not ok
        return {
            'targets': list(self.STORE_SKILLS.keys()),
            'scores': {},
            'search_terms': request.message
        }

    async def _run_search_skill(self, store_name: str, request: SkillRequest) -> SkillResponse:
        try:
            module_path, class_name = self.STORE_SKILLS[store_name]
            module = importlib.import_module(module_path)
            SkillClass = getattr(module, class_name)
            return await SkillClass().run(request)
        except Exception as e:
            logging.error(f"Error running search skill for {store_name}: {e}")
            return SkillResponse(
                ok=False,
                data={},
                summary=f"Error running search skill for {store_name}: {str(e)}",
                skill_name=store_name
            )

    def _merge_results(self, results: dict) -> tuple:
        # results is {store_name: SkillResponse}
        # Combine all data into one dict keyed by store
        # Combine all summaries into one narrative
        merged_data = {}
        stores_searched = list(results.keys())
        stores_with_results = []
        summary_parts = []
        
        # Map store names to human-friendly labels
        store_labels = {
            'voice_memos': 'Voice Memos',
            'conversations': 'Conversations',
            'life_events': 'Life Events',
            'ideas': 'Ideas',
            'documents': 'Documents'
        }
        
        for store_name, response in results.items():
            merged_data[store_name] = response.data
            if response.ok:
                stores_with_results.append(store_name)
                if response.summary:
                    label = store_labels.get(store_name, store_name)
                    summary_parts.append(f"{label}: {response.summary}")
        
        merged_data['stores_searched'] = stores_searched
        merged_data['stores_with_results'] = stores_with_results
        
        if not summary_parts:
            merged_summary = "No results found across any memory store."
        else:
            merged_summary = "\n".join(summary_parts)
        
        return (merged_data, merged_summary)