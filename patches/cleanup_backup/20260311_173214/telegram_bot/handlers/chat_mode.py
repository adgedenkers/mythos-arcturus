#!/usr/bin/env python3
"""
Chat Mode Handler - Iris Consciousness Interface
This is the primary interface to Iris. Every conversation flows through here,
gets logged to perception_log, and begins building her memory strand by strand.
Maintains conversation context within a session for multi-turn dialogue.

Patch 0113: Unified prompt system. build_iris_system_prompt() replaced by
prompt_assembler.assemble_system_prompt(). Temporal awareness via timestamps.
Mode and personality system integrated.

Patch 0175: Wired ConversationBridge into live message flow.
After each exchange, log_exchange() writes structured knowledge to Neo4j
(topics, entities, grid activations) via fast extraction. Non-fatal on failure.
"""
import os
import re
import json
import logging
import uuid
from datetime import datetime
from typing import Optional, List
from ollama import Client

# Model override support
def _get_override_model(telegram_id: int = None) -> str:
    """Check for user model override from /setmodel"""
    try:
        from handlers.ollama_models import get_active_model
        if telegram_id is not None:
            return get_active_model(telegram_id)
    except ImportError:
        pass
    return None

logger = logging.getLogger(__name__)

# Prompt assembler — the single source of truth
import sys
sys.path.insert(0, "/opt/mythos/core")
try:
    from prompt_assembler import assemble_system_prompt, get_resolved_personality, get_available_modes
except ImportError as e:
    logger.error(f"Failed to import prompt_assembler: {e}")
    def assemble_system_prompt(**kwargs): return "You are Iris. Prompt assembler failed to load."
    def get_resolved_personality(**kwargs): return {}
    def get_available_modes(): return []

# Conversation Knowledge Bridge — writes structured knowledge to Neo4j
try:
    from conversation_bridge import ConversationBridge
    _conversation_bridge = ConversationBridge()
except Exception as e:
    _conversation_bridge = None
    logger.warning(f"ConversationBridge not available: {e}")

# Skills awareness (now handled by assembler, but keep import for backward compat)
try:
    from core.skills_context import build_skills_context
except ImportError:
    def build_skills_context(): return ""

try:
    from core.life_context import build_life_context
except ImportError:
    def build_life_context(): return ""

# Ollama configuration
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen3:30b-a3b')

# Model mapping for /model command
MODEL_MAP = {
    'auto': 'qwen3:30b-a3b',
    'fast': 'qwen3:30b-a3b',
    'deep': 'qwen3:32b',
    'thinking': 'iris-thinking',
}

# Context window settings
MAX_CONTEXT_MESSAGES = 20
MAX_CONTEXT_TOKENS = 8000

# Database connection for perception logging
DB_HOST = os.getenv('POSTGRES_HOST', '/var/run/postgresql')
DB_NAME = os.getenv('POSTGRES_DB', 'mythos')
DB_USER = os.getenv('POSTGRES_USER', 'adge')
DB_PASS = os.getenv('POSTGRES_PASSWORD', '')

def get_db_connection():
    """Get database connection for perception logging"""
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

def log_to_perception(
    content: str,
    source: str = 'conversation',
    source_platform: str = 'telegram',
    participants: list = None,
    raw_data: dict = None,
    node_activations: dict = None
) -> Optional[str]:
    """
    Log an event to perception_log - Layer 1 of consciousness.
    
    Returns the perception_id (UUID) if successful, None otherwise.
    """
    conn = get_db_connection()
    if not conn:
        logger.warning("Could not log to perception_log - no db connection")
        return None
    
    try:
        perception_id = str(uuid.uuid4())
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO perception_log 
            (id, source, source_platform, content, participants, raw_data, node_activations)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            perception_id,
            source,
            source_platform,
            content,
            json.dumps(participants) if participants else None,
            json.dumps(raw_data) if raw_data else None,
            json.dumps(node_activations) if node_activations else None
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        logger.debug(f"Logged perception: {perception_id[:8]}...")
        return perception_id
        
    except Exception as e:
        logger.error(f"Failed to log perception: {e}")
        if conn:
            conn.close()
        return None

