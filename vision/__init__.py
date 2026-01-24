"""
Mythos Vision Module
====================
Provides image analysis capabilities via Ollama vision models.

Usage:
    from vision import analyze_image
    from vision.prompts import sales, journal, chat
    
    # For sales item extraction
    result = analyze_image(photos, prompt=sales.ITEM_ANALYSIS)
    
    # For journal entry
    result = analyze_image(photos, prompt=journal.DESCRIBE_FOR_JOURNAL)
    
    # For general chat
    result = analyze_image(photos, prompt=chat.GENERAL_DESCRIPTION)
"""

from .core import analyze_image, analyze_image_async, test_vision
from .config import get_config, VisionConfig

__all__ = [
    'analyze_image',
    'analyze_image_async', 
    'test_vision',
    'get_config',
    'VisionConfig'
]

__version__ = '1.0.0'
