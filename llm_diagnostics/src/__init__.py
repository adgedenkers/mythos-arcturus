"""
Mythos LLM Diagnostics
Natural language interface for system diagnostics
"""

from .conversation_logger import log_conversation, get_conversation_history, get_recent_conversations
from .mythos_ask import MythosAsk

__version__ = "0.1.0"
__all__ = [
    'MythosAsk',
    'log_conversation',
    'get_conversation_history',
    'get_recent_conversations'
]
