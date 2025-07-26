from pydantic import BaseModel
from typing import List

class SearchRequest(BaseModel):
    chat_id: str
    query: str
    k: int = 5

class SearchResult(BaseModel):
    id: int
    username: str
    alias: str
    text: str
    timestamp: str
    user_id: str = None  # Optional for backward compatibility

class SearchResponse(BaseModel):
    results: List[SearchResult]

class AnalyzeRequest(BaseModel):
    chat_id: str
    query: str
    user_id: str = None
    max_messages: int = 100
    k: int = 5

class AnalyzeSourceMessage(BaseModel):
    text: str
    alias: str
    user_id: str

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
    user_id: str = None  # Optional for backward compatibility

class IngestRequest(BaseModel):
    chat_id: str
    messages: List[Message]

class IngestResponse(BaseModel):
    status: str
    message_count: int
    chat_id: str
