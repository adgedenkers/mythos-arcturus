#!/usr/bin/env python3
"""
Chat Assistant - General conversation interface via Ollama

Provides multi-turn conversation with context maintained per user session.
Integrates with Grid Analysis for consciousness mapping.
"""

import os
import uuid
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
from ollama import Client
import redis

load_dotenv('/opt/mythos/.env')

logger = logging.getLogger(__name__)

# Redis configuration for dispatching to workers
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Grid analysis stream
GRID_STREAM = "mythos:assignments:grid_analysis"


class ChatAssistant:
    """
    General-purpose chat assistant using local Ollama.
    
    Maintains conversation context per user for multi-turn dialogue.
    Dispatches exchanges to grid analysis worker for consciousness mapping.
    """
    
    def __init__(self):
        # Ollama client
        self.ollama = Client(host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
        self.default_model = os.getenv('OLLAMA_MODEL', 'qwen2.5:32b')
        
        # Model mapping for preferences
        self.model_map = {
            'auto': self.default_model,
            'fast': 'llama3.2:3b',
            'deep': self.default_model,
        }
        
        # Per-user conversation contexts (keyed by user_uuid)
        self.contexts: Dict[str, Dict] = {}
        
        # Context settings
        self.max_context_messages = 20  # Keep last N message pairs
        
        # Redis for dispatching to workers
        try:
            self.redis = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True
            )
            self.redis.ping()
            self.grid_enabled = True
            logger.info("ChatAssistant: Redis connected, grid analysis enabled")
        except Exception as e:
            self.redis = None
            self.grid_enabled = False
            logger.warning(f"ChatAssistant: Redis not available, grid analysis disabled: {e}")
        
        # System prompt
        self.system_prompt_template = """You are a helpful AI assistant in the Mythos system, speaking with {soul_name}.

You are running locally on the Arcturus server via Ollama. You have access to conversation history within this session.

Be helpful, conversational, and direct. You can discuss any topic freely.

Current time: {current_time}
"""
        
        logger.info("ChatAssistant initialized")
    
    def set_user(self, user_info: Dict[str, Any]) -> None:
        """Set current user context (for compatibility with API pattern)"""
        self.current_user = user_info
    
    def _get_context(self, user_uuid: str) -> Dict:
        """Get or create conversation context for user"""
        if user_uuid not in self.contexts:
            self.contexts[user_uuid] = {
                'messages': [],
                'started_at': datetime.now().isoformat(),
                'message_count': 0,
                'conversation_id': f"chat-{user_uuid[:8]}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            }
        return self.contexts[user_uuid]
    
    def _add_to_context(self, user_uuid: str, role: str, content: str) -> None:
        """Add a message to user's conversation context"""
        context = self._get_context(user_uuid)
        
        context['messages'].append({
            'role': role,
            'content': content
        })
        context['message_count'] += 1
        
        # Trim old messages if exceeding limit
        if len(context['messages']) > self.max_context_messages * 2:
            context['messages'] = context['messages'][-(self.max_context_messages * 2):]
    
    def _build_messages(self, user_uuid: str, user_message: str, soul_name: str) -> List[Dict]:
        """Build the messages array for Ollama API call"""
        context = self._get_context(user_uuid)
        
        # Build system prompt
        system_prompt = self.system_prompt_template.format(
            soul_name=soul_name,
            current_time=datetime.now().strftime('%Y-%m-%d %H:%M')
        )
        
        messages = [{'role': 'system', 'content': system_prompt}]
        
        # Add conversation history
        messages.extend(context['messages'])
        
        # Add current user message
        messages.append({'role': 'user', 'content': user_message})
        
        return messages
    
    def _dispatch_grid_analysis(
        self,
        user_uuid: str,
        conversation_id: str,
        user_message: str,
        assistant_response: str,
        model_used: str
    ) -> Optional[str]:
        """
        Dispatch exchange to grid analysis worker.
        
        Returns assignment_id if dispatched, None if failed/disabled.
        """
        if not self.grid_enabled or not self.redis:
            return None
        
        try:
            exchange_id = str(uuid.uuid4())
            
            payload = {
                "id": exchange_id,
                "type": "grid_analysis",
                "payload": {
                    "exchange_id": exchange_id,
                    "user_uuid": user_uuid,
                    "conversation_id": conversation_id,
                    "user_message": user_message,
                    "assistant_response": assistant_response,
                    "combined_content": f"USER: {user_message}\n\nASSISTANT: {assistant_response}",
                    "model_used": model_used,
                    "timestamp": datetime.now().isoformat()
                },
                "dispatched_at": datetime.now().isoformat()
            }
            
            # Add to Redis stream
            self.redis.xadd(GRID_STREAM, {"data": json.dumps(payload)})
            
            logger.info(f"Dispatched grid analysis for exchange {exchange_id[:8]}")
            return exchange_id
            
        except Exception as e:
            logger.error(f"Failed to dispatch grid analysis: {e}")
            return None
    
    def query(self, message: str, model_preference: str = 'auto') -> str:
        """
        Process a chat message and return the response.
        
        Args:
            message: The user's input text
            model_preference: 'auto', 'fast', or 'deep'
        
        Returns:
            The assistant's response text
        """
        if not self.current_user:
            return "Error: No user context set"
        
        user_uuid = self.current_user.get('uuid', 'unknown')
        soul_name = self.current_user.get('soul_display_name', 'User')
        
        # Get model
        model = self.model_map.get(model_preference, self.default_model)
        
        # Get conversation context
        context = self._get_context(user_uuid)
        conversation_id = context['conversation_id']
        
        try:
            # Build messages with context
            messages = self._build_messages(user_uuid, message, soul_name)
            
            logger.info(f"Chat: Sending to {model} with {len(messages)} messages for user {user_uuid[:8]}")
            
            # Call Ollama
            response = self.ollama.chat(
                model=model,
                messages=messages,
                options={
                    'temperature': 0.7,
                    'num_predict': 2048,
                }
            )
            
            assistant_message = response['message']['content']
            
            # Add both messages to context for future turns
            self._add_to_context(user_uuid, 'user', message)
            self._add_to_context(user_uuid, 'assistant', assistant_message)
            
            logger.info(f"Chat: Got response ({len(assistant_message)} chars)")
            
            # Dispatch to grid analysis (async, fire-and-forget)
            self._dispatch_grid_analysis(
                user_uuid=user_uuid,
                conversation_id=conversation_id,
                user_message=message,
                assistant_response=assistant_message,
                model_used=model
            )
            
            return assistant_message
            
        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            return f"Error communicating with Ollama: {e}"
    
    def clear_context(self, user_uuid: str) -> None:
        """Clear conversation context for a user"""
        if user_uuid in self.contexts:
            del self.contexts[user_uuid]
            logger.info(f"Cleared context for user {user_uuid[:8]}")
    
    def get_context_stats(self, user_uuid: str) -> Dict[str, Any]:
        """Get statistics about a user's conversation context"""
        context = self._get_context(user_uuid)
        return {
            'message_count': context['message_count'],
            'context_messages': len(context['messages']),
            'conversation_id': context.get('conversation_id'),
            'started_at': context.get('started_at', 'unknown')
        }
