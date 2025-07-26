from pydantic import BaseModel
from typing import List, Union, Optional

class SearchRequest(BaseModel):
    chat_id: str
    query: str
    k: int = 5
    after_timestamp: Optional[Union[str, int]] = None  # Filter messages after this timestamp

class SearchResult(BaseModel):
    id: int
    username: str
    alias: str
    text: str
    timestamp: str
    user_id: Optional[str] = None  # Optional for backward compatibility
    # New Telegram fields
    message_id: Optional[Union[int, str]] = None
    message_thread_id: Optional[Union[int, str]] = None
    reply_to_message_id: Optional[Union[int, str]] = None
    chat_id: Optional[Union[int, str]] = None

class SearchResponse(BaseModel):
    results: List[SearchResult]

class AnalyzeRequest(BaseModel):
    chat_id: str
    query: str
    user_id: str = None
    max_messages: int = 100
    k: int = 5
    after_timestamp: Optional[Union[str, int]] = None  # Filter messages after this timestamp

class AnalyzeSourceMessage(BaseModel):
    text: str
    alias: str
    user_id: str
    # New Telegram fields
    message_id: Optional[Union[int, str]] = None
    message_thread_id: Optional[Union[int, str]] = None
    reply_to_message_id: Optional[Union[int, str]] = None
    chat_id: Optional[Union[int, str]] = None

class AnalyzeResponse(BaseModel):
    summary: str
    messages_used: int
    source_messages: List[AnalyzeSourceMessage]

class Message(BaseModel):
    id: int
    username: str
    alias: str
    text: str
    timestamp: str
    user_id: Optional[str] = None  # Optional for backward compatibility
    # New Telegram fields for tracking message structure
    message_id: Optional[Union[int, str]] = None
    message_thread_id: Optional[Union[int, str]] = None
    reply_to_message_id: Optional[Union[int, str]] = None
    chat_id: Optional[Union[int, str]] = None

class IngestRequest(BaseModel):
    chat_id: str
    messages: List[Message]

class IngestResponse(BaseModel):
    status: str
    message_count: int
    chat_id: str
