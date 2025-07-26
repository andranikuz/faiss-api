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

class SearchResponse(BaseModel):
    results: List[SearchResult]

class AnalyzeRequest(BaseModel):
    chat_id: str
    query: str
    k: int = 5

class AnalyzeResponse(BaseModel):
    gpt_answer: str
    messages: List[SearchResult]

class Message(BaseModel):
    id: int
    username: str
    alias: str
    text: str
    timestamp: str

class IngestRequest(BaseModel):
    chat_id: str
    messages: List[Message]

class IngestResponse(BaseModel):
    status: str
    message_count: int
    chat_id: str
