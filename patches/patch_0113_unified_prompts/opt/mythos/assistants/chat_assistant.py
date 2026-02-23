#!/usr/bin/env python3
"""
Chat Assistant - General conversation interface via Ollama
Provides multi-turn conversation with context maintained per user session.
Integrates with Grid Analysis for consciousness mapping.

Patch 0113: Unified prompt system. _build_iris_prompt(), _prompt_strict(),
_prompt_minimal() replaced by prompt_assembler.assemble_system_prompt().
Temporal awareness via timestamps. num_predict → 4096.
"""
import os
import time
import uuid
import json
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from dotenv import load_dotenv
from ollama import Client
import redis
from iris_memory import IrisMemory
import sys
sys.path.insert(0, "/opt/mythos/core")
from life_context import build_life_context
from message_extractor import extract as extract_message, format_extraction_for_context
from action_executor import execute_actions
from prompt_assembler import assemble_system_prompt

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
        
        # Iris memory layer
        self.memory = IrisMemory()
        self._memory_loaded: Dict[str, bool] = {}
        
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
        
        logger.info("ChatAssistant initialized (unified prompt assembler)")
    
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
    
    def _add_to_context(self, user_uuid: str, role: str, content: str, timestamp: datetime = None) -> None:
        """Add a message to user's conversation context"""
        context = self._get_context(user_uuid)
        
        ts = timestamp or datetime.now()
        
        context['messages'].append({
            'role': role,
            'content': content,
            'timestamp': ts.isoformat() if isinstance(ts, datetime) else str(ts)
        })
        context['message_count'] += 1
        
        # Trim old messages if exceeding limit
        if len(context['messages']) > self.max_context_messages * 2:
            context['messages'] = context['messages'][-(self.max_context_messages * 2):]
    
    def _load_db_context(self, user_uuid: str) -> None:
        """
        Load recent conversation history from DB into in-memory context.
        Called once per user per bot session — gives Iris continuity across restarts.
        """
        if self._memory_loaded.get(user_uuid):
            return
        
        self._memory_loaded[user_uuid] = True
        
        past_messages = self.memory.load_recent(user_uuid, limit=30, since_hours=72)
        
        if not past_messages:
            logger.info(f"IrisMemory: No recent history for {user_uuid[:8]}")
            return
        
        context = self._get_context(user_uuid)
        
        # Inject past messages into context (before any current session messages)
        db_messages = []
        for msg in past_messages:
            db_messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # Prepend DB messages before any existing in-memory messages
        existing = context['messages']
        context['messages'] = db_messages + existing
        context['message_count'] = len(context['messages'])
        
        # Trim if too many
        max_total = self.max_context_messages * 2
        if len(context['messages']) > max_total:
            context['messages'] = context['messages'][-max_total:]
        
        logger.info(f"IrisMemory: Loaded {len(db_messages)} past messages for {user_uuid[:8]}")

    def _get_last_message_timestamp(self, user_uuid: str) -> Optional[datetime]:
        """Extract the timestamp of the last message in context."""
        context = self._get_context(user_uuid)
        messages = context.get('messages', [])
        if not messages:
            return None
        last = messages[-1]
        ts_str = last.get('timestamp')
        if ts_str:
            try:
                return datetime.fromisoformat(ts_str)
            except (ValueError, TypeError):
                pass
        return None

    def _build_messages(self, user_uuid: str, user_message: str, soul_name: str, model: str = '') -> List[Dict]:
        """Build the messages array for Ollama API call using unified assembler."""
        context = self._get_context(user_uuid)
        
        # Get timestamps for temporal awareness
        now = datetime.now()
        last_ts = self._get_last_message_timestamp(user_uuid)
        
        # Build system prompt via unified assembler
        system_prompt = assemble_system_prompt(
            user_info={'soul_name': soul_name, 'uuid': user_uuid},
            mode='hearthfire',  # API path defaults to hearthfire
            include_life_context=True,
            include_skills=True,
            message_timestamp=now,
            last_message_timestamp=last_ts,
            model_name=model,
        )
        
        # Append memory context separately (memory layer is API-path specific)
        memory_context = self.memory.build_memory_context(user_uuid, limit=20, since_hours=72)
        if memory_context:
            system_prompt += memory_context
        
        messages = [{'role': 'system', 'content': system_prompt}]
        
        # Add conversation history
        for msg in context['messages']:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
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
    
    def query(self, message: str, model_preference: str = 'auto', telegram_id: int = None) -> str:
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
        # Check for /setmodel override
        if telegram_id is not None:
            try:
                import sys
                sys.path.insert(0, "/opt/mythos/telegram_bot")
                from handlers.ollama_models import get_active_model
                override = get_active_model(telegram_id)
                if override:
                    model = override
                    logger.info(f"Chat: Using /setmodel override: {model}")
            except ImportError:
                pass
        
        # Get conversation context
        context = self._get_context(user_uuid)
        conversation_id = context['conversation_id']
        
        try:
            # Load past conversation history from DB (once per session)
            self._load_db_context(user_uuid)
            
            # Track response time
            _start_time = time.time()
            
            # === EXTRACTOR PRE-PASS ===
            extraction = {"no_action": True}
            extraction_context = ""
            try:
                extraction = extract_message(message)
                extraction_context = format_extraction_for_context(extraction)
                if extraction_context:
                    logger.info(f"Extractor enriched message with: {extraction_context[:100]}")
            except Exception as e:
                logger.warning(f"Extractor pre-pass failed (non-fatal): {e}")
            
            # Build messages with context
            enriched_message = message
            if extraction_context:
                enriched_message = message + "\n\n" + extraction_context
            messages = self._build_messages(user_uuid, enriched_message, soul_name, model=model)
            
            logger.info(f"Chat: Sending to {model} with {len(messages)} messages for user {user_uuid[:8]}")
            
            # Call Ollama
            response = self.ollama.chat(
                model=model,
                messages=messages,
                options={
                    'temperature': 0.7,
                    'num_predict': 4096,
                }
            )
            
            assistant_message = response['message']['content']
            
            # Calculate response time
            _response_ms = int((time.time() - _start_time) * 1000)
            
            # Add both messages to context for future turns
            self._add_to_context(user_uuid, 'user', message)
            self._add_to_context(user_uuid, 'assistant', assistant_message)
            
            # Persist to database — Iris remembers across restarts
            telegram_id_for_save = telegram_id or 0
            self.memory.save_message(
                user_uuid=user_uuid,
                telegram_id=telegram_id_for_save,
                role='user',
                content=message,
                mode='chat',
                conversation_id=conversation_id
            )
            self.memory.save_message(
                user_uuid=user_uuid,
                telegram_id=telegram_id_for_save,
                role='assistant',
                content=assistant_message,
                mode='chat',
                model_used=model,
                conversation_id=conversation_id,
                response_time_ms=_response_ms
            )
            
            logger.info(f"Chat: Got response ({len(assistant_message)} chars)")
            
            # === EXTRACTOR POST-PASS: Execute actions ===
            try:
                if not extraction.get("no_action"):
                    action_results = execute_actions(extraction)
                    if action_results:
                        logger.info(f"Executor completed: {action_results}")
            except Exception as e:
                logger.warning(f"Action execution failed (non-fatal): {e}")
            
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
