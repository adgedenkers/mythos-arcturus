#!/usr/bin/env python3
"""
MNE-0004: Conversation Bridge Wiring
======================================
Wires ConversationBridge into ChatAssistant so every exchange is written
to the Neo4j knowledge graph (fast extraction: topics, entities, grid
activations). Also enables db_memory and life_context layers so Iris
has access to her own memory and knows the current state of the day.

Changes:
  - chat_assistant.py: bridge instantiated in __init__, called after
    memory.save_message() via _log_to_bridge(). Duplicate PerceptionRouter
    init removed. life_context now gated by is_layer_enabled().
  - prompt_layers.yaml: db_memory enabled, life_context enabled.
"""
import sys
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='MNE',
    number=4,
    description='conversation_bridge_wiring',
    patch_type='MINOR',
)
patch.begin()

# Deploy updated chat_assistant.py
patch.deploy_file(
    'opt/mythos/assistants/chat_assistant.py',
    '/opt/mythos/assistants/chat_assistant.py',
)

# Deploy updated prompt_layers.yaml
patch.deploy_file(
    'opt/mythos/prompts/prompt_layers.yaml',
    '/opt/mythos/prompts/prompt_layers.yaml',
)

# Restart bot and API so changes take effect
patch.restart_service('mythos-bot.service')
patch.restart_service('mythos-api.service')

patch.finish()
