import os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from .models import SearchResult
from .config import INDEX_DIR
from .utils import is_timestamp_after
from .query_enhancer import enhance_search_query, should_enhance_query
from typing import Union, Optional

# Создаем единственный экземпляр эмбеддингов для переиспользования
embeddings = OpenAIEmbeddings()

def search(chat_id: str, query: str, k: int = 5, after_timestamp: Optional[Union[str, int]] = None, enhance_query: bool = True) -> list[SearchResult]:
    # Enhance query with GPT if enabled
    search_query = query
    if enhance_query:
        search_query = enhance_search_query(query)
        print(f"Enhanced query: '{query}' → '{search_query}'")  # Debug log
    
    db = FAISS.load_local(
	    os.path.join(INDEX_DIR, chat_id),
	    embeddings,
	    allow_dangerous_deserialization=True
	)
    
    # Get more results if we need to filter by timestamp
    search_k = k * 3 if after_timestamp else k
    results = db.similarity_search(search_query, k=search_k)
    
    search_results = []
    for doc in results:
        # Filter by timestamp if specified
        if after_timestamp:
            message_timestamp = doc.metadata.get("timestamp", "")
            if not is_timestamp_after(message_timestamp, after_timestamp):
                continue
        
        result = SearchResult(
            id=doc.metadata.get("id"),
            username=doc.metadata.get("username", ""),
            alias=doc.metadata.get("alias", ""),
            text=doc.metadata.get("text", ""),
            timestamp=doc.metadata.get("timestamp", ""),
            user_id=doc.metadata.get("user_id"),
            # New Telegram fields
            message_id=doc.metadata.get("message_id"),
            message_thread_id=doc.metadata.get("message_thread_id"),
            reply_to_message_id=doc.metadata.get("reply_to_message_id"),
            chat_id=doc.metadata.get("chat_id")
        )
        search_results.append(result)
        
        # Stop when we have enough results
        if len(search_results) >= k:
            break
    
    return search_results