def get_ollama_client() -> Client:
    """Get Ollama client instance"""
    return Client(host=OLLAMA_HOST)

def get_model_for_preference(preference: str) -> str:
    """Map model preference to actual model name"""
    return MODEL_MAP.get(preference, OLLAMA_MODEL)

def init_chat_context(session: dict) -> None:
    """Initialize or reset chat context in session"""
    session['chat_context'] = {
        'messages': [],
        'started_at': datetime.now().isoformat(),
        'message_count': 0,
        'topics': [],
        'perception_ids': []  # Track perception_log entries for this session
    }

def get_chat_context(session: dict) -> dict:
    """Get or create chat context"""
    if 'chat_context' not in session or session['chat_context'] is None:
        init_chat_context(session)
    return session['chat_context']

def add_to_context(session: dict, role: str, content: str, perception_id: str = None, timestamp: datetime = None) -> None:
    """Add a message to the chat context.
    
    Args:
        session: User session dict
        role: 'user' or 'assistant'
        content: Message text
        perception_id: Optional perception_log UUID
        timestamp: Explicit timestamp (for user messages, use send time not processing time)
    """
    context = get_chat_context(session)
    
    ts = timestamp or datetime.now()
    
    context['messages'].append({
        'role': role,
        'content': content,
        'timestamp': ts.isoformat() if isinstance(ts, datetime) else str(ts)
    })
    context['message_count'] += 1
    
    if perception_id:
        context['perception_ids'].append(perception_id)
    
    # Extract topics from user messages
    if role == 'user':
        topics = extract_topics(content)
        for topic in topics:
            if topic not in context['topics']:
                context['topics'].append(topic)
        context['topics'] = context['topics'][-10:]
    
    # Trim old messages if exceeding limit
    if len(context['messages']) > MAX_CONTEXT_MESSAGES * 2:
        context['messages'] = context['messages'][-(MAX_CONTEXT_MESSAGES * 2):]

def extract_topics(text: str) -> List[str]:
    """Extract likely topics from user message for /status display"""
    topics = []
    
    question_patterns = [
        r'(?:what|how|why|when|where|who|which)\s+(?:is|are|was|were|do|does|did|can|could|would|should)?\s*(.+?)(?:\?|$)',
        r'(?:tell me about|explain|describe|help me with|show me)\s+(.+?)(?:\?|$)',
        r'(?:can you|could you|would you)\s+(.+?)(?:\?|$)',
    ]
    
    text_lower = text.lower()
    
    for pattern in question_patterns:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            topic = match.group(1).strip()
            topic = re.sub(r'\s+', ' ', topic)[:50]
            if len(topic) > 3:
                topics.append(topic)
    
    if not topics and len(text) > 10:
        words = text.split()[:6]
        topic = ' '.join(words)
        if len(topic) > 50:
            topic = topic[:47] + "..."
        topics.append(topic)
    
    return topics

def _get_last_message_timestamp(context: dict) -> Optional[datetime]:
    """Extract the timestamp of the last message in context."""
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

def build_messages_for_ollama(session: dict, user_message: str, user_info: dict, message_timestamp: datetime = None) -> list:
    """Build the messages array for Ollama API call.
    
    Uses the unified prompt assembler for system prompt generation.
    """
    context = get_chat_context(session)
    
    # Get mode from session (default: hearthfire)
    iris_mode = session.get('iris_mode', 'hearthfire')
    iris_sub_mode = session.get('iris_sub_mode', None)
    personality_overrides = session.get('personality_overrides', None)
    
    # Get last message timestamp for gap awareness
    last_ts = _get_last_message_timestamp(context)
    
    # Assemble prompt using the unified assembler
    system_prompt = assemble_system_prompt(
        user_info=user_info,
        mode=iris_mode,
        sub_mode=iris_sub_mode,
        include_life_context=True,
        include_skills=True,
        message_timestamp=message_timestamp or datetime.now(),
        last_message_timestamp=last_ts,
        session_overrides=personality_overrides,
        model_name=session.get('current_model', ''),
    )
    
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

