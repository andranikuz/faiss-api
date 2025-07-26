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

def get_existing_message_ids(chat_id: str) -> set:
    """Get set of existing message IDs to avoid duplicates"""
    path = os.path.join(DATA_DIR, f"messages_{chat_id}.jsonl")
    existing_ids = set()
    
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        msg = json.loads(line)
                        # Use message_id if available, otherwise use id
                        msg_id = msg.get("message_id") or msg.get("id")
                        if msg_id is not None:
                            existing_ids.add(str(msg_id))
                    except json.JSONDecodeError:
                        continue
        except IOError:
            pass
    
    return existing_ids

def save_messages(chat_id: str, messages: List[Message]) -> dict:
    """
    Append new messages to chat file, avoiding duplicates
    
    Returns:
        dict with added_count and skipped_count
    """
    from .config import ensure_directories
    ensure_directories()
    
    path = os.path.join(DATA_DIR, f"messages_{chat_id}.jsonl")
    existing_ids = get_existing_message_ids(chat_id)
    
    added_count = 0
    skipped_count = 0
    
    # Append mode to add only new messages
    with open(path, "a", encoding="utf-8") as f:
        for msg in messages:
            msg_dict = msg.dict()
            
            # Check for duplicates using message_id or id
            msg_id = msg_dict.get("message_id") or msg_dict.get("id")
            if msg_id is not None and str(msg_id) in existing_ids:
                skipped_count += 1
                continue
            
            # Ensure timestamp is set
            if not msg_dict.get("timestamp"):
                msg_dict["timestamp"] = normalize_timestamp(None)
            else:
                msg_dict["timestamp"] = normalize_timestamp(msg_dict["timestamp"])
            
            f.write(json.dumps(msg_dict, ensure_ascii=False) + "\n")
            added_count += 1
    
    return {"added_count": added_count, "skipped_count": skipped_count}

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
