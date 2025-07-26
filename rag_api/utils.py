from datetime import datetime
from typing import Union, Optional

def get_current_timestamp() -> str:
    """Get current UTC timestamp in ISO format"""
    return datetime.utcnow().isoformat() + "Z"

def normalize_timestamp(timestamp: Optional[Union[str, int]]) -> str:
    """
    Normalize timestamp to ISO format string
    
    Args:
        timestamp: Can be ISO string, Unix timestamp, or None
        
    Returns:
        ISO format timestamp string
    """
    if timestamp is None:
        return get_current_timestamp()
    
    if isinstance(timestamp, int):
        # Convert Unix timestamp to ISO format
        return datetime.utcfromtimestamp(timestamp).isoformat() + "Z"
    
    if isinstance(timestamp, str):
        # Assume it's already in correct format, but ensure Z suffix
        if not timestamp.endswith('Z') and '+' not in timestamp:
            return timestamp + "Z"
        return timestamp
    
    # Fallback to current time
    return get_current_timestamp()

def is_timestamp_after(message_timestamp: str, after_timestamp: Union[str, int]) -> bool:
    """
    Check if message timestamp is after the given timestamp
    
    Args:
        message_timestamp: Message timestamp in ISO format
        after_timestamp: Comparison timestamp (ISO string or Unix timestamp)
        
    Returns:
        True if message_timestamp > after_timestamp
    """
    if not after_timestamp:
        return True
    
    try:
        # Parse message timestamp
        if message_timestamp.endswith('Z'):
            msg_dt = datetime.fromisoformat(message_timestamp[:-1])
        else:
            msg_dt = datetime.fromisoformat(message_timestamp)
        
        # Parse comparison timestamp
        if isinstance(after_timestamp, int):
            after_dt = datetime.utcfromtimestamp(after_timestamp)
        else:
            if after_timestamp.endswith('Z'):
                after_dt = datetime.fromisoformat(after_timestamp[:-1])
            else:
                after_dt = datetime.fromisoformat(after_timestamp)
        
        return msg_dt > after_dt
    except (ValueError, TypeError):
        # If parsing fails, include the message
        return True