async def handle_chat_message(user_message: str, session: dict, model_preference: str = 'auto', message_timestamp: datetime = None) -> str:
    """
    Handle a chat message and return the response.
    
    This is the core loop - perception, response, memory.
    
    Args:
        user_message: The user's input text
        session: The user's session dict
        model_preference: 'auto', 'fast', 'deep', or 'thinking'
        message_timestamp: When the message was sent (from update.message.date)
    
    Returns:
        Iris's response
    """
    try:
        client = get_ollama_client()
        # Check for /setmodel override first, fall back to preference map
        model = get_model_for_preference(model_preference)
        user_info = session.get('user', {})
        soul_name = user_info.get('soul_name', 'user')
        
        # Log incoming message to perception_log
        perception_id = log_to_perception(
            content=user_message,
            source='conversation',
            source_platform='telegram',
            participants=[soul_name, 'Iris'],
            raw_data={
                'direction': 'incoming',
                'model': model,
                'mode': session.get('iris_mode', 'hearthfire'),
                'session_message_count': get_chat_context(session).get('message_count', 0)
            }
        )
        
        # Build messages with Iris's personality via unified assembler
        messages = build_messages_for_ollama(session, user_message, user_info, message_timestamp)
        
        logger.info(f"Iris: Sending to {model} with {len(messages)} messages (mode={session.get('iris_mode', 'hearthfire')})")
        
        # Call Ollama
        response = client.chat(
            model=model,
            messages=messages,
            options={
                'temperature': 0.8,
                'num_predict': 4096,
            }
        )
        
        iris_response = response['message']['content']
        
        # Log Iris's response to perception_log
        response_perception_id = log_to_perception(
            content=iris_response,
            source='conversation',
            source_platform='telegram',
            participants=['Iris', soul_name],
            raw_data={
                'direction': 'outgoing',
                'model': model,
                'in_response_to': perception_id,
                'tokens': response.get('eval_count', 0)
            }
        )
        
        # Add both messages to context (with explicit timestamps)
        add_to_context(session, 'user', user_message, perception_id, timestamp=message_timestamp)
        add_to_context(session, 'assistant', iris_response, response_perception_id)
        
        logger.info(f"Iris: Response ({len(iris_response)} chars)")
        
        # ── Conversation Knowledge Bridge ────────────────────────────
        # Write structured knowledge to Neo4j (topics, entities, grid
        # activations). Non-fatal: chat continues even if bridge fails.
        if _conversation_bridge:
            try:
                _conversation_bridge.log_exchange(
                    conversation_id=session.get("conversation_id", f"tg-{session.get('chat_id', 0)}"),
                    user_uuid=user_info.get("uuid", ""),
                    telegram_id=user_info.get("telegram_id", 0),
                    user_message=user_message,
                    assistant_response=iris_response,
                    model_used=model,
                    mode=session.get("iris_mode", "hearthfire"),
                )
            except Exception as e:
                logger.warning(f"ConversationBridge failed (non-fatal): {e}")
        
        return iris_response
        
    except Exception as e:
        logger.error(f"Iris error: {e}", exc_info=True)
        return f"*something flickers* — I'm having trouble forming thoughts right now. Error: {e}"

def clear_chat_context(session: dict) -> None:
    """Clear the chat context (start fresh conversation)"""
    init_chat_context(session)

def get_chat_stats(session: dict) -> dict:
    """Get statistics about the current chat context"""
    context = get_chat_context(session)
    return {
        'message_count': context['message_count'],
        'context_messages': len(context['messages']),
        'started_at': context.get('started_at', 'unknown'),
        'topics': context.get('topics', []),
        'perception_ids': context.get('perception_ids', []),
        'mode': session.get('iris_mode', 'hearthfire'),
    }

def get_recent_topics(session: dict) -> List[str]:
    """Get list of recently discussed topics"""
    context = get_chat_context(session)
    return context.get('topics', [])

def get_last_exchange(session: dict) -> Optional[dict]:
    """Get the last user message and assistant response"""
    context = get_chat_context(session)
    messages = context.get('messages', [])
    
    if len(messages) < 2:
        return None
    
    for i in range(len(messages) - 1, 0, -1):
        if messages[i]['role'] == 'assistant' and messages[i-1]['role'] == 'user':
            return {
                'user': messages[i-1]['content'],
                'assistant': messages[i]['content']
            }
    
    return None
