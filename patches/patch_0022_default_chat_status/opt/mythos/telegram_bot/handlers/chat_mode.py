#!/usr/bin/env python3
"""
Chat Mode Handler - Direct conversation with local Ollama LLM

Maintains conversation context within a session for multi-turn dialogue.
"""

import os
import re
import logging
from datetime import datetime
from typing import Optional, List
from ollama import Client

logger = logging.getLogger(__name__)

# Ollama configuration
OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:32b')

# Model mapping for /model command
MODEL_MAP = {
    'auto': 'qwen2.5:32b',
    'fast': 'llama3.2:3b',
    'deep': 'qwen2.5:32b',  # Could be changed to a larger model if available
}

# Context window settings
MAX_CONTEXT_MESSAGES = 20  # Keep last N message pairs
MAX_CONTEXT_TOKENS = 8000  # Approximate token limit for context


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
        'topics': []  # Track discussed topics for /status
    }


def get_chat_context(session: dict) -> dict:
    """Get or create chat context"""
    if 'chat_context' not in session or session['chat_context'] is None:
        init_chat_context(session)
    return session['chat_context']


def add_to_context(session: dict, role: str, content: str) -> None:
    """Add a message to the chat context"""
    context = get_chat_context(session)
    
    context['messages'].append({
        'role': role,
        'content': content
    })
    context['message_count'] += 1
    
    # Extract topics from user messages
    if role == 'user':
        topics = extract_topics(content)
        for topic in topics:
            if topic not in context['topics']:
                context['topics'].append(topic)
        # Keep only recent topics
        context['topics'] = context['topics'][-10:]
    
    # Trim old messages if exceeding limit
    if len(context['messages']) > MAX_CONTEXT_MESSAGES * 2:
        # Keep system message if present, then recent messages
        context['messages'] = context['messages'][-(MAX_CONTEXT_MESSAGES * 2):]


def extract_topics(text: str) -> List[str]:
    """Extract likely topics from user message for /status display"""
    # Simple heuristic: look for question patterns and key phrases
    topics = []
    
    # Check for question words and extract the subject
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
            # Clean up and truncate
            topic = re.sub(r'\s+', ' ', topic)[:50]
            if len(topic) > 3:
                topics.append(topic)
    
    # If no patterns matched, use first few words as topic
    if not topics and len(text) > 10:
        words = text.split()[:6]
        topic = ' '.join(words)
        if len(topic) > 50:
            topic = topic[:47] + "..."
        topics.append(topic)
    
    return topics


def build_messages_for_ollama(session: dict, user_message: str, user_info: dict) -> list:
    """Build the messages array for Ollama API call"""
    context = get_chat_context(session)
    
    # System prompt for chat mode
    system_prompt = f"""You are a helpful AI assistant in the Mythos system, speaking with {user_info.get('soul_name', 'a user')}.

You are running locally on the Arcturus server via Ollama. You have access to conversation history within this session.

Be helpful, conversational, and direct. You can discuss any topic freely.

Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    
    messages = [{'role': 'system', 'content': system_prompt}]
    
    # Add conversation history
    messages.extend(context['messages'])
    
    # Add current user message
    messages.append({'role': 'user', 'content': user_message})
    
    return messages


async def handle_chat_message(user_message: str, session: dict, model_preference: str = 'auto') -> str:
    """
    Handle a chat message and return the response.
    
    Args:
        user_message: The user's input text
        session: The user's session dict (contains user info and chat context)
        model_preference: 'auto', 'fast', or 'deep'
    
    Returns:
        The assistant's response text
    """
    try:
        client = get_ollama_client()
        model = get_model_for_preference(model_preference)
        user_info = session.get('user', {})
        
        # Build messages with context
        messages = build_messages_for_ollama(session, user_message, user_info)
        
        logger.info(f"Chat mode: Sending to {model} with {len(messages)} messages")
        
        # Call Ollama
        response = client.chat(
            model=model,
            messages=messages,
            options={
                'temperature': 0.7,
                'num_predict': 2048,  # Max response tokens
            }
        )
        
        assistant_message = response['message']['content']
        
        # Add both messages to context for future turns
        add_to_context(session, 'user', user_message)
        add_to_context(session, 'assistant', assistant_message)
        
        logger.info(f"Chat mode: Got response ({len(assistant_message)} chars)")
        
        return assistant_message
        
    except Exception as e:
        logger.error(f"Chat mode error: {e}", exc_info=True)
        return f"❌ Error communicating with Ollama: {e}"


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
        'topics': context.get('topics', [])
    }


def get_recent_topics(session: dict) -> List[str]:
    """Get list of recently discussed topics for /status display"""
    context = get_chat_context(session)
    return context.get('topics', [])


def get_last_exchange(session: dict) -> Optional[dict]:
    """Get the last user message and assistant response"""
    context = get_chat_context(session)
    messages = context.get('messages', [])
    
    if len(messages) < 2:
        return None
    
    # Find the last user-assistant pair
    for i in range(len(messages) - 1, 0, -1):
        if messages[i]['role'] == 'assistant' and messages[i-1]['role'] == 'user':
            return {
                'user': messages[i-1]['content'],
                'assistant': messages[i]['content']
            }
    
    return None
