"""
Utility functions for Mythos Orchestrator.

Provides common utility functions for:
- ID generation
- Hashing
- Time formatting
- JSON handling
- String operations
"""

import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
import json
import logging
import re

logger = logging.getLogger(__name__)


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID with optional prefix.
    
    Uses UUID4 for uniqueness. IDs are 12 characters + optional prefix.
    
    Args:
        prefix: Optional prefix for the ID
    
    Returns:
        Unique identifier string
    
    Examples:
        >>> generate_id("test")
        'test_abc123def456'
        >>> generate_id()
        'abc123def456'
        >>> generate_id("run")
        'run_9f3a7b2c8d1e'
    """
    unique = uuid.uuid4().hex[:12]
    return f"{prefix}_{unique}" if prefix else unique


def hash_string(text: str, length: Optional[int] = None) -> str:
    """
    Generate SHA-256 hash of a string.
    
    Args:
        text: String to hash
        length: Optional length to truncate hash (default: full 64 chars)
    
    Returns:
        Hexadecimal hash string
    
    Examples:
        >>> hash_string("hello world")
        'b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9'
        >>> hash_string("hello world", length=8)
        'b94d27b9'
    """
    hash_hex = hashlib.sha256(text.encode()).hexdigest()
    return hash_hex[:length] if length else hash_hex


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string
    
    Examples:
        >>> format_duration(65.5)
        '1m 5.5s'
        >>> format_duration(3725)
        '1h 2m 5s'
        >>> format_duration(45)
        '45.0s'
        >>> format_duration(86400)
        '1d 0h 0m'
    """
    if seconds < 0:
        return "0s"
    
    # Less than a minute
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    # Less than an hour
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds:.1f}s"
    
    # Less than a day
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if hours < 24:
        return f"{hours}h {remaining_minutes}m {remaining_seconds:.0f}s"
    
    # Days
    days = hours // 24
    remaining_hours = hours % 24
    
    return f"{days}d {remaining_hours}h {remaining_minutes}m"


def format_timestamp(dt: Optional[datetime] = None, format: str = "iso") -> str:
    """
    Format datetime as string.
    
    Args:
        dt: Datetime to format (default: now)
        format: Format type - 'iso', 'date', 'time', 'datetime'
    
    Returns:
        Formatted timestamp string
    
    Examples:
        >>> format_timestamp()
        '2026-02-16T17:30:45.123456'
        >>> format_timestamp(format='date')
        '2026-02-16'
        >>> format_timestamp(format='time')
        '17:30:45'
    """
    if dt is None:
        dt = datetime.now()
    
    if format == "iso":
        return dt.isoformat()
    elif format == "date":
        return dt.strftime("%Y-%m-%d")
    elif format == "time":
        return dt.strftime("%H:%M:%S")
    elif format == "datetime":
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    else:
        return dt.isoformat()


def parse_timestamp(timestamp: str) -> datetime:
    """
    Parse ISO 8601 timestamp string.
    
    Args:
        timestamp: ISO 8601 formatted string
    
    Returns:
        Datetime object
    
    Examples:
        >>> parse_timestamp('2026-02-16T17:30:45')
        datetime.datetime(2026, 2, 16, 17, 30, 45)
    """
    return datetime.fromisoformat(timestamp)


def safe_json_loads(text: str, default: Any = None) -> Any:
    """
    Safely parse JSON string.
    
    Args:
        text: JSON string to parse
        default: Default value if parsing fails
    
    Returns:
        Parsed JSON or default value
    
    Examples:
        >>> safe_json_loads('{"key": "value"}')
        {'key': 'value'}
        >>> safe_json_loads('invalid json', default={})
        {}
    """
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"Failed to parse JSON: {e}")
        return default


def safe_json_dumps(obj: Any, default: str = "{}") -> str:
    """
    Safely serialize object to JSON.
    
    Args:
        obj: Object to serialize
        default: Default value if serialization fails
    
    Returns:
        JSON string or default value
    
    Examples:
        >>> safe_json_dumps({"key": "value"})
        '{"key": "value"}'
        >>> safe_json_dumps(set([1, 2, 3]), default='[]')
        '[]'
    """
    try:
        return json.dumps(obj, default=str, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        logger.warning(f"Failed to serialize JSON: {e}")
        return default


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to maximum length.
    
    Args:
        text: String to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add if truncated
    
    Returns:
        Truncated string
    
    Examples:
        >>> truncate_string("This is a very long string", max_length=15)
        'This is a ve...'
        >>> truncate_string("Short", max_length=100)
        'Short'
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def calculate_percentage(part: float, total: float, decimals: int = 1) -> float:
    """
    Calculate percentage safely (handles division by zero).
    
    Args:
        part: Part value
        total: Total value
        decimals: Number of decimal places
    
    Returns:
        Percentage (0-100)
    
    Examples:
        >>> calculate_percentage(45, 100)
        45.0
        >>> calculate_percentage(1, 3)
        33.3
        >>> calculate_percentage(5, 0)
        0.0
    """
    if total == 0:
        return 0.0
    percentage = (part / total) * 100
    return round(percentage, decimals)


def merge_dicts(*dicts: Dict) -> Dict:
    """
    Merge multiple dictionaries (later dicts override earlier ones).
    
    Args:
        *dicts: Dictionaries to merge
    
    Returns:
        Merged dictionary
    
    Examples:
        >>> merge_dicts({"a": 1}, {"b": 2}, {"a": 3})
        {'a': 3, 'b': 2}
    """
    result = {}
    for d in dicts:
        if d:
            result.update(d)
    return result


def extract_numbers(text: str) -> List[float]:
    """
    Extract all numbers from a string.
    
    Args:
        text: String containing numbers
    
    Returns:
        List of numbers found
    
    Examples:
        >>> extract_numbers("I have 3 apples and 2.5 oranges")
        [3.0, 2.5]
        >>> extract_numbers("Price: $19.99")
        [19.99]
    """
    pattern = r'-?\d+\.?\d*'
    matches = re.findall(pattern, text)
    return [float(m) for m in matches]


def clean_whitespace(text: str) -> str:
    """
    Clean excessive whitespace from text.
    
    Replaces multiple spaces with single space, removes leading/trailing whitespace.
    
    Args:
        text: Text to clean
    
    Returns:
        Cleaned text
    
    Examples:
        >>> clean_whitespace("  Hello    world  ")
        'Hello world'
    """
    return ' '.join(text.split())


def chunks(lst: List, n: int) -> List[List]:
    """
    Split list into chunks of size n.
    
    Args:
        lst: List to split
        n: Chunk size
    
    Returns:
        List of chunks
    
    Examples:
        >>> chunks([1, 2, 3, 4, 5], 2)
        [[1, 2], [3, 4], [5]]
    """
    return [lst[i:i + n] for i in range(0, len(lst), n)]
