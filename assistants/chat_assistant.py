#!/usr/bin/env python3
"""
Chat Assistant - General conversation interface via Ollama
Provides multi-turn conversation with context maintained per user session.
Integrates with Grid Analysis for consciousness mapping.

Patch 0113: Unified prompt system. _build_iris_prompt(), _prompt_strict(),
_prompt_minimal() replaced by prompt_assembler.assemble_system_prompt().
Temporal awareness via timestamps. num_predict → 4096.

MNE-0004: ConversationBridge wired in. Iris now writes every exchange to
Neo4j knowledge graph (fast extraction: topics, entities, grid activations).
life_context and db_memory now gated by is_layer_enabled() — controlled from
prompt_layers.yaml. Duplicate PerceptionRouter init removed.
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
sys.path.insert(0, "/opt/mythos/neuro")
sys.path.insert(0, "/opt/mythos/core")

try:
    from perception_router import PerceptionRouter
    _perception_router_available = True
except ImportError:
    _perception_router_available = False
    PerceptionRouter = None

from life_context import build_life_context
from message_extractor import extract as extract_message, format_extraction_for_context
from action_executor import execute_actions
from prompt_assembler import assemble_system_prompt, is_layer_enabled, _is_baked_model

# Conversation knowledge bridge — events (Postgres) → knowledge (Neo4j)
try:
    from conversation_bridge import ConversationBridge
    _bridge_available = True
except ImportError as e:
    _bridge_available = False
    ConversationBridge = None

load_dotenv('/opt/mythos/.env')
logger = logging.getLogger(__name__)

# Redis configuration for dispatching to workers
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

# Grid analysis stream
GRID_STREAM = "mythos:assignments:grid_analysis"

# Consciousness Stream — subject tracking (Patch 0128)
try:
    from subject_tracker import process_message as track_subject
    _subject_tracking_available = True
    logger.info("ChatAssistant: Subject tracking available")
except ImportError as e:
    _subject_tracking_available = False
    logger.warning(f"ChatAssistant: Subject tracking not available: {e}")
    def track_subject(*args, **kwargs): return {}

# Subject enrichment Redis stream
SUBJECT_STREAM = "mythos:assignments:subject"

# Research framework — Iris thinks before she speaks (Patch 0131)
try:
    from research_router import route_message as research_route
    from node_executor import NodeExecutor
    from convergence import build_context_package, dispatch_to_grid
    _research_available = True
    logger.info("ChatAssistant: Research framework available")
except ImportError as e:
    _research_available = False
    logger.warning(f"ChatAssistant: Research framework not available: {e}")
    def research_route(*args, **kwargs): return {'needs_research': False, 'active_nodes': []}
    def build_context_package(*args, **kwargs): return ""
    def dispatch_to_grid(*args, **kwargs): pass

# Shared node executor instance
_node_executor = NodeExecutor() if _research_available else None

# Skill engine — route messages through data skills for enrichment
try:
    sys.path.insert(0, '/opt/mythos/skills')
    from engine import SkillEngine
    _skill_engine = SkillEngine()
    _skill_engine_available = True
    logger.info('ChatAssistant: Skill engine available')
except ImportError as e:
    _skill_engine_available = False
    _skill_engine = None
    logger.warning(f'ChatAssistant: Skill engine not available: {e}')

# ── PROMPT LAYER FLAGS ──────────────────────────────────────────────────────
# All gating lives in prompt_layers.yaml (single source of truth).
# Use is_layer_enabled('layer_name') from prompt_assembler for all checks.
# ────────────────────────────────────────────────────────────────────────────


class ChatAssistant:
    """
    General-purpose chat assistant using local Ollama.

    Maintains conversation context per user for multi-turn dialogue.
    Dispatches exchanges to grid analysis worker for consciousness mapping.
    Writes every exchange to Neo4j via ConversationBridge for knowledge extraction.
    """

    def __init__(self):
        # Ollama client
        self.ollama = Client(host=os.getenv('OLLAMA_HOST', 'http://localhost:11434'))
        self.default_model = os.getenv('OLLAMA_MODEL', 'qwen2.5:32b')

        # Perception router (NEU stream) — instantiated once, not twice
        self.perception_router = None
        if _perception_router_available:
            try:
                self.perception_router = PerceptionRouter(
                    pg_conn_string="dbname=mythos user=postgres"
                )
                logger.info("ChatAssistant: perception router initialized")
            except Exception as e:
                logger.warning(f"ChatAssistant: perception router unavailable: {e}")

        # Model mapping for preferences
        from core.model_aliases import MODEL_ALIASES
        self.model_map = MODEL_ALIASES.copy()
        self.model_map['auto'] = self.default_model

        # Per-user conversation contexts (keyed by user_uuid)
        self.contexts: Dict[str, Dict] = {}

        # Context settings
        self.max_context_messages = 20  # Keep last N message pairs

        # Iris memory layer
        self.memory = IrisMemory()
        self._memory_loaded: Dict[str, bool] = {}

        # Conversation knowledge bridge — writes exchanges to Neo4j graph
        self.bridge = None
        if _bridge_available:
            try:
                self.bridge = ConversationBridge()
                logger.info("ChatAssistant: ConversationBridge initialized — Neo4j knowledge extraction active")
            except Exception as e:
                logger.warning(f"ChatAssistant: ConversationBridge unavailable: {e}")

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

        logger.info("ChatAssistant initialized (unified prompt assembler, bridge active)")

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

    def _build_messages(self, user_uuid: str, user_message: str, soul_name: str,
                         model: str = '', research_context: str = '',
                         iris_mode: str = 'sovereign') -> List[Dict]:
        """
        Build the messages array for Ollama API call using unified assembler.

        Clean slate (Patch 0133): Only core layers are active.
        Optional layers controlled by prompt_layers.yaml via is_layer_enabled().

        Args:
            user_uuid: User identifier
            user_message: The message text
            soul_name: Display name for the user
            model: Model name for prompt calibration
            research_context: Pre-built context from research phase
            iris_mode: Active Iris mode from session
        """
        context = self._get_context(user_uuid)
        now = datetime.now()
        last_ts = self._get_last_message_timestamp(user_uuid)

        # ── CORE PROMPT (always active) ──
        # Assembler handles: identity, personality, voice, mode, user profile, timestamps
        system_prompt = assemble_system_prompt(
            user_info={'soul_name': soul_name, 'uuid': user_uuid},
            mode=iris_mode,
            message_timestamp=now,
            last_message_timestamp=last_ts,
            model_name=model,
        )

        # ── OPTIONAL: Life context (routines, bills, calendar, balances) ──
        # Gated by prompt_layers.yaml — enable 'life_context' layer to activate
        if is_layer_enabled('life_context'):
            try:
                life_ctx = build_life_context()
                if life_ctx:
                    system_prompt += life_ctx
            except Exception as e:
                logger.warning(f"Life context failed (non-fatal): {e}")

        # ── OPTIONAL: DB Memory (past conversations) ──
        # Gated by prompt_layers.yaml — enable 'db_memory' layer to activate
        if is_layer_enabled('db_memory'):
            memory_context = self.memory.build_memory_context(user_uuid, limit=20, since_hours=72)
            if memory_context:
                system_prompt += memory_context

        # ── OPTIONAL: Research context (node-scoped data) ──
        if research_context:
            system_prompt += "\n\n" + research_context

        # Store assembled prompt for debugging
        self._last_prompt_tokens = len(system_prompt) // 4
        self._last_prompt_text = system_prompt

        # ── BUILD MESSAGES ARRAY ──
        # For baked models (iris:*): NO system message — Modelfile SYSTEM handles identity.
        # Ollama's chat API replaces the Modelfile SYSTEM with any system message,
        # so sending one wipes the baked identity. Dynamic context goes as a
        # [Context] preamble in the user message instead.
        if _is_baked_model(model):
            messages = []

            # Add conversation history (in-memory session context)
            for msg in context['messages']:
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })

            # Build context preamble from dynamic data
            context_parts = []
            if system_prompt.strip():
                context_parts.append(system_prompt.strip())

            # Prepend context to user message
            if context_parts:
                context_preamble = "[Context]\n" + "\n".join(context_parts) + "\n[/Context]"
                final_message = context_preamble + "\n\n" + user_message
            else:
                final_message = user_message

            messages.append({'role': 'user', 'content': final_message})
            logger.info(f"Chat: Baked model — no system message, context preamble {len(context_preamble) if context_parts else 0} chars")
        else:
            # Non-baked models: standard system message
            messages = [{'role': 'system', 'content': system_prompt}]

            # Add conversation history (in-memory session context)
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

            self.redis.xadd(GRID_STREAM, {"data": json.dumps(payload)})
            logger.info(f"Dispatched grid analysis for exchange {exchange_id[:8]}")
            return exchange_id

        except Exception as e:
            logger.error(f"Failed to dispatch grid analysis: {e}")
            return None

    def _log_to_bridge(
        self,
        conversation_id: str,
        user_uuid: str,
        telegram_id: int,
        user_message: str,
        assistant_response: str,
        model_used: str,
        response_time_ms: int,
        mode: str,
        pg_message_id: Optional[int],
    ) -> None:
        """
        Write exchange to Neo4j knowledge graph via ConversationBridge.
        Fire-and-forget — never blocks the response, never raises.
        """
        if not self.bridge:
            return
        try:
            exchange_id = self.bridge.log_exchange(
                conversation_id=conversation_id,
                user_uuid=user_uuid,
                telegram_id=telegram_id,
                user_message=user_message,
                assistant_response=assistant_response,
                model_used=model_used,
                response_time_ms=response_time_ms,
                mode=mode,
                pg_message_id=pg_message_id,
            )
            if exchange_id:
                logger.debug(f"Bridge: logged exchange {exchange_id[:16]}")
        except Exception as e:
            logger.warning(f"Bridge log failed (non-fatal): {e}")

    def query(self, message: str, model_preference: str = 'auto', telegram_id: int = None) -> str:
        """
        Process a chat message and return the response.

        Args:
            message: The user's input text
            model_preference: 'auto', 'fast', or 'deep'
            telegram_id: Telegram user ID for model override lookup

        Returns:
            The assistant's response text
        """
        if not self.current_user:
            return "Error: No user context set"

        user_uuid = self.current_user.get('uuid', 'unknown')

        # NEU perception logging (non-fatal)
        if self.perception_router:
            try:
                self.perception_router.log_event(
                    source="telegram",
                    source_platform="telegram",
                    content=message
                )
            except Exception as e:
                logger.debug(f"Perception logging skipped: {e}")

        soul_name = self.current_user.get('soul_display_name', 'User')

        # Get model
        model = self.model_map.get(model_preference, self.default_model)

        # Check for /setmodel override
        if telegram_id is not None:
            try:
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
            if is_layer_enabled('db_memory'):
                self._load_db_context(user_uuid)

            # Track response time
            _start_time = time.time()

            # === EXTRACTOR PRE-PASS ===
            extraction = {"no_action": True}
            extraction_context = ""
            if is_layer_enabled('message_extractor'):
                try:
                    extraction = extract_message(message)
                    extraction_context = format_extraction_for_context(extraction)
                    if extraction_context:
                        logger.info(f"Extractor enriched message with: {extraction_context[:100]}")
                except Exception as e:
                    logger.warning(f"Extractor pre-pass failed (non-fatal): {e}")

            # === RESEARCH PHASE ===
            research_plan = {'needs_research': False, 'active_nodes': []}
            research_results = []
            research_context = ""
            if is_layer_enabled('research') and _research_available:
                try:
                    research_plan = research_route(
                        message=message,
                        chat_id=telegram_id or 0,
                        telegram_id=telegram_id or 0,
                    )
                    if research_plan.get('needs_research') and _node_executor:
                        research_results = _node_executor.execute_plan(research_plan)
                        research_context = build_context_package(research_results, research_plan)
                        if research_context:
                            logger.info(f"Research: {len(research_results)} nodes, "
                                       f"{len(research_context)} chars context")
                except Exception as e:
                    logger.warning(f"Research pipeline failed (non-fatal): {e}")

            # === SKILL ENGINE ===
            skill_context = ""
            if is_layer_enabled('skill_results') and _skill_engine_available and _skill_engine:
                try:
                    logger.info(f"Skill engine: invoking process_sync for message: {message[:80]}...")
                    skill_context = _skill_engine.process_sync(
                        message=message,
                        context={
                            'user_uuid': user_uuid,
                            'soul_name': soul_name,
                            'telegram_id': telegram_id,
                        }
                    )
                    if skill_context:
                        logger.info(f"Skill engine: {len(skill_context)} chars context")
                    else:
                        logger.info(f"Skill engine: returned empty context")
                except Exception as e:
                    logger.warning(f"Skill engine failed (non-fatal): {e}", exc_info=True)

            # Get iris_mode from session if available
            _iris_mode = 'sovereign'
            if hasattr(self, 'current_user') and self.current_user:
                _iris_mode = self.current_user.get('iris_mode', 'sovereign')

            # Build enriched message and combined context
            enriched_message = message
            if extraction_context:
                enriched_message = message + "\n\n" + extraction_context

            combined_extra_context = ""
            if research_context:
                combined_extra_context += research_context
            if skill_context:
                if combined_extra_context:
                    combined_extra_context += "\n\n"
                combined_extra_context += skill_context

            messages = self._build_messages(
                user_uuid, enriched_message, soul_name,
                model=model, research_context=combined_extra_context,
                iris_mode=_iris_mode,
            )

            logger.info(f"Chat: Sending to {model} with {len(messages)} messages for user {user_uuid[:8]}")
            print(f"DEBUG MODEL TRACE: preference={model_preference} map_result={self.model_map.get(model_preference)} default={self.default_model} override={get_active_model(telegram_id) if telegram_id else 'no_tid'} FINAL={model}", flush=True)

            # Call Ollama
            response = self.ollama.chat(
                model=model,
                messages=messages,
                options={
                    'temperature': 0.7,
                }
            )

            assistant_message = response['message']['content']

            # Calculate response time
            _response_ms = int((time.time() - _start_time) * 1000)

            # Add both messages to in-memory context
            self._add_to_context(user_uuid, 'user', message)
            self._add_to_context(user_uuid, 'assistant', assistant_message)

            # Persist to Postgres — Iris remembers across restarts
            telegram_id_for_save = telegram_id or 0
            _pg_user_id = self.memory.save_message(
                user_uuid=user_uuid,
                telegram_id=telegram_id_for_save,
                role='user',
                content=message,
                mode='chat',
                conversation_id=conversation_id
            )
            _pg_assistant_id = self.memory.save_message(
                user_uuid=user_uuid,
                telegram_id=telegram_id_for_save,
                role='assistant',
                content=assistant_message,
                mode='chat',
                model_used=model,
                conversation_id=conversation_id,
                response_time_ms=_response_ms
            )

            # === KNOWLEDGE BRIDGE — write exchange to Neo4j graph ===
            # Fast extraction: topics, entities, grid activations. Never blocks.
            self._log_to_bridge(
                conversation_id=conversation_id,
                user_uuid=user_uuid,
                telegram_id=telegram_id_for_save,
                user_message=message,
                assistant_response=assistant_message,
                model_used=model,
                response_time_ms=_response_ms,
                mode='chat',
                pg_message_id=_pg_assistant_id,
            )

            logger.info(f"Chat: Got response ({len(assistant_message)} chars)")

            # === CONSCIOUSNESS STREAM: Track subjects ===
            if _subject_tracking_available:
                try:
                    chat_id = telegram_id or 0
                    user_subject_result = track_subject(
                        chat_id=chat_id,
                        telegram_id=telegram_id or 0,
                        message=message,
                        role='user',
                    )
                    if user_subject_result:
                        logger.debug(f"Subject tracked (user): segment={str(user_subject_result.get('segment_id', ''))[:8]}")

                    track_subject(
                        chat_id=chat_id,
                        telegram_id=0,
                        message=assistant_message,
                        role='assistant',
                    )

                    if self.grid_enabled and self.redis and user_subject_result.get('point_id'):
                        try:
                            self.redis.xadd(SUBJECT_STREAM, {
                                'data': json.dumps({
                                    'point_id': user_subject_result['point_id'],
                                    'message_text': message[:500],
                                    'chat_id': chat_id,
                                    'role': 'user',
                                })
                            })
                        except Exception:
                            pass
                except Exception as e:
                    logger.warning(f"Subject tracking failed (non-fatal): {e}")

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

            # Dispatch to consciousness grid (unconscious processing)
            try:
                dispatch_to_grid(
                    message=message,
                    response=assistant_message,
                    node_results=research_results,
                    research_plan=research_plan,
                    chat_id=telegram_id or 0,
                    telegram_id=telegram_id or 0,
                )
            except Exception as e:
                logger.debug(f"Grid dispatch failed (non-fatal): {e}")

            return assistant_message

        except Exception as e:
            logger.error(f"Chat error: {e}", exc_info=True)
            return f"Error communicating with Ollama: {e}"

    def get_last_prompt(self) -> dict:
        """Return the last assembled system prompt for debugging."""
        return {
            'prompt': getattr(self, '_last_prompt_text', '(no prompt yet)'),
            'tokens': getattr(self, '_last_prompt_tokens', 0),
            'flags': {
                'research': is_layer_enabled('research'),
                'life_context': is_layer_enabled('life_context'),
                'skills_context': is_layer_enabled('skills_context'),
                'db_memory': is_layer_enabled('db_memory'),
                'conversation_awareness': is_layer_enabled('conversation_awareness'),
                'skill_results': is_layer_enabled('skill_results'),
                'message_extractor': is_layer_enabled('message_extractor'),
            },
            'bridge_active': self.bridge is not None,
        }

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
            'started_at': context.get('started_at', 'unknown'),
            'bridge_active': self.bridge is not None,
        }
