import json, os
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from .models import Message
from .config import DATA_DIR, INDEX_DIR
from .utils import normalize_timestamp
from typing import List

# Создаем единственный экземпляр эмбеддингов для переиспользования
embeddings = OpenAIEmbeddings()

def save_messages(chat_id: str, messages: List[Message]):
    from .config import ensure_directories
    ensure_directories()
    
    path = os.path.join(DATA_DIR, f"messages_{chat_id}.jsonl")
    
    with open(path, "w", encoding="utf-8") as f:
        for msg in messages:
            # Ensure timestamp is set
            msg_dict = msg.dict()
            if not msg_dict.get("timestamp"):
                msg_dict["timestamp"] = normalize_timestamp(None)
            else:
                msg_dict["timestamp"] = normalize_timestamp(msg_dict["timestamp"])
            f.write(json.dumps(msg_dict, ensure_ascii=False) + "\n")

def ingest_chat(chat_id: str):
    from .config import ensure_directories
    ensure_directories()
    
    path = os.path.join(DATA_DIR, f"messages_{chat_id}.jsonl")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No chat file: {path}")
    docs = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = json.loads(line)
            # Include alias and user_id in page_content for better search
            user_id = m.get("user_id", m.get("username", "unknown"))
            content = f"{m.get('alias', m.get('username', 'Unknown'))} ({user_id}): {m['text']}"
            
            # Ensure all metadata fields are present (backward compatibility)
            # Normalize timestamp - use current time if not provided
            timestamp = normalize_timestamp(m.get("timestamp"))
            
            metadata = {
                "id": m.get("id"),
                "username": m.get("username"),
                "alias": m.get("alias", ""),
                "text": m.get("text"),
                "timestamp": timestamp,
                "user_id": user_id,
                # New Telegram fields
                "message_id": m.get("message_id"),
                "message_thread_id": m.get("message_thread_id"),
                "reply_to_message_id": m.get("reply_to_message_id"),
                "chat_id": m.get("chat_id")
            }
            
            docs.append(Document(page_content=content, metadata=metadata))
    
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(os.path.join(INDEX_DIR, chat_id))
